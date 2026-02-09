#!/usr/bin/env python3
"""
CLI for managing Intelligent Automation Roadmap projects.

This CLI provides commands to:
- Create new projects
- List and inspect projects
- Check project status
- Manage project files and knowledge

Usage:
    python cli.py create "Project Name"
    python cli.py list
    python cli.py status <project-id>
    python cli.py inspect <project-id>
    python cli.py --help
"""

import sys
import argparse
from pathlib import Path
from tabulate import tabulate

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent.project_manager import ProjectManager, Project


class ProjectCLI:
    """Command-line interface for project management."""
    
    def __init__(self):
        self.pm = ProjectManager()
    
    def create(self, args):
        """Create a new project.
        
        Args:
            args: Parsed arguments with name, description, owner, email
        """
        try:
            project = self.pm.create_project(
                name=args.name,
                description=args.description or "",
                process_owner=args.owner or None,
                process_owner_email=args.email or None
            )
            
            print(f"\n✓ Project created successfully!\n")
            print(f"  Name:         {project.project_name}")
            print(f"  ID:           {project.project_id}")
            print(f"  Current Phase: {project.current_phase}")
            print(f"  Status:        READY")
            
            project_path = self.pm.config.projects_root / project.project_id
            print(f"\n  Project folder: {project_path}")
            print(f"  ├── knowledge/")
            print(f"  │   ├── uploaded/    (drop files here)")
            print(f"  │   ├── sessions/    (conversation logs)")
            print(f"  │   └── extracted/   (processed knowledge)")
            print(f"  ├── deliverables/   (generated outputs)")
            print(f"  ├── gate_reviews/   (gate results)")
            print(f"  └── project.json    (project state)\n")
            
        except ValueError as e:
            print(f"\n✗ Error: {e}\n")
            sys.exit(1)
    
    def list(self, args):
        """List all projects."""
        projects = self.pm.list_projects()
        
        if not projects:
            print("\n  No projects found. Create one with:")
            print("  python cli.py create \"Project Name\"\n")
            return
        
        # Prepare table data
        headers = ["Project Name", "Project ID", "Phase", "Created"]
        rows = []
        
        for project in projects:
            created = project.data.get("created", "")[:10]  # Just the date
            rows.append([
                project.project_name,
                project.project_id,
                project.current_phase.replace("_", " ").title(),
                created
            ])
        
        print("\n")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(projects)} project(s)\n")
    
    def status(self, args):
        """Show project status."""
        project = self.pm.get_project(args.project_id)
        
        if not project:
            print(f"\n✗ Project '{args.project_id}' not found.\n")
            sys.exit(1)
        
        status = self.pm.get_project_status(args.project_id)
        
        print(f"\n{'─' * 70}")
        print(f"Project: {project.project_name}")
        print(f"ID:      {project.project_id}")
        print(f"Current Phase: {project.current_phase.replace('_', ' ').title()}")
        print(f"{'─' * 70}\n")
        
        # Show each phase and its deliverables
        for phase_name, phase_data in status["phases"].items():
            phase_title = phase_name.replace("_", " ").title()
            phase_status = phase_data["status"].upper()
            
            # Color-code status
            status_color = {
                "LOCKED": "🔒",
                "IN_PROGRESS": "🔄",
                "COMPLETE": "✓",
                "FAILED": "✗"
            }.get(phase_status, "?")
            
            print(f"{status_color} {phase_title} ({phase_status})")
            
            for deliv_name, deliv_data in phase_data["deliverables"].items():
                deliv_title = deliv_name.replace("_", " ").title()
                deliv_status = deliv_data["status"].replace("_", " ").title()
                completeness = deliv_data["completeness"]
                
                # Progress bar
                bar_length = 30
                filled = int(bar_length * completeness / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                print(f"  ├─ {deliv_title:<20} {deliv_status:<12} [{bar}] {completeness:>3}%")
            
            print()
        
        print(f"{'─' * 70}\n")
    
    def inspect(self, args):
        """Show detailed project information."""
        project = self.pm.get_project(args.project_id)
        
        if not project:
            print(f"\n✗ Project '{args.project_id}' not found.\n")
            sys.exit(1)
        
        import json
        
        print(f"\n{'─' * 70}")
        print(f"Project: {project.project_name}")
        print(f"File: {self.pm.config.projects_root / args.project_id / 'project.json'}")
        print(f"{'─' * 70}\n")
        
        # Pretty-print the project.json
        print(json.dumps(project.to_dict(), indent=2, ensure_ascii=False))
        print()
    
    def run(self):
        """Parse arguments and run the appropriate command."""
        parser = argparse.ArgumentParser(
            description="Intelligent Automation Roadmap Project Manager",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python cli.py create "SD Light Invoicing" -d "Daily invoice booking"
  python cli.py list
  python cli.py status sd-light-invoicing
  python cli.py inspect sd-light-invoicing
            """
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # Create command
        create_parser = subparsers.add_parser("create", help="Create a new project")
        create_parser.add_argument("name", help="Project name")
        create_parser.add_argument("-d", "--description", help="Project description")
        create_parser.add_argument("-o", "--owner", help="Process owner name")
        create_parser.add_argument("-e", "--email", help="Process owner email")
        create_parser.set_defaults(func=self.create)
        
        # List command
        list_parser = subparsers.add_parser("list", help="List all projects")
        list_parser.set_defaults(func=self.list)
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Show project status")
        status_parser.add_argument("project_id", help="Project ID")
        status_parser.set_defaults(func=self.status)
        
        # Inspect command
        inspect_parser = subparsers.add_parser("inspect", help="Show detailed project info")
        inspect_parser.add_argument("project_id", help="Project ID")
        inspect_parser.set_defaults(func=self.inspect)
        
        # Parse arguments
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            sys.exit(0)
        
        # Run the command
        args.func(args)


def main():
    """Entry point for the CLI."""
    cli = ProjectCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
