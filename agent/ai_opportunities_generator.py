"""
AI/ML Opportunities Generator — Stage 9 Autonomization Deliverable

Identifies opportunities for AI/ML technologies to enable autonomous decision-making
and intelligent automation using LLM-based analysis.

AI/ML opportunity types:
- Classification: Categorizing documents, requests, cases
- NLP: Extracting information from unstructured text
- Prediction: Forecasting demand, risk, outcomes
- Optimization: Finding optimal solutions (scheduling, routing)
- Computer Vision: Processing images, documents, forms
- Anomaly Detection: Identifying outliers and fraud
- Recommendation: Suggesting next best actions

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.llm import call_model


class AIOpportunitiesGenerator:
    """
    Generates AI/ML opportunities assessment from knowledge base.

    Uses LLM to intelligently identify where AI/ML can enable autonomous
    decision-making and intelligent processing.
    """

    # LLM prompt template for AI opportunities analysis
    AI_OPPORTUNITIES_PROMPT = """You are an AI/ML strategist analyzing a business process to identify opportunities for AI/ML technologies.

Given the following process information:

Process Steps:
{process_steps}

Decisions Made:
{decisions}

Data Inputs:
{inputs}

Exceptions and Variations:
{exceptions}

Analyze this process and identify SPECIFIC opportunities where AI/ML technologies can enable:
1. **Autonomous decision-making** (replacing human judgment with ML models)
2. **Intelligent processing** (NLP for documents, computer vision for images)
3. **Predictive capabilities** (forecasting outcomes, identifying risks)
4. **Optimization** (finding best solutions automatically)

For each AI/ML opportunity, assess:
- **AI/ML Type**: Classification, NLP, Prediction, Optimization, Computer Vision, Anomaly Detection, Recommendation
- **Use case description**: What will the AI/ML system do?
- **Input data**: What data is available for training?
- **Output/Decision**: What will the model predict or decide?
- **Data availability**: Do we have historical data? How much? (Low/Medium/High)
- **Data quality**: Is the data clean, labeled, consistent? (Poor/Fair/Good/Excellent)
- **Expected accuracy**: Realistic accuracy target (e.g., 85-95%)
- **Confidence level**: How confident are we this will work? (Low/Medium/High)
- **Implementation complexity**: Simple/Medium/Complex
- **Prerequisites**: What's needed (data collection, labeling, infrastructure)
- **Business value**: Time savings, quality improvement, cost reduction

Return your analysis as valid JSON:
{{
  "opportunities": [
    {{
      "id": "AI-1",
      "name": "Brief name of the opportunity",
      "ai_ml_type": "Classification|NLP|Prediction|Optimization|Computer Vision|Anomaly Detection|Recommendation",
      "use_case": "Detailed description of what the AI/ML system will do",
      "business_process_step": "Which step(s) will this impact",
      "input_data": {{
        "data_sources": ["List of data sources"],
        "data_availability": "low|medium|high",
        "data_quality": "poor|fair|good|excellent",
        "historical_records_estimate": number,
        "labeling_required": true|false
      }},
      "output_decision": "What the model will predict or decide",
      "expected_performance": {{
        "accuracy_target": "85-95%",
        "precision_target": "optional",
        "recall_target": "optional",
        "confidence_level": "low|medium|high"
      }},
      "implementation": {{
        "complexity": "simple|medium|complex",
        "estimated_effort_months": number,
        "prerequisites": ["Data collection", "Labeling", "etc."],
        "technology_stack": ["TensorFlow", "scikit-learn", "etc."],
        "infrastructure_needs": "Cloud ML platform, GPU compute, etc."
      }},
      "business_value": {{
        "time_savings_percent": 0-100,
        "quality_improvement": "description",
        "cost_reduction_annual": number,
        "strategic_value": "description"
      }},
      "risks": [
        {{
          "risk": "Description",
          "likelihood": "low|medium|high",
          "mitigation": "How to address"
        }}
      ]
    }}
  ],
  "summary": {{
    "total_opportunities": number,
    "by_type": {{"Classification": count, "NLP": count, ...}},
    "high_confidence_count": number,
    "data_readiness_score": "low|medium|high",
    "recommended_starting_point": "Which opportunity to start with and why"
  }}
}}

Be realistic about data requirements and accuracy targets. Focus on opportunities where sufficient data exists or can be collected.
"""

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize AI Opportunities Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_ai_opportunities(self, project_id: str) -> Dict[str, Any]:
        """
        Generate AI/ML opportunities assessment from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with AI/ML opportunities structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "opportunities": [...],
                "summary": {...},
                "completeness": {
                    "opportunities_identified": 0-100,
                    "data_assessed": 0-100,
                    "implementation_planned": 0-100,
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
            decisions = self._extract_decisions(facts)
            inputs = self._extract_inputs(facts)

            if not process_steps:
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "No process steps found in knowledge base"
                }

            # Use LLM to identify AI opportunities
            llm_result = self._analyze_with_llm(
                project_id=project_id,
                process_steps=process_steps,
                decisions=decisions,
                inputs=inputs,
                exceptions=exceptions
            )

            opportunities_data = llm_result.get("opportunities", [])
            summary = llm_result.get("summary", {})

            # Calculate completeness
            completeness = self._calculate_completeness(opportunities_data)

            # Identify missing fields
            missing = self._identify_missing_fields(opportunities_data, summary)

            # Save deliverable
            self._save_deliverable(project_id, {
                "opportunities": opportunities_data,
                "summary": summary,
                "metadata": {
                    "generation_date": datetime.now().isoformat(),
                    "total_opportunities": len(opportunities_data),
                    "analysis_method": "llm_based"
                }
            })

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "opportunities": opportunities_data,
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

    def _extract_decisions(self, facts: List[Dict]) -> List[str]:
        """Extract decision points from facts."""
        decisions = []
        decision_facts = [f for f in facts if f.get("category") == "decisions"]

        for fact in decision_facts:
            decision_text = fact.get("fact", "").strip()
            if decision_text:
                decisions.append(decision_text)

        return decisions

    def _extract_inputs(self, facts: List[Dict]) -> List[str]:
        """Extract inputs from facts."""
        inputs = []
        input_facts = [f for f in facts if f.get("category") == "inputs"]

        for fact in input_facts:
            input_text = fact.get("fact", "").strip()
            if input_text:
                inputs.append(input_text)

        return inputs

    def _analyze_with_llm(
        self,
        project_id: str,
        process_steps: List[str],
        decisions: List[str],
        inputs: List[str],
        exceptions: List[str]
    ) -> Dict[str, Any]:
        """Use LLM to identify AI/ML opportunities."""

        # Format data for prompt
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(process_steps)])
        decisions_text = "\n".join([f"  - {d}" for d in decisions]) if decisions else "No explicit decisions documented"
        inputs_text = "\n".join([f"  - {inp}" for inp in inputs]) if inputs else "No inputs documented"
        exceptions_text = "\n".join([f"  - {exc}" for exc in exceptions[:15]]) if exceptions else "No exceptions documented"

        # Build prompt
        prompt = self.AI_OPPORTUNITIES_PROMPT.format(
            process_steps=steps_text,
            decisions=decisions_text,
            inputs=inputs_text,
            exceptions=exceptions_text
        )

        # Call LLM
        result = call_model(
            project_id=project_id,
            agent="ai_opportunities_generator",
            prompt=prompt,
            preferred_model="gpt-4o",  # Use premium model for strategic analysis
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
                if "opportunities" not in data:
                    data["opportunities"] = []
                if "summary" not in data:
                    data["summary"] = {
                        "total_opportunities": len(data.get("opportunities", [])),
                        "high_confidence_count": 0
                    }

                return data
            else:
                raise ValueError("No JSON object found in response")

        except Exception as e:
            # Return minimal structure on parse failure
            return {
                "opportunities": [],
                "summary": {
                    "total_opportunities": 0,
                    "high_confidence_count": 0,
                    "parse_error": str(e)
                }
            }

    def _calculate_completeness(self, opportunities: List[Dict]) -> Dict[str, int]:
        """Calculate completeness percentage for AI opportunities."""
        if not opportunities:
            return {
                "opportunities_identified": 0,
                "data_assessed": 0,
                "implementation_planned": 0,
                "overall": 0
            }

        # Check if opportunities are identified
        opportunities_identified = 100 if opportunities else 0

        # Check if data assessment is complete
        data_assessed = sum(
            1 for o in opportunities
            if o.get("input_data", {}).get("data_availability")
        ) / len(opportunities) * 100

        # Check if implementation is planned
        implementation_planned = sum(
            1 for o in opportunities
            if o.get("implementation", {}).get("complexity")
        ) / len(opportunities) * 100

        overall = (opportunities_identified + data_assessed + implementation_planned) // 3

        return {
            "opportunities_identified": int(opportunities_identified),
            "data_assessed": int(data_assessed),
            "implementation_planned": int(implementation_planned),
            "overall": int(overall)
        }

    def _identify_missing_fields(self, opportunities: List[Dict], summary: Dict) -> List[str]:
        """Identify missing or incomplete fields."""
        missing = []

        if not opportunities:
            missing.append("ai_ml_opportunities")
        else:
            # Check for incomplete opportunity data
            for idx, opp in enumerate(opportunities):
                if not opp.get("input_data"):
                    missing.append(f"opportunity_{idx+1}_input_data")
                if not opp.get("expected_performance"):
                    missing.append(f"opportunity_{idx+1}_expected_performance")
                if not opp.get("implementation"):
                    missing.append(f"opportunity_{idx+1}_implementation")

        if not summary:
            missing.append("summary")

        return missing

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save AI/ML opportunities to project deliverables folder.

        Args:
            project_id: Project ID
            data: AI opportunities data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "5-autonomization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "ai_ml_opportunities.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    gen = AIOpportunitiesGenerator()
    result = gen.generate_ai_opportunities("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Opportunities: {len(result.get('opportunities', []))}")
    print(f"Completeness: {result.get('completeness', {}).get('overall', 0)}%")
    if result.get('missing_fields'):
        print(f"Missing fields: {result.get('missing_fields')}")
