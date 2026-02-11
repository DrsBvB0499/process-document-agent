"""
Autonomization Deliverables Orchestrator — Stage 9

Orchestrates Autonomization Phase deliverable generation using dedicated generators:
  1. AI/ML Opportunities Generator (intelligent capability identification)
  2. Self-Healing Design Generator (autonomous resilience patterns)

Produces complete autonomization package for intelligent, self-sustaining operations.

Author: Intelligent Automation Agent
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.ai_opportunities_generator import AIOpportunitiesGenerator
from agent.self_healing_generator import SelfHealingGenerator


class AutonomizationDeliverablesOrchestrator:
    """
    Orchestrates Stage 9 Autonomization Phase deliverable generation.

    Generates:
    1. AI/ML Opportunities with data assessment
    2. Self-Healing Design with resilience patterns

    All deliverables are saved to:
      projects/{project_id}/deliverables/5-autonomization/
    """

    PHASE_DIR = "5-autonomization"

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize the orchestrator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

        # Initialize generators
        self.ai_gen = AIOpportunitiesGenerator(projects_root)
        self.healing_gen = SelfHealingGenerator(projects_root)

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
        Generate all autonomization deliverables from knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with comprehensive autonomization package:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "deliverables": {
                    "ai_ml_opportunities": {...},
                    "self_healing_design": {...}
                },
                "overall_completeness": 0-100,
                "files_saved": {
                    "ai_ml_opportunities": path,
                    "self_healing_design": path
                },
                "completeness_by_deliverable": {
                    "ai_ml_opportunities": 0-100,
                    "self_healing_design": 0-100
                },
                "total_llm_cost_usd": float,
                "next_steps": [...],
                "execution_time_seconds": float
            }
        """
        print(f"\n🚀 Generating Stage 9: Autonomization Deliverables")
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

        # Generate AI/ML Opportunities
        print("\n[1/2] Identifying AI/ML Opportunities (LLM-based)...")
        try:
            ai_result = self.ai_gen.generate_ai_opportunities(project_id)
            results["deliverables"]["ai_ml_opportunities"] = {
                k: v for k, v in ai_result.items()
                if k not in ["opportunities"]  # Exclude large data from summary
            }
            results["completeness_by_deliverable"]["ai_ml_opportunities"] = (
                ai_result.get("completeness", {}).get("overall", 0)
            )
            results["total_llm_cost_usd"] += ai_result.get("llm_cost_usd", 0.0)

            if ai_result.get("status") in ["success", "partial"]:
                opportunities_count = len(ai_result.get("opportunities", []))
                high_confidence = sum(
                    1 for o in ai_result.get("opportunities", [])
                    if o.get("expected_performance", {}).get("confidence_level") == "high"
                )
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, "ai_ml_opportunities.json", languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"ai_ml_opportunities_{lang}"] = path
                else:
                    file_path = self.projects_root / project_id / "deliverables" / self.PHASE_DIR / "ai_ml_opportunities.json"
                    results["files_saved"]["ai_ml_opportunities"] = str(file_path)
                print(f"   ✓ AI/ML Opportunities identified ({opportunities_count} total, {high_confidence} high confidence)")
                print(f"   💰 LLM Cost: ${ai_result.get('llm_cost_usd', 0.0):.4f}")
            else:
                print(f"   ✗ AI/ML Opportunities failed: {ai_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ AI/ML Opportunities error: {str(e)}")
            results["status"] = "partial"

        # Generate Self-Healing Design
        print("\n[2/2] Designing Self-Healing Patterns (LLM-based)...")
        try:
            healing_result = self.healing_gen.generate_self_healing_design(project_id)
            results["deliverables"]["self_healing_design"] = {
                k: v for k, v in healing_result.items()
                if k not in ["healing_patterns"]  # Exclude large data from summary
            }
            results["completeness_by_deliverable"]["self_healing_design"] = (
                healing_result.get("completeness", {}).get("overall", 0)
            )
            results["total_llm_cost_usd"] += healing_result.get("llm_cost_usd", 0.0)

            if healing_result.get("status") in ["success", "partial"]:
                patterns_count = len(healing_result.get("healing_patterns", []))
                critical_patterns = sum(
                    1 for p in healing_result.get("healing_patterns", [])
                    if p.get("impact") == "critical"
                )
                if languages:
                    lang_paths = self._copy_to_lang_dirs(project_id, "self_healing_design.json", languages)
                    for lang, path in lang_paths.items():
                        results["files_saved"][f"self_healing_design_{lang}"] = path
                else:
                    file_path = self.projects_root / project_id / "deliverables" / self.PHASE_DIR / "self_healing_design.json"
                    results["files_saved"]["self_healing_design"] = str(file_path)
                print(f"   ✓ Self-Healing Design completed ({patterns_count} patterns, {critical_patterns} critical)")
                print(f"   💰 LLM Cost: ${healing_result.get('llm_cost_usd', 0.0):.4f}")
            else:
                print(f"   ✗ Self-Healing Design failed: {healing_result.get('error')}")
                results["status"] = "partial"
        except Exception as e:
            print(f"   ✗ Self-Healing Design error: {str(e)}")
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
        print(f"AUTONOMIZATION PHASE SUMMARY")
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

        if completeness.get("ai_ml_opportunities", 0) < 80:
            next_steps.append("Complete AI/ML opportunity assessment (data availability, expected performance)")

        if completeness.get("self_healing_design", 0) < 80:
            next_steps.append("Finalize self-healing patterns with monitoring and learning mechanisms")

        # Check if ready to proceed
        if results["overall_completeness"] >= 80:
            next_steps.append("Gate Review: Evaluate autonomization readiness and strategic fit")
            next_steps.append("Begin AI/ML proof of concept with highest confidence opportunity")
            next_steps.append("Implement critical self-healing patterns in production")
            next_steps.append("Establish MLOps and monitoring infrastructure")
            next_steps.append("Design continuous learning and improvement cycles")
        else:
            next_steps.append("Run Conversation Agent to gather missing autonomization details")
            next_steps.append("Re-run AutonomizationDeliverablesOrchestrator to update analysis")

        # Add specific recommendations based on deliverables
        ai_opportunities = results.get("deliverables", {}).get("ai_ml_opportunities", {})
        if ai_opportunities.get("summary", {}).get("data_readiness_score") == "high":
            next_steps.append("Prioritize AI/ML opportunities with high data readiness")

        healing_design = results.get("deliverables", {}).get("self_healing_design", {})
        if healing_design.get("summary", {}).get("autonomous_recovery_potential", "").startswith("8") or \
           healing_design.get("summary", {}).get("autonomous_recovery_potential", "").startswith("9"):
            next_steps.append("High autonomous recovery potential - prioritize self-healing implementation")

        return next_steps


def main():
    """Test the orchestrator."""
    orchestrator = AutonomizationDeliverablesOrchestrator()
    results = orchestrator.generate_all_deliverables("sd-light-invoicing-2")

    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    print(json.dumps({k: v for k, v in results.items() if k != "deliverables"}, indent=2))


if __name__ == "__main__":
    main()
