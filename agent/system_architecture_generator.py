"""
System Architecture Generator — Stage 7 Digitization Deliverable

Generates system architecture diagram showing all systems, their relationships,
integration points, and data flows. Identifies digital transformation opportunities.

Architecture components:
- Systems inventory (existing and proposed)
- System relationships and dependencies
- Integration patterns (API, file transfer, database, etc.)
- Technology stack
- Cloud vs. on-premise classification
- Security and compliance considerations

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class SystemArchitectureGenerator:
    """
    Generates system architecture from knowledge base facts.

    Expected fact categories in knowledge_base.json:
    - systems: software/tools/platforms used
    - integrations: connections between systems
    - data_sources: where data comes from
    - technology: tech stack details
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize System Architecture Generator.

        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_system_architecture(self, project_id: str) -> Dict[str, Any]:
        """
        Generate System Architecture from project knowledge base.

        Args:
            project_id: ID of the project to analyze

        Returns:
            Dict with system architecture structure:
            {
                "status": "success|partial|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "architecture": {
                    "systems": [
                        {
                            "name": str,
                            "type": "core|supporting|external",
                            "category": "ERP|CRM|Automation|etc.",
                            "deployment": "cloud|on-premise|hybrid",
                            "integrations": [str],
                            "data_produced": [str],
                            "data_consumed": [str]
                        }
                    ],
                    "integrations": [
                        {
                            "from_system": str,
                            "to_system": str,
                            "type": "API|File|Database|Manual",
                            "frequency": "real-time|batch|on-demand",
                            "data_exchanged": str
                        }
                    ],
                    "layers": {
                        "presentation": [...],
                        "application": [...],
                        "data": [...],
                        "infrastructure": [...]
                    },
                    "digital_opportunities": [...]
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
            sources = knowledge_base.get("sources", [])

            # Extract architecture components
            systems = self._extract_systems(facts, sources)
            integrations = self._extract_integrations(facts, systems)
            layers = self._classify_layers(systems)
            digital_opportunities = self._identify_digital_opportunities(facts, systems)

            # Calculate completeness
            completeness = {
                "systems_identified": 100 if systems else 0,
                "integrations_mapped": 100 if integrations else 0,
                "architecture_layered": 100 if any(layers.values()) else 0,
                "overall": sum([
                    100 if systems else 0,
                    100 if integrations else 0,
                    100 if any(layers.values()) else 0
                ]) // 3
            }

            # Identify missing fields
            missing = []
            if not systems:
                missing.append("systems")
            if not integrations:
                missing.append("integrations")

            # Save deliverable
            deliverable_data = {
                "systems": systems,
                "integrations": integrations,
                "layers": layers,
                "digital_opportunities": digital_opportunities,
                "summary": {
                    "total_systems": len(systems),
                    "total_integrations": len(integrations),
                    "digital_readiness": self._calculate_digital_readiness(systems)
                }
            }

            self._save_deliverable(project_id, deliverable_data)

            return {
                "status": "success" if not missing else "partial",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "architecture": deliverable_data,
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

    def _extract_systems(self, facts: List[Dict], sources: List[Dict]) -> List[Dict]:
        """
        Extract systems from facts and sources.
        """
        systems = {}  # Use dict to deduplicate

        # Extract from facts
        system_facts = [f for f in facts if f.get("category") == "systems"]
        for fact in system_facts:
            system_name = fact.get("fact", "").strip()
            if system_name and system_name not in systems:
                systems[system_name] = {
                    "name": system_name,
                    "type": self._classify_system_type(system_name),
                    "category": self._classify_system_category(system_name),
                    "deployment": self._classify_deployment(system_name),
                    "integrations": [],
                    "data_produced": [],
                    "data_consumed": []
                }

        # Extract from sources
        for source in sources:
            system_name = source.get("system", "").strip()
            if system_name and system_name not in systems:
                systems[system_name] = {
                    "name": system_name,
                    "type": self._classify_system_type(system_name),
                    "category": self._classify_system_category(system_name),
                    "deployment": self._classify_deployment(system_name),
                    "integrations": [],
                    "data_produced": [],
                    "data_consumed": [],
                    "description": source.get("description", "")
                }

        return list(systems.values())

    def _classify_system_type(self, system_name: str) -> str:
        """
        Classify system as core, supporting, or external.
        """
        system_lower = system_name.lower()

        # Core systems (ERP, CRM, etc.)
        if any(term in system_lower for term in ["sap", "oracle", "erp", "crm", "salesforce"]):
            return "core"

        # External systems
        if any(term in system_lower for term in ["api", "external", "third-party", "vendor"]):
            return "external"

        # Supporting systems (default)
        return "supporting"

    def _classify_system_category(self, system_name: str) -> str:
        """
        Classify system category (ERP, CRM, Automation, etc.).
        """
        system_lower = system_name.lower()

        if "sap" in system_lower or "erp" in system_lower:
            return "ERP"
        elif "crm" in system_lower or "salesforce" in system_lower:
            return "CRM"
        elif "rpa" in system_lower or "automate" in system_lower or "power automate" in system_lower:
            return "Automation"
        elif "sharepoint" in system_lower or "onedrive" in system_lower:
            return "Collaboration"
        elif "database" in system_lower or "sql" in system_lower:
            return "Database"
        elif "excel" in system_lower or "word" in system_lower:
            return "Desktop Application"
        elif "outlook" in system_lower or "email" in system_lower:
            return "Communication"
        else:
            return "Other"

    def _classify_deployment(self, system_name: str) -> str:
        """
        Classify deployment model (cloud, on-premise, hybrid).
        """
        system_lower = system_name.lower()

        # Cloud indicators
        if any(term in system_lower for term in ["cloud", "365", "online", "saas"]):
            return "cloud"

        # On-premise indicators
        if any(term in system_lower for term in ["on-premise", "on-prem", "local", "server"]):
            return "on-premise"

        # Default to unknown
        return "unknown"

    def _extract_integrations(self, facts: List[Dict], systems: List[Dict]) -> List[Dict]:
        """
        Extract integrations between systems from process steps.
        """
        integrations = []
        system_names = [s["name"] for s in systems]

        # Look for process steps that mention multiple systems
        step_facts = [f for f in facts if f.get("category") == "process_steps"]

        for fact in step_facts:
            fact_text = fact.get("fact", "")

            # Try to identify "System A to System B" patterns
            mentioned_systems = [s for s in system_names if s.lower() in fact_text.lower()]

            if len(mentioned_systems) >= 2:
                # Assume data flows from first to second
                integrations.append({
                    "from_system": mentioned_systems[0],
                    "to_system": mentioned_systems[1],
                    "type": self._classify_integration_type(fact_text),
                    "frequency": self._classify_frequency(fact_text),
                    "data_exchanged": fact_text[:100]  # Truncate for brevity
                })

        return integrations

    def _classify_integration_type(self, text: str) -> str:
        """
        Classify integration type based on text.
        """
        text_lower = text.lower()

        if "api" in text_lower or "rest" in text_lower or "web service" in text_lower:
            return "API"
        elif "file" in text_lower or "upload" in text_lower or "download" in text_lower:
            return "File"
        elif "database" in text_lower or "sql" in text_lower or "query" in text_lower:
            return "Database"
        elif "manual" in text_lower or "copy" in text_lower or "enter" in text_lower:
            return "Manual"
        else:
            return "Unknown"

    def _classify_frequency(self, text: str) -> str:
        """
        Classify integration frequency.
        """
        text_lower = text.lower()

        if "real-time" in text_lower or "immediate" in text_lower:
            return "real-time"
        elif "batch" in text_lower or "daily" in text_lower or "nightly" in text_lower:
            return "batch"
        else:
            return "on-demand"

    def _classify_layers(self, systems: List[Dict]) -> Dict[str, List[str]]:
        """
        Classify systems into architectural layers.
        """
        layers = {
            "presentation": [],
            "application": [],
            "data": [],
            "infrastructure": []
        }

        for system in systems:
            category = system.get("category", "Other")
            name = system.get("name")

            if category in ["Desktop Application", "Collaboration"]:
                layers["presentation"].append(name)
            elif category in ["Automation", "CRM", "ERP"]:
                layers["application"].append(name)
            elif category == "Database":
                layers["data"].append(name)
            else:
                layers["infrastructure"].append(name)

        return layers

    def _identify_digital_opportunities(
        self,
        facts: List[Dict],
        systems: List[Dict]
    ) -> List[str]:
        """
        Identify digital transformation opportunities.
        """
        opportunities = []

        # Check for manual integrations
        manual_count = sum(1 for s in systems if "manual" in s.get("name", "").lower())
        if manual_count > 0:
            opportunities.append(f"Automate {manual_count} manual system integration(s)")

        # Check for desktop applications
        desktop_systems = [s for s in systems if s.get("category") == "Desktop Application"]
        if desktop_systems:
            opportunities.append(f"Migrate {len(desktop_systems)} desktop application(s) to cloud-based alternatives")

        # Check for on-premise systems
        on_prem = [s for s in systems if s.get("deployment") == "on-premise"]
        if on_prem:
            opportunities.append(f"Consider cloud migration for {len(on_prem)} on-premise system(s)")

        # Check for manual data entry
        manual_steps = [f for f in facts if "manual" in f.get("fact", "").lower() and f.get("category") == "process_steps"]
        if manual_steps:
            opportunities.append(f"Digitize {len(manual_steps)} manual process step(s)")

        return opportunities

    def _calculate_digital_readiness(self, systems: List[Dict]) -> str:
        """
        Calculate overall digital readiness score.
        """
        if not systems:
            return "low"

        # Calculate cloud adoption
        cloud_systems = sum(1 for s in systems if s.get("deployment") == "cloud")
        cloud_ratio = cloud_systems / len(systems)

        # Calculate automation systems
        automation_systems = sum(1 for s in systems if s.get("category") == "Automation")

        if cloud_ratio > 0.7 and automation_systems > 0:
            return "high"
        elif cloud_ratio > 0.4 or automation_systems > 0:
            return "medium"
        else:
            return "low"

    def _save_deliverable(self, project_id: str, data: Dict[str, Any]) -> None:
        """
        Save system architecture to project deliverables folder.

        Args:
            project_id: Project ID
            data: System architecture data
        """
        deliverable_path = (
            self.projects_root / project_id / "deliverables" / "3-digitization"
        )
        deliverable_path.mkdir(parents=True, exist_ok=True)

        output_file = deliverable_path / "system_architecture.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Quick test
    sag = SystemArchitectureGenerator()
    result = sag.generate_system_architecture("sd-light-invoicing-2")

    print(f"Status: {result.get('status')}")
    print(f"Total Systems: {result.get('architecture', {}).get('summary', {}).get('total_systems', 0)}")
    print(f"Digital Readiness: {result.get('architecture', {}).get('summary', {}).get('digital_readiness', 'unknown')}")
    print(f"\nMissing fields: {result.get('missing_fields', [])}")
