# CLAUDE.md — Project Context for Claude Code

## Project Overview

This is the **Intelligent Automation Roadmap Agent System** — a multi-agent system that guides organizations through transforming messy manual processes into optimized, automated operations.

The system follows 5 phases: Standardization → Optimization → Digitization → Automation → Autonomization. Each phase has a gate checkpoint with specific deliverables.

See `system_architecture.md` for the full system design.

## Current State (Stages 1-3 Complete ✅)

### Stage 1: Foundation (✅ Complete)
- **Project Manager** (`agent/project_manager.py`) — Creates project folder structure, manages `project.json` state, handles project CRUD operations
- **CLI Interface** (`cli.py`) — `python cli.py create|list|status|inspect` commands for project management
- **Project Schema** (`PROJECT_JSON_SCHEMA.md`) — Documents `project.json` structure with 5 phases, deliverables, team roster, gate criteria

### Stage 2: Knowledge Processing (✅ Complete)
- **Knowledge Processor** (`agent/knowledge_processor.py`) — Reads uploaded files (PDF, DOCX, TXT, CSV, JSON, images), extracts structured info via LLM, creates `knowledge_base.json` and `analysis_log.json`
- **LLM Router** (`agent/llm.py`) — Runtime model selection via MODEL_MAP, automatic escalation on low confidence, cost logging to `cost_log.json`

### Stage 3: Intelligent Conversation (✅ Complete)
- **Gap Analyzer** (`agent/gap_analyzer.py`) — Compares knowledge base vs. deliverable requirements, identifies missing fields, generates role-aware recommendations
- **Conversation Agent** (`agent/conversation_agent.py`) — Interface-agnostic message handler, role-aware question generation, session logging to `knowledge/sessions/`

### Testing (✅ Complete)
- **Integration Test** (`test_integration_1_to_3.py`) — End-to-end test exercising all Stages 1-3, verifies project creation → knowledge processing → gap analysis → conversation logging

### What's Next (Stage 4+)
**Stage 4: Full Standardization Phase** — Implement SIPOC generator, process map analyzer, baseline metrics aggregator, flowchart generator from map, exception register builder

**Stage 5: Gate Review** — Implement gate evaluation agent to check deliverable completeness and unlock phases

**Stages 6-10:** Optimization, Digitization, Automation, Autonomization phases following the same pattern

**Teams Integration (Optional):** Wire Conversation Agent to Azure Bot Service for Teams channel operation

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

### Check Status
```bash
python cli.py status my-process-automation
```

### Run Integration Tests
```bash
python test_integration_1_to_3.py
```
Tests Stages 1-3 complete workflow end-to-end.

## Important Notes

- The `.env` file contains API keys and is NOT committed to git.
- Each project maintains independent cost tracking in `cost_log.json`.
- Knowledge consolidation is incremental — files are never re-processed unless explicitly cleared.
- Session logging is automatic and date-based; multiple conversations on the same day are appended to the same session file.
- Model selection is centralized in `agent/llm.py` via `DEFAULT_MODEL_MAP`. Override specific models via `.env` if needed.
- The Conversation Agent is interface-agnostic; `handle_message()` is a pure function suitable for CLI, web, Teams, or Slack.
- Always read gap brief before generating response — this ensures agent only asks about missing information and maintains knowledge-first principle.
