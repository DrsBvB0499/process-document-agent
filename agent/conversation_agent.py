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
            message: The user's message
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

        # Determine what to respond with
        response = self._generate_response(
            message=message,
            user_role=user_role,
            gap_brief=gap_brief,
            project_id=project_id,
        )

        # Append learnings to knowledge base (simplified: user message itself is logged)
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

        # Build a prompt that tells the LLM what gaps exist and what to ask
        prompt = self._build_response_prompt(
            user_message=message,
            role_config=role_config,
            gap_brief=gap_brief,
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

    def _build_response_prompt(
        self,
        user_message: str,
        role_config: Dict[str, Any],
        gap_brief: Dict[str, Any],
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

USER'S LAST MESSAGE:
"{user_message}"

WHAT WE'RE WORKING ON:
{gap_context}

CRITICAL CONVERSATION RULES:
1. **ONE QUESTION AT A TIME** - Never ask multiple questions in one response
2. **EXPLAIN FIRST** - Before asking, explain what you're asking for in simple terms (no jargon like "SIPOC")
3. **PROVIDE AN EXAMPLE** - Give a concrete example to help the user understand
4. **EXPLAIN WHY** - Tell them why this information is important for the analysis
5. **BE ENCOURAGING** - Acknowledge what they've already shared before asking for more
6. **SIMPLE LANGUAGE** - Avoid technical terms unless the user is a developer

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

Now respond to the user's message following these rules.
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
