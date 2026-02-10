"""
Automation Candidates Generator — Stage 8 Automation Deliverable

Analyzes process steps and identifies automation opportunities using LLM-based
intelligent assessment rather than simple keyword matching.

Automation assessment criteria:
- Repeatability: How often is this step performed?
- Rule-based: Can it be defined with clear rules?
- Volume: How many transactions?
- Stability: How often does the process change?
- Complexity: Manual vs. cognitive work
- ROI potential: Time savings vs. implementation cost
- Technology fit: RPA, API, Workflow, Low-Code, etc.

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.llm import call_model


class AutomationCandidatesGenerator:
    """
    Generates automation candidates assessment from knowledge base.

    Uses LLM to intelligently analyze process steps for automation potential,
    scoring based on multiple criteria and recommending appropriate technologies.
    """

    # LLM prompt template for automation analysis
    AUTOMATION_ANALYSIS_PROMPT = """You are an automation expert analyzing process steps to identify automation opportunities.

Given the following process information:

Process Steps:
{process_steps}

Process Metrics:
{metrics}

Exception Types:
{exceptions}

Analyze EACH process step and provide a structured assessment of its automation potential.

For each step, evaluate:
1. **Repeatability**: How often is this performed? (daily, weekly, monthly)
2. **Rule-based nature**: Can it be automated with clear rules? (0-100%)
3. **Volume**: How many transactions/executions per month?
4. **Stability**: How stable is the process? (stable/moderate/volatile)
5. **Manual effort**: Time per execution
6. **Complexity**: Simple/Medium/Complex
7. **Current pain points**: Errors, delays, manual handoffs
8. **Automation feasibility**: Low/Medium/High

Then recommend:
- **Technology approach**: RPA, API Integration, Workflow Automation, Low-Code Platform, Custom Development
- **Implementation effort**: Low (< 1 month), Medium (1-3 months), High (> 3 months)
- **ROI potential**: Time savings % and cost reduction estimate
- **Risk level**: Low/Medium/High
- **Prerequisites**: What's needed before automation (data quality, system access, etc.)

Return your analysis as valid JSON:
{{
  "candidates": [
    {{
      "step_id": "AUTO-1",
      "step_description": "Description of the step",
      "automation_score": 0-100,
      "assessment": {{
        "repeatability": "daily|weekly|monthly",
        "rule_based_percentage": 0-100,
        "volume_per_month": number,
        "stability": "stable|moderate|volatile",
        "manual_effort_minutes": number,
        "complexity": "simple|medium|complex",
        "current_pain_points": ["list", "of", "issues"]
      }},
      "recommendation": {{
        "technology": "RPA|API|Workflow|Low-Code|Custom",
        "implementation_effort": "low|medium|high",
        "effort_months": number,
        "roi_time_savings_percent": 0-100,
        "roi_cost_reduction_annual": number,
        "risk_level": "low|medium|high",
        "prerequisites": ["list", "of", "requirements"]
      }},
      "business_case": "Brief justification for automation"
    }}
  ],
  "summary": {{
    "total_candidates": number,
    "high_priority_count": number,
    "quick_wins_count": number,
    "total_potential_savings_percent": number,
    "recommended_approach": "Start with quick wins or pilot high-value candidates"
  }}
}}

Focus on realistic, actionable automation opportunities. Be specific about technology choices and ROI estimates.
"""

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Automation Candidates Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_automation_candidates(self, project_id: str) -> Dict[str, Any]:
        """
        Generate automation candidates assessment from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with automation candidates structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "candidates": [...],
                "summary": {...},
                "completeness": {
                    "candidates_identified": 0-100,
                    "assessments_complete": 0-100,
                    "roi_estimated": 0-100,
                    "overall": 0-100
                },
                "missing_fields": [...],
                "llm_cost_usd": float
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
            exceptions = knowledge_base.get("exceptions", [])

            # Extract relevant information
            process_steps = self._extract_process_steps(facts)
            metrics = self._extract_metrics(facts)

            if not process_steps:
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "No process steps found in knowledge base"
                }

            # Use LLM to analyze automation candidates
            llm_result = self._analyze_with_llm(
                project_id=project_id,
                process_steps=process_steps,
                metrics=metrics,
                exceptions=exceptions
            )

            candidates_data = llm_result.get("candidates", [])
            summary = llm_result.get("summary", {})

            # Calculate completeness
            completeness = self._calculate_completeness(candidates_data)

            # Identify missing fields
            missing = self._identify_missing_fields(candidates_data, summary)

            # Save deliverable
            self._save_deliverable(project_id, {
                "candidates": candidates_data,
                "summary": summary,
                "metadata": {
                    "generation_date": datetime.now().isoformat(),
                    "total_candidates": len(candidates_data),
                    "analysis_method": "llm_based"
                }
            })

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "candidates": candidates_data,
                "summary": summary,
                "completeness": completeness,
                "missing_fields": missing,
                "llm_cost_usd": llm_result.get("cost_usd", 0.0)
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _extract_process_steps(self, facts: List[Dict]) -> List[str]:
        """Extract process steps from facts."""
        steps = []
        step_facts = [f for f in facts if f.get("category") == "process_steps"]

        for fact in step_facts:
            step_text = fact.get("fact", "").strip()
            if step_text:
                steps.append(step_text)

        return steps

    def _extract_metrics(self, facts: List[Dict]) -> Dict[str, Any]:
        """Extract relevant metrics from facts."""
        metrics = {
            "volume": [],
            "time": [],
            "cost": [],
            "quality": []
        }

        for fact in facts:
            category = fact.get("category", "")
            fact_text = fact.get("fact", "")

            if category == "volume_metrics":
                metrics["volume"].append(fact_text)
            elif category == "time_metrics":
                metrics["time"].append(fact_text)
            elif category == "cost_metrics":
                metrics["cost"].append(fact_text)
            elif category == "quality_metrics":
                metrics["quality"].append(fact_text)

        return metrics

    def _analyze_with_llm(
        self,
        project_id: str,
        process_steps: List[str],
        metrics: Dict[str, Any],
        exceptions: List[str]
    ) -> Dict[str, Any]:
        """Use LLM to analyze automation candidates."""

        # Format process steps for prompt
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(process_steps)])

        # Format metrics
        metrics_text = ""
        for category, items in metrics.items():
            if items:
                metrics_text += f"\n{category.upper()}:\n"
                metrics_text += "\n".join([f"  - {item}" for item in items[:5]])  # Limit to 5 per category

        if not metrics_text:
            metrics_text = "No specific metrics available"

        # Format exceptions
        exceptions_text = "\n".join([f"  - {exc}" for exc in exceptions[:10]]) if exceptions else "No exceptions documented"

        # Build prompt
        prompt = self.AUTOMATION_ANALYSIS_PROMPT.format(
            process_steps=steps_text,
            metrics=metrics_text,
            exceptions=exceptions_text
        )

        # Call LLM
        result = call_model(
            project_id=project_id,
            agent="automation_candidates_generator",
            prompt=prompt,
            preferred_model="gpt-4o",  # Use premium model for analysis
            escalate_on_low_confidence=False
        )

        # Parse JSON response
        response_text = result.get("text", "")
        parsed_data = self._parse_llm_response(response_text)

        # Add cost info
        parsed_data["cost_usd"] = result.get("cost_usd", 0.0)

        return parsed_data

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            # Try to extract JSON from response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                data = json.loads(json_str)

                # Validate required fields
                if "candidates" not in data:
                    data["candidates"] = []
                if "summary" not in data:
                    data["summary"] = {
                        "total_candidates": len(data.get("candidates", [])),
                        "high_priority_count": 0,
                        "quick_wins_count": 0
                    }

                return data
            else:
                raise ValueError("No JSON object found in response")

        except Exception as e:
            # Return minimal structure on parse failure
            return {
                "candidates": [],
                "summary": {
                    "total_candidates": 0,
                    "high_priority_count": 0,
                    "quick_wins_count": 0,
                    "parse_error": str(e)
                }
            }

    def _calculate_completeness(self, candidates: List[Dict]) -> Dict[str, int]:
        """Calculate completeness percentage for automation candidates."""
        if not candidates:
            return {
                "candidates_identified": 0,
                "assessments_complete": 0,
                "roi_estimated": 0,
                "overall": 0
            }

        # Check if candidates are identified
        candidates_identified = 100 if candidates else 0

        # Check if assessments are complete (has assessment object)
        assessments_complete = sum(1 for c in candidates if c.get("assessment")) / len(candidates) * 100

        # Check if ROI is estimated (has recommendation with ROI data)
        roi_estimated = sum(
            1 for c in candidates
            if c.get("recommendation", {}).get("roi_time_savings_percent") is not None
        ) / len(candidates) * 100

        overall = (candidates_identified + assessments_complete + roi_estimated) // 3

        return {
            "candidates_identified": int(candidates_identified),
            "assessments_complete": int(assessments_complete),
            "roi_estimated": int(roi_estimated),
            "overall": int(overall)
        }

    def _identify_missing_fields(self, candidates: List[Dict], summary: Dict) -> List[str]:
        """Identify missing or incomplete fields."""
        missing = []

        if not candidates:
            missing.append("automation_candidates")
        else:
            # Check for incomplete candidate data
            for idx, candidate in enumerate(candidates):
                if not candidate.get("assessment"):
                    missing.append(f"candidate_{idx+1}_assessment")
                if not candidate.get("recommendation"):
                    missing.append(f"candidate_{idx+1}_recommendation")
                if not candidate.get("automation_score"):
                    missing.append(f"candidate_{idx+1}_automation_score")

        if not summary:
            missing.append("summary")

        return missing

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save automation candidates to project deliverables folder.

        Args:
            project_id: Project ID
            data: Automation candidates data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "4-automation"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "automation_candidates.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    gen = AutomationCandidatesGenerator()
    result = gen.generate_automation_candidates("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Candidates: {len(result.get('candidates', []))}")
    print(f"Completeness: {result.get('completeness', {}).get('overall', 0)}%")
    if result.get('missing_fields'):
        print(f"Missing fields: {result.get('missing_fields')}")
