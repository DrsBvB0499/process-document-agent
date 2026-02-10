"""
Waste Analysis Generator — Stage 6 Optimization Deliverable

Identifies the 8 types of waste (TIMWOODS) in the process using Lean methodology.
Analyzes knowledge base for waste indicators and provides improvement recommendations.

8 Types of Waste (TIMWOODS):
1. Transport - Unnecessary movement of materials/information
2. Inventory - Excess work-in-progress or supplies
3. Motion - Unnecessary movement of people
4. Waiting - Idle time between steps
5. Overproduction - Producing more than needed
6. Overprocessing - More work than required
7. Defects - Errors requiring rework
8. Skills - Underutilized talent/knowledge

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class WasteAnalysisGenerator:
    """
    Identifies 8 types of waste from knowledge base facts.

    Expected fact categories in knowledge_base.json:
    - process_steps: to identify waiting, motion, transport
    - exceptions: to identify defects and rework
    - constraints: to identify bottlenecks
    - metrics: to quantify waste impact
    - decisions: to identify overprocessing
    """

    # Waste detection patterns
    WASTE_PATTERNS = {
        "transport": [
            "move", "transfer", "send", "email", "forward", "copy",
            "upload", "download", "share", "attach"
        ],
        "inventory": [
            "queue", "backlog", "pending", "waiting list", "buffer",
            "stockpile", "accumulate", "pile up"
        ],
        "motion": [
            "walk", "go to", "navigate", "switch between", "toggle",
            "search for", "look up", "find"
        ],
        "waiting": [
            "wait", "delay", "pending approval", "on hold", "idle",
            "blocked", "stuck", "await", "pause"
        ],
        "overproduction": [
            "batch", "excess", "unused", "redundant", "just in case",
            "extra", "surplus", "over-capacity"
        ],
        "overprocessing": [
            "duplicate", "re-enter", "copy-paste", "manual entry",
            "double-check", "multiple approvals", "redundant check"
        ],
        "defects": [
            "error", "mistake", "rework", "correction", "fix",
            "exception", "failure", "reject", "invalid"
        ],
        "skills": [
            "underutilized", "manual", "repetitive", "routine",
            "low-value", "administrative", "data entry"
        ]
    }

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Waste Analysis Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_waste_analysis(self, project_id: str) -> Dict[str, Any]:
        """
        Generate Waste Analysis from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with waste analysis structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "waste_analysis": {
                    "transport": {...},
                    "inventory": {...},
                    "motion": {...},
                    "waiting": {...},
                    "overproduction": {...},
                    "overprocessing": {...},
                    "defects": {...},
                    "skills": {...},
                    "summary": {
                        "total_waste_instances": int,
                        "most_common_waste": str,
                        "estimated_impact": str
                    }
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

            # Analyze each type of waste
            waste_analysis = {}
            for waste_type in self.WASTE_PATTERNS.keys():
                waste_analysis[waste_type] = self._analyze_waste_type(
                    waste_type=waste_type,
                    facts=facts,
                    exceptions=exceptions
                )

            # Calculate summary
            summary = self._calculate_summary(waste_analysis)

            # Calculate completeness
            completeness = self._calculate_completeness(waste_analysis)

            # Identify missing fields
            missing = []
            if summary["total_waste_instances"] == 0:
                missing.append("waste_indicators")

            # Save deliverable
            deliverable_data = {
                **waste_analysis,
                "summary": summary
            }

            self._save_deliverable(project_id, deliverable_data)

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "waste_analysis": deliverable_data,
                "completeness": completeness,
                "missing_fields": missing,
                "total_waste_instances": summary["total_waste_instances"]
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _analyze_waste_type(
        self,
        waste_type: str,
        facts: List[Dict],
        exceptions: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze a specific type of waste.

        Args:
            waste_type: One of the 8 waste types
            facts: Knowledge base facts
            exceptions: Known exceptions

        Returns:
            Dict with:
                - instances: List of detected waste instances
                - count: Number of instances
                - impact: Estimated impact (low/medium/high)
                - recommendations: Improvement suggestions
        """
        patterns = self.WASTE_PATTERNS[waste_type]
        instances = []

        # Search facts for waste patterns
        for fact in facts:
            fact_text = fact.get("fact", "").lower()
            for pattern in patterns:
                if pattern in fact_text:
                    instances.append({
                        "description": fact.get("fact"),
                        "category": fact.get("category"),
                        "confidence": fact.get("confidence", 0.7)
                    })
                    break  # Only count each fact once per waste type

        # Search exceptions for defect-related waste
        if waste_type == "defects":
            for exception in exceptions:
                instances.append({
                    "description": exception,
                    "category": "exception",
                    "confidence": 0.9
                })

        # Estimate impact
        impact = self._estimate_impact(waste_type, len(instances))

        # Generate recommendations
        recommendations = self._generate_recommendations(waste_type, instances)

        return {
            "instances": instances,
            "count": len(instances),
            "impact": impact,
            "recommendations": recommendations
        }

    def _estimate_impact(self, waste_type: str, instance_count: int) -> str:
        """
        Estimate the impact of a waste type based on instance count.

        Returns:
            "low", "medium", or "high"
        """
        if instance_count == 0:
            return "none"
        elif instance_count <= 2:
            return "low"
        elif instance_count <= 5:
            return "medium"
        else:
            return "high"

    def _generate_recommendations(
        self,
        waste_type: str,
        instances: List[Dict]
    ) -> List[str]:
        """
        Generate improvement recommendations for a waste type.
        """
        recommendations = []

        if len(instances) == 0:
            return []

        # Waste-specific recommendations
        if waste_type == "transport":
            recommendations.append("Consider centralizing information storage to reduce data transfers")
            recommendations.append("Implement API integrations to automate data exchange")

        elif waste_type == "inventory":
            recommendations.append("Implement pull-based processing (just-in-time)")
            recommendations.append("Set up automated triggers to process work as it arrives")

        elif waste_type == "motion":
            recommendations.append("Consolidate information into a single dashboard")
            recommendations.append("Reduce system switching with integrated tools")

        elif waste_type == "waiting":
            recommendations.append("Identify and eliminate bottlenecks causing delays")
            recommendations.append("Automate approval workflows to reduce wait times")

        elif waste_type == "overproduction":
            recommendations.append("Align production with actual demand")
            recommendations.append("Implement pull signals to trigger work")

        elif waste_type == "overprocessing":
            recommendations.append("Eliminate redundant data entry and checks")
            recommendations.append("Standardize processes to required level only")

        elif waste_type == "defects":
            recommendations.append("Implement validation at the point of entry")
            recommendations.append("Add automated checks to prevent errors")

        elif waste_type == "skills":
            recommendations.append("Automate repetitive, low-value tasks")
            recommendations.append("Reallocate human effort to high-value activities")

        return recommendations

    def _calculate_summary(self, waste_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall summary of waste findings.
        """
        # Count total instances
        total_instances = sum(
            data.get("count", 0)
            for data in waste_analysis.values()
        )

        # Find most common waste type
        most_common = max(
            waste_analysis.items(),
            key=lambda x: x[1].get("count", 0)
        )[0] if total_instances > 0 else "none"

        # Estimate overall impact
        high_impact_count = sum(
            1 for data in waste_analysis.values()
            if data.get("impact") == "high"
        )

        if high_impact_count >= 3:
            estimated_impact = "high"
        elif high_impact_count >= 1 or total_instances >= 10:
            estimated_impact = "medium"
        elif total_instances > 0:
            estimated_impact = "low"
        else:
            estimated_impact = "none"

        return {
            "total_waste_instances": total_instances,
            "most_common_waste": most_common,
            "estimated_impact": estimated_impact,
            "high_impact_wastes": [
                waste_type
                for waste_type, data in waste_analysis.items()
                if data.get("impact") == "high"
            ]
        }

    def _calculate_completeness(self, waste_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate completeness of waste analysis.
        """
        # Count how many waste types have been detected
        detected_types = sum(
            1 for data in waste_analysis.values()
            if data.get("count", 0) > 0
        )

        completeness_pct = (detected_types / 8) * 100

        return {
            "detected_types": detected_types,
            "total_types": 8,
            "overall": round(completeness_pct, 1)
        }

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save waste analysis to project deliverables folder.

        Args:
            project_id: Project ID
            data: Waste analysis data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "waste_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    wag = WasteAnalysisGenerator()
    result = wag.generate_waste_analysis("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Total Waste Instances: {result.get('total_waste_instances', 0)}")
    print(f"Most Common Waste: {result.get('waste_analysis', {}).get('summary', {}).get('most_common_waste')}")
    print(f"\nMissing fields: {result.get('missing_fields', [])}")
