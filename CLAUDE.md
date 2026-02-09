# CLAUDE.md — Project Context for Claude Code

## Project Overview

This is the **Intelligent Automation Roadmap Agent System** — a multi-agent system that guides organizations through transforming messy manual processes into optimized, automated operations.

The system follows 5 phases: Standardization → Optimization → Digitization → Automation → Autonomization. Each phase has a gate checkpoint with specific deliverables.

See `system_architecture.md` for the full system design.

## Current State

### What's Built (Working)
- **Process Analysis Agent** (`agent/process_agent.py`) — conversational agent that interviews users about a business process to collect SIPOC, process map, and baseline data. Uses OpenAI API.
- **Intelligent Document Generator** (`agent/intelligent_doc_generator.py`) — takes a session JSON, sends the conversation to OpenAI for structured extraction (4 API calls), generates a professional Word document with SIPOC table, process map, baseline metrics, and Mermaid flowchart rendered to PNG via `mmdc`.
- **Document Generator** (`agent/document_generator.py`) — older static document generator (being replaced by intelligent_doc_generator.py).
- **Flowchart Generator** (`agent/flowchart_generator.py`) — Pillow-based flowchart renderer (being replaced by Mermaid + mmdc approach).
- **Session Bridge** (`agent/session_to_document.py`) — older bridge script (being replaced by intelligent_doc_generator.py).
- **Project Manager** (`agent/project_manager.py`) — manages project lifecycle, folder structure, and `project.json` state tracker (Stage 1 Foundation).
- **CLI Interface** (`cli.py`) — command-line tool to create projects, list projects, check status, and inspect project state (Stage 1 Foundation).
- **Knowledge Processor** (`agent/knowledge_processor.py`) — reads uploaded files (PDF, DOCX, TXT, images), extracts structured information using LLM, consolidates into `knowledge_base.json` and `analysis_log.json` (Stage 2).

### What's Next (Stage 1: Foundation)
We are building the **project-based foundation** as described in system_architecture.md Section 6, Stage 1:
- Project folder structure with `project.json` state tracker
- Knowledge folder where humans can upload files and the agent can store information
- CLI to create projects, list projects, check status
- Refactoring current agent to work within project context

## Tech Stack

- **Language:** Python 3.12
- **AI Provider:** OpenAI (GPT-4o) via `openai` package
- **Environment:** `.env` file with `OPENAI_API_KEY` and `OPENAI_MODEL`
- **Document Generation:** `python-docx` for Word files
- **Flowcharts:** Mermaid.js rendered via `mmdc` (Mermaid CLI, requires Node.js)
- **Config:** `python-dotenv` for environment variables
- **OS:** Windows (development), should work cross-platform

## Project Structure

```
process-document-agent/
├── system_architecture.md   # System design document
├── CLAUDE.md                # This file — project context for Claude Code
├── README.md                # User-facing documentation
├── requirements.txt         # Python dependencies
├── .env                     # API keys (not in git)
├── .gitignore
├── agent/                   # Agent source code
│   ├── process_agent.py     # Conversational analysis agent
│   ├── intelligent_doc_generator.py  # AI-powered document generator
│   ├── document_generator.py         # Legacy static generator
│   ├── flowchart_generator.py        # Legacy Pillow-based flowcharts
│   ├── session_to_document.py        # Legacy bridge script
│   └── project_manager.py            # Project lifecycle management (new)
├── outputs/                 # Generated outputs (session files, documents)
├── cli.py                   # Command-line interface for project management
├── projects/                # Project knowledge stores with project.json
└── PROJECT_JSON_SCHEMA.md   # Documentation of project.json structure
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

## Important Notes

- The `.env` file contains API keys and is NOT committed to git.
- The `outputs/` folder contains generated files and session data.
- When creating new agents or scripts, follow the pattern in `intelligent_doc_generator.py` for .env loading (try multiple paths).
- Mermaid flowcharts: always use `cleanup_mermaid()` to ensure proper formatting before passing to `mmdc`. Avoid special characters (€, <, >) in node labels.
- On Windows, always use `shell=True` for subprocess calls to `mmdc`.
