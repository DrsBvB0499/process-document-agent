"""
SIPOC Generator — Stage 4 Standardization Deliverable

Extracts SIPOC (Suppliers, Inputs, Process, Outputs, Customers) information
from the knowledge base and produces a structured SIPOC table.

SIPOC structure:
  Suppliers → (provide) → Inputs → (used in) → Process → (produces) → Outputs → (delivered to) → Customers

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class SIPOCGenerator:
    """
    Generates SIPOC table from knowledge base facts.
    
    Expected fact categories in knowledge_base.json:
    - suppliers: organizations or systems that provide inputs
    - inputs: data/materials/documents required to start the process
    - process_owner: person/team responsible for the process
    - process_name: name or description of the process
    - outputs: deliverables produced by the process
    - customers: recipients of the process outputs
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize SIPOC Generator.
        
        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_sipoc(self, project_id: str) -> Dict[str, Any]:
        """
        Generate SIPOC from project knowledge base.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with SIPOC structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "sipoc": {
                    "suppliers": [...],
                    "inputs": [...],
                    "process": {...},
                    "outputs": [...],
                    "customers": [...]
                },
                "completeness": {
                    "suppliers": 0-100,
                    "inputs": 0-100,
                    "process": 0-100,
                    "outputs": 0-100,
                    "customers": 0-100,
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
            sources = knowledge_base.get("sources", [])

            # Extract SIPOC components
            suppliers = self._extract_by_category(facts, "suppliers")
            inputs = self._extract_by_category(facts, "inputs")
            process = self._extract_process(facts)
            outputs = self._extract_by_category(facts, "outputs")
            customers = self._extract_by_category(facts, "customers")

            # Calculate completeness
            completeness = {
                "suppliers": 100 if suppliers else 0,
                "inputs": 100 if inputs else 0,
                "process": 100 if process else 0,
                "outputs": 100 if outputs else 0,
                "customers": 100 if customers else 0
            }
            completeness["overall"] = sum(completeness.values()) // 5

            # Identify missing fields
            missing = []
            if not suppliers:
                missing.append("suppliers")
            if not inputs:
                missing.append("inputs")
            if not process:
                missing.append("process_owner, process_name, process_description")
            if not outputs:
                missing.append("outputs")
            if not customers:
                missing.append("customers")

            return {
                "status": "success",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "sipoc": {
                    "suppliers": suppliers if suppliers else [],
                    "inputs": inputs if inputs else [],
                    "process": process if process else {},
                    "outputs": outputs if outputs else [],
                    "customers": customers if customers else []
                },
                "completeness": completeness,
                "missing_fields": missing,
                "sources_used": self._count_sources_by_type(sources),
                "facts_extracted": len(suppliers) + len(inputs) + len(outputs) + len(customers) + (1 if process else 0)
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

    def _extract_process(self, facts: List[Dict]) -> Dict[str, str]:
        """
        Extract process-level information.
        
        Args:
            facts: List of fact dictionaries
            
        Returns:
            Dict with process_owner, name, and description
        """
        process = {}

        # Extract by category
        for fact_obj in facts:
            if not isinstance(fact_obj, dict):
                continue

            category = fact_obj.get("category", "")
            fact = fact_obj.get("fact", "")

            if category == "process_owner":
                process["owner"] = fact
            elif category == "process_name":
                process["name"] = fact
            elif category == "process_description":
                process["description"] = fact

        return process if process else {}

    def _count_sources_by_type(self, sources: List[Dict]) -> Dict[str, int]:
        """
        Count sources by type.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Count of sources by system type
        """
        counts = {}
        for source in sources:
            if isinstance(source, dict):
                system = source.get("system", "Unknown")
                counts[system] = counts.get(system, 0) + 1
        return counts

    def save_sipoc(self, project_id: str, sipoc_data: Dict[str, Any]) -> Path:
        """
        Save SIPOC data to project deliverables folder.
        
        Args:
            project_id: ID of the project
            sipoc_data: SIPOC data from generate_sipoc()
            
        Returns:
            Path to saved file
        """
        output_dir = self.projects_root / project_id / "deliverables" / "1-standardization"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "sipoc.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sipoc_data, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Test the SIPOC generator."""
    gen = SIPOCGenerator()
    result = gen.generate_sipoc("test-project")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success":
        saved_path = gen.save_sipoc("test-project", result)
        print(f"\n✓ SIPOC saved to: {saved_path}")


if __name__ == "__main__":
    main()
