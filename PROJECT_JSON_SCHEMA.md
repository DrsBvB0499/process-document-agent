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
"team": {
  "process_owner": {
    "name": "string",
    "email": "string"
  },
  "business_analyst": {
    "name": "string",
    "email": "string"
  },
  "sme": {
    "name": "string",
    "email": "string"
  },
  "developer": {
    "name": "string",
    "email": "string"
  }
}
```

The team object contains the core roles involved in the project. Use "TBD" as the name for roles not yet assigned.

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
    "file": "knowledge/uploaded/current_sop.pdf",
    "type": "sop",
    "processed": false,
    "added_by": "user@example.com",
    "date_added": "2026-02-09T11:00:00Z"
  }
]
```

The source `type` field can be: `sop`, `notes`, `transcript`, `policy`, `data`, or other custom types.
The `processed` flag indicates whether this file has been analyzed by the Knowledge Processor agent.

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
    "digitization": {
      "status": "locked",
      "description": "Ensure systems, data, and access are ready for automation",
      "gate_criteria": {
        "required_deliverables": ["system_integration_map", "data_model", "access_security_plan"],
        "minimum_completeness": 80,
        "sign_off_required": true
      },
      "deliverables": {
        "system_integration_map": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/3_digitization/system_integration_map.json",
          "gaps": []
        },
        "data_model": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/3_digitization/data_model.json",
          "gaps": []
        },
        "access_security_plan": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/3_digitization/access_security_plan.json",
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
        "sign_off_required": true
      },
      "deliverables": {
        "automation_spec": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/4_automation/automation_spec.json",
          "gaps": []
        },
        "test_plan": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/4_automation/test_plan.json",
          "gaps": []
        },
        "runbook": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/4_automation/runbook.json",
          "gaps": []
        },
        "deployment_checklist": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/4_automation/deployment_checklist.json",
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
        "sign_off_required": true
      },
      "deliverables": {
        "decision_rules": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/5_autonomization/decision_rules.json",
          "gaps": []
        },
        "monitoring_dashboard_spec": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/5_autonomization/monitoring_dashboard_spec.json",
          "gaps": []
        },
        "learning_loop_design": {
          "status": "not_started",
          "completeness": 0,
          "last_updated": null,
          "file": "deliverables/5_autonomization/learning_loop_design.json",
          "gaps": []
        }
      }
    }
  },
  "team": {
    "process_owner": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "business_analyst": {
      "name": "TBD",
      "email": ""
    },
    "sme": {
      "name": "TBD",
      "email": ""
    },
    "developer": {
      "name": "TBD",
      "email": ""
    }
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
      "file": "knowledge/uploaded/vendor_policy.pdf",
      "type": "sop",
      "processed": false,
      "added_by": "john@example.com",
      "date_added": "2026-02-09T11:00:00Z"
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
    file_path='knowledge/uploaded/policy.pdf',
    source_type='sop',
    added_by='user@example.com'
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
