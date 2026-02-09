"""
Exception Register Generator — Stage 4 Standardization Deliverable

Extracts and documents known exceptions, how they're handled, and frequency
from the knowledge base and produces an exception register.

Exception register structure:
  Exception: [Description of the exception]
  Trigger: [What causes it]
  Frequency: [How often it occurs]
  Handling: [How it's currently managed]
  Root Cause: [Why does it happen]
  Owner: [Who's responsible]

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ExceptionRegisterGenerator:
    """
    Generates exception register from knowledge base facts and exceptions.
    
    Expected structures in knowledge_base.json:
    - facts with categories:
      - exceptions: descriptions of known exceptions
      - exception_handling: how exceptions are managed
      - exception_frequency: how often they occur
    - exceptions: array of exception objects (if manually added)
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Exception Register Generator.
        
        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_exception_register(self, project_id: str) -> Dict[str, Any]:
        """
        Generate exception register from project knowledge base.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with exception register:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "exception_register": {
                    "total_exceptions": int,
                    "exceptions": [
                        {
                            "id": "EXC-001",
                            "description": str,
                            "trigger": str,
                            "frequency": str,
                            "handling": str,
                            "impact": str,
                            "owner": str,
                            "workaround": str
                        },
                        ...
                    ]
                },
                "completeness": {"overall": 0-100},
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
            exceptions_from_kb = knowledge_base.get("exceptions", [])

            # Extract exception information
            exception_descriptions = self._extract_by_category(facts, "exceptions")
            exception_handling = self._extract_by_category(facts, "exception_handling")
            exception_frequency = self._extract_by_category(facts, "exception_frequency")
            exception_triggers = self._extract_by_category(facts, "exception_trigger")
            exception_impacts = self._extract_by_category(facts, "exception_impact")

            # Build exception records
            exceptions = []
            all_exception_texts = exception_descriptions + exceptions_from_kb

            for i, exc_text in enumerate(all_exception_texts, 1):
                exc_data = {
                    "id": f"EXC-{i:03d}",
                    "description": exc_text if isinstance(exc_text, str) else exc_text.get("description", ""),
                    "trigger": exception_triggers[i-1] if i <= len(exception_triggers) else "Not documented",
                    "frequency": exception_frequency[i-1] if i <= len(exception_frequency) else "Unknown",
                    "handling": exception_handling[i-1] if i <= len(exception_handling) else "No documented handling",
                    "impact": exception_impacts[i-1] if i <= len(exception_impacts) else "Not quantified",
                    "owner": "To be assigned",
                    "workaround": ""
                }
                exceptions.append(exc_data)

            # Calculate completeness
            exception_count = len(exceptions)
            documented_count = sum(
                1 for e in exceptions 
                if e.get("handling") != "No documented handling"
            )
            completeness = (documented_count / exception_count * 100) if exception_count > 0 else 0

            # Identify missing fields
            missing = []
            if exception_count == 0:
                missing.append("exceptions")
            if not any(e.get("handling") != "No documented handling" for e in exceptions):
                missing.append("exception_handling")
            if not any(e.get("frequency") != "Unknown" for e in exceptions):
                missing.append("exception_frequency")

            return {
                "status": "success",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "exception_register": {
                    "total_exceptions": exception_count,
                    "documented_count": documented_count,
                    "exceptions": exceptions
                },
                "completeness": {
                    "overall": round(completeness),
                    "descriptions": 100 if exception_descriptions else 0,
                    "handling": 100 if exception_handling else 0,
                    "frequency": 100 if exception_frequency else 0
                },
                "missing_fields": missing,
                "exception_categories": {
                    "total": exception_count,
                    "with_handling": documented_count,
                    "without_handling": exception_count - documented_count
                }
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
        Extract all facts by category.
        
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

    def save_exception_register(self, project_id: str, register_data: Dict[str, Any]) -> Path:
        """
        Save exception register to project deliverables folder.
        
        Args:
            project_id: ID of the project
            register_data: Register data from generate_exception_register()
            
        Returns:
            Path to saved file
        """
        output_dir = self.projects_root / project_id / "deliverables" / "1-standardization"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "exception_register.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(register_data, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Test the exception register generator."""
    gen = ExceptionRegisterGenerator()
    result = gen.generate_exception_register("test-project")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success":
        saved_path = gen.save_exception_register("test-project", result)
        print(f"\n✓ Exception register saved to: {saved_path}")


if __name__ == "__main__":
    main()
