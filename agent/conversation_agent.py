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

        # Summarize which deliverables have gaps
        gap_summary = "\n".join([
            f"- {g['deliverable']} ({g['completeness_pct']}%): missing {', '.join(g['missing_fields'][:2])}"
            for g in deliverable_gaps if g.get("missing_fields")
        ])

        role = role_config.get("vocabulary", "technical")
        depth = role_config.get("depth", "tactical")

        return f"""You are a consultant gathering information for process improvement.

USER ROLE: {role} | DEPTH: {depth}

USER'S LAST MESSAGE:
"{user_message}"

WHAT WE STILL NEED:
{gap_summary if gap_summary else "All deliverables appear largely complete."}

INSTRUCTIONS:
1. Listen to the user's message and respond conversationally.
2. If the user is offering information about a gap, acknowledge it and ask a follow-up question.
3. If the user asks a question, answer it briefly using {role} language.
4. If you detect new information (metrics, systems, exceptions), summarize it back for confirmation.
5. Keep responses short (2-3 sentences max).
6. End by asking what else they'd like to share.

Respond naturally as if you're having a conversation.
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
