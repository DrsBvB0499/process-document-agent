# Project JSON Schema Documentation

## Overview

Each project maintains a `project.json` file as its single source of truth for state, progress, and metadata. This file is automatically managed by the `ProjectManager` class and is updated as deliverables progress through their lifecycle.

## File Location

```
projects/{project_id}/project.json
```

Example: `projects/test-project/project.json`

## Schema Structure

### Root Level

```json
{
  "project_id": "string",           // URL-safe project identifier (auto-generated from project_name)
  "project_name": "string",         // Human-readable project name
  "description": "string",          // Optional project description
  "created": "ISO8601 timestamp",   // Project creation timestamp (e.g., "2026-02-09T10:24:52.054080")
  "current_phase": "string",        // Current active phase (standardization|optimization|digitization|automation|autonomization)
  "phases": { /* Phase objects */ },// 5 phases with deliverables and status
  "team_roster": { /* Team info */ },// Project team members
  "gate_reviews": { /* Reviews */ },// Gate approval records
  "knowledge_sources": [ /* ... */ ]// Uploaded knowledge files tracking
}
```

### Phases Object

Each of the 5 phases follows this structure:

```json
"standardization": {
  "status": "not_started|in_progress|complete|blocked",  // Phase overall status
  "description": "string",                                 // Phase purpose description
  "gate_criteria": {                                       // Gate requirements to advance
    "required_deliverables": ["list", "of", "deliverable_keys"],
    "minimum_completeness": 80,                            // Percentage (0-100)
    "sign_off_required": "bool"
  },
  "deliverables": { /* Deliverable objects */ }           // All deliverables in phase
}
```

#### Phase Values (by order):

1. **standardization** - Document the AS-IS process
   - Deliverables: SIPOC, Process Map, Baseline Metrics, Exception Register, Flowchart
   - Gate: All 5 deliverables >= 80% complete

2. **optimization** - Identify improvement opportunities
   - Deliverables: Waste Analysis, To Be Process, Improvement Register
   - Gate: All 3 deliverables >= 80% complete

3. **digitization** - Design digital solution
   - Deliverables: Solution Design, Digital Roadmap, Integration Plan
   - Gate: All 3 deliverables >= 80% complete + sign-off

4. **automation** - Build and deploy automation
   - Deliverables: Build & Test, Deployment Plan, Training Materials
   - Gate: All 3 deliverables >= 80% complete + sign-off

5. **autonomization** - Full autonomous operation
   - Deliverables: Autonomous Monitoring, Continuous Optimization, Feedback Loop
   - Gate: All 3 deliverables >= 90% complete + sign-off

### Deliverable Object

Each deliverable has this structure:

```json
"sipoc": {
  "status": "not_started|in_progress|complete|blocked|pending_review",  // Deliverable status
  "completeness": 0-100,              // Percentage complete (0-100)
  "last_updated": "ISO8601 timestamp" | null,  // When last modified
  "file": "deliverables/1_standardization/sipoc.json",  // File path to deliverable
  "gaps": ["string", "string"]        // Known gaps or issues (empty array if none)
}
```

#### Deliverable Status Values:

- **not_started** - Not yet begun
- **in_progress** - Currently being worked on
- **complete** - Finished and ready for review
- **blocked** - Unable to proceed (check `gaps` for reasons)
- **pending_review** - Waiting for gate review/approval

### Team Roster

```json
"team_roster": {
  "owner": {
    "name": "string",
    "email": "string",
    "role": "Project Owner"
  },
  "stakeholders": [
    {
      "name": "string",
      "email": "string",
      "role": "Business Analyst|SME|Developer|Tester"
    }
  ]
}
```

### Gate Reviews

```json
"gate_reviews": {
  "standardization_gate": {
    "status": "not_requested|pending|approved|rejected",
    "reviewed_date": "ISO8601 timestamp" | null,
    "reviewed_by": "email@example.com" | null,
    "comments": "string" | null,
    "deliverables_reviewed": ["sipoc", "process_map", ...]
  }
}
```

### Knowledge Sources Array

```json
"knowledge_sources": [
  {
    "source_id": "uuid string",
    "filename": "string",
    "file_type": "pdf|docx|xlsx|txt|json",
    "uploaded_date": "ISO8601 timestamp",
    "uploaded_by": "email@example.com",
    "extraction_status": "pending|in_progress|complete|failed",
    "extracted_folder": "knowledge/extracted/{source_id}/",
    "notes": "string"
  }
]
```

## Complete Example

```json
{
  "project_id": "vendor-onboarding",
  "project_name": "Vendor Onboarding Process",
  "description": "Standardize and automate vendor onboarding workflow",
  "created": "2026-02-09T10:24:52.054080",
  "current_phase": "standardization",
  "phases": {
    "standardization": {
      "status": "in_progress",
      "description": "Document the AS-IS process",
      "gate_criteria": {
        "required_deliverables": ["sipoc", "process_map", "baseline_metrics", "exception_register", "flowchart"],
        "minimum_completeness": 80,
        "sign_off_required": false
      },
      "deliverables": {
        "sipoc": {
          "status": "complete",
          "completeness": 100,
          "last_updated": "2026-02-09T14:30:00",
          "file": "deliverables/1_standardization/sipoc.json",
          "gaps": []
        },
        "process_map": {
          "status": "in_progress",
          "completeness": 65,
          "last_updated": "2026-02-09T16:45:00",
          "file": "deliverables/1_standardization/process_map.json",
          "gaps": ["Missing approval steps for >$50k purchases"]
        },
        "baseline_metrics": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/1_standardization/baseline_metrics.json",
          "gaps": []
        },
        "exception_register": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/1_standardization/exceptions.json",
          "gaps": []
        },
        "flowchart": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/1_standardization/flowchart.mmd",
          "gaps": []
        }
      }
    },
    "optimization": {
      "status": "locked",
      "description": "Identify improvement opportunities",
      "gate_criteria": {
        "required_deliverables": ["waste_analysis", "to_be_process", "improvement_register"],
        "minimum_completeness": 80,
        "sign_off_required": false
      },
      "deliverables": {
        "waste_analysis": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/2_optimization/waste_analysis.json",
          "gaps": []
        },
        "to_be_process": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/2_optimization/to_be_process.json",
          "gaps": []
        },
        "improvement_register": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/2_optimization/improvement_register.json",
          "gaps": []
        }
      }
    },
    "digitization": { "status": "locked", "description": "Design digital solution", "gate_criteria": {}, "deliverables": {} },
    "automation": { "status": "locked", "description": "Build and deploy automation", "gate_criteria": {}, "deliverables": {} },
    "autonomization": { "status": "locked", "description": "Full autonomous operation", "gate_criteria": {}, "deliverables": {} }
  },
  "team_roster": {
    "owner": {
      "name": "John Doe",
      "email": "john@example.com",
      "role": "Project Owner"
    },
    "stakeholders": []
  },
  "gate_reviews": {
    "standardization_gate": {
      "status": "not_requested",
      "reviewed_date": null,
      "reviewed_by": null,
      "comments": null,
      "deliverables_reviewed": []
    }
  },
  "knowledge_sources": [
    {
      "source_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "vendor_policy.pdf",
      "file_type": "pdf",
      "uploaded_date": "2026-02-09T11:00:00",
      "uploaded_by": "john@example.com",
      "extraction_status": "complete",
      "extracted_folder": "knowledge/extracted/550e8400-e29b-41d4-a716-446655440000/",
      "notes": "Current vendor onboarding policy document"
    }
  ]
}
```

## Working with project.json

### Reading Project State

The `ProjectManager` class provides convenient methods:

```python
from agent.project_manager import ProjectManager

pm = ProjectManager()
project = pm.get_project('test-project')

# Access attributes
current_phase = project.current_phase
sipoc_status = project.get_deliverable_status('standardization', 'sipoc')
```

### Updating Deliverable Status

```python
pm.update_deliverable_status(
    project_id='test-project',
    phase='standardization',
    deliverable='sipoc',
    status='complete',
    completeness=100,
    gaps=[]
)
```

### Adding Knowledge Source

```python
pm.add_knowledge_source(
    project_id='test-project',
    filename='policy.pdf',
    file_type='pdf',
    uploaded_by='user@example.com',
    notes='Company policy document'
)
```

### CLI Commands

View project.json contents:

```bash
python cli.py inspect test-project
```

Check project status:

```bash
python cli.py status test-project
```

## Notes

- **Timestamps** are always in ISO 8601 format (e.g., "2026-02-09T10:24:52.054080")
- **Status values** are always lowercase (not_started, in_progress, complete, etc.)
- **Completeness** is always an integer 0-100
- **File paths** are relative to the project root directory
- **project_id** is automatically slugified from project_name (spaces → hyphens, lowercase)
- Gates are locked until the previous phase reaches required completeness threshold
- All deliverable files should be created in their designated directories under deliverables/
