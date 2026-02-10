"""
Data Flow Diagram Generator — Stage 7 Digitization Deliverable

Generates data flow diagrams showing how data moves between systems, processes,
and external entities. Maps data inputs, outputs, transformations, and storage.

Data flow components:
- External entities (data sources/destinations)
- Processes (data transformations)
- Data stores (databases, files, etc.)
- Data flows (connections showing data movement)
- Data attributes and formats

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataFlowGenerator:
    """
    Generates data flow diagram from knowledge base facts.

    Expected fact categories in knowledge_base.json:
    - inputs: data entering the process
    - outputs: data leaving the process
    - process_steps: where data is transformed
    - systems: where data is stored/processed
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Data Flow Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_data_flow(self, project_id: str) -> Dict[str, Any]:
        """
        Generate Data Flow Diagram from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with data flow structure
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

            # Extract data flow components
            external_entities = self._extract_external_entities(facts)
            processes = self._extract_processes(facts)
            data_stores = self._extract_data_stores(facts)
            data_flows = self._extract_data_flows(facts)

            # Calculate completeness
            completeness = {
                "external_entities": 100 if external_entities else 0,
                "processes": 100 if processes else 0,
                "data_stores": 100 if data_stores else 0,
                "data_flows": 100 if data_flows else 0,
                "overall": sum([
                    100 if external_entities else 0,
                    100 if processes else 0,
                    100 if data_stores else 0,
                    100 if data_flows else 0
                ]) // 4
            }

            # Identify missing fields
            missing = []
            if not external_entities:
                missing.append("external_entities")
            if not processes:
                missing.append("processes")
            if not data_stores:
                missing.append("data_stores")

            # Save deliverable
            deliverable_data = {
                "external_entities": external_entities,
                "processes": processes,
                "data_stores": data_stores,
                "data_flows": data_flows,
                "summary": {
                    "total_entities": len(external_entities),
                    "total_processes": len(processes),
                    "total_data_stores": len(data_stores),
                    "total_flows": len(data_flows)
                }
            }

            self._save_deliverable(project_id, deliverable_data)

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "data_flow": deliverable_data,
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

    def _extract_external_entities(self, facts: List[Dict]) -> List[Dict]:
        """Extract external data sources and destinations."""
        entities = []

        # Extract from suppliers (data sources)
        suppliers = [f for f in facts if f.get("category") == "suppliers"]
        for supplier in suppliers:
            entities.append({
                "name": supplier.get("fact", ""),
                "type": "source",
                "data_provided": []
            })

        # Extract from customers (data destinations)
        customers = [f for f in facts if f.get("category") == "customers"]
        for customer in customers:
            entities.append({
                "name": customer.get("fact", ""),
                "type": "destination",
                "data_received": []
            })

        return entities

    def _extract_processes(self, facts: List[Dict]) -> List[Dict]:
        """Extract data transformation processes."""
        processes = []

        # Extract from process steps
        step_facts = [f for f in facts if f.get("category") == "process_steps"]
        for idx, fact in enumerate(step_facts):
            processes.append({
                "id": f"P{idx+1}",
                "name": fact.get("fact", "")[:50],
                "inputs": [],
                "outputs": [],
                "transformations": []
            })

        return processes

    def _extract_data_stores(self, facts: List[Dict]) -> List[Dict]:
        """Extract data storage locations."""
        stores = []

        # Extract from systems
        system_facts = [f for f in facts if f.get("category") == "systems"]
        for system in system_facts:
            system_name = system.get("fact", "")
            if any(term in system_name.lower() for term in ["database", "sharepoint", "storage", "sap", "crm"]):
                stores.append({
                    "name": system_name,
                    "type": self._classify_store_type(system_name),
                    "data_stored": []
                })

        return stores

    def _classify_store_type(self, name: str) -> str:
        """Classify data store type."""
        name_lower = name.lower()

        if "database" in name_lower or "sql" in name_lower:
            return "database"
        elif "sharepoint" in name_lower or "onedrive" in name_lower:
            return "document_repository"
        elif "sap" in name_lower or "erp" in name_lower:
            return "transactional_system"
        else:
            return "other"

    def _extract_data_flows(self, facts: List[Dict]) -> List[Dict]:
        """Extract data flows between components."""
        flows = []

        # Extract from inputs
        input_facts = [f for f in facts if f.get("category") == "inputs"]
        for inp in input_facts:
            flows.append({
                "from": "External",
                "to": "Process",
                "data": inp.get("fact", ""),
                "format": "unknown"
            })

        # Extract from outputs
        output_facts = [f for f in facts if f.get("category") == "outputs"]
        for out in output_facts:
            flows.append({
                "from": "Process",
                "to": "External",
                "data": out.get("fact", ""),
                "format": "unknown"
            })

        return flows

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """Save data flow diagram to project deliverables folder."""
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "3-digitization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "data_flow_diagram.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    dfg = DataFlowGenerator()
    result = dfg.generate_data_flow("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Total Flows: {result.get('data_flow', {}).get('summary', {}).get('total_flows', 0)}")
    print(f"\nMissing fields: {result.get('missing_fields', [])}")
