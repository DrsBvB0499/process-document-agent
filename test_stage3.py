#!/usr/bin/env python3
"""Quick tests for Stage 3 agents."""

from agent.gap_analyzer import GapAnalyzer
from agent.conversation_agent import ConversationAgent

print("=" * 60)
print("Testing Gap Analyzer")
print("=" * 60)
ga = GapAnalyzer()
gap_result = ga.analyze_project("test-project")
print(f"Status: {gap_result.get('status')}")
print(f"Phase: {gap_result.get('phase')}")
print(f"Overall completeness: {gap_result.get('overall_completeness_pct')}%")
print(f"\nDeliverables:")
for gap in gap_result.get("deliverable_gaps", []):
    print(f"  {gap['deliverable']}: {gap['completeness_pct']}% ({', '.join(gap['found_fields'])})")

print(f"\nNext steps:")
for step in gap_result.get("next_steps", []):
    print(f"  {step}")

print("\n" + "=" * 60)
print("Testing Conversation Agent")
print("=" * 60)
ca = ConversationAgent()
response = ca.handle_message(
    message="Our invoice process handles about 600 invoices a day, split across 3 approval levels.",
    user_id="test@example.com",
    user_role="sme",
    project_id="test-project",
)
print(f"User: Our invoice process handles about 600 invoices a day...")
print(f"\nAgent response:\n{response}")

# Check session history
history = ca.get_session_history("test-project")
print(f"\nSession logged: {history.get('count', 0)} turns recorded")
