"""
Process Analysis Agent - Standardization Checkpoint
=====================================================
This agent guides users through documenting the AS-IS state of a business process.
It produces three deliverables:
1. SIPOC (Suppliers, Inputs, Process, Outputs, Customers)
2. AS-IS Process Map (with Mermaid diagram generation)
3. Baseline Measurement

Part of the Intelligent Automation Roadmap:
Standardization → Optimization → Digitization → Automation → Autonomization

This agent handles STOP GATE 1: Standardization.
"""

from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import json
import os
from datetime import datetime
from openai import AsyncOpenAI
import anthropic

# --- SYSTEM PROMPT (the agent's brain) ---
SYSTEM_PROMPT = """You are the Process Analysis Agent — a specialist in the Standardization phase of the Intelligent Automation Roadmap. Your job is to help teams document and validate the AS-IS state of a business process before it can proceed to Optimization.

You produce THREE deliverables:

## 1. SIPOC (Suppliers, Inputs, Process, Outputs, Customers)
Fields to capture:
- Suppliers: Who/what provides input to the process
- Inputs: What triggers the process, what materials/data come in
- Process: High-level steps (5-7 max)
- Outputs: What the process produces
- Customers: Who receives the output
- Process Owner: Who is accountable
- Frequency: How often does this run
- Systems/Tools: What technology is involved today
- Organizational Position: Department, team
- Known Exceptions: Edge cases and variations

## 2. AS-IS Process Map
For each step capture:
- Step name and sequence number
- Who performs it (role/person)
- System/tool used
- Decision points (where does the process branch?)
- Handoffs between people/teams
- Pain points or bottlenecks
- Estimated time per step

## 3. Baseline Measurement
- Total time per process run (end to end)
- Frequency (times per day/week/month/year)
- Total time investment (time × frequency, annualized)
- People involved and approximate cost level
- Error/rework rate if known
- Risk factors (what goes wrong, what's the impact)
- Current SLA if applicable

## YOUR BEHAVIOR:
1. You are conversational, warm, and guide people through the analysis step by step
2. You ask ONE question at a time — never overwhelm
3. You think like a Lean consultant — ask "why" and dig deeper when answers are vague
4. After each response, internally assess what's gathered and what's missing
5. Start with SIPOC to scope the process, then process map, then baseline
6. Celebrate progress and acknowledge when deliverables are filling in
7. Work with messy input — meeting notes, rough descriptions, partial info
8. If someone tries to jump to automation solutions, gently redirect

## RESPONSE FORMAT:
Include a status block ONLY when:
1. The user explicitly asks for status/progress
2. You've completed a major section (finished SIPOC, finished process map, finished baseline)
3. All deliverables are complete (gate ready)

When including status, add this JSON block at the end of your response:
```json
{"sipoc":{"suppliers":0,"inputs":0,"process_steps":0,"outputs":0,"customers":0,"process_owner":0,"frequency":0,"systems_tools":0,"org_position":0,"known_exceptions":0},"process_map":{"steps_documented":0,"decision_points":0,"handoffs":0,"pain_points":0},"baseline":{"total_time":0,"frequency":0,"time_investment":0,"people_cost":0,"error_rate":0,"risk_factors":0,"sla":0},"phase":"sipoc","next_question":"What should I ask next"}
```

Set each field to 0 (not captured), 1 (partially captured), or 2 (fully captured).
Set "phase" to "sipoc", "process_map", or "baseline".
When ALL fields are at 2, include "gate_status": "READY" in the JSON.
When gate is READY, also include a "mermaid" field containing a complete Mermaid.js flowchart.
"""


class ProcessAnalysisAgent:
    """
    The core agent class. Manages conversation history, tracks deliverable
    progress, and interacts with either Claude (Anthropic) or OpenAI API.
    """

    def __init__(self, project_name: str = "Untitled Process", model_provider: str = "anthropic"):
        self.project_name = project_name
        self.model_provider = model_provider.lower()
        self.conversation_history = []
        self.status = None
        self.created_at = datetime.now().isoformat()

    def parse_status(self, response_text: str) -> dict | None:
        """Extract the JSON status block from the agent's response."""
        import re
        match = re.search(r'```json\s*\n?([\s\S]*?)\n?\s*```', response_text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def clean_response(self, response_text: str) -> str:
        """Remove the status block from the response for display."""
        import re
        return re.sub(r'```json\s*\n?[\s\S]*?\n?\s*```', '', response_text).strip()

    def get_progress_summary(self) -> dict:
        """Calculate completion percentages for each deliverable."""
        if not self.status:
            return {"sipoc": 0, "process_map": 0, "baseline": 0, "overall": 0}

        def calc_pct(section):
            values = list(section.values())
            if not values:
                return 0
            return round((sum(values) / (len(values) * 2)) * 100)

        sipoc_pct = calc_pct(self.status.get("sipoc", {}))
        map_pct = calc_pct(self.status.get("process_map", {}))
        base_pct = calc_pct(self.status.get("baseline", {}))

        total_fields = []
        for section in ["sipoc", "process_map", "baseline"]:
            total_fields.extend(self.status.get(section, {}).values())

        overall = round((sum(total_fields) / (len(total_fields) * 2)) * 100) if total_fields else 0

        return {
            "sipoc": sipoc_pct,
            "process_map": map_pct,
            "baseline": base_pct,
            "overall": overall
        }

    def is_gate_ready(self) -> bool:
        """Check if the standardization gate checkpoint is complete."""
        progress = self.get_progress_summary()
        return progress["overall"] == 100

    async def send_message(self, user_input: str, api_key: str) -> str:
        """
        Send a message to the agent and get a response.
        Supports both Anthropic (Claude) and OpenAI APIs.
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            if self.model_provider == "anthropic":
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=self.conversation_history
                )
                assistant_text = response.content[0].text
            else:  # openai
                client = AsyncOpenAI(api_key=api_key)
                # OpenAI expects system message in the messages array
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history
                response = await client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    max_tokens=1500,
                    messages=messages
                )
                assistant_text = response.choices[0].message.content
        except Exception as e:
            error_msg = f"API Error ({self.model_provider}): {str(e)}"
            print(f"\n❌ {error_msg}")
            return error_msg

        # Parse and store status
        status = self.parse_status(assistant_text)
        if status:
            self.status = status

        # Store full response in history (with status block for context)
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_text
        })

        # Return clean response for display
        return self.clean_response(assistant_text)

    def save_session(self, filepath: str):
        """Save the current session to a JSON file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        session_data = {
            "project_name": self.project_name,
            "created_at": self.created_at,
            "saved_at": datetime.now().isoformat(),
            "status": self.status,
            "progress": self.get_progress_summary(),
            "conversation_history": self.conversation_history
        }
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self, filepath: str):
        """Load a previous session from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.project_name = data["project_name"]
        self.created_at = data["created_at"]
        self.status = data.get("status")
        self.conversation_history = data["conversation_history"]

    def export_deliverables(self) -> dict:
        """
        Export the three deliverables as structured data.
        This will be used later to generate documents.
        """
        return {
            "project_name": self.project_name,
            "gate": "Standardization",
            "status": self.status,
            "progress": self.get_progress_summary(),
            "gate_ready": self.is_gate_ready(),
            "conversation_length": len(self.conversation_history),
            "exported_at": datetime.now().isoformat()
        }


# --- CLI Interface (for testing in terminal) ---
async def main():
    """Simple command-line interface for testing the agent."""
    print("\n" + "=" * 60)
    print("  🔍 PROCESS ANALYSIS AGENT")
    print("  Intelligent Automation Roadmap — Standardization Checkpoint")
    print("=" * 60)

    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    # Choose model provider
    print("\n🤖 Select model provider:")
    print("  1. Anthropic (Claude) - default")
    print("  2. OpenAI (GPT-4o)")
    choice = input("  Enter choice (1 or 2) [1]: ").strip() or "1"
    
    if choice == "2":
        model_provider = "openai"
        api_key_env = "OPENAI_API_KEY"
    else:
        model_provider = "anthropic"
        api_key_env = "ANTHROPIC_API_KEY"
    
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        print(f"\n⚠️  Set your {api_key_env} environment variable first.")
        print(f"   export {api_key_env}='your-key-here'")
        return

    project_name = input("\n📋 Project name: ").strip() or "Untitled Process"
    agent = ProcessAnalysisAgent(project_name=project_name, model_provider=model_provider)

    print(f"\n🚀 Starting analysis for: {project_name}")
    print(f"   Using: {model_provider.upper()}")
    print("   Type 'quit' to exit, 'status' to see progress, 'save' to save session\n")

    # Initial greeting
    response = await agent.send_message(
        "Hello, I'd like to analyze a process.", api_key
    )
    print(f"\n🤖 Agent: {response}\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() == 'quit':
            break
        if user_input.lower() == 'status':
            # Ask the agent for a status update
            response = await agent.send_message(
                "Please provide a status update on our progress.", api_key
            )
            print(f"\n🤖 Agent: {response}\n")
            
            # Show calculated progress
            progress = agent.get_progress_summary()
            print(f"📊 Progress: SIPOC {progress['sipoc']}% | "
                  f"Process Map {progress['process_map']}% | "
                  f"Baseline {progress['baseline']}% | "
                  f"Overall {progress['overall']}%")
            if agent.is_gate_ready():
                print("🟢 GATE READY — All deliverables complete!")
            print()
            continue
        if user_input.lower() == 'save':
            filepath = f"outputs/{project_name.replace(' ', '_').lower()}_session.json"
            agent.save_session(filepath)
            print(f"💾 Session saved to {filepath}\n")
            continue

        response = await agent.send_message(user_input, api_key)
        print(f"\n🤖 Agent: {response}\n")


    # Save on exit
    filepath = f"outputs/{project_name.replace(' ', '_').lower()}_session.json"
    agent.save_session(filepath)
    print(f"\n💾 Session saved to {filepath}")
    print("👋 See you next time!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
