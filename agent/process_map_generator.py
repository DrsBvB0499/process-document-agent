"""
Process Map Generator — Stage 4 Standardization Deliverable

Extracts process steps and related information (performers, systems, decision points)
from the knowledge base and produces a structured process map.

Process map structure:
  Step 1 → Performer: X, System: Y, Decision: Z?
  Step 2 → Performer: A, System: B, Decision: W?
  ...

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ProcessMapGenerator:
    """
    Generates structured process map from knowledge base facts.
    
    Expected fact categories in knowledge_base.json:
    - process_steps: sequential steps in the process
    - performers: people/roles who perform steps
    - systems: software/tools/systems used
    - decision_points: conditional branching points
    - handoffs: transfers between performers
    - cycle_time: time to complete each step
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Process Map Generator.
        
        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_process_map(self, project_id: str) -> Dict[str, Any]:
        """
        Generate process map from project knowledge base.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with process map structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "process_map": {
                    "steps": [...],
                    "performers": [...],
                    "systems": [...],
                    "decision_points": [...],
                    "handoffs": [...],
                    "connections": [...]
                },
                "completeness": {
                    "steps": 0-100,
                    "performers": 0-100,
                    "systems": 0-100,
                    "decisions": 0-100,
                    "overall": 0-100
                },
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

            # Extract process components
            steps = self._extract_by_category(facts, "process_steps")
            performers = self._extract_by_category(facts, "performers")
            systems = self._extract_by_category(facts, "systems")
            decisions = self._extract_by_category(facts, "decision_points")
            handoffs = self._extract_by_category(facts, "handoffs")

            # Build connections between elements
            connections = self._build_connections(steps, performers, systems, decisions)

            # Calculate completeness
            completeness = {
                "steps": 100 if steps else 0,
                "performers": 100 if performers else 0,
                "systems": 100 if systems else 0,
                "decisions": 100 if decisions else 0
            }
            completeness["overall"] = sum(completeness.values()) // 4

            # Identify missing fields
            missing = []
            if not steps:
                missing.append("process_steps")
            if not performers:
                missing.append("performers")
            if not systems:
                missing.append("systems")
            if not decisions:
                missing.append("decision_points")

            return {
                "status": "success",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "process_map": {
                    "steps": steps if steps else [],
                    "performers": performers if performers else [],
                    "systems": systems if systems else [],
                    "decision_points": decisions if decisions else [],
                    "handoffs": handoffs if handoffs else [],
                    "connections": connections
                },
                "completeness": completeness,
                "missing_fields": missing,
                "step_count": len(steps),
                "performer_count": len(performers),
                "system_count": len(systems),
                "decision_count": len(decisions)
            }

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _extract_by_category(self, facts: List[Dict], category: str) -> List[str]:
        """
        Extract facts by category.
        
        Args:
            facts: List of fact dictionaries
            category: Category to filter by
            
        Returns:
            List of fact strings for this category
        """
        extracted = []
        for fact_obj in facts:
            if isinstance(fact_obj, dict) and fact_obj.get("category") == category:
                fact_text = fact_obj.get("fact", "")
                if fact_text and fact_text not in extracted:
                    extracted.append(fact_text)
        return extracted

    def _build_connections(self, steps: List[str], performers: List[str], 
                          systems: List[str], decisions: List[str]) -> List[Dict]:
        """
        Build explicit connections between process elements.
        
        In a real implementation, this would use more sophisticated
        NLP to understand which performers perform which steps, etc.
        For now, return basic structure.
        
        Args:
            steps: List of process steps
            performers: List of performers
            systems: List of systems
            decisions: List of decisions
            
        Returns:
            List of connection objects
        """
        connections = []
        
        # Note: In production, this would use semantic analysis or
        # explicit annotations in the knowledge base to map relationships
        # For now, we just structure what we have
        
        if steps:
            # Create step sequence
            for i in range(len(steps) - 1):
                connections.append({
                    "from": steps[i],
                    "to": steps[i + 1],
                    "type": "sequence"
                })
        
        # Add decision branches if mentioned in decision points
        for decision in decisions:
            if steps:
                # Find which step has the decision
                connections.append({
                    "from": steps[0] if steps else "start",
                    "decision": decision,
                    "type": "decision"
                })

        return connections

    def save_process_map(self, project_id: str, process_map_data: Dict[str, Any]) -> Path:
        """
        Save process map data to project deliverables folder.
        
        Args:
            project_id: ID of the project
            process_map_data: Process map data from generate_process_map()
            
        Returns:
            Path to saved file
        """
        output_dir = self.projects_root / project_id / "deliverables" / "1-standardization"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "process_map.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(process_map_data, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Test the process map generator."""
    gen = ProcessMapGenerator()
    result = gen.generate_process_map("test-project")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success":
        saved_path = gen.save_process_map("test-project", result)
        print(f"\n✓ Process map saved to: {saved_path}")


if __name__ == "__main__":
    main()
