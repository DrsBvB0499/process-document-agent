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

    def handle_message(
        self,
        message: str,
        user_id: str,
        user_role: str,
        project_id: str,
    ) -> str:
        """Handle a message from the user and return a response.

        This is the main entry point for the conversation agent.
        It's interface-agnostic: can be called from CLI, web, or Teams.

        Args:
            message: The user's message (use "__START__" for initial greeting)
            user_id: Email or identifier of the user
            user_role: Role of the user (process_owner, sme, etc.)
            project_id: The project being worked on

        Returns:
            Response string to send back to the user
        """
        # Validate inputs to prevent path traversal and injection attacks
        if not validate_project_id(project_id):
            return f"Error: Invalid project ID '{project_id}'. Project IDs must contain only lowercase letters, numbers, and hyphens."

        if not validate_user_role(user_role):
            return f"Error: Invalid user role '{user_role}'. Valid roles are: process_owner, business_analyst, sme, developer."

        # Get gap brief
        gap_brief = self.gap_analyzer.analyze_project(project_id)
        if gap_brief.get("status") != "success":
            return "Error loading project gaps. Please ensure the project exists and has a knowledge base."

        # Check if this is an initial greeting request
        if message.strip() == "__START__":
            response = self._generate_initial_greeting(
                user_id=user_id,
                user_role=user_role,
                gap_brief=gap_brief,
                project_id=project_id,
            )
        else:
            # Normal conversation flow
            response = self._generate_response(
                message=message,
                user_role=user_role,
                gap_brief=gap_brief,
                project_id=project_id,
            )

        # Append learnings to knowledge base (simplified: user message itself is logged)
        # Skip logging for __START__ messages
        if message.strip() != "__START__":
            self._log_conversation(
                project_id=project_id,
                user_id=user_id,
                user_role=user_role,
                user_message=message,
                agent_response=response,
            )

        return response

    def _generate_response(
        self,
        message: str,
        user_role: str,
        gap_brief: Dict[str, Any],
        project_id: str,
    ) -> str:
        """Generate a response guided by gap brief."""
        role_config = self.ROLE_CONFIG.get(user_role, self.ROLE_CONFIG["sme"])

        # Load recent conversation history to avoid asking same questions
        conversation_history = self._get_recent_history(project_id, limit=5)

        # Build a prompt that tells the LLM what gaps exist and what to ask
        prompt = self._build_response_prompt(
            user_message=message,
            role_config=role_config,
            gap_brief=gap_brief,
            conversation_history=conversation_history,
        )

        # Call LLM
        result = call_model(
            project_id=project_id,
            agent="conversation_agent",
            prompt=prompt,
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
        greeting_prompt = f"""You are a friendly consultant starting a conversation about process improvement.

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
Write a warm, personalized greeting to start the conversation. Follow this structure:

1. Greet the user by name if known (otherwise just say "Hi there!")
2. Acknowledge what's been done so far (files processed, progress made)
3. Mention the current phase and what that means
4. Suggest what to work on next (based on the focus area)
5. Give them control - ask if they want to work on that, or have something else in mind

TONE: Friendly, encouraging, professional. Make them feel like progress is being made.
LENGTH: 3-4 sentences maximum.

EXAMPLE:
"Hi Sarah, great to see you! I can see you've uploaded and processed some documents - we now have 47 facts in the knowledge base, which is a solid start. We're currently in the Standardization phase, where we're mapping out how the process works today. I think we should focus on identifying who provides information for this process - does that sound good, or did you have something else you wanted to discuss first?"

Now write a similar greeting for this user and project.
"""

        # Call LLM to generate greeting
        result = call_model(
            project_id=project_id,
            agent="conversation_agent",
            prompt=greeting_prompt,
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

    def _build_response_prompt(
        self,
        user_message: str,
        role_config: Dict[str, Any],
        gap_brief: Dict[str, Any],
        conversation_history: str = "",
    ) -> str:
        """Build a prompt that guides the LLM on how to respond."""
        deliverable_gaps = gap_brief.get("deliverable_gaps", [])

        # Find the most important gap to focus on (lowest completeness first)
        focus_gap = None
        if deliverable_gaps:
            incomplete_gaps = [g for g in deliverable_gaps if g.get("missing_fields")]
            if incomplete_gaps:
                focus_gap = min(incomplete_gaps, key=lambda g: g.get("completeness_pct", 100))

        role = role_config.get("vocabulary", "technical")
        depth = role_config.get("depth", "tactical")

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

        return f"""You are a friendly, patient consultant helping to document a business process.

USER'S ROLE: {role.capitalize()} | CONVERSATION STYLE: {depth}

===== FULL CONVERSATION HISTORY (READ THIS CAREFULLY!) =====
{conversation_history if conversation_history else "No previous conversation."}
==============================================================

USER'S CURRENT MESSAGE:
"{user_message}"

WHAT WE'RE WORKING ON:
{gap_context}

🚨 CRITICAL: DETECT LOOP SITUATIONS 🚨
If the user says ANY of these phrases, you are in a LOOP and must STOP:
- "I already told you this"
- "You already asked me that"
- "You're repeating yourself"
- "We already discussed this"
- "I shared that information earlier"

When detected, you MUST:
1. Apologize sincerely for the repetition
2. Review the history above to find what they told you
3. Acknowledge the specific information they provided
4. Move to a COMPLETELY DIFFERENT topic from the gap context
5. DO NOT ask for clarification on the same topic again

CRITICAL CONVERSATION RULES:
1. **READ THE ENTIRE HISTORY ABOVE** - Before asking ANY question, scan the full history to see if the user already answered it!
2. **ONE QUESTION AT A TIME** - Never ask multiple questions in one response
3. **EXPLAIN FIRST** - Before asking, explain what you're asking for in simple terms (no jargon like "SIPOC")
4. **PROVIDE AN EXAMPLE** - Give a concrete example to help the user understand
5. **EXPLAIN WHY** - Tell them why this information is important for the analysis
6. **BE ENCOURAGING** - Acknowledge what they've already shared before asking for more
7. **SIMPLE LANGUAGE** - Avoid technical terms unless the user is a developer
8. **MOVE FORWARD** - If they've answered your question, acknowledge it and move to the NEXT gap item
9. **CHECK FOR DUPLICATES** - Before asking about exceptions, frequency, tracking, or handling, search the history above first!

RESPONSE STRUCTURE (follow this exactly):
- First: Acknowledge their input or answer their question warmly
- Second: If asking for information, explain what you need in simple terms
- Third: Provide a concrete example to guide them
- Fourth: Ask ONE specific question
- NEVER end with "What else would you like to share?" - be specific!

EXAMPLE GOOD RESPONSE:
"Great! The information about your approval workflow is really helpful. I can see there are multiple steps involved.

To help map this out clearly, I need to understand who provides the information at the start of this process. By 'providers' I mean anyone who sends you data, documents, or requests that kick off the workflow.

For example, in an invoice process, the suppliers might be: vendors (who send invoices), the purchasing team (who provide purchase orders), or employees (who submit expense reports).

Can you tell me who the main providers of information are for your process?"

EXAMPLE BAD RESPONSE (DON'T DO THIS):
"Thanks for sharing! We still need details on suppliers, inputs, performers, decisions, and metrics. Could you provide more information on these areas? What else would you like to share?"

Now respond to the user's message following these rules. REMEMBER: Read the full history above before asking ANY question!
"""

    def _clean_response(self, text: str) -> str:
        """Clean up response text (remove code blocks, markdown artifacts)."""
        # Remove markdown code blocks if present
        if "```" in text:
            parts = text.split("```")
            text = parts[0]  # Take text before first code block

        text = text.strip()
        return text

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
    response = ca.handle_message(
        message="Our invoice process handles about 600 invoices a day.",
        user_id="test@example.com",
        user_role="sme",
        project_id="test-project",
    )
    print(f"Agent response:\n{response}")
    
    # Check session history
    history = ca.get_session_history("test-project")
    print(f"\nSession turns: {history.get('count', 0)}")
