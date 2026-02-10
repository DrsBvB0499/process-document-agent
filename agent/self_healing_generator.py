"""
Self-Healing Design Generator — Stage 9 Autonomization Deliverable

Designs self-healing patterns for autonomous exception handling and system
resilience using LLM-based analysis of exception patterns.

Self-healing capabilities:
- Automatic error detection and diagnosis
- Self-recovery patterns (retry, fallback, circuit breaker)
- Predictive failure prevention
- Automated escalation and alerting
- Continuous learning from failures
- Graceful degradation strategies

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent.llm import call_model


class SelfHealingGenerator:
    """
    Generates self-healing design patterns from knowledge base exceptions.

    Uses LLM to analyze exception patterns and design intelligent
    recovery strategies that enable autonomous operation.
    """

    # LLM prompt template for self-healing design
    SELF_HEALING_PROMPT = """You are a resilience engineer designing self-healing patterns for an automated business process.

Given the following exception and error information:

Known Exceptions:
{exceptions}

Process Steps:
{process_steps}

System Integrations:
{systems}

Analyze these exceptions and design SPECIFIC self-healing patterns that will:
1. **Detect errors automatically** (monitoring, health checks)
2. **Diagnose root causes** (pattern recognition, correlation)
3. **Attempt self-recovery** (retry logic, alternative paths, fallbacks)
4. **Escalate intelligently** (only when recovery fails)
5. **Learn continuously** (improve healing strategies over time)

For each exception or error pattern, design:
- **Exception pattern**: What type of error/exception
- **Frequency**: How often does this occur? (rare/occasional/frequent)
- **Impact**: Business impact if unhandled (low/medium/high/critical)
- **Detection strategy**: How to detect this error automatically
- **Healing strategy**: Specific recovery actions to attempt
- **Healing sequence**: Ordered list of recovery steps
- **Success criteria**: How to know if healing worked
- **Fallback strategy**: What to do if healing fails
- **Escalation trigger**: When to involve humans
- **Monitoring metrics**: What to track
- **Learning mechanism**: How to improve over time

Also design:
- **Health check framework**: Proactive monitoring to prevent failures
- **Circuit breaker patterns**: Prevent cascading failures
- **Graceful degradation**: Maintain partial service during issues
- **Chaos engineering approach**: How to test resilience

Return your design as valid JSON:
{{
  "healing_patterns": [
    {{
      "id": "HEAL-1",
      "exception_pattern": "Description of the error/exception",
      "frequency": "rare|occasional|frequent",
      "impact": "low|medium|high|critical",
      "detection": {{
        "monitoring_type": "Exception handler|Health check|Log analysis|Metric threshold",
        "detection_mechanism": "How this error is detected",
        "alert_threshold": "When to trigger detection"
      }},
      "healing_strategy": {{
        "strategy_type": "Retry|Fallback|Alternative Path|Data Repair|Service Restart|Cache Refresh",
        "healing_sequence": [
          {{
            "step": 1,
            "action": "Specific action to take",
            "timeout_seconds": number,
            "expected_outcome": "What should happen"
          }}
        ],
        "max_attempts": number,
        "backoff_strategy": "Immediate|Linear|Exponential"
      }},
      "success_criteria": {{
        "validation": "How to confirm healing worked",
        "success_metrics": ["Metric 1", "Metric 2"]
      }},
      "fallback": {{
        "fallback_action": "What to do if healing fails",
        "degraded_mode": "Can process continue with reduced functionality?",
        "user_impact": "What does the user experience?"
      }},
      "escalation": {{
        "escalation_trigger": "When to escalate to humans",
        "escalation_target": "Who to notify (role/team)",
        "escalation_data": "What information to provide"
      }},
      "monitoring": {{
        "metrics": ["healing_success_rate", "mean_time_to_recovery"],
        "dashboards": "Where to visualize",
        "alerts": ["Alert 1", "Alert 2"]
      }},
      "learning": {{
        "data_collection": "What to log for learning",
        "pattern_analysis": "How to identify trends",
        "improvement_cycle": "How often to review and improve"
      }}
    }}
  ],
  "resilience_framework": {{
    "health_checks": [
      {{
        "check_name": "Name of health check",
        "frequency": "Interval",
        "validation": "What to check",
        "failure_action": "What to do if check fails"
      }}
    ],
    "circuit_breakers": [
      {{
        "protected_service": "Service name",
        "failure_threshold": number,
        "timeout_seconds": number,
        "half_open_retry_delay": number
      }}
    ],
    "graceful_degradation": [
      {{
        "scenario": "Failure scenario",
        "degraded_functionality": "What still works",
        "recovery_path": "How to restore full function"
      }}
    ]
  }},
  "chaos_engineering": {{
    "test_scenarios": ["Scenario 1", "Scenario 2"],
    "frequency": "How often to test",
    "safety_controls": ["Control 1", "Control 2"]
  }},
  "summary": {{
    "total_patterns": number,
    "coverage": "Percentage of exceptions covered",
    "autonomous_recovery_potential": "Percentage that can self-heal",
    "estimated_mttr_improvement": "Mean time to recovery improvement"
  }}
}}

Design practical, implementable self-healing strategies. Prioritize high-impact, frequent exceptions.
"""

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Self-Healing Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_self_healing_design(self, project_id: str) -> Dict[str, Any]:
        """
        Generate self-healing design from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with self-healing design structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "healing_patterns": [...],
                "resilience_framework": {...},
                "chaos_engineering": {...},
                "summary": {...},
                "completeness": {
                    "patterns_designed": 0-100,
                    "monitoring_defined": 0-100,
                    "learning_enabled": 0-100,
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
            systems = self._extract_systems(facts)

            if not exceptions:
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "No exceptions found in knowledge base"
                }

            # Use LLM to design self-healing patterns
            llm_result = self._design_with_llm(
                project_id=project_id,
                exceptions=exceptions,
                process_steps=process_steps,
                systems=systems
            )

            healing_data = {
                "healing_patterns": llm_result.get("healing_patterns", []),
                "resilience_framework": llm_result.get("resilience_framework", {}),
                "chaos_engineering": llm_result.get("chaos_engineering", {}),
                "summary": llm_result.get("summary", {})
            }

            # Calculate completeness
            completeness = self._calculate_completeness(healing_data)

            # Identify missing fields
            missing = self._identify_missing_fields(healing_data)

            # Save deliverable
            self._save_deliverable(project_id, {
                **healing_data,
                "metadata": {
                    "generation_date": datetime.now().isoformat(),
                    "exceptions_analyzed": len(exceptions),
                    "design_method": "llm_based"
                }
            })

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                **healing_data,
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

    def _extract_systems(self, facts: List[Dict]) -> List[str]:
        """Extract systems from facts."""
        systems = []
        system_facts = [f for f in facts if f.get("category") == "systems"]

        for fact in system_facts:
            system_text = fact.get("fact", "").strip()
            if system_text:
                systems.append(system_text)

        return systems

    def _design_with_llm(
        self,
        project_id: str,
        exceptions: List[str],
        process_steps: List[str],
        systems: List[str]
    ) -> Dict[str, Any]:
        """Use LLM to design self-healing patterns."""

        # Format data for prompt
        exceptions_text = "\n".join([f"  - {exc}" for exc in exceptions[:20]])  # Limit to 20
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(process_steps[:15])])  # Limit to 15
        systems_text = "\n".join([f"  - {sys}" for sys in systems]) if systems else "No systems documented"

        # Build prompt
        prompt = self.SELF_HEALING_PROMPT.format(
            exceptions=exceptions_text,
            process_steps=steps_text,
            systems=systems_text
        )

        # Call LLM
        result = call_model(
            project_id=project_id,
            agent="self_healing_generator",
            prompt=prompt,
            preferred_model="gpt-4o",  # Use premium model for resilience design
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
                if "healing_patterns" not in data:
                    data["healing_patterns"] = []
                if "summary" not in data:
                    data["summary"] = {
                        "total_patterns": len(data.get("healing_patterns", []))
                    }

                return data
            else:
                raise ValueError("No JSON object found in response")

        except Exception as e:
            # Return minimal structure on parse failure
            return {
                "healing_patterns": [],
                "resilience_framework": {},
                "chaos_engineering": {},
                "summary": {
                    "total_patterns": 0,
                    "parse_error": str(e)
                }
            }

    def _calculate_completeness(self, healing_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate completeness percentage for self-healing design."""
        patterns = healing_data.get("healing_patterns", [])
        resilience = healing_data.get("resilience_framework", {})

        # Check if patterns are designed
        patterns_designed = 100 if patterns else 0

        # Check if monitoring is defined
        monitoring_defined = sum(
            1 for p in patterns
            if p.get("monitoring", {}).get("metrics")
        ) / len(patterns) * 100 if patterns else 0

        # Check if learning is enabled
        learning_enabled = sum(
            1 for p in patterns
            if p.get("learning")
        ) / len(patterns) * 100 if patterns else 0

        overall = (patterns_designed + monitoring_defined + learning_enabled) // 3

        return {
            "patterns_designed": int(patterns_designed),
            "monitoring_defined": int(monitoring_defined),
            "learning_enabled": int(learning_enabled),
            "overall": int(overall)
        }

    def _identify_missing_fields(self, healing_data: Dict[str, Any]) -> List[str]:
        """Identify missing or incomplete fields."""
        missing = []

        if not healing_data.get("healing_patterns"):
            missing.append("healing_patterns")

        if not healing_data.get("resilience_framework"):
            missing.append("resilience_framework")

        if not healing_data.get("chaos_engineering"):
            missing.append("chaos_engineering")

        if not healing_data.get("summary"):
            missing.append("summary")

        return missing

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save self-healing design to project deliverables folder.

        Args:
            project_id: Project ID
            data: Self-healing design data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "5-autonomization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "self_healing_design.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    gen = SelfHealingGenerator()
    result = gen.generate_self_healing_design("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Patterns: {len(result.get('healing_patterns', []))}")
    print(f"Completeness: {result.get('completeness', {}).get('overall', 0)}%")
    if result.get('missing_fields'):
        print(f"Missing fields: {result.get('missing_fields')}")
