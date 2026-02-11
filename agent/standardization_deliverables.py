"""
Standardization Deliverables Orchestrator — Stage 4

Orchestrates all 5 Phase 1 (Standardization) deliverable generators:
  1. SIPOC generator
  2. Process map generator
  3. Baseline metrics generator
  4. Flowchart generator
  5. Exception register generator

Produces complete standardization package and Word document.

Author: Intelligent Automation Agent
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.sipoc_generator import SIPOCGenerator
from agent.process_map_generator import ProcessMapGenerator
from agent.baseline_metrics_generator import BaselineMetricsGenerator
from agent.flowchart_generator import FlowchartGenerator
from agent.exception_register_generator import ExceptionRegisterGenerator


class StandardizationDeliverablesOrchestrator:
    """
    Orchestrates Stage 4 Standardization Phase deliverable generation.
    
    Generates:
    1. SIPOC table
    2. Process map with steps, performers, systems, decisions
    3. Baseline metrics (volume, time, cost, quality, SLA)
    4. Mermaid flowchart diagram
    5. Exception register with handling
    
    All deliverables are saved to:
      projects/{project_id}/deliverables/1-standardization/
    """

    PHASE_DIR = "1-standardization"

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize the orchestrator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

        # Initialize all generators
        self.sipoc_gen = SIPOCGenerator(projects_root)
        self.process_map_gen = ProcessMapGenerator(projects_root)
        self.metrics_gen = BaselineMetricsGenerator(projects_root)
        self.flowchart_gen = FlowchartGenerator(projects_root)
        self.exception_gen = ExceptionRegisterGenerator(projects_root)

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
        """
        Generate all 5 standardization deliverables from knowledge base.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with comprehensive standardization package:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "deliverables": {
                    "sipoc": {...},
                    "process_map": {...},
                    "baseline_metrics": {...},
                    "flowchart": {...},
                    "exception_register": {...}
                },
                "overall_completeness": 0-100,
                "files_saved": {
                    "sipoc": path,
                    "process_map": path,
                    "baseline_metrics": path,
                    "flowchart": path,
                    "exception_register": path
                },
                "next_steps": [...]
            }
        """
        print(f"\n🚀 Generating Stage 4: Standardization Deliverables")
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

        # Generate SIPOC
        print("\n[1/5] Generating SIPOC...")
        try:
            sipoc_result = self.sipoc_gen.generate_sipoc(project_id)
            results["deliverables"]["sipoc"] = sipoc_result
            results["completeness_by_deliverable"]["sipoc"] = sipoc_result.get("completeness", {}).get("overall", 0)
            
            if sipoc_result.get("status") == "success":
                saved_path = self.sipoc_gen.save_sipoc(project_id, sipoc_result)
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, Path(saved_path).name, languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"sipoc_{lang}"] = path
                else:
                    results["files_saved"]["sipoc"] = str(saved_path)
                print(f"   ✓ SIPOC completed ({sipoc_result['completeness']['overall']}% complete)")
            else:
                print(f"   ✗ SIPOC failed: {sipoc_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ SIPOC error: {str(e)}")
            results["status"] = "partial"

        # Generate Process Map
        print("\n[2/5] Generating Process Map...")
        try:
            process_map_result = self.process_map_gen.generate_process_map(project_id)
            results["deliverables"]["process_map"] = process_map_result
            results["completeness_by_deliverable"]["process_map"] = process_map_result.get("completeness", {}).get("overall", 0)
            
            if process_map_result.get("status") == "success":
                saved_path = self.process_map_gen.save_process_map(project_id, process_map_result)
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, Path(saved_path).name, languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"process_map_{lang}"] = path
                else:
                    results["files_saved"]["process_map"] = str(saved_path)
                print(f"   ✓ Process Map completed ({process_map_result['completeness']['overall']}% complete)")
            else:
                print(f"   ✗ Process Map failed: {process_map_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Process Map error: {str(e)}")
            results["status"] = "partial"

        # Generate Baseline Metrics
        print("\n[3/5] Aggregating Baseline Metrics...")
        try:
            metrics_result = self.metrics_gen.generate_baseline_metrics(project_id)
            results["deliverables"]["baseline_metrics"] = metrics_result
            results["completeness_by_deliverable"]["baseline_metrics"] = metrics_result.get("completeness", {}).get("overall", 0)
            
            if metrics_result.get("status") == "success":
                saved_path = self.metrics_gen.save_baseline_metrics(project_id, metrics_result)
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, Path(saved_path).name, languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"baseline_metrics_{lang}"] = path
                else:
                    results["files_saved"]["baseline_metrics"] = str(saved_path)
                print(f"   ✓ Baseline Metrics completed ({metrics_result['completeness']['overall']}% complete)")
            else:
                print(f"   ✗ Baseline Metrics failed: {metrics_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Baseline Metrics error: {str(e)}")
            results["status"] = "partial"

        # Generate Flowchart
        print("\n[4/5] Generating Flowchart (Mermaid)...")
        try:
            flowchart_result = self.flowchart_gen.generate_flowchart(project_id)
            results["deliverables"]["flowchart"] = {k: v for k, v in flowchart_result.items() if k != "flowchart"}
            
            if flowchart_result.get("status") == "success":
                saved_path = self.flowchart_gen.save_flowchart(project_id, flowchart_result)
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, Path(saved_path).name, languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"flowchart_{lang}"] = path
                else:
                    results["files_saved"]["flowchart"] = str(saved_path)
                nodes = flowchart_result.get("flowchart", {}).get("node_count", 0)
                connections = flowchart_result.get("flowchart", {}).get("connection_count", 0)
                print(f"   ✓ Flowchart completed ({nodes} nodes, {connections} connections)")
            else:
                print(f"   ✗ Flowchart failed: {flowchart_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Flowchart error: {str(e)}")
            results["status"] = "partial"

        # Generate Exception Register
        print("\n[5/5] Building Exception Register...")
        try:
            exception_result = self.exception_gen.generate_exception_register(project_id)
            results["deliverables"]["exception_register"] = exception_result
            results["completeness_by_deliverable"]["exception_register"] = exception_result.get("completeness", {}).get("overall", 0)
            
            if exception_result.get("status") == "success":
                saved_path = self.exception_gen.save_exception_register(project_id, exception_result)
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, Path(saved_path).name, languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"exception_register_{lang}"] = path
                else:
                    results["files_saved"]["exception_register"] = str(saved_path)
                exc_count = exception_result.get("exception_register", {}).get("total_exceptions", 0)
                print(f"   ✓ Exception Register completed ({exc_count} exceptions documented)")
            else:
                print(f"   ✗ Exception Register failed: {exception_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Exception Register error: {str(e)}")
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
        print(f"STANDARDIZATION PHASE SUMMARY")
        print(f"{'='*60}")
        print(f"Overall Completeness: {results['overall_completeness']}%")
        print(f"Execution Time: {results['execution_time_seconds']}s")
        print(f"\nFiles Saved:")
        for deliverable, path in results["files_saved"].items():
            completeness = results["completeness_by_deliverable"].get(deliverable, 0)
            print(f"  ✓ {deliverable:20} ({completeness:3}%) -> {Path(path).name}")

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

        if completeness.get("sipoc", 0) < 80:
            next_steps.append("Complete SIPOC table (suppliers, inputs, process, outputs, customers)")
        if completeness.get("process_map", 0) < 80:
            next_steps.append("Document all process steps with performers and systems")
        if completeness.get("baseline_metrics", 0) < 80:
            next_steps.append("Collect baseline metrics (volume, time, cost, error rate, SLA)")
        if completeness.get("exception_register", 0) < 80:
            next_steps.append("Document known exceptions and their handling procedures")

        if results["overall_completeness"] >= 80:
            next_steps.append("Gate Review: Evaluate completeness and sign-off")
            next_steps.append("Proceed to Optimization Phase")
        else:
            next_steps.append("Run Conversation Agent to fill identified gaps")
            next_steps.append("Re-run StandardizationDeliverablesOrchestrator")

        return next_steps


def main():
    """Test the orchestrator."""
    orchestrator = StandardizationDeliverablesOrchestrator()
    results = orchestrator.generate_all_deliverables("test-project")

    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    print(json.dumps({k: v for k, v in results.items() if k != "deliverables"}, indent=2))


if __name__ == "__main__":
    main()
