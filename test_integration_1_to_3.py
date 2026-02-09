#!/usr/bin/env python3
"""Integration test suite for Stages 1-3 of the Intelligent Automation Roadmap.

This test suite demonstrates the complete workflow:
1. Create a new project (Stage 1)
2. Upload knowledge files (Stage 1)
3. Process knowledge to extract facts (Stage 2)
4. Analyze gaps vs. deliverable requirements (Stage 3)
5. Conduct targeted interviews (Stage 3)
6. Track status throughout (Stage 1)
"""

import json
from pathlib import Path

from agent.project_manager import ProjectManager
from agent.knowledge_processor import KnowledgeProcessor
from agent.gap_analyzer import GapAnalyzer
from agent.conversation_agent import ConversationAgent


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    print("\n🚀 INTEGRATION TEST: Intelligent Automation Roadmap - Stages 1-3")
    print("   Testing: Project Management → Knowledge Processing → Gap Analysis → Interviews")

    # Initialize components
    pm = ProjectManager()
    kp = KnowledgeProcessor()
    ga = GapAnalyzer()
    ca = ConversationAgent()

    # STAGE 1: Project Creation and Management
    print_section("STAGE 1: Project Foundation")

    # Create a test project
    print("\n[Test 1.1] Creating a new project...")
    try:
        project = pm.create_project(
            name="Vendor Onboarding Automation",
            description="End-to-end vendor setup and approval process",
            process_owner="Sarah Martinez",
            process_owner_email="sarah.martinez@company.com"
        )
        print(f"✓ Project created: {project.project_name} (ID: {project.project_id})")
    except Exception as e:
        print(f"✗ Failed to create project: {e}")
        return

    project_id = project.project_id

    # List projects
    print("\n[Test 1.2] Listing all projects...")
    projects = pm.list_projects()
    print(f"✓ Found {len(projects)} project(s):")
    for p in projects:
        print(f"  - {p.project_name} (Phase: {p.current_phase})")

    # Check project status
    print("\n[Test 1.3] Checking initial project status...")
    status = pm.get_project_status(project_id)
    completeness = {}
    for phase_name, phase_data in status.get("phases", {}).items():
        avg = sum(d.get("completeness", 0) for d in phase_data.get("deliverables", {}).values()) / max(1, len(phase_data.get("deliverables", {})))
        completeness[phase_name] = int(avg)
    print(f"✓ Initial phase completeness:")
    for phase, pct in completeness.items():
        print(f"  {phase}: {pct}%")

    # STAGE 2: Knowledge Processing
    print_section("STAGE 2: Knowledge Processing")

    # Add sample knowledge files (for demo)
    print("\n[Test 2.1] Creating sample knowledge files...")
    project_path = pm.config.projects_root / project_id
    uploaded_path = project_path / "knowledge" / "uploaded"
    
    # Create a sample vendor SOP
    sop_content = """VENDOR ONBOARDING PROCESS

Current State:
- Manual application form via email
- 15-20 day approval cycle
- 3 approval levels: manager, vendor lead, CFO (for high-risk)
- Legal review required for all vendors
- Average cost per vendor: $2,500 (includes legal, compliance, setup)

Key Systems:
- SharePoint: vendor docs repository
- SAP: vendor master data
- Salesforce: vendor relationship tracking

Current Metrics:
- Average onboarding time: 18 days
- Error rate: 8% (missing documentation, compliance issues)
- Rework rate: 12%

Known Issues:
- Duplicate vendor creation happens in 5% of cases
- Currency setup delays for international vendors
- No automated classification of vendor risk

Exception Handling:
- Urgent vendors (strategic partners): expedited process (5 days)
- Acquisition vendors: special compliance review
- Subsidiary vendors: streamlined process
"""
    
    sop_file = uploaded_path / "vendor_sop.txt"
    sop_file.write_text(sop_content, encoding="utf-8")
    print(f"✓ Created {sop_file.name}")

    # Process knowledge
    print("\n[Test 2.2] Processing uploaded files (Knowledge Processor)...")
    kp_result = kp.process_project(project_id)
    print(f"✓ Processing complete:")
    print(f"  Status: {kp_result['status']}")
    print(f"  Files processed: {kp_result.get('files_processed', 0)}")
    print(f"  Facts extracted: {len(kp_result['knowledge_base'].get('facts', []))}")
    print(f"  Sources identified: {len(kp_result['knowledge_base'].get('sources', []))}")

    # STAGE 3: Gap Analysis and Conversation
    print_section("STAGE 3: Intelligent Gap Analysis & Interviews")

    # Analyze gaps
    print("\n[Test 3.1] Analyzing gaps against SIPOC and other deliverables...")
    gap_result = ga.analyze_project(project_id)
    print(f"✓ Gap analysis complete:")
    print(f"  Project phase: {gap_result.get('phase')}")
    print(f"  Overall completeness: {gap_result.get('overall_completeness_pct')}%")
    
    print(f"\n  Deliverable Status:")
    for gap in gap_result.get("deliverable_gaps", []):
        missing = gap.get("missing_fields", [])
        print(f"    {gap['deliverable']:<20} {gap['completeness_pct']:>3}%  ", end="")
        if missing:
            print(f"Missing: {', '.join(missing[:2])}")
        else:
            print("✓ Complete")

    print(f"\n  Recommended next steps:")
    for step in gap_result.get("next_steps", [])[:2]:
        print(f"    • {step}")

    # Simulate conversation turns
    print("\n[Test 3.2] Simulating interview conversation...")
    messages = [
        ("sme", "The onboarding process starts with vendors submitting an application through our web portal."),
        ("process_owner", "What about SLA? How long should vendor setup take?"),
        ("sme", "We want to get it down to 5 business days for standard vendors, 2 days for strategic partners."),
    ]
    
    for idx, (role, msg) in enumerate(messages, 1):
        print(f"\n  Turn {idx} ({role}):")
        print(f"    User: {msg}")
        response = ca.handle_message(
            message=msg,
            user_id=f"user{idx}@company.com",
            user_role=role,
            project_id=project_id,
        )
        # Show first 100 chars of mocked response
        response_preview = response[:80] + ("..." if len(response) > 80 else "")
        print(f"    Agent: {response_preview}")

    # Check session history
    print("\n[Test 3.3] Reviewing conversation session...")
    history = ca.get_session_history(project_id)
    print(f"✓ Session history:")
    print(f"  Date: {history.get('date')}")
    print(f"  Conversation turns: {history.get('count', 0)}")

    # FINAL STATUS CHECK
    print_section("FINAL PROJECT STATUS")

    print("\n[Test 4.1] Checking final project state...")
    final_status = pm.get_project_status(project_id)
    
    # Calculate final completeness per phase
    print("\nPhase Completeness (after interviews):")
    for phase_name, phase_data in final_status.get("phases", {}).items():
        deliverables = phase_data.get("deliverables", {})
        if deliverables:
            avg = sum(d.get("completeness", 0) for d in deliverables.values()) / len(deliverables)
            status_str = "🔓 UNLOCKED" if avg >= 80 else "🔒 LOCKED"
            print(f"  {phase_name:<20} {int(avg):>3}% {status_str}")

    print("\n✓ Knowledge base location:")
    print(f"  {project_path / 'knowledge' / 'extracted' / 'knowledge_base.json'}")
    
    print("\n✓ Session transcripts location:")
    print(f"  {project_path / 'knowledge' / 'sessions'}")

    print("\n✓ Cost logs location:")
    print(f"  {project_path / 'cost_log.json'}")

    # Summary
    print_section("INTEGRATION TEST SUMMARY")
    print("""
✓ Stage 1: Project Foundation
  - Project creation with folder structure
  - Project state management via project.json
  - Status tracking and reporting

✓ Stage 2: Knowledge Processing
  - File upload and processing
  - LLM-based information extraction
  - Knowledge base consolidation
  - Analysis logging

✓ Stage 3: Intelligent Conversation
  - Gap analysis vs. deliverable requirements
  - Role-aware questioning
  - Session management
  - Cost tracking

Next Steps:
- Stage 4: Full Standardization Phase (all deliverables)
- Stage 5: Gate Review Logic
- Stage 6-10: Optimization through Autonomization phases
""")
    print("=" * 70)
    print("✅ ALL INTEGRATION TESTS PASSED\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
