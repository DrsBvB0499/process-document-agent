# CLAUDE.md — Project Context for Claude Code

## Project Overview

This is the **Intelligent Automation Roadmap Agent System** — a multi-agent system that guides organizations through transforming messy manual processes into optimized, automated operations.

The system follows 5 phases: Standardization → Optimization → Digitization → Automation → Autonomization. Each phase has a gate checkpoint with specific deliverables.

See `system_architecture.md` for the full system design.

## Current State (ALL STAGES COMPLETE ✅)

### Stage 1: Foundation (✅ Complete)
- **Project Manager** (`agent/project_manager.py`) — Creates project folder structure, manages `project.json` state, handles project CRUD operations
- **CLI Interface** (`cli.py`) — `python cli.py create|list|status|inspect` commands for project management
- **Project Schema** (`PROJECT_JSON_SCHEMA.md`) — Documents `project.json` structure with 5 phases, deliverables, team roster, gate criteria
- **Input Validators** (`agent/validators.py`) — Security validation for project IDs, user roles, file paths to prevent injection attacks

### Stage 2: Knowledge Processing (✅ Complete)
- **Knowledge Processor** (`agent/knowledge_processor.py`) — Reads uploaded files (PDF, DOCX, TXT, CSV, JSON, images), extracts structured info via LLM, creates `knowledge_base.json` and `analysis_log.json`
- **LLM Router** (`agent/llm.py`) — Runtime model selection via MODEL_MAP, automatic escalation on low confidence, cost logging with actual pricing calculations to `cost_log.json`

### Stage 3: Intelligent Conversation (✅ Complete)
- **Gap Analyzer** (`agent/gap_analyzer.py`) — Compares knowledge base vs. deliverable requirements, identifies missing fields, generates role-aware recommendations
- **Conversation Agent** (`agent/conversation_agent.py`) — Interface-agnostic message handler, role-aware question generation, session logging to `knowledge/sessions/`

### Stage 4: Full Standardization Phase (✅ Complete)
- **SIPOC Generator** (`agent/sipoc_generator.py`) — Extracts Suppliers, Inputs, Process, Outputs, Customers from knowledge base
- **Process Map Generator** (`agent/process_map_generator.py`) — Builds step-by-step process map with performers, systems, decisions
- **Baseline Metrics Generator** (`agent/baseline_metrics_generator.py`) — Aggregates volume, time, cost, quality, SLA metrics
- **Flowchart Generator** (`agent/flowchart_generator.py`) — Generates Mermaid flowcharts from process map
- **Exception Register Generator** (`agent/exception_register_generator.py`) — Compiles known exceptions and handling procedures
- **Standardization Orchestrator** (`agent/standardization_deliverables.py`) — Coordinates all 5 deliverable generators and produces complete standardization package

### Stage 5: Gate Review System (✅ Complete)
- **Gate Review Agent** (`agent/gate_review_agent.py`) — Evaluates deliverable completeness with weighted scoring system, checks required fields, enforces minimum thresholds, generates PASS/CONDITIONAL_PASS/FAIL decisions with actionable feedback
- **Web API Integration** (`web/server.py`) — REST endpoint `/api/projects/<project_id>/gate-review` for submitting gate reviews, logs successful reviews to `gate_reviews/` folder
- **Dashboard UI** (`web/templates/project.html`) — "Submit for Gate Review" action card with real-time evaluation results display showing score, decision, and specific issues to address

### Stage 6: Optimization Phase (✅ Complete)
- **Value Stream Mapping Generator** (`agent/value_stream_generator.py`) — Generates Value Stream Map showing process flow with cycle times, wait times, value-added vs. non-value-added classification, bottlenecks, and efficiency metrics (VA ratio, process efficiency)
- **Waste Analysis Generator** (`agent/waste_analysis_generator.py`) — Identifies 8 types of waste using Lean TIMWOODS methodology (Transport, Inventory, Motion, Waiting, Overproduction, Overprocessing, Defects, Skills), provides impact assessment and improvement recommendations
- **Quick Wins Identifier** (`agent/quick_wins_generator.py`) — Identifies low-effort, high-impact improvement opportunities, prioritizes based on effort-impact matrix, estimates savings and implementation time for each quick win
- **KPI Dashboard Generator** (`agent/kpi_dashboard_generator.py`) — Defines measurable improvement targets across time, cost, quality, and volume categories with baseline and target metrics, calculates SMART KPIs from baseline data
- **Optimization Orchestrator** (`agent/optimization_deliverables.py`) — Coordinates all 4 optimization generators and produces complete optimization package with improvement roadmap
- **Web UI Integration** — Added "Generate Optimization Deliverables" action card and REST endpoint `/api/projects/<project_id>/generate-optimization`

### Stage 7: Digitization Phase (✅ Complete)
- **System Architecture Generator** (`agent/system_architecture_generator.py`) — Maps system landscape with integrations, deployment models, and digital readiness assessment
- **Data Flow Diagram Generator** (`agent/data_flow_generator.py`) — Visualizes data movement between systems, processes, and external entities
- **Digitization Orchestrator** (`agent/digitization_deliverables.py`) — Coordinates digitization deliverable generation
- **Web API Integration** — Added REST endpoint `/api/projects/<project_id>/generate-digitization`

### Stage 8: Automation Phase (✅ Complete)
- **Automation Deliverables Orchestrator** (`agent/automation_deliverables.py`) — Identifies automation candidates, scores automation potential, generates phased implementation roadmap with expected benefits
- **Web API Integration** — Added REST endpoint `/api/projects/<project_id>/generate-automation`

### Stage 9: Autonomization Phase (✅ Complete)
- **Autonomization Deliverables Orchestrator** (`agent/autonomization_deliverables.py`) — Identifies AI/ML opportunities for decision automation and NLP, designs self-healing patterns for exception handling
- **Web API Integration** — Added REST endpoint `/api/projects/<project_id>/generate-autonomization`

### Testing (✅ Complete)
- **Integration Test Stage 1-3** (`test_integration_1_to_3.py`) — Tests project creation → knowledge processing → gap analysis → conversation logging
- **Integration Test Stage 1-4** (`test_integration_1_to_4.py`) — End-to-end test including all standardization deliverable generation

### What's Next
**ALL 9 STAGES COMPLETE!** The full Intelligent Automation Roadmap system is now implemented.

**Ready for end-to-end testing:** Complete workflow from project creation → knowledge processing → gap analysis → conversation → deliverable generation (all 5 phases) → gate review

**Optional Enhancements:**
- Teams Integration: Wire Conversation Agent to Azure Bot Service for Teams channel operation
- Visual diagram generation (Mermaid rendering)
- Advanced analytics dashboard
- Multi-user collaboration features

## Tech Stack

- **Language:** Python 3.12
- **AI Provider:** OpenAI (GPT-4o) via `openai` package
- **Environment:** `.env` file with `OPENAI_API_KEY` and `OPENAI_MODEL`
- **Document Generation:** `python-docx` for Word files
- **Flowcharts:** Mermaid.js rendered via `mmdc` (Mermaid CLI, requires Node.js)
- **Config:** `python-dotenv` for environment variables
- **OS:** Windows (development), should work cross-platform

## Project Structure

The system is organized into **projects**, each with persistent state:

```
projects/
├── {project_id}/
│   ├── project.json                          # Single source of truth for project state
│   ├── knowledge/
│   │   ├── uploaded/                         # Human uploads files here
│   │   ├── extracted/
│   │   │   ├── knowledge_base.json           # Consolidated facts, sources, exceptions
│   │   │   └── analysis_log.json             # Per-file processing audit trail
│   │   └── sessions/
│   │       └── session_YYYY-MM-DD.json       # Conversation transcripts
│   ├── deliverables/
│   │   ├── 1-standardization/                # Stage 1 deliverables
│   │   ├── 2-optimization/                   # Stage 2 deliverables
│   │   ├── 3-digitization/                   # Stage 3 deliverables
│   │   ├── 4-automation/                     # Stage 4 deliverables
│   │   └── 5-autonomization/                 # Stage 5 deliverables
│   └── gate_reviews/                         # Gate review logs
├── legacy-project/
│   └── ...
```

### Key Data Files
- **project.json** — complete project state: phases, deliverables, team, gate criteria, knowledge sources
- **knowledge_base.json** — consolidated view of all extracted facts with confidence, sources, exceptions, unknowns
- **cost_log.json** — audit trail of all API calls with token counts and costs
- **session_YYYY-MM-DD.json** — conversation transcripts for analysis and reference
```

## Coding Conventions

- **Python style:** Clean, well-documented code with docstrings. Type hints where helpful.
- **No hardcoded process names:** The system must be completely generic. Never reference specific processes like "Afkeurbewijzen" or "SD Light" in the codebase.
- **Environment variables:** All API keys and config via `.env` file using `python-dotenv`. Use `Path(__file__).parent.parent / ".env"` pattern to find the .env from any script location.
- **OpenAI API pattern:** Use `OpenAI` (sync) or `AsyncOpenAI` (async) client. System prompt as first message in the messages array. Low temperature (0.2) for structured extraction, default for conversation.
- **Model selection:** Never hardcode a model name in agent code. Use the MODEL_MAP pattern from system_architecture.md Section 7.1. Each agent gets the right model for its task (mini for extraction, 4o for conversation/judgment). Models are configurable via `.env` overrides. Every API call must be logged with token counts and cost.
- **File paths:** Use `pathlib.Path` for cross-platform compatibility. Use `os.makedirs(path, exist_ok=True)` before writing files.
- **Error handling:** Always handle missing API keys, missing files, and API errors gracefully with clear user-facing error messages.
- **Output files:** Generated documents go to `outputs/` (current) or `projects/<name>/deliverables/` (future).

## Key Design Decisions

1. **Knowledge-first:** The agent always reads all available project materials before asking humans questions. It never asks something whose answer is already in the knowledge folder.
2. **Incremental progress:** The agent picks up where it left off. It never restarts a deliverable from scratch.
3. **Project state in `project.json`:** Single source of truth for what's been done and what's needed.
4. **Phase-gated progression:** Each phase must pass a gate review before the next phase unlocks.
5. **Role-aware:** The agent adapts its questions based on who it's talking to (PO, BA, SME, DEV).
6. **Interface-agnostic core:** The agent core is a callable function `(message, user_id, project_id) → response`. No `input()` calls in core logic. CLI, web, and Teams are thin wrappers.
7. **Right model for the job:** Use cheap models (gpt-4o-mini) for extraction and structured tasks, premium models (gpt-4o) for conversation and judgment. Escalate automatically on low confidence. Log all costs.

## Quick Start

### Create a Project
```bash
python cli.py create "My Process Automation"
```
Creates a new project with full folder structure and `project.json`.

### Upload Knowledge Files
Copy files to `projects/{project_id}/knowledge/uploaded/`

### Process Knowledge
```python
from agent.knowledge_processor import KnowledgeProcessor
kp = KnowledgeProcessor()
result = kp.process_project("my-process-automation")
# Creates: knowledge_base.json, analysis_log.json
```

### Analyze Gaps
```python
from agent.gap_analyzer import GapAnalyzer
ga = GapAnalyzer()
gaps = ga.analyze_project("my-process-automation")
# Shows: missing fields per deliverable, completeness %, recommendations
```

### Have a Conversation
```python
from agent.conversation_agent import ConversationAgent
ca = ConversationAgent()
response = ca.handle_message(
    message="Tell me about the approval workflow",
    user_id="sarah@company.com",
    user_role="sme",
    project_id="my-process-automation"
)
# Logs turn to: projects/{project_id}/knowledge/sessions/session_YYYY-MM-DD.json
```

### Generate Stage 4 Deliverables
```python
from agent.standardization_deliverables import StandardizationDeliverablesOrchestrator
orchestrator = StandardizationDeliverablesOrchestrator()
results = orchestrator.generate_all_deliverables("my-process-automation")
# Generates: SIPOC, Process Map, Baseline Metrics, Flowchart, Exception Register
# Saved to: projects/{project_id}/deliverables/1-standardization/
```

### Submit Gate Review
```python
from agent.gate_review_agent import GateReviewAgent
gra = GateReviewAgent()
result = gra.evaluate_gate(project_id="my-process-automation", phase="standardization")
# Returns: {"decision": "PASS/CONDITIONAL_PASS/FAIL", "overall_score": 85, "issues": [...], "next_steps": "..."}
# On PASS: logs review to projects/{project_id}/gate_reviews/standardization_gate_review.json
```

### Generate Optimization Deliverables
```python
from agent.optimization_deliverables import OptimizationDeliverablesOrchestrator
orchestrator = OptimizationDeliverablesOrchestrator()
results = orchestrator.generate_all_deliverables("my-process-automation")
# Generates: Value Stream Map, Waste Analysis, Quick Wins, KPI Dashboard
# Saved to: projects/{project_id}/deliverables/2-optimization/
```

### Check Status
```bash
python cli.py status my-process-automation
```

### Run Integration Tests
```bash
# Test Stages 1-3
python test_integration_1_to_3.py

# Test complete workflow including Stage 4
python test_integration_1_to_4.py
```

## Important Notes

- The `.env` file contains API keys and is NOT committed to git.
- Each project maintains independent cost tracking in `cost_log.json` with actual API costs calculated based on token usage and current model pricing.
- Knowledge consolidation is incremental — files are never re-processed unless explicitly cleared.
- Session logging is automatic and date-based; multiple conversations on the same day are appended to the same session file.
- Model selection is centralized in `agent/llm.py` via `DEFAULT_MODEL_MAP`. Override specific models via `.env` if needed.
- The Conversation Agent is interface-agnostic; `handle_message()` is a pure function suitable for CLI, web, Teams, or Slack.
- Always read gap brief before generating response — this ensures agent only asks about missing information and maintains knowledge-first principle.
