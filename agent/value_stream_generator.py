"""
Value Stream Mapping Generator — Stage 6 Optimization Deliverable

Generates Value Stream Map (VSM) showing the flow of materials and information
through the process, highlighting value-added vs. non-value-added activities.

VSM components:
- Process steps with cycle time, wait time, lead time
- Value-added (VA) vs. Non-value-added (NVA) classification
- Bottlenecks and delays
- Information flows and handoffs
- Process efficiency metrics (VA ratio, lead time, throughput)

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ValueStreamGenerator:
    """
    Generates Value Stream Map from knowledge base facts.

    Expected fact categories in knowledge_base.json:
    - process_steps: sequential steps with timing information
    - cycle_time: time to complete each step (value-added time)
    - wait_time: delays between steps (non-value-added time)
    - handoffs: transfers between teams/systems
    - bottlenecks: identified constraints or delays
    - metrics: volume, throughput, lead time data
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Value Stream Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_value_stream(self, project_id: str) -> Dict[str, Any]:
        """
        Generate Value Stream Map from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with VSM structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "value_stream": {
                    "steps": [
                        {
                            "name": str,
                            "cycle_time": float (seconds),
                            "wait_time": float (seconds),
                            "value_added": bool,
                            "performer": str,
                            "system": str
                        }
                    ],
                    "metrics": {
                        "total_cycle_time": float,
                        "total_wait_time": float,
                        "total_lead_time": float,
                        "value_added_time": float,
                        "value_added_ratio": float (0-100%),
                        "process_efficiency": float (0-100%)
                    },
                    "bottlenecks": [...],
                    "handoffs": [...],
                    "improvement_opportunities": [...]
                },
                "completeness": {
                    "steps": 0-100,
                    "timing": 0-100,
                    "bottlenecks": 0-100,
                    "overall": 0-100
                },
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

            # Extract VSM components
            steps = self._extract_process_steps(facts)
            bottlenecks = self._extract_by_category(facts, "bottlenecks")
            handoffs = self._extract_by_category(facts, "handoffs")
            metrics_facts = self._extract_by_category(facts, "metrics")

            # Calculate VSM metrics
            metrics = self._calculate_metrics(steps, metrics_facts)

            # Identify improvement opportunities
            improvement_opportunities = self._identify_improvements(steps, bottlenecks, metrics)

            # Calculate completeness
            completeness = {
                "steps": 100 if steps else 0,
                "timing": 50 if any(s.get("cycle_time") for s in steps) else 0,
                "bottlenecks": 100 if bottlenecks else 0
            }
            completeness["overall"] = sum(completeness.values()) // 3

            # Identify missing fields
            missing = []
            if not steps:
                missing.append("process_steps")
            if not any(s.get("cycle_time") for s in steps):
                missing.append("cycle_time")
            if not bottlenecks:
                missing.append("bottlenecks")

            # Save deliverable
            deliverable_data = {
                "steps": steps,
                "metrics": metrics,
                "bottlenecks": bottlenecks,
                "handoffs": handoffs,
                "improvement_opportunities": improvement_opportunities
            }

            self._save_deliverable(project_id, deliverable_data)

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "value_stream": deliverable_data,
                "completeness": completeness,
                "missing_fields": missing,
                "step_count": len(steps),
                "bottleneck_count": len(bottlenecks),
                "va_ratio": metrics.get("value_added_ratio", 0)
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _extract_process_steps(self, facts: List[Dict]) -> List[Dict]:
        """
        Extract process steps with timing and classification.

        Returns:
            List of steps with cycle_time, wait_time, value_added flag
        """
        steps = []
        step_facts = [f for f in facts if f.get("category") == "process_steps"]

        for fact in step_facts:
            fact_text = fact.get("fact", "")

            # Parse step information
            step = {
                "name": fact_text,
                "cycle_time": None,
                "wait_time": None,
                "value_added": self._is_value_added(fact_text),
                "performer": None,
                "system": None
            }

            # Try to extract timing from fact text
            # Example: "Step 1: Process invoice (5 minutes)"
            if "minute" in fact_text.lower():
                import re
                time_match = re.search(r'(\d+)\s*minute', fact_text.lower())
                if time_match:
                    step["cycle_time"] = int(time_match.group(1)) * 60  # Convert to seconds

            # Extract performer if mentioned
            if " by " in fact_text:
                performer_part = fact_text.split(" by ")[-1].split(" using")[0]
                step["performer"] = performer_part.strip()

            # Extract system if mentioned
            if " using " in fact_text:
                system_part = fact_text.split(" using ")[-1].strip()
                step["system"] = system_part.strip()

            steps.append(step)

        return steps

    def _is_value_added(self, step_text: str) -> bool:
        """
        Classify if a step is value-added or non-value-added.

        Value-added: directly transforms the product/service
        Non-value-added: waiting, handoffs, checks, approvals
        """
        nva_keywords = [
            "wait", "approve", "approval", "check", "verify", "review",
            "forward", "send", "transfer", "handoff", "store", "file"
        ]

        step_lower = step_text.lower()
        return not any(keyword in step_lower for keyword in nva_keywords)

    def _extract_by_category(self, facts: List[Dict], category: str) -> List[str]:
        """
        Extract facts by category.

        Args:
            facts: List of fact dictionaries
            category: Category to filter by

        Returns:
            List of fact strings for that category
        """
        return [
            fact.get("fact", "")
            for fact in facts
            if fact.get("category") == category
        ]

    def _calculate_metrics(self, steps: List[Dict], metrics_facts: List[str]) -> Dict[str, Any]:
        """
        Calculate VSM metrics from steps and facts.
        """
        # Sum cycle times and wait times
        total_cycle_time = sum(s.get("cycle_time", 0) for s in steps if s.get("cycle_time"))
        total_wait_time = sum(s.get("wait_time", 0) for s in steps if s.get("wait_time"))

        # Calculate value-added time
        value_added_time = sum(
            s.get("cycle_time", 0)
            for s in steps
            if s.get("value_added") and s.get("cycle_time")
        )

        # Calculate total lead time
        total_lead_time = total_cycle_time + total_wait_time

        # Calculate value-added ratio
        va_ratio = (value_added_time / total_cycle_time * 100) if total_cycle_time > 0 else 0

        # Calculate process efficiency (VA time / Lead time)
        process_efficiency = (value_added_time / total_lead_time * 100) if total_lead_time > 0 else 0

        return {
            "total_cycle_time": total_cycle_time,
            "total_wait_time": total_wait_time,
            "total_lead_time": total_lead_time,
            "value_added_time": value_added_time,
            "value_added_ratio": round(va_ratio, 1),
            "process_efficiency": round(process_efficiency, 1),
            "step_count": len(steps)
        }

    def _identify_improvements(
        self,
        steps: List[Dict],
        bottlenecks: List[str],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Identify improvement opportunities from VSM analysis.
        """
        opportunities = []

        # Low VA ratio suggests too much waste
        if metrics.get("value_added_ratio", 0) < 30:
            opportunities.append("Value-added ratio is low (<30%). Consider eliminating non-value-added activities.")

        # Low process efficiency suggests high wait times
        if metrics.get("process_efficiency", 0) < 20:
            opportunities.append("Process efficiency is low (<20%). Focus on reducing wait times between steps.")

        # Too many handoffs
        handoff_count = sum(1 for s in steps if not s.get("value_added"))
        if handoff_count > len(steps) / 2:
            opportunities.append(f"High number of handoffs ({handoff_count}). Consider consolidating tasks or automating transfers.")

        # Bottlenecks mentioned
        if bottlenecks:
            opportunities.append(f"Identified {len(bottlenecks)} bottleneck(s). Prioritize resolving these constraints.")

        return opportunities

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save value stream map to project deliverables folder.

        Args:
            project_id: Project ID
            data: Value stream map data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "value_stream_map.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    vsg = ValueStreamGenerator()
    result = vsg.generate_value_stream("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Overall Completeness: {result.get('completeness', {}).get('overall', 0)}%")
    print(f"VA Ratio: {result.get('va_ratio', 0)}%")
    print(f"\nMissing fields: {result.get('missing_fields', [])}")
