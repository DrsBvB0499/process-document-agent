"""
Project Manager — Handles project lifecycle, state, and knowledge stores.

This module provides the core functionality for managing projects in the
Intelligent Automation Roadmap system. Each project has:

- project.json: Single source of truth for project state
- knowledge/: Files uploaded by humans, extracted knowledge, and analysis logs
- deliverables/: Generated outputs per phase
- gate_reviews/: Gate pass/fail records

Usage:
    from agent.project_manager import ProjectManager
    
    pm = ProjectManager()
    project = pm.create_project(
        name="SD Light Invoicing",
        description="Daily invoice booking process"
    )
    
    # Check project status
    status = pm.get_project_status(project.project_id)
    
    # Update deliverable progress
    pm.update_deliverable_status(
        project_id=project.project_id,
        phase="standardization",
        deliverable="sipoc",
        status="complete",
        completeness=100
    )
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import uuid


class ProjectConfig:
    """Configuration for project paths and defaults."""
    
    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize project configuration.
        
        Args:
            projects_root: Root directory for all projects. 
                          Defaults to ./projects/
        """
        if projects_root is None:
            projects_root = Path(__file__).parent.parent / "projects"
        
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(parents=True, exist_ok=True)


class Project:
    """Represents a single project with all metadata."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize from project.json data."""
        self.data = data
    
    @property
    def project_id(self) -> str:
        return self.data.get("project_id", "")
    
    @property
    def project_name(self) -> str:
        return self.data.get("project_name", "")
    
    @property
    def current_phase(self) -> str:
        return self.data.get("current_phase", "standardization")
    
    @property
    def phases(self) -> Dict:
        return self.data.get("phases", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.data


class ProjectManager:
    """Manages project lifecycle, state, and file structure."""
    
    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize the ProjectManager.
        
        Args:
            projects_root: Root directory for projects. 
                          Defaults to ./projects/
        """
        self.config = ProjectConfig(projects_root)
    
    def create_project(
        self,
        name: str,
        description: str = "",
        process_owner: Optional[str] = None,
        process_owner_email: Optional[str] = None
    ) -> Project:
        """Create a new project with full folder structure.
        
        Args:
            name: Human-readable project name (e.g., "SD Light Invoicing")
            description: Project description
            process_owner: Name of the process owner
            process_owner_email: Email of the process owner
        
        Returns:
            Project object with initialized state
        
        Raises:
            ValueError: If project name is empty
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        
        # Generate project ID from name (slugified)
        project_id = self._slugify(name)
        project_path = self.config.projects_root / project_id
        
        # Check if project already exists
        if project_path.exists():
            raise ValueError(f"Project '{project_id}' already exists")
        
        # Create folder structure
        self._create_project_structure(project_path)
        
        # Create initial project.json
        project_data = self._create_empty_project(
            project_id=project_id,
            project_name=name,
            description=description,
            process_owner=process_owner,
            process_owner_email=process_owner_email
        )
        
        # Save project.json
        project_file = project_path / "project.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to save project.json: {e}")

        return Project(project_data)
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Load an existing project.
        
        Args:
            project_id: The project ID to load
        
        Returns:
            Project object, or None if not found
        """
        project_path = self.config.projects_root / project_id
        project_file = project_path / "project.json"
        
        if not project_file.exists():
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Project(data)
        except (json.JSONDecodeError, IOError):
            return None
    
    def list_projects(self) -> List[Project]:
        """List all projects.
        
        Returns:
            List of Project objects sorted by creation date (newest first)
        """
        projects = []
        
        if not self.config.projects_root.exists():
            return projects
        
        for project_dir in self.config.projects_root.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_file = project_dir / "project.json"
            if not project_file.exists():
                continue
            
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                projects.append(Project(data))
            except (json.JSONDecodeError, IOError):
                # Skip invalid projects
                continue
        
        # Sort by created date (newest first)
        projects.sort(
            key=lambda p: p.data.get("created", ""),
            reverse=True
        )
        
        return projects
    
    def update_deliverable_status(
        self,
        project_id: str,
        phase: str,
        deliverable: str,
        status: str = None,
        completeness: int = None,
        gaps: List[str] = None
    ) -> bool:
        """Update the status of a deliverable.
        
        Args:
            project_id: Project ID
            phase: Phase name (e.g., "standardization")
            deliverable: Deliverable name (e.g., "sipoc")
            status: Status ("not_started","in_progress", "complete")
            completeness: Percentage complete (0-100)
            gaps: List of identified gaps
        
        Returns:
            True if successful, False otherwise
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        if phase not in project.data.get("phases", {}):
            return False
        
        if deliverable not in project.data["phases"][phase].get("deliverables", {}):
            return False
        
        deliverable_data = project.data["phases"][phase]["deliverables"][deliverable]
        
        if status:
            deliverable_data["status"] = status
        if completeness is not None:
            deliverable_data["completeness"] = max(0, min(100, completeness))
        if gaps is not None:
            deliverable_data["gaps"] = gaps
        
        deliverable_data["last_updated"] = datetime.now().isoformat()
        
        # Save updated project.json
        project_path = self.config.projects_root / project_id
        project_file = project_path / "project.json"
        
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def add_knowledge_source(
        self,
        project_id: str,
        file_path: str,
        source_type: str,
        added_by: str = "User"
    ) -> bool:
        """Record that a knowledge file was added.
        
        Args:
            project_id: Project ID
            file_path: Relative path to file in knowledge/uploaded/
            source_type: Type of source (sop, notes, transcript, etc.)
            added_by: Name of person who added it
        
        Returns:
            True if successful
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        knowledge_source = {
            "file": file_path,
            "type": source_type,
            "processed": False,
            "added_by": added_by,
            "date_added": datetime.now().isoformat()
        }
        
        if "knowledge_sources" not in project.data:
            project.data["knowledge_sources"] = []
        
        project.data["knowledge_sources"].append(knowledge_source)
        
        # Save
        project_path = self.config.projects_root / project_id
        project_file = project_path / "project.json"
        
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def get_knowledge_folder(self, project_id: str) -> Optional[Path]:
        """Get the path to a project's knowledge folder.
        
        Args:
            project_id: Project ID
        
        Returns:
            Path object, or None if project doesn't exist
        """
        project_path = self.config.projects_root / project_id
        if not project_path.exists():
            return None
        
        knowledge_path = project_path / "knowledge"
        knowledge_path.mkdir(exist_ok=True)
        
        return knowledge_path
    
    def get_deliverables_folder(self, project_id: str) -> Optional[Path]:
        """Get the path to a project's deliverables folder.
        
        Args:
            project_id: Project ID
        
        Returns:
            Path object, or None if project doesn't exist
        """
        project_path = self.config.projects_root / project_id
        if not project_path.exists():
            return None
        
        deliverables_path = project_path / "deliverables"
        deliverables_path.mkdir(exist_ok=True)
        
        return deliverables_path
    
    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of project status.
        
        Args:
            project_id: Project ID
        
        Returns:
            Dictionary with phase/deliverable status, or None if not found
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        status = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "current_phase": project.current_phase,
            "phases": {}
        }
        
        for phase_name, phase_data in project.phases.items():
            phase_status = {
                "status": phase_data.get("status", "locked"),
                "deliverables": {}
            }
            
            for deliv_name, deliv_data in phase_data.get("deliverables", {}).items():
                phase_status["deliverables"][deliv_name] = {
                    "status": deliv_data.get("status", "not_started"),
                    "completeness": deliv_data.get("completeness", 0)
                }
            
            status["phases"][phase_name] = phase_status
        
        return status
    
    # ────────────────────────────────────────────────────────────
    # Private helper methods
    # ────────────────────────────────────────────────────────────
    
    def _create_project_structure(self, project_path: Path) -> None:
        """Create the complete folder structure for a project.
        
        Args:
            project_path: Root path for the project
        """
        # Create main directories
        (project_path / "knowledge").mkdir(parents=True, exist_ok=True)
        (project_path / "knowledge" / "uploaded").mkdir(parents=True, exist_ok=True)
        (project_path / "knowledge" / "sessions").mkdir(parents=True, exist_ok=True)
        (project_path / "knowledge" / "extracted").mkdir(parents=True, exist_ok=True)
        
        (project_path / "deliverables").mkdir(parents=True, exist_ok=True)
        for i in range(1, 6):
            phase_num = i
            phase_names = {
                1: "standardization",
                2: "optimization",
                3: "digitization",
                4: "automation",
                5: "autonomization"
            }
            (project_path / "deliverables" / f"{phase_num}_{phase_names[i]}").mkdir(
                parents=True, exist_ok=True
            )
        
        (project_path / "gate_reviews").mkdir(parents=True, exist_ok=True)
    
    def _create_empty_project(
        self,
        project_id: str,
        project_name: str,
        description: str = "",
        process_owner: Optional[str] = None,
        process_owner_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an initial project.json structure.
        
        Args:
            project_id: Unique project identifier
            project_name: Human-readable project name
            description: Project description
            process_owner: Name of process owner
            process_owner_email: Email of process owner
        
        Returns:
            Dictionary ready to be serialized to JSON
        """
        return {
            "project_id": project_id,
            "project_name": project_name,
            "description": description,
            "created": datetime.now().isoformat(),
            "current_phase": "standardization",
            "phases": {
                "standardization": {
                    "status": "locked",
                    "description": "Document the AS-IS process",
                    "gate_criteria": {
                        "required_deliverables": ["sipoc", "process_map", "baseline_metrics", "exception_register", "flowchart"],
                        "minimum_completeness": 80,
                        "sign_off_required": False
                    },
                    "deliverables": {
                        "sipoc": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/1-standardization/sipoc.json",
                            "gaps": []
                        },
                        "process_map": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/1-standardization/process_map.json",
                            "gaps": []
                        },
                        "baseline_metrics": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/1-standardization/baseline_metrics.json",
                            "gaps": []
                        },
                        "exception_register": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/1-standardization/exceptions.json",
                            "gaps": []
                        },
                        "flowchart": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/1-standardization/flowchart.mmd",
                            "gaps": []
                        }
                    }
                },
                "optimization": {
                    "status": "locked",
                    "description": "Design the TO-BE process and improvements",
                    "gate_criteria": {
                        "required_deliverables": ["waste_analysis", "to_be_process", "improvement_register"],
                        "minimum_completeness": 80,
                        "sign_off_required": False
                    },
                    "deliverables": {
                        "waste_analysis": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/2-optimization/waste_analysis.json",
                            "gaps": []
                        },
                        "to_be_process": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/2-optimization/to_be_process.json",
                            "gaps": []
                        },
                        "improvement_register": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/2-optimization/improvement_register.json",
                            "gaps": []
                        }
                    }
                },
                "digitization": {
                    "status": "locked",
                    "description": "Ensure systems, data, and access are ready for automation",
                    "gate_criteria": {
                        "required_deliverables": ["system_integration_map", "data_model", "access_security_plan"],
                        "minimum_completeness": 80,
                        "sign_off_required": True
                    },
                    "deliverables": {
                        "system_integration_map": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/3-digitization/system_integration_map.json",
                            "gaps": []
                        },
                        "data_model": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/3-digitization/data_model.json",
                            "gaps": []
                        },
                        "access_security_plan": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/3-digitization/access_security_plan.json",
                            "gaps": []
                        }
                    }
                },
                "automation": {
                    "status": "locked",
                    "description": "Build, test, and deploy the automated solution",
                    "gate_criteria": {
                        "required_deliverables": ["automation_spec", "test_plan", "runbook", "deployment_checklist"],
                        "minimum_completeness": 80,
                        "sign_off_required": True
                    },
                    "deliverables": {
                        "automation_spec": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/4-automation/automation_spec.json",
                            "gaps": []
                        },
                        "test_plan": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/4-automation/test_plan.json",
                            "gaps": []
                        },
                        "runbook": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/4-automation/runbook.json",
                            "gaps": []
                        },
                        "deployment_checklist": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/4-automation/deployment_checklist.json",
                            "gaps": []
                        }
                    }
                },
                "autonomization": {
                    "status": "locked",
                    "description": "Establish rules for autonomous operation with human oversight",
                    "gate_criteria": {
                        "required_deliverables": ["decision_rules", "monitoring_dashboard_spec", "learning_loop_design"],
                        "minimum_completeness": 90,
                        "sign_off_required": True
                    },
                    "deliverables": {
                        "decision_rules": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/5-autonomization/decision_rules.json",
                            "gaps": []
                        },
                        "monitoring_dashboard_spec": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/5-autonomization/monitoring_dashboard_spec.json",
                            "gaps": []
                        },
                        "learning_loop_design": {
                            "status": "not_started",
                            "completeness": 0,
                            "last_updated": None,
                            "file": "deliverables/5-autonomization/learning_loop_design.json",
                            "gaps": []
                        }
                    }
                }
            },
            "team": {
                "process_owner": {
                    "name": process_owner or "TBD",
                    "email": process_owner_email or ""
                },
                "business_analyst": {"name": "TBD", "email": ""},
                "sme": {"name": "TBD", "email": ""},
                "developer": {"name": "TBD", "email": ""}
            },
            "knowledge_sources": [],
            "gate_reviews": {}
        }
    
    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to a URL-safe slug.
        
        Examples:
            "SD Light Invoicing" → "sd-light-invoicing"
            "Customer Onboarding" → "customer-onboarding"
        """
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        text = text.strip('-')
        return text


if __name__ == "__main__":
    # Example usage
    pm = ProjectManager()
    
    # Create a test project
    try:
        project = pm.create_project(
            name="Test Invoice Process",
            description="Testing the Stage 1 foundation"
        )
        print(f"✓ Created project: {project.project_name} ({project.project_id})")
        print(f"  Path: {pm.config.projects_root / project.project_id}")
        
        # List all projects
        projects = pm.list_projects()
        print(f"\n✓ Found {len(projects)} project(s)")
        for p in projects:
            print(f"  - {p.project_name}")
        
        # Get status
        status = pm.get_project_status(project.project_id)
        print(f"\n✓ Project status:")
        print(f"  Current phase: {status['current_phase']}")
        print(f"  Phase statuses: {list(status['phases'].keys())}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
