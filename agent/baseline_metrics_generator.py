"""
Baseline Metrics Generator — Stage 4 Standardization Deliverable

Extracts current-state metrics (volume, time, cost, quality, SLA)
from the knowledge base and produces a baseline metrics summary.

Baseline metrics track the "AS-IS" state before improvement:
  Volume: How many cases per period?
  Time: How long does it take?
  Cost: What's the actual cost?
  Error Rate: How many defects?
  SLA: What's the service level agreement?

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaselineMetricsGenerator:
    """
    Generates baseline metrics summary from knowledge base facts.
    
    Expected fact categories in knowledge_base.json:
    - volume: transaction/case volume per period
    - cycle_time: total time to complete process
    - processing_time: time spent actually working (vs. waiting)
    - cost: direct and indirect costs
    - error_rate: percentage of failed or reworked cases
    - rework_rate: percentage requiring manual intervention
    - sla: service level agreements (time, quality, availability)
    - staffing: number of people/roles involved
    - system_cost: cost of systems/tools used
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Baseline Metrics Generator.
        
        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_baseline_metrics(self, project_id: str) -> Dict[str, Any]:
        """
        Generate baseline metrics from project knowledge base.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with baseline metrics:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "baseline_metrics": {
                    "volume": {...},
                    "time": {...},
                    "cost": {...},
                    "quality": {...},
                    "sla": {...},
                    "staffing": {...}
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

            # Extract metric categories
            volume = self._extract_metric(facts, "volume")
            cycle_time = self._extract_metric(facts, "cycle_time")
            processing_time = self._extract_metric(facts, "processing_time")
            cost = self._extract_metric(facts, "cost")
            error_rate = self._extract_metric(facts, "error_rate")
            rework_rate = self._extract_metric(facts, "rework_rate")
            sla = self._extract_metric(facts, "sla")
            staffing = self._extract_metric(facts, "staffing")

            # Build metrics structure
            metrics = {
                "volume": volume,
                "time": {
                    "cycle_time": cycle_time,
                    "processing_time": processing_time
                },
                "cost": cost,
                "quality": {
                    "error_rate": error_rate,
                    "rework_rate": rework_rate
                },
                "sla": sla,
                "staffing": staffing
            }

            # Calculate completeness
            metric_groups = [
                volume, cycle_time, processing_time, cost, 
                error_rate, rework_rate, sla, staffing
            ]
            completeness_pct = (sum(1 for m in metric_groups if m) / len(metric_groups)) * 100

            # Identify missing metrics
            missing = []
            if not volume:
                missing.append("volume")
            if not cycle_time:
                missing.append("cycle_time")
            if not cost:
                missing.append("cost")
            if not error_rate:
                missing.append("error_rate")
            if not sla:
                missing.append("sla")

            return {
                "status": "success",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "baseline_metrics": metrics,
                "completeness": {
                    "volume": 100 if volume else 0,
                    "cycle_time": 100 if cycle_time else 0,
                    "processing_time": 100 if processing_time else 0,
                    "cost": 100 if cost else 0,
                    "error_rate": 100 if error_rate else 0,
                    "rework_rate": 100 if rework_rate else 0,
                    "sla": 100 if sla else 0,
                    "staffing": 100 if staffing else 0,
                    "overall": round(completeness_pct)
                },
                "missing_fields": missing,
                "metrics_extracted": sum(1 for m in metric_groups if m)
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _extract_metric(self, facts: List[Dict], category: str) -> Optional[str]:
        """
        Extract first fact for a metric category.
        
        Args:
            facts: List of fact dictionaries
            category: Metric category to look for
            
        Returns:
            First matching fact or None
        """
        for fact_obj in facts:
            if isinstance(fact_obj, dict) and fact_obj.get("category") == category:
                fact_text = fact_obj.get("fact")
                if fact_text:
                    return fact_text
        return None

    def save_baseline_metrics(self, project_id: str, metrics_data: Dict[str, Any]) -> Path:
        """
        Save baseline metrics to project deliverables folder.
        
        Args:
            project_id: ID of the project
            metrics_data: Metrics data from generate_baseline_metrics()
            
        Returns:
            Path to saved file
        """
        output_dir = self.projects_root / project_id / "deliverables" / "1-standardization"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "baseline_metrics.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Test the baseline metrics generator."""
    gen = BaselineMetricsGenerator()
    result = gen.generate_baseline_metrics("test-project")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success":
        saved_path = gen.save_baseline_metrics("test-project", result)
        print(f"\n✓ Baseline metrics saved to: {saved_path}")


if __name__ == "__main__":
    main()
