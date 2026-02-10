"""
Automation Roadmap Generator — Stage 8 Automation Deliverable

Creates a phased implementation roadmap for automation initiatives using
intelligent dependency analysis and resource planning.

Roadmap considerations:
- Dependencies between automation candidates
- Resource availability and constraints
- Quick wins vs. strategic initiatives
- Risk mitigation and change management
- Benefits realization timeline
- Technology stack evolution

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.llm import call_model


class AutomationRoadmapGenerator:
    """
    Generates phased automation implementation roadmap from candidates assessment.

    Uses LLM to intelligently sequence automation initiatives based on
    dependencies, ROI, resources, and strategic priorities.
    """

    # LLM prompt template for roadmap planning
    ROADMAP_PLANNING_PROMPT = """You are an automation program manager creating an implementation roadmap.

Given the following automation candidates:

{candidates_summary}

Analyze these candidates and create a phased implementation roadmap that:

1. **Identifies dependencies**: Which automations must come first?
2. **Sequences intelligently**: Balance quick wins with strategic value
3. **Considers resources**: Don't overload capacity
4. **Manages risk**: Start with lower-risk automations to build capability
5. **Maximizes learning**: Each phase builds on previous learnings

Create a roadmap with 2-4 phases over 6-18 months:

Phase structure:
- **Phase name and duration**
- **Objectives**: What will be achieved
- **Candidates in this phase**: Which automations to implement (by ID)
- **Dependencies**: What must be completed first
- **Resource requirements**: Team size, skills needed
- **Expected benefits**: Time savings, cost reduction, quality improvement
- **Key risks and mitigations**
- **Success criteria**: How to measure phase success

Also provide:
- **Overall timeline**: Total program duration
- **Resource plan**: Team composition and growth
- **Benefits realization**: When will ROI be achieved
- **Technology evolution**: How the automation platform will develop
- **Change management approach**: How to ensure adoption

Return your roadmap as valid JSON:
{{
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Pilot & Quick Wins",
      "duration_months": 2-3,
      "start_month": 1,
      "end_month": 3,
      "objectives": ["Prove concept", "Build capability", "Deliver quick wins"],
      "candidates": ["AUTO-1", "AUTO-3"],
      "dependencies": ["None - this is phase 1"],
      "resource_requirements": {{
        "team_size": number,
        "skills_needed": ["RPA Developer", "Business Analyst"],
        "estimated_hours": number
      }},
      "expected_benefits": {{
        "time_savings_hours_per_month": number,
        "cost_reduction_annual": number,
        "quality_improvement": "description"
      }},
      "risks": [
        {{
          "risk": "Description of risk",
          "likelihood": "low|medium|high",
          "impact": "low|medium|high",
          "mitigation": "How to address"
        }}
      ],
      "success_criteria": ["Measurable criteria"]
    }}
  ],
  "program_summary": {{
    "total_duration_months": number,
    "total_candidates": number,
    "phases_count": number,
    "cumulative_benefits": {{
      "year_1_savings": number,
      "year_2_savings": number,
      "year_3_savings": number
    }},
    "investment_required": {{
      "technology": number,
      "resources": number,
      "training": number,
      "total": number
    }}
  }},
  "resource_plan": {{
    "phase_1": {{"roles": [{{"role": "name", "fte": number}}]}},
    "phase_2": {{"roles": [{{"role": "name", "fte": number}}]}},
    "ramp_up_strategy": "Description"
  }},
  "technology_roadmap": {{
    "current_state": "Description",
    "target_state": "Description",
    "evolution_steps": ["Step 1", "Step 2"]
  }},
  "change_management": {{
    "approach": "Description",
    "stakeholder_engagement": ["Activity 1", "Activity 2"],
    "training_plan": "Description",
    "communication_strategy": "Description"
  }}
}}

Be realistic about timelines and resources. Focus on delivering value incrementally.
"""

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Automation Roadmap Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_automation_roadmap(self, project_id: str) -> Dict[str, Any]:
        """
        Generate automation implementation roadmap from candidates assessment.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with roadmap structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "roadmap": {
                    "phases": [...],
                    "program_summary": {...},
                    "resource_plan": {...},
                    "technology_roadmap": {...},
                    "change_management": {...}
                },
                "completeness": {
                    "phases_defined": 0-100,
                    "resources_planned": 0-100,
                    "benefits_quantified": 0-100,
                    "overall": 0-100
                },
                "missing_fields": [...],
                "llm_cost_usd": float
            }
        """
        try:
            # Load automation candidates
            candidates_path = (
                self.projects_root / project_id / "deliverables" / "4-automation" /
                "automation_candidates.json"
            )

            if not candidates_path.exists():
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "Automation candidates not found. Generate candidates first."
                }

            with open(candidates_path, 'r', encoding='utf-8') as f:
                candidates_data = json.load(f)

            candidates = candidates_data.get("candidates", [])

            if not candidates:
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "No automation candidates found"
                }

            # Use LLM to create roadmap
            llm_result = self._plan_with_llm(
                project_id=project_id,
                candidates=candidates
            )

            roadmap_data = {
                "phases": llm_result.get("phases", []),
                "program_summary": llm_result.get("program_summary", {}),
                "resource_plan": llm_result.get("resource_plan", {}),
                "technology_roadmap": llm_result.get("technology_roadmap", {}),
                "change_management": llm_result.get("change_management", {})
            }

            # Calculate completeness
            completeness = self._calculate_completeness(roadmap_data)

            # Identify missing fields
            missing = self._identify_missing_fields(roadmap_data)

            # Save deliverable
            self._save_deliverable(project_id, {
                **roadmap_data,
                "metadata": {
                    "generation_date": datetime.now().isoformat(),
                    "candidates_analyzed": len(candidates),
                    "planning_method": "llm_based"
                }
            })

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "roadmap": roadmap_data,
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

    def _plan_with_llm(
        self,
        project_id: str,
        candidates: List[Dict]
    ) -> Dict[str, Any]:
        """Use LLM to create implementation roadmap."""

        # Format candidates for prompt
        candidates_summary = self._format_candidates_summary(candidates)

        # Build prompt
        prompt = self.ROADMAP_PLANNING_PROMPT.format(
            candidates_summary=candidates_summary
        )

        # Call LLM
        result = call_model(
            project_id=project_id,
            agent="automation_roadmap_generator",
            prompt=prompt,
            preferred_model="gpt-4o",  # Use premium model for strategic planning
            escalate_on_low_confidence=False
        )

        # Parse JSON response
        response_text = result.get("text", "")
        parsed_data = self._parse_llm_response(response_text)

        # Add cost info
        parsed_data["cost_usd"] = result.get("cost_usd", 0.0)

        return parsed_data

    def _format_candidates_summary(self, candidates: List[Dict]) -> str:
        """Format candidates for LLM prompt."""
        summary_lines = []

        for candidate in candidates:
            step_id = candidate.get("step_id", "UNKNOWN")
            description = candidate.get("step_description", "")[:100]
            score = candidate.get("automation_score", 0)

            recommendation = candidate.get("recommendation", {})
            technology = recommendation.get("technology", "Unknown")
            effort = recommendation.get("implementation_effort", "unknown")
            roi = recommendation.get("roi_time_savings_percent", 0)

            summary_lines.append(
                f"- **{step_id}** (Score: {score}/100): {description}\n"
                f"  Technology: {technology}, Effort: {effort}, ROI: {roi}% time savings"
            )

        return "\n\n".join(summary_lines)

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
                if "phases" not in data:
                    data["phases"] = []
                if "program_summary" not in data:
                    data["program_summary"] = {}

                return data
            else:
                raise ValueError("No JSON object found in response")

        except Exception as e:
            # Return minimal structure on parse failure
            return {
                "phases": [],
                "program_summary": {
                    "total_duration_months": 0,
                    "parse_error": str(e)
                },
                "resource_plan": {},
                "technology_roadmap": {},
                "change_management": {}
            }

    def _calculate_completeness(self, roadmap: Dict[str, Any]) -> Dict[str, int]:
        """Calculate completeness percentage for roadmap."""
        phases = roadmap.get("phases", [])
        resource_plan = roadmap.get("resource_plan", {})
        program_summary = roadmap.get("program_summary", {})

        # Check if phases are defined
        phases_defined = 100 if phases else 0

        # Check if resources are planned (resource_plan has content)
        resources_planned = 100 if resource_plan else 0

        # Check if benefits are quantified (program_summary has cumulative_benefits)
        benefits_quantified = 100 if program_summary.get("cumulative_benefits") else 0

        overall = (phases_defined + resources_planned + benefits_quantified) // 3

        return {
            "phases_defined": int(phases_defined),
            "resources_planned": int(resources_planned),
            "benefits_quantified": int(benefits_quantified),
            "overall": int(overall)
        }

    def _identify_missing_fields(self, roadmap: Dict[str, Any]) -> List[str]:
        """Identify missing or incomplete fields."""
        missing = []

        if not roadmap.get("phases"):
            missing.append("implementation_phases")

        if not roadmap.get("program_summary"):
            missing.append("program_summary")

        if not roadmap.get("resource_plan"):
            missing.append("resource_plan")

        if not roadmap.get("technology_roadmap"):
            missing.append("technology_roadmap")

        if not roadmap.get("change_management"):
            missing.append("change_management")

        return missing

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save automation roadmap to project deliverables folder.

        Args:
            project_id: Project ID
            data: Roadmap data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "4-automation"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "implementation_roadmap.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    gen = AutomationRoadmapGenerator()
    result = gen.generate_automation_roadmap("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Phases: {len(result.get('roadmap', {}).get('phases', []))}")
    print(f"Completeness: {result.get('completeness', {}).get('overall', 0)}%")
    if result.get('missing_fields'):
        print(f"Missing fields: {result.get('missing_fields')}")
