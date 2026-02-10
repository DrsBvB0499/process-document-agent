"""
Optimization Deliverables Orchestrator — Stage 6

Orchestrates all 4 Phase 2 (Optimization) deliverable generators:
  1. Value Stream Mapping generator
  2. Waste Analysis generator (8 types of waste - TIMWOODS)
  3. Quick Wins Identifier
  4. KPI Dashboard generator

Produces complete optimization package with improvement roadmap.

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.value_stream_generator import ValueStreamGenerator
from agent.waste_analysis_generator import WasteAnalysisGenerator
from agent.quick_wins_generator import QuickWinsGenerator
from agent.kpi_dashboard_generator import KPIDashboardGenerator


class OptimizationDeliverablesOrchestrator:
    """
    Orchestrates Stage 6 Optimization Phase deliverable generation.

    Generates:
    1. Value Stream Map (VSM) with VA ratio and efficiency metrics
    2. Waste Analysis identifying 8 types of waste (TIMWOODS)
    3. Quick Wins list with prioritized improvements
    4. KPI Dashboard with baseline and target metrics

    All deliverables are saved to:
      projects/{project_id}/deliverables/2-optimization/
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize the orchestrator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

        # Initialize all generators
        self.vsm_gen = ValueStreamGenerator(projects_root)
        self.waste_gen = WasteAnalysisGenerator(projects_root)
        self.quick_wins_gen = QuickWinsGenerator(projects_root)
        self.kpi_gen = KPIDashboardGenerator(projects_root)

    def generate_all_deliverables(self, project_id: str) -> Dict[str, Any]:
        """
        Generate all 4 optimization deliverables from knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with comprehensive optimization package:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "deliverables": {
                    "value_stream": {...},
                    "waste_analysis": {...},
                    "quick_wins": {...},
                    "kpi_dashboard": {...}
                },
                "overall_completeness": 0-100,
                "files_saved": {
                    "value_stream": path,
                    "waste_analysis": path,
                    "quick_wins": path,
                    "kpi_dashboard": path
                },
                "next_steps": [...]
            }
        """
        print(f"\n🚀 Generating Stage 6: Optimization Deliverables")
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
            "completeness_by_deliverable": {}
        }

        # Generate Value Stream Map
        print("\n[1/4] Generating Value Stream Map...")
        try:
            vsm_result = self.vsm_gen.generate_value_stream(project_id)
            results["deliverables"]["value_stream"] = vsm_result
            results["completeness_by_deliverable"]["value_stream"] = vsm_result.get("completeness", {}).get("overall", 0)

            if vsm_result.get("status") == "success" or vsm_result.get("status") == "partial":
                file_path = self.projects_root / project_id / "deliverables" / "2-optimization" / "value_stream_map.json"
                results["files_saved"]["value_stream"] = str(file_path)
                va_ratio = vsm_result.get("va_ratio", 0)
                print(f"   ✓ Value Stream Map completed (VA Ratio: {va_ratio}%)")
            else:
                print(f"   ✗ Value Stream Map failed: {vsm_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Value Stream Map error: {str(e)}")
            results["status"] = "partial"

        # Generate Waste Analysis
        print("\n[2/4] Analyzing Waste (TIMWOODS)...")
        try:
            waste_result = self.waste_gen.generate_waste_analysis(project_id)
            results["deliverables"]["waste_analysis"] = waste_result
            results["completeness_by_deliverable"]["waste_analysis"] = waste_result.get("completeness", {}).get("overall", 0)

            if waste_result.get("status") == "success" or waste_result.get("status") == "partial":
                file_path = self.projects_root / project_id / "deliverables" / "2-optimization" / "waste_analysis.json"
                results["files_saved"]["waste_analysis"] = str(file_path)
                total_waste = waste_result.get("total_waste_instances", 0)
                print(f"   ✓ Waste Analysis completed ({total_waste} waste instances identified)")
            else:
                print(f"   ✗ Waste Analysis failed: {waste_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Waste Analysis error: {str(e)}")
            results["status"] = "partial"

        # Generate Quick Wins
        print("\n[3/4] Identifying Quick Wins...")
        try:
            qw_result = self.quick_wins_gen.generate_quick_wins(project_id)
            results["deliverables"]["quick_wins"] = qw_result
            results["completeness_by_deliverable"]["quick_wins"] = qw_result.get("completeness", {}).get("overall", 0)

            if qw_result.get("status") == "success" or qw_result.get("status") == "partial":
                file_path = self.projects_root / project_id / "deliverables" / "2-optimization" / "quick_wins.json"
                results["files_saved"]["quick_wins"] = str(file_path)
                qw_count = qw_result.get("summary", {}).get("total_quick_wins", 0)
                high_priority = qw_result.get("summary", {}).get("high_priority_count", 0)
                print(f"   ✓ Quick Wins identified ({qw_count} total, {high_priority} high priority)")
            else:
                print(f"   ✗ Quick Wins failed: {qw_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Quick Wins error: {str(e)}")
            results["status"] = "partial"

        # Generate KPI Dashboard
        print("\n[4/4] Building KPI Dashboard...")
        try:
            kpi_result = self.kpi_gen.generate_kpi_dashboard(project_id)
            results["deliverables"]["kpi_dashboard"] = kpi_result
            results["completeness_by_deliverable"]["kpi_dashboard"] = kpi_result.get("completeness", {}).get("overall", 0)

            if kpi_result.get("status") == "success" or kpi_result.get("status") == "partial":
                file_path = self.projects_root / project_id / "deliverables" / "2-optimization" / "kpi_dashboard.json"
                results["files_saved"]["kpi_dashboard"] = str(file_path)
                kpi_count = kpi_result.get("kpi_dashboard", {}).get("summary", {}).get("total_kpis", 0)
                print(f"   ✓ KPI Dashboard completed ({kpi_count} KPIs defined)")
            else:
                print(f"   ✗ KPI Dashboard failed: {kpi_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ KPI Dashboard error: {str(e)}")
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
        print(f"OPTIMIZATION PHASE SUMMARY")
        print(f"{'='*60}")
        print(f"Overall Completeness: {results['overall_completeness']}%")
        print(f"Execution Time: {results['execution_time_seconds']}s")
        print(f"\nFiles Saved:")
        for deliverable, path in results["files_saved"].items():
            completeness = results["completeness_by_deliverable"].get(deliverable, 0)
            print(f"  ✓ {deliverable:20} ({completeness:3}%) -> {Path(path).name}")

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

        if completeness.get("value_stream", 0) < 80:
            next_steps.append("Complete Value Stream Map with timing data and bottlenecks")
        if completeness.get("waste_analysis", 0) < 80:
            next_steps.append("Identify all 8 types of waste (TIMWOODS) in the process")
        if completeness.get("quick_wins", 0) < 80:
            next_steps.append("Document quick win opportunities with effort and impact estimates")
        if completeness.get("kpi_dashboard", 0) < 80:
            next_steps.append("Define KPIs with baselines and improvement targets")

        if results["overall_completeness"] >= 80:
            next_steps.append("Gate Review: Evaluate optimization readiness")
            next_steps.append("Implement quick wins to deliver immediate value")
            next_steps.append("Track KPIs to measure improvement progress")
            next_steps.append("Proceed to Digitization Phase")
        else:
            next_steps.append("Run Conversation Agent to gather missing optimization data")
            next_steps.append("Re-run OptimizationDeliverablesOrchestrator")

        return next_steps


def main():
    """Test the orchestrator."""
    orchestrator = OptimizationDeliverablesOrchestrator()
    results = orchestrator.generate_all_deliverables("sd-light-invoicing-2")

    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    print(json.dumps({k: v for k, v in results.items() if k != "deliverables"}, indent=2))


if __name__ == "__main__":
    main()
