"""
KPI Dashboard Generator — Stage 6 Optimization Deliverable

Defines measurable improvement targets (KPIs) based on baseline metrics
and optimization opportunities. Creates a dashboard structure for tracking progress.

KPI Categories:
- Time: Cycle time, lead time, wait time reduction
- Cost: Labor cost, error cost, resource utilization
- Quality: First-pass yield, error rate, defect rate
- Volume: Throughput, capacity utilization
- Customer: Response time, satisfaction, SLA compliance

SMART KPI Criteria:
- Specific: Clearly defined measure
- Measurable: Quantifiable metric
- Achievable: Realistic target
- Relevant: Aligned with business goals
- Time-bound: Target deadline

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class KPIDashboardGenerator:
    """
    Generates KPI dashboard with targets based on baseline metrics.

    Expected inputs:
    - Baseline metrics (from Standardization phase)
    - Value stream map (timing data)
    - Waste analysis (improvement opportunities)
    - Quick wins (expected impact)
    """

    # Standard KPI templates by category
    KPI_TEMPLATES = {
        "time": [
            {
                "name": "Cycle Time",
                "description": "Average time to complete process from start to finish",
                "unit": "hours",
                "target_improvement": 30,  # 30% reduction
                "calculation": "Sum of all step cycle times"
            },
            {
                "name": "Lead Time",
                "description": "Total elapsed time including wait times",
                "unit": "hours",
                "target_improvement": 40,  # 40% reduction
                "calculation": "Cycle time + Wait time"
            },
            {
                "name": "Wait Time",
                "description": "Time spent waiting between steps",
                "unit": "hours",
                "target_improvement": 50,  # 50% reduction
                "calculation": "Sum of all delays and queuing"
            }
        ],
        "cost": [
            {
                "name": "Process Cost per Unit",
                "description": "Average cost to process one transaction/item",
                "unit": "currency",
                "target_improvement": 25,  # 25% reduction
                "calculation": "Total labor cost / Volume"
            },
            {
                "name": "Error Cost",
                "description": "Cost of rework and corrections",
                "unit": "currency",
                "target_improvement": 60,  # 60% reduction
                "calculation": "Exception count * Average rework time * Hourly rate"
            }
        ],
        "quality": [
            {
                "name": "First Pass Yield",
                "description": "Percentage of work completed correctly the first time",
                "unit": "percentage",
                "target_improvement": 20,  # 20 percentage point increase
                "calculation": "(Total - Exceptions) / Total * 100"
            },
            {
                "name": "Error Rate",
                "description": "Percentage of transactions with errors",
                "unit": "percentage",
                "target_improvement": -50,  # 50% reduction (negative = reduce)
                "calculation": "Exceptions / Total * 100"
            }
        ],
        "volume": [
            {
                "name": "Throughput",
                "description": "Number of transactions processed per day",
                "unit": "count/day",
                "target_improvement": 50,  # 50% increase
                "calculation": "Total transactions / Working days"
            },
            {
                "name": "Capacity Utilization",
                "description": "Percentage of available capacity being used",
                "unit": "percentage",
                "target_improvement": 30,  # 30 percentage point increase
                "calculation": "Actual volume / Maximum capacity * 100"
            }
        ]
    }

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize KPI Dashboard Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_kpi_dashboard(self, project_id: str) -> Dict[str, Any]:
        """
        Generate KPI Dashboard from project deliverables and knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with KPI dashboard structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "kpi_dashboard": {
                    "time_kpis": [...],
                    "cost_kpis": [...],
                    "quality_kpis": [...],
                    "volume_kpis": [...],
                    "summary": {
                        "total_kpis": int,
                        "baseline_established": bool,
                        "targets_set": bool
                    }
                },
                "completeness": {...},
                "missing_fields": [...]
            }
        """
        try:
            # Load baseline metrics
            baseline_metrics = self._load_baseline_metrics(project_id)
            if not baseline_metrics:
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "Baseline metrics not found. Generate baseline metrics first."
                }

            # Load value stream map (optional)
            value_stream = self._load_value_stream(project_id)

            # Load waste analysis (optional)
            waste_analysis = self._load_waste_analysis(project_id)

            # Generate KPIs for each category
            time_kpis = self._generate_time_kpis(baseline_metrics, value_stream)
            cost_kpis = self._generate_cost_kpis(baseline_metrics, waste_analysis)
            quality_kpis = self._generate_quality_kpis(baseline_metrics, waste_analysis)
            volume_kpis = self._generate_volume_kpis(baseline_metrics)

            # Combine all KPIs
            all_kpis = time_kpis + cost_kpis + quality_kpis + volume_kpis

            # Calculate summary
            summary = {
                "total_kpis": len(all_kpis),
                "baseline_established": True,
                "targets_set": all(kpi.get("target") is not None for kpi in all_kpis),
                "categories": {
                    "time": len(time_kpis),
                    "cost": len(cost_kpis),
                    "quality": len(quality_kpis),
                    "volume": len(volume_kpis)
                }
            }

            # Calculate completeness
            completeness = {
                "kpis_defined": 100 if all_kpis else 0,
                "baselines_set": 100 if baseline_metrics else 0,
                "targets_set": 100 if summary["targets_set"] else 50,
                "overall": sum([
                    100 if all_kpis else 0,
                    100 if baseline_metrics else 0,
                    100 if summary["targets_set"] else 50
                ]) // 3
            }

            # Identify missing fields
            missing = []
            if not all_kpis:
                missing.append("kpis")
            if not summary["targets_set"]:
                missing.append("targets")

            # Save deliverable
            deliverable_data = {
                "time_kpis": time_kpis,
                "cost_kpis": cost_kpis,
                "quality_kpis": quality_kpis,
                "volume_kpis": volume_kpis,
                "summary": summary
            }

            self._save_deliverable(project_id, deliverable_data)

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "kpi_dashboard": deliverable_data,
                "completeness": completeness,
                "missing_fields": missing
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _generate_time_kpis(
        self,
        baseline_metrics: Dict[str, Any],
        value_stream: Optional[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Generate time-based KPIs.
        """
        kpis = []

        # Extract baseline time data
        time_data = baseline_metrics.get("time", {})

        for template in self.KPI_TEMPLATES["time"]:
            kpi_name = template["name"]
            baseline_value = None

            # Map KPI to baseline metric
            if "cycle time" in kpi_name.lower():
                baseline_value = time_data.get("average_cycle_time")
            elif "lead time" in kpi_name.lower():
                baseline_value = time_data.get("average_lead_time")
            elif "wait time" in kpi_name.lower():
                # Calculate from value stream if available
                if value_stream:
                    baseline_value = value_stream.get("metrics", {}).get("total_wait_time")

            if baseline_value is not None:
                # Calculate target
                improvement_pct = template["target_improvement"]
                target_value = baseline_value * (1 - improvement_pct / 100)

                kpis.append({
                    "name": kpi_name,
                    "description": template["description"],
                    "category": "time",
                    "unit": template["unit"],
                    "baseline": round(baseline_value, 2),
                    "target": round(target_value, 2),
                    "improvement_target_pct": improvement_pct,
                    "calculation": template["calculation"],
                    "tracking_frequency": "weekly"
                })

        return kpis

    def _generate_cost_kpis(
        self,
        baseline_metrics: Dict[str, Any],
        waste_analysis: Optional[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Generate cost-based KPIs.
        """
        kpis = []
        cost_data = baseline_metrics.get("cost", {})

        for template in self.KPI_TEMPLATES["cost"]:
            kpi_name = template["name"]
            baseline_value = None

            if "process cost" in kpi_name.lower():
                baseline_value = cost_data.get("cost_per_transaction")
            elif "error cost" in kpi_name.lower():
                baseline_value = cost_data.get("error_cost")

            if baseline_value is not None:
                improvement_pct = template["target_improvement"]
                target_value = baseline_value * (1 - improvement_pct / 100)

                kpis.append({
                    "name": kpi_name,
                    "description": template["description"],
                    "category": "cost",
                    "unit": template["unit"],
                    "baseline": round(baseline_value, 2),
                    "target": round(target_value, 2),
                    "improvement_target_pct": improvement_pct,
                    "calculation": template["calculation"],
                    "tracking_frequency": "monthly"
                })

        return kpis

    def _generate_quality_kpis(
        self,
        baseline_metrics: Dict[str, Any],
        waste_analysis: Optional[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Generate quality-based KPIs.
        """
        kpis = []
        quality_data = baseline_metrics.get("quality", {})

        for template in self.KPI_TEMPLATES["quality"]:
            kpi_name = template["name"]
            baseline_value = None

            if "first pass yield" in kpi_name.lower():
                error_rate = quality_data.get("error_rate", 10)  # Default 10%
                baseline_value = 100 - error_rate  # FPY = 100% - error rate
            elif "error rate" in kpi_name.lower():
                baseline_value = quality_data.get("error_rate", 10)

            if baseline_value is not None:
                improvement_pct = template["target_improvement"]

                if improvement_pct < 0:  # For metrics we want to reduce
                    target_value = baseline_value * (1 + improvement_pct / 100)
                else:  # For metrics we want to increase
                    target_value = baseline_value + improvement_pct

                kpis.append({
                    "name": kpi_name,
                    "description": template["description"],
                    "category": "quality",
                    "unit": template["unit"],
                    "baseline": round(baseline_value, 1),
                    "target": round(target_value, 1),
                    "improvement_target_pct": abs(improvement_pct),
                    "calculation": template["calculation"],
                    "tracking_frequency": "weekly"
                })

        return kpis

    def _generate_volume_kpis(self, baseline_metrics: Dict[str, Any]) -> List[Dict]:
        """
        Generate volume/throughput KPIs.
        """
        kpis = []
        volume_data = baseline_metrics.get("volume", {})

        for template in self.KPI_TEMPLATES["volume"]:
            kpi_name = template["name"]
            baseline_value = None

            if "throughput" in kpi_name.lower():
                baseline_value = volume_data.get("daily_volume")
            elif "capacity" in kpi_name.lower():
                baseline_value = volume_data.get("capacity_utilization", 60)

            if baseline_value is not None:
                improvement_pct = template["target_improvement"]
                target_value = baseline_value * (1 + improvement_pct / 100)

                kpis.append({
                    "name": kpi_name,
                    "description": template["description"],
                    "category": "volume",
                    "unit": template["unit"],
                    "baseline": round(baseline_value, 1),
                    "target": round(target_value, 1),
                    "improvement_target_pct": improvement_pct,
                    "calculation": template["calculation"],
                    "tracking_frequency": "daily"
                })

        return kpis

    def _load_baseline_metrics(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load baseline metrics from Standardization phase."""
        metrics_path = (
            self.projects_root / project_id / "deliverables" / "1-standardization" / "baseline_metrics.json"
        )

        if metrics_path.exists():
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def _load_value_stream(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load value stream map if it exists."""
        vsm_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization" / "value_stream_map.json"
        )

        if vsm_path.exists():
            try:
                with open(vsm_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def _load_waste_analysis(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load waste analysis if it exists."""
        waste_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization" / "waste_analysis.json"
        )

        if waste_path.exists():
            try:
                with open(waste_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save KPI dashboard to project deliverables folder.

        Args:
            project_id: Project ID
            data: KPI dashboard data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "2-optimization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "kpi_dashboard.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    kpig = KPIDashboardGenerator()
    result = kpig.generate_kpi_dashboard("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Total KPIs: {result.get('kpi_dashboard', {}).get('summary', {}).get('total_kpis', 0)}")
    print(f"\nMissing fields: {result.get('missing_fields', [])}")
