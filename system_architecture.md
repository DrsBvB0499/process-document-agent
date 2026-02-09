# Intelligent Automation Roadmap — System Architecture

## 1. Vision

A multi-agent system that guides organizations through the full Intelligent Automation Roadmap: from messy manual processes to optimized, automated, and eventually autonomous operations.

The system behaves like a **senior consultant with perfect memory**: it reads everything available about a project, understands what's already been done, identifies gaps, and only asks humans for what's genuinely missing.

---

## 2. Core Design Principles

1. **Knowledge-first, not question-first** — The agent always reads all available project materials before engaging with people. It never asks a question whose answer already exists in the knowledge folder.

2. **Persistent project state** — Each process being analyzed lives as a long-running project with accumulated knowledge, not a single chat session. The project might span weeks or months.

3. **Phase-aware intelligence** — The agent knows exactly where it is on the roadmap (Standardization → Optimization → Digitization → Automation → Autonomization) and within each phase, which deliverables are complete and which still need work.

4. **Role-adaptive** — The agent adjusts its depth, vocabulary, and questions based on who it's talking to (Process Owner, BA, SME, Developer).

5. **Incremental, not repetitive** — If the SIPOC is 80% complete, the agent picks up from where it left off. It never starts from scratch.

---

## 3. System Components

### 3.1 Project Knowledge Store

Every process on the roadmap gets a **project folder** — the single source of truth.

```
projects/
└── sd-light-invoicing/
    ├── project.json              # Project metadata & state tracker
    ├── knowledge/                # Everything the agent can read
    │   ├── uploaded/             # Files added by humans
    │   │   ├── current_sop.pdf
    │   │   ├── whiteboard_photo.jpg
    │   │   ├── meeting_notes_2025-01-15.docx
    │   │   └── email_thread_complaints.msg
    │   ├── sessions/             # Conversation transcripts
    │   │   ├── session_2025-01-20_sipoc.json
    │   │   └── session_2025-01-22_process_map.json
    │   └── extracted/            # AI-processed knowledge
    │       ├── knowledge_base.json    # Structured facts the agent has learned
    │       └── analysis_log.json      # What the agent concluded from each source
    ├── deliverables/             # Generated outputs per phase
    │   ├── 1_standardization/
    │   │   ├── sipoc.json
    │   │   ├── process_map.json
    │   │   ├── baseline_metrics.json
    │   │   ├── flowchart.mmd
    │   │   └── Standardization_Checkpoint.docx
    │   ├── 2_optimization/
    │   │   ├── waste_analysis.json
    │   │   ├── to_be_process.json
    │   │   └── Optimization_Checkpoint.docx
    │   ├── 3_digitization/
    │   ├── 4_automation/
    │   └── 5_autonomization/
    └── gate_reviews/             # Gate pass/fail records
        ├── gate_1_standardization.json
        └── gate_2_optimization.json
```

### 3.2 Project State Tracker (`project.json`)

The brain of the project — tracks exactly what's been done and what's needed.

```json
{
  "project_id": "sd-light-invoicing",
  "project_name": "SD Light Invoicing",
  "created": "2025-01-20T09:00:00Z",
  "current_phase": "standardization",
  "phases": {
    "standardization": {
      "status": "in_progress",
      "deliverables": {
        "sipoc": {
          "status": "complete",
          "completeness": 100,
          "last_updated": "2025-01-20T11:00:00Z",
          "file": "deliverables/1_standardization/sipoc.json",
          "gaps": []
        },
        "process_map": {
          "status": "in_progress",
          "completeness": 60,
          "last_updated": "2025-01-22T10:00:00Z",
          "file": "deliverables/1_standardization/process_map.json",
          "gaps": [
            "Exception handling path not fully documented",
            "Time estimates missing for steps 4-7"
          ]
        },
        "baseline_metrics": {
          "status": "not_started",
          "completeness": 0,
          "gaps": [
            "No volume data captured",
            "No error rate data",
            "No time measurements"
          ]
        },
        "flowchart": {
          "status": "not_started",
          "completeness": 0
        }
      },
      "gate_criteria": {
        "single_process_defined": true,
        "exceptions_known": true,
        "baseline_stable": false
      }
    },
    "optimization": {
      "status": "locked",
      "deliverables": {}
    }
  },
  "team": {
    "process_owner": { "name": "TBD", "email": "" },
    "business_analyst": { "name": "TBD", "email": "" },
    "sme": { "name": "TBD", "email": "" },
    "developer": { "name": "TBD", "email": "" }
  },
  "knowledge_sources": [
    {
      "file": "knowledge/uploaded/current_sop.pdf",
      "type": "sop",
      "processed": true,
      "added_by": "PO",
      "date_added": "2025-01-19T14:00:00Z"
    }
  ]
}
```

### 3.3 Knowledge Processor Agent

Before any conversation happens, this agent:

1. **Scans** all files in the `knowledge/uploaded/` folder
2. **Extracts** structured information from each file (PDFs, images, docs, notes)
3. **Consolidates** into `knowledge_base.json` — a structured representation of everything known about the process
4. **Logs** what it learned from each source in `analysis_log.json`

This runs automatically whenever new files are added.

```
Input:  knowledge/uploaded/current_sop.pdf
Output: "From the SOP, I learned that the process has 12 steps,
         involves 3 teams, uses SAP and SharePoint, and runs daily.
         The SOP does not mention exception handling or error rates."
```

### 3.4 Gap Analyzer Agent

Compares what's in the knowledge base against what each deliverable requires:

```
SIPOC needs:    suppliers, inputs, process steps, outputs, customers,
                process owner, frequency, systems, exceptions
We have:        suppliers (from SOP), process steps (from SOP, partial),
                systems (from SOP)
Still missing:  inputs (trigger), outputs (specific), customers,
                process owner, frequency, exceptions
```

This analysis determines what the Conversation Agent needs to ask about.

### 3.5 Conversation Agent

The agent that talks to humans. But unlike the current version, it:

1. **Receives a brief from the Gap Analyzer** — "Here's what we know, here's what we still need"
2. **Only asks about gaps** — never re-asks what's already documented
3. **Knows its phase and deliverable** — "I'm working on the process map for Standardization"
4. **Adapts to the role** — asks the PO about ownership and strategy, asks the SME about daily operations and exceptions
5. **Saves incrementally** — after each conversation, updates the knowledge base and deliverable files

### 3.6 Document Generator Agent

Takes completed (or partially completed) deliverables and generates professional documents. This is what we've already built — the intelligent doc generator that uses AI to transform structured data into Word documents, flowcharts, etc.

### 3.7 Gate Review Agent

When all deliverables for a phase reach sufficient completeness:

1. **Evaluates** whether gate criteria are met
2. **Produces** a gate review summary
3. **Identifies** any remaining risks or gaps
4. **Recommends** pass/fail
5. If passed, **unlocks** the next phase

---

## 4. Agent Orchestration Flow

```
User starts a session
        │
        ▼
┌─────────────────────┐
│  Orchestrator Agent  │  ← Reads project.json
│  "Where are we?"     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Knowledge Processor │  ← Scans knowledge/ folder
│  "What do we know?"  │  ← Processes any new files
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Gap Analyzer        │  ← Compares knowledge vs requirements
│  "What's missing?"   │
└─────────┬───────────┘
          │
          ▼
    ┌─────┴─────┐
    │           │
    ▼           ▼
 Nothing    Gaps found
 missing        │
    │           ▼
    │    ┌──────────────┐
    │    │ Conversation │  ← Asks targeted questions
    │    │ Agent        │  ← Updates knowledge base
    │    └──────┬───────┘
    │           │
    ▼           ▼
┌─────────────────────┐
│  Deliverable Check   │  ← Are deliverables complete?
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
   Yes          No → back to Gap Analyzer
    │
    ▼
┌─────────────────────┐
│  Document Generator  │  ← Creates Word docs, flowcharts
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Gate Review Agent   │  ← Evaluates pass/fail
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
  PASS        FAIL → identifies what's missing
    │
    ▼
  Unlock next phase
```

---

## 5. Phase Definitions

### Phase 1: STANDARDIZATION (AS-IS)
**Goal:** Document the current process clearly enough that anyone could understand and follow it.

| Deliverable | Description | Source |
|---|---|---|
| SIPOC | Suppliers, Inputs, Process, Outputs, Customers | PO + SME conversation |
| AS-IS Process Map | Step-by-step with performers, systems, decisions | SME conversation + existing SOPs |
| Baseline Metrics | Volume, time, cost, error rates, SLAs | SME + data from systems |
| Process Flowchart | Visual diagram of the current flow | Generated from process map |
| Exception Register | Known exceptions and how they're handled | SME conversation |

**Gate criteria:** Single process scoped, all exceptions documented, baseline metrics captured.

### Phase 2: OPTIMIZATION (TO-BE)
**Goal:** Remove waste, streamline, and establish clear ownership.

| Deliverable | Description | Source |
|---|---|---|
| Waste Analysis | Categorized waste (waiting, rework, handoffs, etc.) | BA analysis of AS-IS |
| TO-BE Process Map | Redesigned process with improvements | BA + PO workshop |
| Improvement Register | What changes, expected impact, effort | BA + PO |
| Ownership Matrix (RACI) | Clear roles and responsibilities | PO |
| Business Case | Cost/benefit of optimization | BA |

**Gate criteria:** Waste eliminated or justified, end-to-end flow documented, clear ownership assigned.

**Key dependency:** Requires completed Standardization deliverables as input. The agent reads the AS-IS process map and proactively identifies waste patterns before asking the BA for confirmation.

### Phase 3: DIGITIZATION (READY)
**Goal:** Ensure systems, data, and access are ready for automation.

| Deliverable | Description | Source |
|---|---|---|
| System Integration Map | All systems involved, APIs, data flows | BA + DEV |
| Data Model | Structure of data moving through the process | DEV |
| Access & Security Plan | Who/what needs access to what | DEV + PO |
| Technical Readiness Assessment | Can we automate this? What's blocking? | DEV |

**Gate criteria:** Systems mapped, data structured, access provisioned.

### Phase 4: AUTOMATION (BUILD)
**Goal:** Build, test, and deploy the automated solution.

| Deliverable | Description | Source |
|---|---|---|
| Automation Spec | Detailed technical specification | DEV + BA |
| Test Plan & Results | What was tested, outcomes | DEV |
| Runbook | How to operate and maintain | DEV + PO |
| Deployment Checklist | Go-live readiness | DEV + PO |

**Gate criteria:** Built to spec, secure, operationally ready.

### Phase 5: AUTONOMIZATION (LET GO)
**Goal:** Establish rules for autonomous operation with human oversight.

| Deliverable | Description | Source |
|---|---|---|
| Decision Rules | When the system acts vs. escalates | PO + BA |
| Monitoring Dashboard Spec | What to monitor, thresholds, alerts | BA + DEV |
| Learning Loop Design | How the system improves over time | DEV + SME |
| Bounded Autonomy Charter | What the system is and isn't allowed to do | PO |

**Gate criteria:** Decision rules defined, learning data available, boundaries clear.

---

## 6. Implementation Sequence

Build this incrementally. Each stage adds capability on top of the last.

### Stage 1: Foundation (Build Next) ← YOU ARE HERE
- [ ] Project folder structure & `project.json` schema
- [ ] Knowledge folder with file upload support
- [ ] Project state tracker (read/write `project.json`)
- [ ] CLI to create a new project, list projects, check status

### Stage 2: Knowledge Processing
- [ ] Knowledge Processor agent (reads PDFs, images, docs, notes)
- [ ] Structured knowledge base (`knowledge_base.json`)
- [ ] Analysis logging (what was learned from each source)

### Stage 3: Intelligent Conversation
- [ ] Gap Analyzer (compares knowledge vs. deliverable requirements)
- [ ] Refactored Conversation Agent that receives gap briefs
- [ ] Incremental saving (updates knowledge base after each conversation)
- [ ] Role-aware questioning

### Stage 4: Full Standardization Phase
- [ ] All Standardization deliverables generated from knowledge + conversations
- [ ] Gate Review Agent for Standardization
- [ ] End-to-end test: upload docs → agent processes → conversation fills gaps → documents generated → gate review

### Stage 5: Optimization Phase
- [ ] Optimization agent reads Standardization outputs
- [ ] Waste identification from AS-IS analysis
- [ ] TO-BE process design conversation
- [ ] Gate Review for Optimization

### Stage 6: Digitization, Automation, Autonomization Phases
- [ ] Each built on the same foundation
- [ ] Increasingly technical agents for later phases

### Stage 7: Teams Integration
- [ ] Azure Bot Service setup
- [ ] Connect agent core to Teams bot
- [ ] File attachment handling
- [ ] Project channels with SharePoint knowledge folders
- [ ] Proactive notifications

---

## 7. Technology Decisions

| Component | Current | Recommended |
|---|---|---|
| AI Provider | OpenAI (GPT-4o) | Keep — works well, consider adding Claude as option |
| Conversation Interface | Terminal (CLI) | CLI now → Microsoft Teams (end goal) |
| File Storage | Local filesystem | Local for now, later SharePoint |
| Project State | JSON files | JSON for now, later database |
| Document Generation | python-docx + mmdc | Keep — working well |
| File Processing | Manual | Add: PyPDF2, Pillow, python-docx for reading, OpenAI Vision for images |
| Bot Framework | N/A | Microsoft Bot Framework + Azure Bot Service (for Teams) |

### 7.1 Model Strategy

Not every agent needs the most expensive model. The system uses a **model map** that assigns the right model to each agent based on task complexity.

```python
# Model assignments per agent role
MODEL_MAP = {
  "knowledge_processor":        "gpt-3.5-turbo-16k",  # cheap but bigger context
  "gap_analyzer":               "gpt-3.5-turbo",     # very cheap logic / diffing
  "conversation_agent":         "gpt-4o",            # high reasoning quality
  "document_generator":         "gpt-4.1-mini",      # solid text generation at mid cost
  "gate_review_agent":          "gpt-4o",            # high-impact summary/decision
  "mermaid_generator":          "gpt-4.1-mini",      # structured code generation
}
```

**Guiding principles:**

| Task Type | Model Tier | Reasoning |
|---|---|---|
| Extracting facts from documents | Cheap (mini) | High volume, pattern matching, structured output |
| Comparing lists / finding gaps | Cheap (mini) | Deterministic logic, structured input and output |
| Human-facing conversation | Premium (4o) | Needs nuance, follow-up questions, empathy |
| Generating structured JSON | Cheap (mini) | Template-following, well-defined schemas |
| Judgment and evaluation | Premium (4o) | Needs reasoning about quality, completeness, risk |
| Code generation (Mermaid, etc.) | Cheap (mini) | Structured syntax, clear rules |

**Fallback escalation:**

When a cheap model produces low-confidence results, automatically retry with the premium model.

```python
result = call_model(MODEL_MAP["knowledge_processor"], prompt)

if result.confidence < 0.7 or result.has_parse_errors:
    result = call_model("gpt-4o", prompt)  # Escalate
    log_escalation(agent="knowledge_processor", reason="low_confidence")
```

Confidence signals to watch for:
- JSON parse failures (model didn't follow the schema)
- Empty or "Not discussed" for fields that should have data
- Unusually short responses for complex documents
- Extraction contradicts known facts in the knowledge base

**Cost tracking and logging:**

Every API call is logged with:

```json
{
    "timestamp": "2025-01-20T10:05:00Z",
    "project_id": "sd-light-invoicing",
    "agent": "knowledge_processor",
    "model": "gpt-4o-mini",
    "phase": "standardization",
    "deliverable": "sipoc",
    "input_tokens": 1250,
    "output_tokens": 800,
    "cost_usd": 0.0004,
    "escalated": false,
    "duration_ms": 1200
}
```

This enables:
- **Cost per project** — how much does it cost to take one process through the roadmap?
- **Cost per phase** — which phase is most expensive?
- **Cost per deliverable** — which deliverables are cheapest to generate?
- **Escalation rate** — how often does the cheap model fail and need premium?
- **Model comparison** — is gpt-4o-mini good enough for a task, or does it always escalate?

The cost log lives at `projects/<id>/cost_log.json` and can be aggregated across projects for enterprise reporting.

**Configuration in `.env`:**

```env
# Model assignments (override defaults)
MODEL_KNOWLEDGE_PROCESSOR=gpt-4o-mini
MODEL_GAP_ANALYZER=gpt-4o-mini
MODEL_CONVERSATION_AGENT=gpt-4o
MODEL_DOCUMENT_GENERATOR=gpt-4o-mini
MODEL_GATE_REVIEW=gpt-4o

# Fallback threshold
MODEL_ESCALATION_CONFIDENCE=0.7

# Cost tracking
COST_TRACKING_ENABLED=true
```

This gives full flexibility to tune quality vs. spend per deployment, and makes the system viable at enterprise scale.

---

## 8. Interface Layer & Microsoft Teams Roadmap

### 8.1 End Goal

The agent lives in **Microsoft Teams** as a colleague people can chat with. No new tools, no terminal — just a Teams conversation. People can message the agent, drop files into the chat, and collaborate across roles in group channels.

### 8.2 Architecture: Separation of Brain and Interface

The agent core must be **completely interface-agnostic**. It receives a message and a user identity, processes it, returns a response. The interface (CLI, web, Teams) is a thin layer on top.

```
┌──────────────────────────────────────────────┐
│              INTERFACE LAYER                  │
│                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │   CLI   │  │ Web UI  │  │ MS Teams Bot│  │
│  │(current)│  │(future) │  │ (end goal)  │  │
│  └────┬────┘  └────┬────┘  └──────┬──────┘  │
│       └────────────┼──────────────┘          │
│                    ▼                         │
│          ┌──────────────────┐                │
│          │   Agent API      │                │
│          │   (message in,   │                │
│          │    response out) │                │
│          └────────┬─────────┘                │
└───────────────────┼──────────────────────────┘
                    ▼
┌──────────────────────────────────────────────┐
│              AGENT CORE                      │
│  Orchestrator → Knowledge Processor →        │
│  Gap Analyzer → Conversation Agent →         │
│  Document Generator → Gate Review            │
└──────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────┐
│         PROJECT KNOWLEDGE STORE              │
│  projects/<name>/knowledge, deliverables...  │
└──────────────────────────────────────────────┘
```

### 8.3 What Teams Gives Us

| Capability | Benefit |
|---|---|
| **User identity** | Agent automatically knows who's talking (PO, BA, SME, DEV) — no need to ask for role. Can look up from project team roster. |
| **Asynchronous conversation** | People message throughout the day, days apart. Agent handles fragmented conversations by always re-reading project state before responding. |
| **File sharing** | Users drop PDFs, photos, Excel files directly into chat. Agent processes them into the knowledge folder. |
| **Group channels** | A project can have a dedicated Teams channel. Multiple roles collaborate with the agent in one place. |
| **SharePoint integration** | Teams channels have a built-in SharePoint folder. The knowledge folder could live there natively. |
| **Notifications** | Agent can proactively notify: "SIPOC is complete, I still need baseline metrics. Can the SME help?" |
| **Familiarity** | No training needed — people already use Teams every day. |

### 8.4 What Teams Requires

| Requirement | Details |
|---|---|
| **Microsoft Bot Framework** | SDK for building Teams bots. Python SDK available (`botbuilder-python`). |
| **Azure Bot Service** | Hosts the bot and handles Teams channel registration. |
| **Azure App Service** | Runs the agent as a web service (the API layer). |
| **App Registration** | Azure AD app registration for authentication. |
| **Admin Approval** | IT/admin must approve the bot for deployment in the Teams tenant. |
| **Microsoft Graph API** | For reading SharePoint files, user profiles, team membership. |

### 8.5 Design Rules (Apply Now)

To ensure a smooth transition to Teams later, follow these rules during all development stages:

1. **No CLI-specific logic in the agent core.** Input/output handling must be separate from reasoning and knowledge processing.
2. **Every agent function takes `(message: str, user_id: str, project_id: str)` and returns a response string.** This is the API contract — works for CLI, web, and Teams.
3. **File processing accepts file paths or byte streams.** Teams will send files as downloads; the agent shouldn't assume files are already on disk.
4. **No blocking input() calls in the core.** The CLI can use `input()`, but the core agent must be callable as a function, not an interactive loop.
5. **User identity drives role lookup.** The core accepts a `user_id` and looks up their role from `project.json`, not from the conversation.

### 8.6 Teams Implementation Stages

This is later-stage work, but documenting the path now:

**Stage T1: Bot Skeleton**
- Register Azure Bot Service
- Create basic Teams bot that echoes messages
- Deploy to Azure App Service

**Stage T2: Connect Agent Core**
- Wire the Teams bot to the Agent API
- Map Teams user IDs to project roles
- Handle file attachments (download → knowledge folder)

**Stage T3: Project Channels**
- Each project gets a Teams channel
- Channel's SharePoint folder = knowledge folder
- Agent responds in-channel with awareness of project context

**Stage T4: Proactive Engagement**
- Agent notifies the right person when it needs input
- Agent posts summaries when deliverables are completed
- Agent announces gate review results

---

## 9. What Changes From Current Code

| Current | Future |
|---|---|
| Single session, single process | Multi-project, persistent state |
| Agent asks everything from scratch | Agent reads first, asks only gaps |
| One conversation = one deliverable | Multiple conversations build one deliverable incrementally |
| Hardcoded phase (standardization only) | Phase-aware with 5 phases |
| No file upload processing | Reads PDFs, images, docs, meeting notes |
| Session JSON = raw conversation | Structured knowledge base + conversation logs |
| Status tracked in conversation | Status tracked in `project.json` |
| CLI-only interface | Interface-agnostic core, CLI now, Teams later |
| Interactive input() loop | Callable API: message in, response out |
