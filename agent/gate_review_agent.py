"""Gate Review Agent — Evaluates deliverable completeness and phase transition readiness.

This agent acts as a quality gatekeeper between phases. It evaluates whether
deliverables are complete enough to move from one phase to the next.

Features:
- Evaluates each deliverable against gate criteria
- Calculates overall gate score (0-100%)
- Provides actionable feedback on gaps
- Returns PASS/FAIL decision

Usage:
    from agent.gate_review_agent import GateReviewAgent

    gra = GateReviewAgent()
    result = gra.evaluate_gate(
        project_id="invoice-processing",
        phase="standardization"
    )

    if result["decision"] == "PASS":
        print("Ready to unlock next phase!")
    else:
        print(f"Score: {result['score']}/100")
        print(f"Feedback: {result['feedback']}")
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.llm import call_model


class GateReviewAgent:
    """Evaluates deliverable completeness and readiness for phase transition."""

    # Map phase names to deliverable directory names
    PHASE_DIRS = {
        "standardization": "1-standardization",
        "optimization": "2-optimization",
        "digitization": "3-digitization",
        "automation": "4-automation",
        "autonomization": "5-autonomization",
    }

    # Gate criteria for each phase
    GATE_CRITERIA = {
        "standardization": {
            "threshold": 80,  # Need 80% to pass
            "deliverables": {
                "sipoc": {
                    "weight": 20,
                    "required_fields": ["suppliers", "inputs", "process", "outputs", "customers"],
                    "min_completeness": 80,
                },
                "process_map": {
                    "weight": 25,
                    "required_fields": ["steps", "performers", "systems"],
                    "min_completeness": 70,
                },
                "baseline_metrics": {
                    "weight": 20,
                    "required_fields": ["volume", "time", "cost"],
                    "min_completeness": 60,
                },
                "flowchart": {
                    "weight": 15,
                    "required_fields": ["diagram"],
                    "min_completeness": 80,
                },
                "exception_register": {
                    "weight": 20,
                    "required_fields": ["exceptions", "handling"],
                    "min_completeness": 70,
                },
            },
        },
        # Future phases will be added here
        "optimization": {
            "threshold": 80,
            "deliverables": {},
        },
        "digitization": {
            "threshold": 80,
            "deliverables": {},
        },
        "automation": {
            "threshold": 80,
            "deliverables": {},
        },
        "autonomization": {
            "threshold": 80,
            "deliverables": {},
        },
    }

    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize the Gate Review Agent.

        Args:
            projects_root: Root directory for projects.
        """
        self.projects_root = Path(
            projects_root or (Path(__file__).parent.parent / "projects")
        )

    def evaluate_gate(self, project_id: str, phase: str = "standardization") -> Dict[str, Any]:
        """Evaluate whether a project is ready to pass the gate for a phase.

        Args:
            project_id: The project ID
            phase: The phase to evaluate (default: "standardization")

        Returns:
            Dictionary with:
                - decision: "PASS" or "FAIL"
                - score: Overall score (0-100)
                - threshold: Required threshold
                - deliverable_scores: Score breakdown per deliverable
                - feedback: Actionable feedback list
                - timestamp: ISO timestamp
        """
        # Load gate criteria for this phase
        gate_criteria = self.GATE_CRITERIA.get(phase)
        if not gate_criteria:
            return {
                "status": "error",
                "message": f"No gate criteria defined for phase '{phase}'",
            }

        # Load deliverables from project
        project_path = self.projects_root / project_id
        phase_dir = self.PHASE_DIRS.get(phase, f"1-{phase}")
        base_deliverables_path = project_path / "deliverables" / phase_dir

        # Check en/ subdirectory first (new layout), fall back to phase root (legacy)
        en_path = base_deliverables_path / "en"
        deliverables_path = en_path if en_path.exists() else base_deliverables_path

        if not deliverables_path.exists():
            return {
                "status": "error",
                "message": "No deliverables found. Generate deliverables first.",
            }

        # Evaluate each deliverable
        deliverable_scores = {}
        feedback = []
        weighted_scores = []

        for deliverable_name, criteria in gate_criteria["deliverables"].items():
            # Load deliverable JSON
            deliverable_file = deliverables_path / f"{deliverable_name}.json"

            if not deliverable_file.exists():
                # Deliverable missing
                deliverable_scores[deliverable_name] = {
                    "score": 0,
                    "weight": criteria["weight"],
                    "status": "MISSING",
                    "feedback": f"{deliverable_name.replace('_', ' ').title()} not generated",
                }
                feedback.append(f"❌ {deliverable_name.replace('_', ' ').title()}: Not generated")
                weighted_scores.append(0)
                continue

            # Load and evaluate deliverable
            try:
                with open(deliverable_file, "r", encoding="utf-8") as f:
                    deliverable_data = json.load(f)

                score, issues = self._evaluate_deliverable(
                    deliverable_name=deliverable_name,
                    deliverable_data=deliverable_data,
                    criteria=criteria,
                )

                deliverable_scores[deliverable_name] = {
                    "score": score,
                    "weight": criteria["weight"],
                    "status": "PASS" if score >= criteria["min_completeness"] else "FAIL",
                    "issues": issues,
                }

                # Calculate weighted score
                weighted_score = (score * criteria["weight"]) / 100
                weighted_scores.append(weighted_score)

                # Add feedback
                if score >= criteria["min_completeness"]:
                    feedback.append(f"✅ {deliverable_name.replace('_', ' ').title()}: {score}%")
                else:
                    feedback.append(f"❌ {deliverable_name.replace('_', ' ').title()}: {score}% (need {criteria['min_completeness']}%)")
                    for issue in issues:
                        feedback.append(f"   • {issue}")

            except Exception as e:
                deliverable_scores[deliverable_name] = {
                    "score": 0,
                    "weight": criteria["weight"],
                    "status": "ERROR",
                    "feedback": f"Error reading deliverable: {str(e)}",
                }
                feedback.append(f"❌ {deliverable_name.replace('_', ' ').title()}: Error reading file")
                weighted_scores.append(0)

        # Calculate overall score
        overall_score = sum(weighted_scores)
        threshold = gate_criteria["threshold"]
        decision = "PASS" if overall_score >= threshold else "FAIL"

        # Generate summary feedback
        if decision == "PASS":
            summary = f"🎉 Gate Review PASSED! Score: {overall_score:.0f}/{threshold} - Ready to proceed to next phase."
        else:
            summary = f"Gate Review FAILED. Score: {overall_score:.0f}/{threshold} - More work needed before proceeding."

        return {
            "status": "success",
            "decision": decision,
            "score": round(overall_score, 1),
            "threshold": threshold,
            "phase": phase,
            "deliverable_scores": deliverable_scores,
            "feedback": feedback,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _evaluate_deliverable(
        self,
        deliverable_name: str,
        deliverable_data: Dict[str, Any],
        criteria: Dict[str, Any],
    ) -> tuple[float, List[str]]:
        """Evaluate a single deliverable against criteria.

        Args:
            deliverable_name: Name of the deliverable
            deliverable_data: The deliverable JSON data
            criteria: Evaluation criteria

        Returns:
            Tuple of (score, issues_list)
        """
        issues = []
        required_fields = criteria.get("required_fields", [])

        if deliverable_name == "sipoc":
            return self._evaluate_sipoc(deliverable_data, required_fields)
        elif deliverable_name == "process_map":
            return self._evaluate_process_map(deliverable_data, required_fields)
        elif deliverable_name == "baseline_metrics":
            return self._evaluate_baseline_metrics(deliverable_data, required_fields)
        elif deliverable_name == "flowchart":
            return self._evaluate_flowchart(deliverable_data, required_fields)
        elif deliverable_name == "exception_register":
            return self._evaluate_exception_register(deliverable_data, required_fields)
        else:
            return 0.0, [f"Unknown deliverable type: {deliverable_name}"]

    def _evaluate_sipoc(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[float, List[str]]:
        """Evaluate SIPOC deliverable."""
        issues = []
        present_count = 0

        for field in required_fields:
            if field in data and data[field]:
                if isinstance(data[field], list) and len(data[field]) > 0:
                    present_count += 1
                elif isinstance(data[field], str) and data[field].strip():
                    present_count += 1
            else:
                issues.append(f"Missing or empty: {field}")

        score = (present_count / len(required_fields)) * 100
        return score, issues

    def _evaluate_process_map(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[float, List[str]]:
        """Evaluate Process Map deliverable."""
        issues = []
        score = 0.0

        steps = data.get("steps", [])
        if not steps or len(steps) == 0:
            issues.append("No process steps defined")
            return 0.0, issues

        # Check if steps have required attributes
        steps_with_performers = sum(1 for step in steps if step.get("performer"))
        steps_with_systems = sum(1 for step in steps if step.get("system"))

        step_score = (len(steps) >= 3) * 40  # At least 3 steps
        performer_score = (steps_with_performers / len(steps)) * 30  # Performers present
        system_score = (steps_with_systems / len(steps)) * 30  # Systems present

        score = step_score + performer_score + system_score

        if len(steps) < 3:
            issues.append(f"Only {len(steps)} steps (need at least 3)")
        if steps_with_performers < len(steps):
            issues.append(f"Missing performers for {len(steps) - steps_with_performers} steps")
        if steps_with_systems < len(steps):
            issues.append(f"Missing systems for {len(steps) - steps_with_systems} steps")

        return score, issues

    def _evaluate_baseline_metrics(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[float, List[str]]:
        """Evaluate Baseline Metrics deliverable."""
        issues = []
        present_count = 0

        # Check for metrics in each category
        for field in required_fields:
            category_metrics = data.get(field, {})
            if isinstance(category_metrics, dict) and len(category_metrics) > 0:
                # Check if metrics have actual values
                has_values = any(v is not None and v != "" for v in category_metrics.values())
                if has_values:
                    present_count += 1
                else:
                    issues.append(f"{field.title()} metrics defined but no values")
            else:
                issues.append(f"Missing {field} metrics")

        score = (present_count / len(required_fields)) * 100
        return score, issues

    def _evaluate_flowchart(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[float, List[str]]:
        """Evaluate Flowchart deliverable."""
        issues = []

        diagram = data.get("diagram", "")
        if not diagram or len(diagram.strip()) < 50:
            issues.append("Flowchart diagram missing or too short")
            return 0.0, issues

        # Check for valid Mermaid syntax
        if not diagram.strip().startswith("flowchart") and not diagram.strip().startswith("graph"):
            issues.append("Invalid Mermaid syntax (should start with 'flowchart' or 'graph')")
            return 50.0, issues

        # Check for multiple nodes
        node_count = diagram.count("-->") + diagram.count("---")
        if node_count < 2:
            issues.append("Flowchart has too few connections (need at least 2)")
            return 60.0, issues

        return 100.0, issues

    def _evaluate_exception_register(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[float, List[str]]:
        """Evaluate Exception Register deliverable."""
        issues = []

        exceptions = data.get("exceptions", [])
        if not exceptions or len(exceptions) == 0:
            issues.append("No exceptions documented")
            return 0.0, issues

        # Check if exceptions have handling procedures
        exceptions_with_handling = sum(
            1 for exc in exceptions
            if exc.get("handling") or exc.get("resolution")
        )

        score = (exceptions_with_handling / len(exceptions)) * 100

        if exceptions_with_handling < len(exceptions):
            issues.append(f"Missing handling procedures for {len(exceptions) - exceptions_with_handling} exceptions")

        return score, issues


if __name__ == "__main__":
    # Quick test
    gra = GateReviewAgent()
    result = gra.evaluate_gate(
        project_id="sd-light-invoicing-2",
        phase="standardization"
    )

    print(f"Decision: {result.get('decision')}")
    print(f"Score: {result.get('score')}/{result.get('threshold')}")
    print(f"\nFeedback:")
    for item in result.get('feedback', []):
        print(f"  {item}")
