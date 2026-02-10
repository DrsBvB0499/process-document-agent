"""
Quick Wins Identifier — Stage 6 Optimization Deliverable

Identifies low-effort, high-impact improvement opportunities that can be
implemented quickly to deliver immediate value.

Quick Win Criteria:
- Low implementation effort (< 1 month, minimal resources)
- High impact (measurable improvement in time, cost, quality)
- Low risk (minimal disruption to operations)
- Fast ROI (payback < 6 months)

Categorization Matrix:
    High Impact  |  Quick Win!  |  Strategic Project
    Low Impact   |  Easy Fix    |  Not Worth It
                    Low Effort      High Effort

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class QuickWinsGenerator:
    """
    Identifies quick win opportunities from knowledge base and waste analysis.

    Expected inputs:
    - Knowledge base with process steps, metrics, constraints
    - Waste analysis (if available)
    - Exception register
    - Baseline metrics
    """

    # Quick win detection patterns
    QUICK_WIN_PATTERNS = {
        "automation": {
            "keywords": ["manual", "copy-paste", "data entry", "repetitive", "routine"],
            "effort": "low",
            "impact": "high",
            "category": "Automation"
        },
        "elimination": {
            "keywords": ["redundant", "duplicate", "unnecessary", "unused"],
            "effort": "low",
            "impact": "medium",
            "category": "Elimination"
        },
        "standardization": {
            "keywords": ["inconsistent", "varies", "different methods", "ad-hoc"],
            "effort": "low",
            "impact": "medium",
            "category": "Standardization"
        },
        "consolidation": {
            "keywords": ["multiple systems", "scattered", "fragmented"],
            "effort": "medium",
            "impact": "high",
            "category": "Consolidation"
        },
        "self_service": {
            "keywords": ["request", "ask for", "wait for", "manual approval"],
            "effort": "medium",
            "impact": "medium",
            "category": "Self-Service"
        }
    }

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Quick Wins Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_quick_wins(self, project_id: str) -> Dict[str, Any]:
        """
        Generate Quick Wins list from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with quick wins structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "quick_wins": [
                    {
                        "id": str,
                        "title": str,
                        "description": str,
                        "category": str,
                        "effort": "low|medium",
                        "impact": "high|medium",
                        "priority": int (1-10),
                        "estimated_savings": str,
                        "implementation_time": str,
                        "risks": [str]
                    }
                ],
                "summary": {
                    "total_quick_wins": int,
                    "high_priority_count": int,
                    "estimated_total_savings": str
                },
                "completeness": {...},
                "missing_fields": [...]
            }
        """
        try:
            # Load knowledge base
            kb_path = self.projects_root / project_id / "knowledge" / "extracted" / "knowledge_base.json"
            if not kb_path.exists():
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": f"Knowledge base not found at {kb_path}"
                }

            with open(kb_path, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)

            facts = knowledge_base.get("facts", [])
            exceptions = knowledge_base.get("exceptions", [])

            # Try to load waste analysis if available
            waste_data = self._load_waste_analysis(project_id)

            # Identify quick wins
            quick_wins = []

            # 1. From process steps (automation opportunities)
            quick_wins.extend(self._identify_automation_wins(facts))

            # 2. From exceptions (error prevention)
            quick_wins.extend(self._identify_exception_wins(exceptions))

            # 3. From waste analysis (waste elimination)
            if waste_data:
                quick_wins.extend(self._identify_waste_wins(waste_data))

            # 4. From constraints (bottleneck resolution)
            quick_wins.extend(self._identify_constraint_wins(facts))

            # Prioritize and rank quick wins
            quick_wins = self._prioritize_quick_wins(quick_wins)

            # Calculate summary
            summary = self._calculate_summary(quick_wins)

            # Calculate completeness
            completeness = {
                "quick_wins_identified": 100 if quick_wins else 0,
                "overall": 100 if quick_wins else 0
            }

            # Identify missing fields
            missing = []
            if not quick_wins:
                missing.append("improvement_opportunities")

            # Save deliverable
            deliverable_data = {
                "quick_wins": quick_wins,
                "summary": summary
            }

            self._save_deliverable(project_id, deliverable_data)

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                **deliverable_data,
                "completeness": completeness,
                "missing_fields": missing
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _identify_automation_wins(self, facts: List[Dict]) -> List[Dict]:
        """
        Identify automation quick wins from process steps.
        """
        wins = []
        step_facts = [f for f in facts if f.get("category") == "process_steps"]

        for idx, fact in enumerate(step_facts):
            fact_text = fact.get("fact", "").lower()

            # Look for manual/repetitive activities
            if any(keyword in fact_text for keyword in ["manual", "copy", "data entry", "repetitive"]):
                wins.append({
                    "id": f"QW-AUTO-{idx+1}",
                    "title": f"Automate: {fact.get('fact')[:50]}...",
                    "description": f"Automate the manual step: {fact.get('fact')}",
                    "category": "Automation",
                    "effort": "low",
                    "impact": "high",
                    "priority": 9,
                    "estimated_savings": "5-10 hours/week",
                    "implementation_time": "2-4 weeks",
                    "risks": ["May require system integration"]
                })

        return wins

    def _identify_exception_wins(self, exceptions: List[str]) -> List[Dict]:
        """
        Identify quick wins from exceptions (error prevention).
        """
        wins = []

        for idx, exception in enumerate(exceptions):
            wins.append({
                "id": f"QW-EXCEP-{idx+1}",
                "title": f"Prevent: {exception[:50]}...",
                "description": f"Add validation to prevent: {exception}",
                "category": "Error Prevention",
                "effort": "low",
                "impact": "medium",
                "priority": 7,
                "estimated_savings": "2-5 hours/week",
                "implementation_time": "1-2 weeks",
                "risks": ["May slow down initial entry"]
            })

        return wins

    def _identify_waste_wins(self, waste_data: Dict[str, Any]) -> List[Dict]:
        """
        Identify quick wins from waste analysis.
        """
        wins = []

        # Look for high-impact waste types
        for waste_type, data in waste_data.items():
            if waste_type == "summary":
                continue

            if data.get("impact") in ["high", "medium"] and data.get("count", 0) > 0:
                # Get first recommendation
                recommendations = data.get("recommendations", [])
                if recommendations:
                    wins.append({
                        "id": f"QW-WASTE-{waste_type}",
                        "title": f"Reduce {waste_type.title()} waste",
                        "description": recommendations[0],
                        "category": "Waste Elimination",
                        "effort": "low" if data.get("impact") == "medium" else "medium",
                        "impact": data.get("impact"),
                        "priority": 8 if data.get("impact") == "high" else 6,
                        "estimated_savings": "3-8 hours/week",
                        "implementation_time": "2-3 weeks",
                        "risks": ["May require process redesign"]
                    })

        return wins

    def _identify_constraint_wins(self, facts: List[Dict]) -> List[Dict]:
        """
        Identify quick wins from constraints/bottlenecks.
        """
        wins = []
        constraint_facts = [f for f in facts if f.get("category") in ["constraints", "bottlenecks"]]

        for idx, fact in enumerate(constraint_facts):
            wins.append({
                "id": f"QW-CONST-{idx+1}",
                "title": f"Resolve: {fact.get('fact')[:50]}...",
                "description": f"Address constraint: {fact.get('fact')}",
                "category": "Bottleneck Resolution",
                "effort": "medium",
                "impact": "high",
                "priority": 8,
                "estimated_savings": "10-15 hours/week",
                "implementation_time": "3-4 weeks",
                "risks": ["May require management approval"]
            })

        return wins

    def _prioritize_quick_wins(self, quick_wins: List[Dict]) -> List[Dict]:
        """
        Sort quick wins by priority (highest first).
        """
        return sorted(quick_wins, key=lambda x: x.get("priority", 0), reverse=True)

    def _calculate_summary(self, quick_wins: List[Dict]) -> Dict[str, Any]:
        """
        Calculate summary statistics for quick wins.
        """
        high_priority = [qw for qw in quick_wins if qw.get("priority", 0) >= 8]

        return {
            "total_quick_wins": len(quick_wins),
            "high_priority_count": len(high_priority),
            "estimated_total_savings": f"{len(quick_wins) * 5}-{len(quick_wins) * 10} hours/week"
        }

    def _load_waste_analysis(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Load waste analysis if it exists.
        """
        waste_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization" / "waste_analysis.json"
        )

        if waste_path.exists():
            try:
                with open(waste_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save quick wins to project deliverables folder.

        Args:
            project_id: Project ID
            data: Quick wins data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "quick_wins.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    qwg = QuickWinsGenerator()
    result = qwg.generate_quick_wins("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Total Quick Wins: {result.get('summary', {}).get('total_quick_wins', 0)}")
    print(f"High Priority: {result.get('summary', {}).get('high_priority_count', 0)}")
    print(f"\nMissing fields: {result.get('missing_fields', [])}")
