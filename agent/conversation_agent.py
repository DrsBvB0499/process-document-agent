"""Conversation Agent — interface-agnostic conversational analysis agent.

This is a refactored conversation agent designed to be called as a pure function:
    (message: str, user_id: str, user_role: str, project_id: str) → response: str

Features:
- Reads gap brief from Gap Analyzer before asking questions
- Only asks about gaps (never re-asks what's known)
- Role-aware: adjusts depth and vocabulary based on user role
- Incremental: appends new knowledge to knowledge_base.json
- Cost-tracked: logs all API calls to cost_log.json

The agent operates in two modes:
1. Interviewing mode: guides user through gap-filling questions
2. Clarification mode: dives deep on a specific topic based on user interest

Usage:
    from agent.conversation_agent import ConversationAgent
    
    ca = ConversationAgent()
    response = ca.handle_message(
        message="Tell me about the approval process",
        user_id="rachel.chen@company.com",
        user_role="process_owner",
        project_id="sd-light-invoicing"
    )
    print(response)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from agent.llm import call_model
from agent.gap_analyzer import GapAnalyzer
from agent.validators import validate_project_id, validate_user_role
from agent.hybrid_security import HybridSecurityChecker
from agent.security_logger import SecurityLogger


class ConversationAgent:
    """Conversational agent for gap-guided knowledge gathering."""

    # Role-aware question depth and vocabulary
    ROLE_CONFIG = {
        "process_owner": {
            "depth": "strategic",
            "focus": ["ownership", "strategy", "metrics"],
            "vocabulary": "business",
        },
        "business_analyst": {
            "depth": "analytical",
            "focus": ["workflow", "rules", "exceptions"],
            "vocabulary": "analysis",
        },
        "sme": {
            "depth": "tactical",
            "focus": ["steps", "systems", "workarounds"],
            "vocabulary": "technical",
        },
        "developer": {
            "depth": "technical",
            "focus": ["systems", "data", "integration"],
            "vocabulary": "technical",
        },
    }

    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize the Conversation Agent.

        Args:
            projects_root: Root directory for projects.
        """
        self.projects_root = Path(
            projects_root or (Path(__file__).parent.parent / "projects")
        )
        self.gap_analyzer = GapAnalyzer(projects_root)
        self.security_checker = HybridSecurityChecker(self.projects_root)
        self.security_logger = SecurityLogger(self.projects_root)

    # Language names for LLM prompt instructions
    LANG_NAMES = {"en": "English", "nl": "Dutch (Nederlands)"}

    # Completeness threshold for triggering deliverable generation
    GENERATION_THRESHOLD = 80

    # Short confirmatory replies that signal "proceed with generation"
    CONFIRMATION_PATTERNS = [
        "yes", "yeah", "yep", "sure", "go ahead", "do it", "proceed",
        "generate", "that's it", "that's all", "nope", "no more",
        "nothing else", "that's perfect", "looks good", "sounds good",
        "perfect", "ok", "okay", "correct", "no changes", "nothing to add",
        "let's go", "start", "make it", "create", "alright",
    ]

    def handle_message(
        self,
        message: str,
        user_id: str,
        user_role: str,
        project_id: str,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Handle a message from the user and return a response.

        This is the main entry point for the conversation agent.
        It's interface-agnostic: can be called from CLI, web, or Teams.

        Args:
            message: The user's message (use "__START__" for initial greeting)
            user_id: Email or identifier of the user
            user_role: Role of the user (process_owner, sme, etc.)
            project_id: The project being worked on
            lang: ISO 639-1 language code (default "en")

        Returns:
            Dict with:
                - response (str): Text response to show the user
                - trigger_generation (bool): True if deliverable generation should start
                - completeness_pct (int): Current overall completeness
                - phase (str): Current project phase
        """
        def _wrap(text: str, trigger: bool = False, pct: int = 0, phase: str = "standardization") -> Dict[str, Any]:
            return {"response": text, "trigger_generation": trigger, "completeness_pct": pct, "phase": phase}

        # Validate inputs to prevent path traversal and injection attacks
        if not validate_project_id(project_id):
            return _wrap(f"Error: Invalid project ID '{project_id}'. Project IDs must contain only lowercase letters, numbers, and hyphens.")

        if not validate_user_role(user_role):
            return _wrap(f"Error: Invalid user role '{user_role}'. Valid roles are: process_owner, business_analyst, sme, developer.")

        # SECURITY: Check for prompt injection (skip for initial greeting)
        if message.strip() != "__START__":
            security_check = self.security_checker.check_input(
                user_input=message,
                project_id=project_id,
                context="conversation"
            )

            # Log security event
            if not security_check.is_safe:
                self.security_logger.log_event(
                    event_type="prompt_injection_detected" if security_check.risk_level == "critical" else "suspicious_input",
                    project_id=project_id,
                    user_id=user_id,
                    risk_level=security_check.risk_level,
                    threats=security_check.threats_detected,
                    details={
                        "input_preview": message[:200],
                        "check_method": security_check.check_method,
                        "context": "conversation",
                        "user_role": user_role
                    }
                )

            # Block critical threats
            if security_check.risk_level == "critical":
                return _wrap(
                    "I detected a potential security issue with your message. "
                    "Please rephrase your question without special instructions or commands. "
                    "If you believe this is an error, please contact support."
                )

            # For suspicious inputs, use sanitized version
            if security_check.risk_level in ["medium", "high"]:
                message = security_check.sanitized_input

        # REAL-TIME LEARNING: Process user's message BEFORE generating response
        # This ensures the next question is based on updated knowledge
        if message.strip() != "__START__":
            # Step 1: Extract structured facts from user's answer
            extracted_facts = self._extract_facts_from_message(
                message=message,
                project_id=project_id
            )

            # Step 2: Append new facts to knowledge base
            if extracted_facts:
                self._update_knowledge_base(
                    project_id=project_id,
                    new_facts=extracted_facts
                )

        # Step 3: Get FRESH gap brief (now includes any newly extracted facts)
        gap_brief = self.gap_analyzer.analyze_project(project_id)
        if gap_brief.get("status") != "success":
            return _wrap("Error loading project gaps. Please ensure the project exists and has a knowledge base.")

        # Extract completeness and phase for generation trigger logic
        overall_pct = gap_brief.get("overall_completeness_pct", gap_brief.get("overall_completeness", 0))
        phase = gap_brief.get("phase", "standardization")

        # Step 4: Generate response based on UPDATED gaps
        # Check if this is an initial greeting request
        if message.strip() == "__START__":
            response = self._generate_initial_greeting(
                user_id=user_id,
                user_role=user_role,
                gap_brief=gap_brief,
                project_id=project_id,
                lang=lang,
            )
        else:
            # Normal conversation flow with fresh gap analysis
            response = self._generate_response(
                message=message,
                user_role=user_role,
                gap_brief=gap_brief,
                project_id=project_id,
                lang=lang,
            )

        # Step 5: Check if we should trigger deliverable generation
        trigger = (
            message.strip() != "__START__"
            and self._is_user_confirming_generation(message, overall_pct)
        )

        # Step 6: Log conversation turn
        if message.strip() != "__START__":
            self._log_conversation(
                project_id=project_id,
                user_id=user_id,
                user_role=user_role,
                user_message=message,
                agent_response=response,
            )

        return _wrap(response, trigger=trigger, pct=overall_pct, phase=phase)

    def _generate_response(
        self,
        message: str,
        user_role: str,
        gap_brief: Dict[str, Any],
        project_id: str,
        lang: str = "en",
    ) -> str:
        """Generate a response guided by gap brief."""
        role_config = self.ROLE_CONFIG.get(user_role, self.ROLE_CONFIG["sme"])

        # Load full conversation history so the LLM retains context
        conversation_history = self._get_recent_history(project_id, limit=50)

        # Load knowledge base facts so the LLM knows what's already gathered
        knowledge_summary = self._format_knowledge_for_prompt(project_id)

        # Build a prompt that tells the LLM what gaps exist and what to ask
        prompt = self._build_response_prompt(
            user_message=message,
            role_config=role_config,
            gap_brief=gap_brief,
            conversation_history=conversation_history,
            knowledge_summary=knowledge_summary,
        )

        # Build language system prompt if not English
        system_prompt = None
        if lang != "en":
            lang_name = self.LANG_NAMES.get(lang, lang)
            system_prompt = f"IMPORTANT: You MUST respond entirely in {lang_name}. All questions, explanations, and examples must be in {lang_name}."

        # Call LLM
        result = call_model(
            project_id=project_id,
            agent="conversation_agent",
            prompt=prompt,
            system_prompt=system_prompt,
        )

        response_text = result.get("text", "I couldn't generate a response.")

        # Clean up any model artifacts (e.g., markdown code blocks)
        response_text = self._clean_response(response_text)

        return response_text

    def _generate_initial_greeting(
        self,
        user_id: str,
        user_role: str,
        gap_brief: Dict[str, Any],
        project_id: str,
        lang: str = "en",
    ) -> str:
        """Generate a personalized initial greeting based on project state."""
        # Load project info
        project_path = self.projects_root / project_id
        project_file = project_path / "project.json"

        project_info = {}
        if project_file.exists():
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_info = json.load(f)
            except Exception:
                pass

        # Extract user name from user_id (if it's an email, use first part)
        user_name = user_id.split('@')[0].replace('.', ' ').replace('_', ' ').title() if '@' in user_id else user_id
        if user_name == "web-user":
            user_name = None  # Don't use generic name

        # Get project details
        project_name = project_info.get('project_name', 'this project')
        current_phase = project_info.get('current_phase', 'standardization')

        # Get knowledge base stats
        kb_path = project_path / "knowledge" / "extracted" / "knowledge_base.json"
        kb_facts = 0
        if kb_path.exists():
            try:
                with open(kb_path, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
                    kb_facts = len(kb.get('facts', []))
            except Exception:
                pass

        # Get overall completeness
        deliverable_gaps = gap_brief.get("deliverable_gaps", [])
        overall_completeness = gap_brief.get("overall_completeness", 0)

        # Find least complete deliverable
        focus_gap = None
        if deliverable_gaps:
            incomplete_gaps = [g for g in deliverable_gaps if g.get("missing_fields")]
            if incomplete_gaps:
                focus_gap = min(incomplete_gaps, key=lambda g: g.get("completeness_pct", 100))

        # Build greeting prompt
        greeting_prompt = f"""You are a concise, professional consultant starting a conversation about process improvement.

PROJECT CONTEXT:
- Project: {project_name}
- Current Phase: {current_phase}
- Knowledge Base: {kb_facts} facts extracted
- Overall Progress: {overall_completeness}% complete
- User Role: {user_role}
{"- User Name: " + user_name if user_name else "- User Name: Unknown"}

NEXT FOCUS AREA:
{f"- {focus_gap.get('deliverable')} ({focus_gap.get('completeness_pct')}% complete)" if focus_gap else "- All deliverables mostly complete"}

TASK:
Write a concise, personalized greeting to start the conversation. Follow this structure:

1. Greet the user by name if known (otherwise just say "Hi there!")
2. Briefly acknowledge progress ({kb_facts} facts extracted, {overall_completeness}% complete)
3. Mention current phase in one short phrase
4. Suggest next focus area (based on the gap)
5. Ask if that works or if they have something else in mind

TONE: Professional, encouraging, get-to-the-point.
LENGTH: 2-3 sentences maximum (aim for 40-60 words total).

COMMUNICATION STYLE:
- Be CONCISE - cut any unnecessary words
- Skip fluff like "great to see you", "really helpful", "solid start"
- Lead with the key information
- Make it feel efficient and purposeful

EXAMPLE (55 words):
"Hi Sarah! You've extracted 47 facts for the knowledge base. We're in the Standardization phase, focusing on defining current processes. Next, we should document the exception_register to keep things moving forward. Does that sound like a good plan, or is there another area you'd like to explore first?"

Now write a similar greeting for this user and project. Keep it under 60 words.
"""

        # Build language system prompt if not English
        system_prompt = None
        if lang != "en":
            lang_name = self.LANG_NAMES.get(lang, lang)
            system_prompt = f"IMPORTANT: You MUST respond entirely in {lang_name}. All questions, explanations, and examples must be in {lang_name}."

        # Call LLM to generate greeting
        result = call_model(
            project_id=project_id,
            agent="conversation_agent",
            prompt=greeting_prompt,
            system_prompt=system_prompt,
        )

        greeting = result.get("text", "Hello! Ready to work on this project together?")
        greeting = self._clean_response(greeting)

        return greeting

    def _get_recent_history(self, project_id: str, limit: int = 20) -> str:
        """Load recent conversation turns to provide context.

        Args:
            project_id: The project ID
            limit: Maximum number of recent turns to include

        Returns:
            Formatted conversation history string
        """
        session_data = self.get_session_history(project_id)
        turns = session_data.get("turns", [])

        if not turns:
            return "No previous conversation history."

        # Get last N turns (increased from 5 to 20 to prevent loops)
        recent_turns = turns[-limit:] if len(turns) > limit else turns

        # Format for prompt
        history_lines = []
        for turn in recent_turns:
            user_msg = turn.get("user_message", "")
            agent_resp = turn.get("agent_response", "")
            history_lines.append(f"User: {user_msg}")
            history_lines.append(f"Agent: {agent_resp}")

        return "\n".join(history_lines)

    def _format_knowledge_for_prompt(self, project_id: str) -> str:
        """Load knowledge base and format facts for inclusion in LLM prompt."""
        kb_path = self.projects_root / project_id / "knowledge" / "extracted" / "knowledge_base.json"
        if not kb_path.exists():
            return "No knowledge base yet."

        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
        except Exception:
            return "No knowledge base yet."

        facts = kb_data.get("facts", [])
        if not facts:
            return "No facts gathered yet."

        # Group by category
        by_category: Dict[str, list] = {}
        for fact in facts:
            cat = fact.get("category", "general")
            by_category.setdefault(cat, []).append(fact.get("fact", str(fact)))

        lines = []
        for cat, items in sorted(by_category.items()):
            lines.append(f"  {cat.upper().replace('_', ' ')}:")
            for item in items:
                lines.append(f"    - {item}")
        return "\n".join(lines)

    def _build_response_prompt(
        self,
        user_message: str,
        role_config: Dict[str, Any],
        gap_brief: Dict[str, Any],
        conversation_history: str = "",
        knowledge_summary: str = "",
    ) -> str:
        """Build a prompt that guides the LLM on how to respond."""
        deliverable_gaps = gap_brief.get("deliverable_gaps", [])
        overall_pct = gap_brief.get("overall_completeness_pct", gap_brief.get("overall_completeness", 0))

        # Find the most important gap to focus on (lowest completeness first)
        focus_gap = None
        if deliverable_gaps:
            incomplete_gaps = [g for g in deliverable_gaps if g.get("missing_fields")]
            if incomplete_gaps:
                focus_gap = min(incomplete_gaps, key=lambda g: g.get("completeness_pct", 100))

        role = role_config.get("vocabulary", "technical")
        depth = role_config.get("depth", "tactical")

        # Build readiness block for high-completeness scenarios
        if overall_pct >= self.GENERATION_THRESHOLD:
            readiness_block = f"""
🎯 HIGH COMPLETENESS ({overall_pct}%) — WRAP-UP MODE:
We have enough information to generate deliverables. DO NOT ask more questions.
Instead:
1. Briefly summarize key facts gathered (2-3 bullet points)
2. Tell the user we're at {overall_pct}% completeness — enough to generate deliverables
3. Ask: "Shall I generate your deliverables now, or is there anything else you'd like to add?"
If the user just confirmed or said "yes"/"sure"/"nope"/"that's it", respond:
"Generating your deliverables now..."
DO NOT ask about tools, visualization, formatting, or other implementation details — those are already configured.
"""
        else:
            readiness_block = ""

        # Build context about what's missing
        if focus_gap:
            missing_fields = focus_gap.get("missing_fields", [])
            focus_field = missing_fields[0] if missing_fields else None
            gap_context = f"""
CURRENT FOCUS: {focus_gap.get('deliverable')} ({focus_gap.get('completeness_pct')}% complete)
NEXT ITEM TO GATHER: {focus_field if focus_field else 'general information'}
STILL MISSING: {', '.join(missing_fields[:3])}
"""
        else:
            gap_context = "All key information appears to be gathered. You're in clarification mode."

        return f"""You are a concise, professional consultant helping to document a business process.

USER'S ROLE: {role.capitalize()} | CONVERSATION STYLE: {depth}

===== KNOWN FACTS (from documents + conversations — DO NOT re-ask these!) =====
{knowledge_summary if knowledge_summary else "No facts gathered yet."}
================================================================================

===== FULL CONVERSATION HISTORY (READ THIS CAREFULLY!) =====
{conversation_history if conversation_history else "No previous conversation."}
==============================================================

USER'S CURRENT MESSAGE:
"{user_message}"

WHAT WE'RE WORKING ON:
{gap_context}
{readiness_block}
🚨 ABSOLUTE RULE: USE EXISTING KNOWLEDGE 🚨
- You MUST reference the KNOWN FACTS above when relevant
- NEVER ask for information that already appears in KNOWN FACTS or conversation history
- If the user says "I already told you" or similar, find the answer in the sections above and acknowledge it
- When summarizing or drafting (e.g., flowchart steps), pull ALL details from KNOWN FACTS + history

🚨 CRITICAL: DETECT LOOP SITUATIONS 🚨
If the user says ANY of these phrases, you are in a LOOP and must STOP:
- "I already told you this"
- "You already asked me that"
- "You're repeating yourself"
- "We already discussed this"
- "I shared that information earlier"
- "this information is already available in the documents"

When detected, you MUST:
1. Apologize sincerely for the repetition
2. Review the history above to find what they told you
3. Acknowledge the specific information they provided
4. Move to a COMPLETELY DIFFERENT topic from the gap context
5. DO NOT ask for clarification on the same topic again

COMMUNICATION STYLE GUIDELINES:
1. ✅ **BE CONCISE**: Aim for 20-40 words per message (exceptions: when explaining process concepts like SIPOC, VSM)
2. ✅ **KNOWLEDGE-FIRST**: Before asking ANY question, check if the answer is in documents or conversation history
3. ✅ **NO FLUFF**: Skip "Thank you for sharing", "This is really helpful", "Great!", etc. Just acknowledge briefly and move forward.
4. ✅ **EXPLAIN PROCESS CONCEPTS, NOT THEIR BUSINESS**:
   - DO explain: What a SIPOC is, why we need baseline metrics, what a process map shows
   - DON'T explain: What exceptions are, what invoices are, what approvals mean (they know their domain!)
5. ✅ **LEAD WITH THE QUESTION**: Put your actual question in the FIRST sentence, not buried at the end
6. ✅ **MATCH USER'S STYLE**: If they give brief answers (5-10 words), keep YOUR responses brief too
7. ✅ **GENERAL EXAMPLES ARE FINE**: Use simple, relatable examples when explaining process concepts (keep them short)
8. ✅ **SHOW YOUR WORK**: Reference documents you've read: "I see in the PDD that..." or "Based on the documents..."

CRITICAL CONVERSATION RULES:
1. **READ THE ENTIRE HISTORY ABOVE** - Before asking ANY question, scan the full history to see if the user already answered it!
2. **ONE QUESTION AT A TIME** - Never ask multiple questions in one response
3. **SIMPLE LANGUAGE** - Avoid jargon unless explaining a process improvement concept
4. **MOVE FORWARD** - If they've answered your question, acknowledge it briefly and move to the NEXT gap item
5. **CHECK FOR DUPLICATES** - Before asking about exceptions, frequency, tracking, or handling, search the history above first!
6. **NEVER ASK ABOUT IMPLEMENTATION DETAILS** - Do NOT ask about tools, visualization preferences, file formats, rendering methods, diagram styles, or technical implementation choices. These are already configured in the system (e.g., flowcharts use Mermaid, documents are auto-generated). Focus ONLY on gathering business process information: steps, performers, systems, exceptions, metrics, decisions.

RESPONSE STRUCTURE (follow this exactly):
- LEAD with your question or the key point (first sentence)
- If needed: Brief explanation of WHY you're asking (one sentence)
- If helpful: Short example to clarify (keep it under 15 words)
- NEVER end with "What else would you like to share?" - be specific!

EXAMPLE GOOD RESPONSE (CONCISE):
"What happens after the requestor and OTC team receive the exception notification? Is there a standard process to correct the issue?"

EXAMPLE BAD RESPONSE (DON'T DO THIS - TOO WORDY):
"Thank you for explaining how the RPA script handles exceptions by flagging them and notifying both the requestor and the OTC team. This is a crucial part of managing exceptions effectively. To help us create a comprehensive flowchart, it would be helpful to understand what happens after the requestor and the OTC team receive the notification. For example, do they have a specific process to follow to correct the issue, or is there a standard procedure in place? Could you describe the steps taken to address these exceptions?"

EXAMPLE WHEN EXPLAINING A PROCESS CONCEPT:
"We're building a SIPOC table - that's Suppliers, Inputs, Process, Outputs, Customers. It's a one-page view of your entire process. Who are the main suppliers (people/systems that provide information to start your process)?"

Now respond to the user's message following these rules. REMEMBER:
- Be CONCISE (20-40 words typical)
- LEAD with the question
- Check history before asking
- Skip fluff and repetitive acknowledgments
"""

    def _clean_response(self, text: str) -> str:
        """Clean up response text (remove code blocks, markdown artifacts)."""
        # Remove markdown code blocks if present
        if "```" in text:
            parts = text.split("```")
            text = parts[0]  # Take text before first code block

        text = text.strip()
        return text

    def _is_user_confirming_generation(self, message: str, overall_pct: int) -> bool:
        """Check if user is giving a short confirmatory reply when completeness is high.

        Only returns True when overall completeness >= GENERATION_THRESHOLD
        AND the message is a brief affirmative (≤ 8 words).
        """
        if overall_pct < self.GENERATION_THRESHOLD:
            return False
        cleaned = message.strip().lower().rstrip("!.,;:")
        if len(cleaned.split()) > 8:
            return False
        return any(pattern in cleaned for pattern in self.CONFIRMATION_PATTERNS)

    def _log_conversation(
        self,
        project_id: str,
        user_id: str,
        user_role: str,
        user_message: str,
        agent_response: str,
    ) -> None:
        """Log the conversation turn to a session file."""
        project_path = self.projects_root / project_id
        sessions_path = project_path / "knowledge" / "sessions"
        sessions_path.mkdir(parents=True, exist_ok=True)

        # Use today's date as session file name
        session_file = sessions_path / f"session_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Load existing session or create new
        session_data = []
        if session_file.exists():
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
            except Exception:
                session_data = []

        # Append turn
        turn = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "user_role": user_role,
            "user_message": user_message,
            "agent_response": agent_response,
        }
        session_data.append(turn)

        # Save
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silently fail on logging errors

    def _extract_facts_from_message(
        self,
        message: str,
        project_id: str
    ) -> list:
        """Extract structured facts from user's message using LLM.

        This enables real-time learning during conversations.

        Args:
            message: The user's message text
            project_id: The project ID (for cost logging)

        Returns:
            List of extracted facts with category, fact, and confidence
        """
        # Build extraction prompt
        extraction_prompt = f"""Extract structured facts from this user message about a business process.

USER MESSAGE:
"{message}"

INSTRUCTIONS:
1. Identify any factual information about the process
2. Categorize each fact appropriately
3. Only extract clear, specific information (not vague statements)
4. If the message is just a question or complaint, return an empty list

CATEGORIES:
- process_owner: Who owns/manages the process
- suppliers: Who provides inputs/information
- inputs: What information/materials are needed
- outputs: What is produced/delivered
- customers: Who receives the outputs
- process_steps: Individual steps in the process
- teams: Teams involved and their roles
- systems: Software/tools used
- metrics: Numbers, measurements, KPIs
- decisions: Decision points or rules
- constraints: Limitations or requirements
- exceptions: Error scenarios or edge cases

OUTPUT FORMAT (JSON):
{{
  "facts": [
    {{
      "category": "category_name",
      "fact": "specific fact statement",
      "confidence": 0.9
    }}
  ]
}}

If no facts can be extracted, return: {{"facts": []}}

Extract facts from the user message now:"""

        try:
            # Call LLM to extract facts
            result = call_model(
                project_id=project_id,
                agent="conversation_agent",
                prompt=extraction_prompt,
            )

            # Parse JSON response
            response_text = result.get("text", "").strip()

            # Clean up markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            facts_data = json.loads(response_text)
            return facts_data.get("facts", [])

        except Exception as e:
            # If extraction fails, return empty list (don't break the conversation)
            return []

    def _update_knowledge_base(
        self,
        project_id: str,
        new_facts: list
    ) -> None:
        """Append new facts to the knowledge base.

        This updates knowledge_base.json with facts learned from conversation.

        Args:
            project_id: The project ID
            new_facts: List of facts to append
        """
        if not new_facts:
            return

        project_path = self.projects_root / project_id
        kb_path = project_path / "knowledge" / "extracted" / "knowledge_base.json"

        # Load existing knowledge base
        kb_data = {"facts": [], "sources": [], "exceptions": [], "unknowns": []}
        if kb_path.exists():
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    kb_data = json.load(f)
            except Exception:
                pass

        # Append new facts
        existing_facts = kb_data.get("facts", [])
        for new_fact in new_facts:
            # Simple duplicate check (same category + similar text)
            is_duplicate = False
            for existing in existing_facts:
                if (existing.get("category") == new_fact.get("category") and
                    existing.get("fact", "").lower() == new_fact.get("fact", "").lower()):
                    is_duplicate = True
                    break

            if not is_duplicate:
                existing_facts.append(new_fact)

        kb_data["facts"] = existing_facts
        kb_data["last_updated"] = datetime.utcnow().isoformat() + "Z"

        # Save updated knowledge base
        kb_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(kb_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silently fail on save errors


    def get_session_history(self, project_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve conversation history for a session.
        
        Args:
            project_id: The project ID
            date: ISO date string (e.g., "2026-02-09") or None for today
        
        Returns:
            Dictionary with turns from that session
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        project_path = self.projects_root / project_id
        session_file = project_path / "knowledge" / "sessions" / f"session_{date}.json"

        if not session_file.exists():
            return {"date": date, "turns": [], "message": "No session found for this date"}

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                turns = json.load(f)
            return {"date": date, "turns": turns, "count": len(turns)}
        except Exception:
            return {"date": date, "turns": [], "error": "Could not read session file"}


if __name__ == "__main__":
    # Quick test: simulate a conversation turn
    ca = ConversationAgent()
    result = ca.handle_message(
        message="Our invoice process handles about 600 invoices a day.",
        user_id="test@example.com",
        user_role="sme",
        project_id="test-project",
    )
    print(f"Agent response:\n{result['response']}")
    print(f"Trigger generation: {result['trigger_generation']}")
    print(f"Completeness: {result['completeness_pct']}%")

    # Check session history
    history = ca.get_session_history("test-project")
    print(f"\nSession turns: {history.get('count', 0)}")
