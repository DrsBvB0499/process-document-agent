"""
Automation Deliverables Orchestrator — Stage 8

Orchestrates Automation Phase deliverable generation using dedicated generators:
  1. Automation Candidates Generator (LLM-based analysis)
  2. Automation Roadmap Generator (intelligent phasing)

Produces complete automation package with implementation plan.

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.automation_candidates_generator import AutomationCandidatesGenerator
from agent.automation_roadmap_generator import AutomationRoadmapGenerator


class AutomationDeliverablesOrchestrator:
    """
    Orchestrates Stage 8 Automation Phase deliverable generation.

    Generates:
    1. Automation Candidates with LLM-based assessment
    2. Implementation Roadmap with phased plan

    All deliverables are saved to:
      projects/{project_id}/deliverables/4-automation/
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize the orchestrator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

        # Initialize generators
        self.candidates_gen = AutomationCandidatesGenerator(projects_root)
        self.roadmap_gen = AutomationRoadmapGenerator(projects_root)

    def generate_all_deliverables(self, project_id: str) -> Dict[str, Any]:
        """
        Generate all automation deliverables from knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with comprehensive automation package:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "deliverables": {
                    "automation_candidates": {...},
                    "implementation_roadmap": {...}
                },
                "overall_completeness": 0-100,
                "files_saved": {
                    "automation_candidates": path,
                    "implementation_roadmap": path
                },
                "completeness_by_deliverable": {
                    "automation_candidates": 0-100,
                    "implementation_roadmap": 0-100
                },
                "total_llm_cost_usd": float,
                "next_steps": [...],
                "execution_time_seconds": float
            }
        """
        print(f"\n🚀 Generating Stage 8: Automation Deliverables")
        print(f"   Project: {project_id}")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        print(f"   {'='*60}")

        start_time = datetime.now()

        # Track results
        results = {
            "status": "success",
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "deliverables": {},
            "files_saved": {},
            "completeness_by_deliverable": {},
            "total_llm_cost_usd": 0.0
        }

        # Generate Automation Candidates
        print("\n[1/2] Analyzing Automation Candidates (LLM-based)...")
        try:
            candidates_result = self.candidates_gen.generate_automation_candidates(project_id)
            results["deliverables"]["automation_candidates"] = {
                k: v for k, v in candidates_result.items()
                if k not in ["candidates"]  # Exclude large data from summary
            }
            results["completeness_by_deliverable"]["automation_candidates"] = (
                candidates_result.get("completeness", {}).get("overall", 0)
            )
            results["total_llm_cost_usd"] += candidates_result.get("llm_cost_usd", 0.0)

            if candidates_result.get("status") in ["success", "partial"]:
                candidates_count = len(candidates_result.get("candidates", []))
                high_priority = sum(
                    1 for c in candidates_result.get("candidates", [])
                    if c.get("automation_score", 0) >= 70
                )
                file_path = self.projects_root / project_id / "deliverables" / "4-automation" / "automation_candidates.json"
                results["files_saved"]["automation_candidates"] = str(file_path)
                print(f"   ✓ Automation Candidates completed ({candidates_count} total, {high_priority} high priority)")
                print(f"   💰 LLM Cost: ${candidates_result.get('llm_cost_usd', 0.0):.4f}")
            else:
                print(f"   ✗ Automation Candidates failed: {candidates_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Automation Candidates error: {str(e)}")
            results["status"] = "partial"

        # Generate Implementation Roadmap
        print("\n[2/2] Creating Implementation Roadmap (LLM-based)...")
        try:
            roadmap_result = self.roadmap_gen.generate_automation_roadmap(project_id)
            results["deliverables"]["implementation_roadmap"] = {
                k: v for k, v in roadmap_result.items()
                if k not in ["roadmap"]  # Exclude large data from summary
            }
            results["completeness_by_deliverable"]["implementation_roadmap"] = (
                roadmap_result.get("completeness", {}).get("overall", 0)
            )
            results["total_llm_cost_usd"] += roadmap_result.get("llm_cost_usd", 0.0)

            if roadmap_result.get("status") in ["success", "partial"]:
                phases_count = len(roadmap_result.get("roadmap", {}).get("phases", []))
                duration = roadmap_result.get("roadmap", {}).get("program_summary", {}).get("total_duration_months", 0)
                file_path = self.projects_root / project_id / "deliverables" / "4-automation" / "implementation_roadmap.json"
                results["files_saved"]["implementation_roadmap"] = str(file_path)
                print(f"   ✓ Implementation Roadmap completed ({phases_count} phases, {duration} months)")
                print(f"   💰 LLM Cost: ${roadmap_result.get('llm_cost_usd', 0.0):.4f}")
            else:
                print(f"   ✗ Implementation Roadmap failed: {roadmap_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Implementation Roadmap error: {str(e)}")
            results["status"] = "partial"

        # Calculate overall completeness
        completeness_values = [v for v in results["completeness_by_deliverable"].values()]
        results["overall_completeness"] = sum(completeness_values) // len(completeness_values) if completeness_values else 0

        # Generate next steps
        results["next_steps"] = self._recommend_next_steps(results)

        # Execution time
        duration = (datetime.now() - start_time).total_seconds()
        results["execution_time_seconds"] = round(duration, 2)

        # Summary
        print(f"\n{'='*60}")
        print(f"AUTOMATION PHASE SUMMARY")
        print(f"{'='*60}")
        print(f"Overall Completeness: {results['overall_completeness']}%")
        print(f"Execution Time: {results['execution_time_seconds']}s")
        print(f"Total LLM Cost: ${results['total_llm_cost_usd']:.4f}")
        print(f"\nFiles Saved:")
        for deliverable, path in results["files_saved"].items():
            completeness = results["completeness_by_deliverable"].get(deliverable, 0)
            print(f"  ✓ {deliverable:25} ({completeness:3}%) -> {Path(path).name}")

        print(f"\nNext Steps:")
        for step in results["next_steps"]:
            print(f"  • {step}")

        return results

    def _recommend_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for next steps based on completeness.

        Args:
            results: Results from deliverable generation

        Returns:
            List of recommended next steps
        """
        next_steps = []

        # Analyze completeness by deliverable
        completeness = results["completeness_by_deliverable"]

        if completeness.get("automation_candidates", 0) < 80:
            next_steps.append("Complete automation candidates assessment (scoring, ROI, technology recommendations)")

        if completeness.get("implementation_roadmap", 0) < 80:
            next_steps.append("Finalize implementation roadmap with phasing, resources, and timeline")

        # Check if ready to proceed
        if results["overall_completeness"] >= 80:
            next_steps.append("Gate Review: Evaluate automation readiness and business case")
            next_steps.append("Secure budget and resources for Phase 1 implementation")
            next_steps.append("Begin pilot automation with highest ROI candidate")
            next_steps.append("Proceed to Autonomization Phase planning")
        else:
            next_steps.append("Run Conversation Agent to gather missing automation details")
            next_steps.append("Re-run AutomationDeliverablesOrchestrator to update analysis")

        # Add specific recommendations based on deliverables
        automation_candidates = results.get("deliverables", {}).get("automation_candidates", {})
        if automation_candidates.get("summary", {}).get("quick_wins_count", 0) > 0:
            next_steps.append("Prioritize quick wins for immediate value delivery")

        return next_steps


def main():
    """Test the orchestrator."""
    orchestrator = AutomationDeliverablesOrchestrator()
    results = orchestrator.generate_all_deliverables("sd-light-invoicing-2")

    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    print(json.dumps({k: v for k, v in results.items() if k != "deliverables"}, indent=2))


if __name__ == "__main__":
    main()
