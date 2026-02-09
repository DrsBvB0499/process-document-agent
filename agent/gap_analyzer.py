"""Gap Analyzer — identifies missing information for project deliverables.

Compares the knowledge_base against the requirements for each deliverable
in the current phase, producing a gap brief that guides the Conversation Agent
on what questions still need answers.

The gap brief is structured so the Conversation Agent can ask targeted,
role-aware questions without re-asking what's already documented.

Usage:
    from agent.gap_analyzer import GapAnalyzer
    
    ga = GapAnalyzer()
    gaps = ga.analyze_project("sd-light-invoicing")
    
    for gap in gaps['deliverable_gaps']:
        print(f"Deliverable: {gap['deliverable']}")
        print(f"Missing: {gap['missing_fields']}")
        print(f"Recommendation: {gap['recommendation']}")
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.llm import call_model
from agent.validators import validate_project_id


class GapAnalyzer:
    """Analyzes gaps between knowledge and deliverable requirements."""

    # Defines what each deliverable in Standardization phase requires
    STANDARDIZATION_REQUIREMENTS = {
        "sipoc": {
            "fields": ["suppliers", "inputs", "process_owner", "outputs", "customers"],
            "importance": "critical",
            "description": "SIPOC table showing suppliers, inputs, process, outputs, customers",
        },
        "process_map": {
            "fields": ["steps", "performers", "systems", "decisions"],
            "importance": "critical",
            "description": "Step-by-step process flow with who performs each step and what systems are involved",
        },
        "baseline_metrics": {
            "fields": ["volume", "time", "cost", "error_rate", "sla"],
            "importance": "critical",
            "description": "AS-IS metrics: transaction volume, processing time, cost, error rates, SLAs",
        },
        "exception_register": {
            "fields": ["exceptions", "handling", "frequency"],
            "importance": "high",
            "description": "Known process exceptions and how they are handled",
        },
        "flowchart": {
            "fields": ["diagram"],
            "importance": "medium",
            "description": "Visual flowchart of the process (generated from process map)",
        },
    }

    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize the Gap Analyzer.
        
        Args:
            projects_root: Root directory for projects.
        """
        self.projects_root = Path(
            projects_root or (Path(__file__).parent.parent / "projects")
        )

    def analyze_project(self, project_id: str) -> Dict[str, Any]:
        """Analyze gaps for a project in its current phase.

        Compares knowledge_base.json against deliverable requirements
        and produces a gap brief for the Conversation Agent.

        Args:
            project_id: The project ID to analyze

        Returns:
            Dictionary with keys: phase, current_deliverables, knowledge_summary,
            deliverable_gaps, recommendations, next_steps
        """
        # Validate project_id to prevent path traversal attacks
        if not validate_project_id(project_id):
            return {
                "status": "error",
                "message": f"Invalid project ID '{project_id}'. Must contain only lowercase letters, numbers, and hyphens.",
            }

        project_path = self.projects_root / project_id
        extracted_path = project_path / "knowledge" / "extracted"

        # Load knowledge base
        knowledge_base = self._load_knowledge_base(extracted_path)
        project_json = self._load_project_json(project_path)

        if not project_json:
            return {
                "status": "error",
                "message": "project.json not found",
            }

        # Get current phase and requirements
        phase = project_json.get("current_phase", "standardization")
        phase_data = project_json.get("phases", {}).get(phase, {})
        deliverables = phase_data.get("deliverables", {})

        # Analyze gaps per deliverable
        deliverable_gaps = []
        for deliverable_key, deliverable_info in deliverables.items():
            requirements = self.STANDARDIZATION_REQUIREMENTS.get(
                deliverable_key, {}
            )
            if not requirements:
                continue

            gaps = self._analyze_deliverable_gaps(
                deliverable_key, requirements, knowledge_base
            )
            if gaps:
                deliverable_gaps.append(gaps)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            deliverable_gaps, knowledge_base, project_json
        )

        return {
            "status": "success",
            "project_id": project_id,
            "phase": phase,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "knowledge_summary": {
                "facts_count": len(knowledge_base.get("facts", [])),
                "sources_count": len(knowledge_base.get("sources", [])),
                "categories": self._summarize_facts_by_category(
                    knowledge_base.get("facts", [])
                ),
            },
            "deliverable_gaps": deliverable_gaps,
            "overall_completeness_pct": self._calculate_overall_completeness(
                deliverable_gaps
            ),
            "recommendations": recommendations,
            "next_steps": self._recommend_next_steps(deliverable_gaps),
        }

    def _analyze_deliverable_gaps(
        self, deliverable_key: str, requirements: Dict[str, Any], knowledge_base: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze gaps for a single deliverable."""
        facts = knowledge_base.get("facts", [])
        missing_fields = []
        found_fields = []

        for field in requirements.get("fields", []):
            # Simple heuristic: check if any fact mentions the field
            found = any(
                field.lower() in str(fact).lower() for fact in facts
            )
            if found:
                found_fields.append(field)
            else:
                missing_fields.append(field)

        completeness = (
            len(found_fields) / len(requirements.get("fields", []))
            if requirements.get("fields")
            else 0
        ) * 100

        return {
            "deliverable": deliverable_key,
            "description": requirements.get("description", ""),
            "importance": requirements.get("importance", "medium"),
            "found_fields": found_fields,
            "missing_fields": missing_fields,
            "completeness_pct": int(completeness),
            "recommendation": self._recommend_for_deliverable(
                deliverable_key, missing_fields, knowledge_base
            ),
        }

    def _recommend_for_deliverable(
        self, deliverable_key: str, missing_fields: List[str], knowledge_base: Dict[str, Any]
    ) -> str:
        """Generate a recommendation for filling gaps."""
        if not missing_fields:
            return "Deliverable appears complete based on knowledge base."

        role_map = {
            "sipoc": "Process Owner and SME",
            "process_map": "SME (Subject Matter Expert)",
            "baseline_metrics": "SME or data analyst",
            "exception_register": "SME",
            "flowchart": "Generated automatically once process map is complete",
        }

        role = role_map.get(deliverable_key, "stakeholder")
        fields_str = ", ".join(missing_fields)

        if deliverable_key == "flowchart":
            return f"Will be generated automatically once {role} completes the process map."
        else:
            return f"Interview {role} about: {fields_str}"

    def _summarize_facts_by_category(self, facts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count facts by category."""
        categories = {}
        for fact in facts:
            cat = fact.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _calculate_overall_completeness(self, deliverable_gaps: List[Dict[str, Any]]) -> int:
        """Calculate average completeness across all deliverables."""
        if not deliverable_gaps:
            return 0
        avg = sum(d.get("completeness_pct", 0) for d in deliverable_gaps) / len(
            deliverable_gaps
        )
        return int(avg)

    def _generate_recommendations(
        self, deliverable_gaps: List[Dict[str, Any]], knowledge_base: Dict[str, Any], project_json: Dict[str, Any]
    ) -> List[str]:
        """Generate overall recommendations."""
        recs = []

        # Check which sources we have
        sources = knowledge_base.get("sources", [])
        source_systems = [s.get("system") for s in sources]

        if not sources:
            recs.append("Start by uploading SOP, process documentation, or meeting notes.")

        # Check unknowns
        unknowns = knowledge_base.get("unknowns", [])
        if unknowns:
            recs.append(f"There are {len(unknowns)} questions raised: prioritize clarifying these.")

        # Check completeness
        all_complete = all(
            d.get("completeness_pct", 0) >= 80 for d in deliverable_gaps
        )
        if not all_complete:
            incomplete = [
                d["deliverable"] for d in deliverable_gaps
                if d.get("completeness_pct", 0) < 80
            ]
            recs.append(f"Complete the following: {', '.join(incomplete)}")
        else:
            recs.append("All deliverables appear > 80% complete. Ready for gate review.")

        return recs

    def _recommend_next_steps(self, deliverable_gaps: List[Dict[str, Any]]) -> List[str]:
        """Recommend next steps based on gaps."""
        steps = []

        # Find most critical gap
        critical = [d for d in deliverable_gaps if d.get("importance") == "critical"]
        if critical:
            incomplete_critical = [d for d in critical if d.get("completeness_pct", 0) < 80]
            if incomplete_critical:
                steps.append(
                    f"1. Complete critical deliverable: {incomplete_critical[0]['deliverable']}"
                )

        # Suggest conversation
        steps.append("2. Run Conversation Agent to fill identified gaps")
        steps.append("3. Re-run Gap Analyzer to track progress")
        steps.append("4. Proceed to gate review once all >= 80% complete")

        return steps

    def _load_knowledge_base(self, extracted_path: Path) -> Dict[str, Any]:
        """Load knowledge_base.json."""
        kb_path = extracted_path / "knowledge_base.json"
        if kb_path.exists():
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"facts": [], "sources": []}

    def _load_project_json(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Load project.json."""
        proj_file = project_path / "project.json"
        if proj_file.exists():
            try:
                with open(proj_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None


if __name__ == "__main__":
    # Quick test: analyze test-project
    ga = GapAnalyzer()
    result = ga.analyze_project("test-project")
    print(f"Status: {result.get('status')}")
    print(f"Phase: {result.get('phase')}")
    print(f"Overall completeness: {result.get('overall_completeness_pct')}%")
    print(f"\nGaps identified:")
    for gap in result.get("deliverable_gaps", []):
        print(f"  - {gap['deliverable']}: {gap['completeness_pct']}% complete")
    print(f"\nNext steps:")
    for step in result.get("next_steps", []):
        print(f"  {step}")
