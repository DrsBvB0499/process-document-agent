"""
Digitization Deliverables Orchestrator — Stage 7

Orchestrates Digitization Phase deliverable generation.
Generates System Architecture and Data Flow diagrams.

Author: Intelligent Automation Agent
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.system_architecture_generator import SystemArchitectureGenerator
from agent.data_flow_generator import DataFlowGenerator


class DigitizationDeliverablesOrchestrator:
    """Orchestrates Stage 7 Digitization Phase deliverable generation."""

    PHASE_DIR = "3-digitization"

    def __init__(self, projects_root: str = "projects"):
        self.projects_root = Path(projects_root)
        self.arch_gen = SystemArchitectureGenerator(projects_root)
        self.data_flow_gen = DataFlowGenerator(projects_root)

    def _copy_to_lang_dirs(self, project_id: str, filename: str, languages: List[str]) -> Dict[str, str]:
        """Copy a generated deliverable file to each language subdirectory."""
        base_dir = self.projects_root / project_id / "deliverables" / self.PHASE_DIR
        source = base_dir / filename
        paths = {}
        if not source.exists():
            return paths
        for lang in languages:
            lang_dir = base_dir / lang
            lang_dir.mkdir(parents=True, exist_ok=True)
            dest = lang_dir / filename
            shutil.copy2(str(source), str(dest))
            paths[lang] = str(dest)
        source.unlink(missing_ok=True)
        return paths

    def generate_all_deliverables(self, project_id: str, languages: Optional[List[str]] = None) -> Dict[str, Any]:
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
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, "system_architecture.json", languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"system_architecture_{lang}"] = path
                else:
                    file_path = self.projects_root / project_id / "deliverables" / self.PHASE_DIR / "system_architecture.json"
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
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, "data_flow_diagram.json", languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"data_flow_{lang}"] = path
                else:
                    file_path = self.projects_root / project_id / "deliverables" / self.PHASE_DIR / "data_flow_diagram.json"
                    results["files_saved"]["data_flow"] = str(file_path)
                print(f"   ✓ Data Flow Diagram completed")
        except Exception as e:
            print(f"   ✗ Data Flow Diagram error: {str(e)}")
            results["status"] = "partial"

        # Calculate overall completeness
        completeness_values = list(results["completeness_by_deliverable"].values())
        results["overall_completeness"] = sum(completeness_values) // len(completeness_values) if completeness_values else 0
        results["execution_time_seconds"] = round((datetime.now() - start_time).total_seconds(), 2)

        # Generate next steps
        results["next_steps"] = self._recommend_next_steps(results)

        print(f"\n{'='*60}")
        print(f"DIGITIZATION PHASE SUMMARY")
        print(f"{'='*60}")
        print(f"Overall Completeness: {results['overall_completeness']}%")
        print(f"Execution Time: {results['execution_time_seconds']}s")
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

        if completeness.get("system_architecture", 0) < 80:
            next_steps.append("Complete system architecture (identify all systems, integrations, and deployment models)")

        if completeness.get("data_flow", 0) < 80:
            next_steps.append("Map complete data flows between systems and processes")

        # Check if ready to proceed
        if results["overall_completeness"] >= 80:
            next_steps.append("Gate Review: Evaluate digitization readiness")
            next_steps.append("Assess cloud migration opportunities for on-premise systems")
            next_steps.append("Plan API integration strategy to replace manual system handoffs")
            next_steps.append("Proceed to Automation Phase")
        else:
            next_steps.append("Run Conversation Agent to gather missing digitization details")
            next_steps.append("Re-run DigitizationDeliverablesOrchestrator to update analysis")

        # Add specific recommendations based on architecture
        system_arch = results.get("deliverables", {}).get("system_architecture", {})
        if system_arch.get("architecture", {}).get("summary", {}).get("digital_readiness") == "low":
            next_steps.append("Low digital readiness - prioritize cloud adoption and system modernization")

        digital_opportunities = system_arch.get("architecture", {}).get("digital_opportunities", [])
        if digital_opportunities:
            next_steps.append(f"Address {len(digital_opportunities)} digital transformation opportunities identified")

        return next_steps


if __name__ == "__main__":
    orchestrator = DigitizationDeliverablesOrchestrator()
    results = orchestrator.generate_all_deliverables("sd-light-invoicing-2")
    print(f"\nStatus: {results['status']}")
