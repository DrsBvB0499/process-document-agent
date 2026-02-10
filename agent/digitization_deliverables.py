"""
Digitization Deliverables Orchestrator — Stage 7

Orchestrates Digitization Phase deliverable generation.
Generates System Architecture and Data Flow diagrams.

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from agent.system_architecture_generator import SystemArchitectureGenerator
from agent.data_flow_generator import DataFlowGenerator


class DigitizationDeliverablesOrchestrator:
    """Orchestrates Stage 7 Digitization Phase deliverable generation."""

    def __init__(self, projects_root: str = "projects"):
        self.projects_root = Path(projects_root)
        self.arch_gen = SystemArchitectureGenerator(projects_root)
        self.data_flow_gen = DataFlowGenerator(projects_root)

    def generate_all_deliverables(self, project_id: str) -> Dict[str, Any]:
        """Generate all digitization deliverables."""
        print(f"\n🚀 Generating Stage 7: Digitization Deliverables")
        print(f"   Project: {project_id}")
        print(f"   {'='*60}")

        start_time = datetime.now()
        results = {
            "status": "success",
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "deliverables": {},
            "files_saved": {},
            "completeness_by_deliverable": {}
        }

        # Generate System Architecture
        print("\n[1/2] Generating System Architecture...")
        try:
            arch_result = self.arch_gen.generate_system_architecture(project_id)
            results["deliverables"]["system_architecture"] = arch_result
            results["completeness_by_deliverable"]["system_architecture"] = arch_result.get("completeness", {}).get("overall", 0)
            if arch_result.get("status") in ["success", "partial"]:
                file_path = self.projects_root / project_id / "deliverables" / "3-digitization" / "system_architecture.json"
                results["files_saved"]["system_architecture"] = str(file_path)
                print(f"   ✓ System Architecture completed")
        except Exception as e:
            print(f"   ✗ System Architecture error: {str(e)}")
            results["status"] = "partial"

        # Generate Data Flow Diagram
        print("\n[2/2] Generating Data Flow Diagram...")
        try:
            df_result = self.data_flow_gen.generate_data_flow(project_id)
            results["deliverables"]["data_flow"] = df_result
            results["completeness_by_deliverable"]["data_flow"] = df_result.get("completeness", {}).get("overall", 0)
            if df_result.get("status") in ["success", "partial"]:
                file_path = self.projects_root / project_id / "deliverables" / "3-digitization" / "data_flow_diagram.json"
                results["files_saved"]["data_flow"] = str(file_path)
                print(f"   ✓ Data Flow Diagram completed")
        except Exception as e:
            print(f"   ✗ Data Flow Diagram error: {str(e)}")
            results["status"] = "partial"

        # Calculate overall completeness
        completeness_values = list(results["completeness_by_deliverable"].values())
        results["overall_completeness"] = sum(completeness_values) // len(completeness_values) if completeness_values else 0
        results["execution_time_seconds"] = round((datetime.now() - start_time).total_seconds(), 2)

        print(f"\n{'='*60}")
        print(f"DIGITIZATION PHASE SUMMARY")
        print(f"{'='*60}")
        print(f"Overall Completeness: {results['overall_completeness']}%")
        print(f"Execution Time: {results['execution_time_seconds']}s")

        return results


if __name__ == "__main__":
    orchestrator = DigitizationDeliverablesOrchestrator()
    results = orchestrator.generate_all_deliverables("sd-light-invoicing-2")
    print(f"\nStatus: {results['status']}")
