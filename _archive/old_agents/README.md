# Archived Agents

This folder contains legacy agents that were replaced by the Stage 1-4 architecture.

## Archived on: 2026-02-09

## Files Archived:

### 1. **process_agent.py** (Replaced by: conversation_agent.py)
- **Reason:** Old async conversational agent using legacy architecture
- **Replacement:** `agent/conversation_agent.py` - Interface-agnostic conversation agent with gap analysis integration
- **Status:** Deprecated

### 2. **session_to_document.py** (No longer needed)
- **Reason:** Session converter for old conversation format
- **Replacement:** Stage 4 deliverable generators (sipoc_generator.py, process_map_generator.py, etc.)
- **Status:** Deprecated

### 3. **intelligent_doc_generator.py** (Replaced by: Stage 4 generators)
- **Reason:** Monolithic document generator
- **Replacement:** Modular Stage 4 generators orchestrated by `standardization_deliverables.py`
- **Status:** Deprecated

### 4. **document_generator.py** (Replaced by: Stage 4 generators)
- **Reason:** Old document generator using different architecture
- **Replacement:** Stage 4 deliverable generators with standardization orchestrator
- **Status:** Deprecated

## Why These Were Archived

The system underwent a major refactoring from a single-session conversation model to a multi-stage, persistent project architecture:

**Old Architecture:**
- Single conversation session
- All-in-one agents
- No persistent project state
- Limited phase awareness

**New Architecture (Stages 1-4):**
- Project-based with persistent state (project.json)
- Modular agents (Project Manager, Knowledge Processor, Gap Analyzer, Conversation Agent)
- Stage 4 specialized deliverable generators
- Phase-aware with gate checkpoints
- Cost tracking and session logging

## If You Need These Files

These files are preserved for reference. If you need to review the old implementation:

1. They contain working code from the Phase 1 implementation
2. Some patterns (like async conversation flow) might be useful references
3. The document generation logic in intelligent_doc_generator.py has some Word formatting utilities

**Do not** integrate these back into the main codebase without significant refactoring to match the Stage 1-4 architecture.

## Current Active Agents (as of Stage 4)

- `agent/project_manager.py` - Project lifecycle management
- `agent/knowledge_processor.py` - File reading and extraction
- `agent/gap_analyzer.py` - Gap identification
- `agent/conversation_agent.py` - Gap-guided conversations
- `agent/sipoc_generator.py` - SIPOC deliverable
- `agent/process_map_generator.py` - Process map deliverable
- `agent/baseline_metrics_generator.py` - Metrics deliverable
- `agent/flowchart_generator.py` - Flowchart deliverable
- `agent/exception_register_generator.py` - Exception register deliverable
- `agent/standardization_deliverables.py` - Stage 4 orchestrator
- `agent/llm.py` - LLM abstraction with cost tracking
- `agent/validators.py` - Input validation and security

## Related Documentation

- See `IMPLEMENTATION_SUMMARY.md` for Stages 1-3 details
- See `system_architecture.md` for overall system design
- See `CLAUDE.md` for project context and conventions
