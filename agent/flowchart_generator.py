"""
Flowchart Generator — Stage 4 Standardization Deliverable

Converts structured process map data into a Mermaid flowchart diagram.
Produces both the Mermaid markup (.mmd) and can optionally render to PNG.

Author: Intelligent Automation Agent
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class FlowchartGenerator:
    """
    Generates Mermaid flowchart from process map data.
    
    Input: process_map.json with steps, decisions, performers, systems
    Output: flowchart.mmd (Mermaid markup) and optionally flowchart.png
    """

    def __init__(self, projects_root: str = "projects"):
        """
        Initialize Flowchart Generator.
        
        Args:
            projects_root: Root directory where projects are stored
        """
        self.projects_root = Path(projects_root)

    def generate_flowchart(self, project_id: str, process_map_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate Mermaid flowchart from process map.
        
        Args:
            project_id: ID of the project
            process_map_file: Optional path to process_map.json (auto-detects if not provided)
            
        Returns:
            Dict with flowchart data:
            {
                "status": "success|failed",
                "project_id": str,
                "timestamp": ISO8601,
                "flowchart": {
                    "mermaid_code": "graph TD\n  ...",
                    "node_count": int,
                    "connection_count": int
                }
            }
        """
        try:
            # Load process map
            if not process_map_file:
                process_map_file = (
                    self.projects_root / project_id / "deliverables" / "1-standardization" / "process_map.json"
                )

            if not process_map_file.exists():
                # Try loading from knowledge base as fallback
                kb_path = self.projects_root / project_id / "knowledge" / "extracted" / "knowledge_base.json"
                if kb_path.exists():
                    with open(kb_path, 'r', encoding='utf-8') as f:
                        kb = json.load(f)
                    process_map = {"process_map": {"steps": self._extract_steps(kb)}}
                else:
                    return {
                        "status": "failed",
                        "project_id": project_id,
                        "timestamp": datetime.now().isoformat(),
                        "error": f"Process map not found at {process_map_file}"
                    }
            else:
                with open(process_map_file, 'r', encoding='utf-8') as f:
                    process_map = json.load(f)

            # Generate Mermaid code
            mermaid_code = self._build_mermaid(process_map.get("process_map", {}))

            result = {
                "status": "success",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "flowchart": {
                    "mermaid_code": mermaid_code,
                    "node_count": mermaid_code.count("\n  "),
                    "connection_count": mermaid_code.count("-->")
                }
            }

            return result

        except Exception as e:
            return {
                "status": "failed",
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _extract_steps(self, knowledge_base: Dict) -> List[str]:
        """
        Extract process steps from knowledge base.
        
        Args:
            knowledge_base: Knowledge base dict
            
        Returns:
            List of process step facts
        """
        steps = []
        for fact_obj in knowledge_base.get("facts", []):
            if isinstance(fact_obj, dict) and fact_obj.get("category") == "process_steps":
                step = fact_obj.get("fact")
                if step and step not in steps:
                    steps.append(step)
        return steps

    def _build_mermaid(self, process_map: Dict) -> str:
        """
        Build Mermaid flowchart markup from process map.
        
        Args:
            process_map: Process map data with steps, decisions, performers
            
        Returns:
            Mermaid markdown code
        """
        # Start flowchart
        mermaid = "graph TD\n"

        steps = process_map.get("steps", [])
        decisions = process_map.get("decision_points", [])
        performers = process_map.get("performers", [])
        systems = process_map.get("systems", [])

        if not steps:
            # Empty flowchart
            mermaid += "  Start[Start] --> End[End]\n"
            return mermaid

        # Create node IDs (sanitized for Mermaid)
        node_map = {}
        for i, step in enumerate(steps):
            node_id = f"Step{i + 1}"
            sanitized_label = self._sanitize_label(step)
            node_map[step] = node_id
            mermaid += f"  {node_id}[{sanitized_label}]\n"

        # Add decision nodes
        for i, decision in enumerate(decisions):
            decision_id = f"Decision{i + 1}"
            sanitized_label = self._sanitize_label(decision)
            mermaid += f"  {decision_id}{{{{✓ {sanitized_label}?}}}}\n"

        # Add START and END nodes
        start_node = "Start"
        end_node = "End"
        mermaid += f"  {start_node}([Start])\n"
        mermaid += f"  {end_node}([End])\n"

        # Connect START to first step
        if steps:
            first_step = node_map[steps[0]]
            mermaid += f"  {start_node} --> {first_step}\n"

        # Connect steps in sequence
        for i in range(len(steps) - 1):
            current_node = node_map[steps[i]]
            next_node = node_map[steps[i + 1]]
            mermaid += f"  {current_node} --> {next_node}\n"

        # Connect last step to END
        if steps:
            last_node = node_map[steps[-1]]
            mermaid += f"  {last_node} --> {end_node}\n"

        # Add decision branches
        for i, decision in enumerate(decisions):
            decision_id = f"Decision{i + 1}"
            mermaid += f"  {decision_id} -->|✓ Yes| {node_map[steps[0]] if steps else end_node}\n"
            mermaid += f"  {decision_id} -->|✗ No| {end_node}\n"

        # Add style directives
        mermaid += "\n  style Start fill:#90EE90\n"
        mermaid += "  style End fill:#FFB6C6\n"
        mermaid += "  style Decision1 fill:#87CEEB\n"

        return mermaid

    def _sanitize_label(self, text: str) -> str:
        """
        Make text safe for Mermaid (remove special chars, limit length).
        
        Args:
            text: Original text
            
        Returns:
            Sanitized text safe for Mermaid
        """
        # Remove special characters
        sanitized = text.replace('"', "'").replace('<', '').replace('>', '')
        
        # Wrap in quotes if it contains spaces
        if ' ' in sanitized:
            sanitized = f'"{sanitized}"'
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:47] + "..."
        
        return sanitized

    def save_flowchart(self, project_id: str, flowchart_data: Dict[str, Any]) -> Path:
        """
        Save Mermaid flowchart to project deliverables folder.
        
        Args:
            project_id: ID of the project
            flowchart_data: Flowchart data from generate_flowchart()
            
        Returns:
            Path to saved .mmd file
        """
        output_dir = self.projects_root / project_id / "deliverables" / "1-standardization"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save Mermaid markdown
        mmd_file = output_dir / "flowchart.mmd"
        mermaid_code = flowchart_data.get("flowchart", {}).get("mermaid_code", "")
        with open(mmd_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)

        # Save metadata
        metadata_file = output_dir / "flowchart.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(flowchart_data, f, indent=2, ensure_ascii=False)

        return mmd_file


def main():
    """Test the flowchart generator."""
    gen = FlowchartGenerator()
    result = gen.generate_flowchart("test-project")
    print(json.dumps({k: v for k, v in result.items() if k != "flowchart"}, indent=2))
    
    if result.get("status") == "success":
        flowchart = result["flowchart"]["mermaid_code"]
        print("\n=== Generated Mermaid Code ===")
        print(flowchart)
        
        saved_path = gen.save_flowchart("test-project", result)
        print(f"\n✓ Flowchart saved to: {saved_path}")


if __name__ == "__main__":
    main()
