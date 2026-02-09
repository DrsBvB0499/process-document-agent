# 🔍 Intelligent Automation Roadmap Agent System

**Multi-Stage Process Automation Framework — Stages 1-4 Complete**

An intelligent multi-agent system that guides organizations through transforming messy manual processes into optimized, automated operations using a 5-phase methodology: Standardization → Optimization → Digitization → Automation → Autonomization.

## ✨ Current Features (Stages 1-4)

### 🚀 Web Interface (NEW!)
- Browser-based UAT-ready interface
- Project management dashboard
- File upload and knowledge processing
- Real-time conversational chat
- Deliverable generation and viewing
- Cost tracking visualization

### 📋 Stage 4 Deliverables

| Deliverable | Description |
|---|---|
| **SIPOC** | Suppliers, Inputs, Process, Outputs, Customers analysis |
| **Process Map** | Step-by-step process with performers, systems, decisions |
| **Baseline Metrics** | Volume, time, cost, quality, SLA measurements |
| **Flowchart** | Mermaid flowchart visualization |
| **Exception Register** | Known exceptions and handling procedures |

### 🧠 Intelligence Features
- Knowledge-first approach (reads all files before asking questions)
- Gap analysis with intelligent recommendations
- Role-aware conversations (Process Owner, BA, SME, Developer)
- Incremental knowledge processing
- Automatic LLM model selection with cost optimization
- Session logging with full audit trail

## Project Structure

```
Project-Document-Agent/
├── agent/                              # Core agent modules
│   ├── project_manager.py             # Project lifecycle management
│   ├── knowledge_processor.py         # File reading & extraction
│   ├── gap_analyzer.py                # Gap identification
│   ├── conversation_agent.py          # Conversational interface
│   ├── sipoc_generator.py             # SIPOC deliverable
│   ├── process_map_generator.py       # Process map deliverable
│   ├── baseline_metrics_generator.py  # Metrics deliverable
│   ├── flowchart_generator.py         # Mermaid flowchart generator
│   ├── exception_register_generator.py # Exception register
│   ├── standardization_deliverables.py # Stage 4 orchestrator
│   ├── llm.py                         # LLM abstraction with cost tracking
│   └── validators.py                  # Security validation
├── web/                                # Browser interface (NEW!)
│   ├── server.py                      # Flask web server
│   ├── templates/                     # HTML templates
│   ├── static/                        # CSS & JavaScript
│   └── README.md                      # Web interface guide
├── projects/                          # Project data (gitignored)
│   └── {project-id}/
│       ├── project.json              # Project state
│       ├── knowledge/                # Uploaded files & extracted data
│       ├── deliverables/             # Generated deliverables
│       └── cost_log.json             # API cost tracking
├── cli.py                            # CLI interface
├── requirements.txt                  # Python dependencies
├── start_web.bat / start_web.sh      # Quick start scripts
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **OpenAI or Anthropic API key**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Project-Document-Agent.git
   cd Project-Document-Agent
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv

   # Windows:
   .venv\Scripts\activate

   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys:**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API key:
   # OPENAI_API_KEY=sk-proj-...
   # OPENAI_MODEL=gpt-4o
   ```

### Start the Web Interface (Recommended for UAT)

**Windows:**
```bash
start_web.bat
```

**macOS/Linux:**
```bash
chmod +x start_web.sh
./start_web.sh
```

Then open: **http://localhost:5000**

### Alternative: CLI Interface

```bash
# Create a project
python cli.py create "Invoice Processing Automation"

# List projects
python cli.py list

# Check project status
python cli.py status invoice-processing-automation
```

## 🎯 Usage

### Web Interface (UAT)

1. **Create a Project**
   - Click "Create First Project"
   - Enter project name and description
   - View project dashboard

2. **Upload Files**
   - Upload SOPs, documentation, images
   - Supports: PDF, DOCX, TXT, CSV, JSON, PNG, JPG

3. **Process Knowledge**
   - Click "Process Files"
   - LLM extracts structured information
   - View facts in knowledge base

4. **Analyze Gaps**
   - Click "Run Gap Analysis"
   - See what's missing for deliverables
   - Get role-aware recommendations

5. **Have a Conversation**
   - Navigate to Chat interface
   - Select your role (BA, SME, etc.)
   - Agent asks intelligent gap-guided questions
   - Agent never asks for info already in files

6. **Generate Deliverables**
   - Click "Generate All"
   - Creates SIPOC, Process Map, Metrics, Flowchart, Exception Register
   - Download as JSON or DOCX

### CLI Interface

```bash
# Create project
python cli.py create "Process Name" --description "Optional description"

# View project status
python cli.py status project-id

# Inspect project details
python cli.py inspect project-id
```

### Python API

```python
from agent.project_manager import ProjectManager
from agent.knowledge_processor import KnowledgeProcessor
from agent.gap_analyzer import GapAnalyzer
from agent.conversation_agent import ConversationAgent
from agent.standardization_deliverables import StandardizationDeliverablesOrchestrator

# Create project
pm = ProjectManager()
project = pm.create_project("Invoice Processing", "AP automation project")

# Process uploaded files
kp = KnowledgeProcessor()
result = kp.process_project(project['project_id'])

# Analyze gaps
ga = GapAnalyzer()
gaps = ga.analyze_project(project['project_id'])

# Chat with agent
ca = ConversationAgent()
response = ca.handle_message(
    message="What are the approval steps?",
    user_id="john@company.com",
    user_role="business_analyst",
    project_id=project['project_id']
)

# Generate deliverables
sdo = StandardizationDeliverablesOrchestrator()
deliverables = sdo.generate_all_deliverables(project['project_id'])
```

## 🏗️ Architecture

The system follows a **4-stage architecture**:

### Stage 1: Foundation
- Project Manager: Creates projects, manages state
- Validators: Security checks for user inputs
- CLI Interface: Command-line operations

### Stage 2: Knowledge Processing
- Knowledge Processor: Reads files, extracts facts via LLM
- LLM Router: Model selection, escalation, cost tracking

### Stage 3: Intelligent Conversation
- Gap Analyzer: Identifies missing information
- Conversation Agent: Gap-guided, role-aware interviews

### Stage 4: Deliverable Generation
- 5 specialized generators (SIPOC, Process Map, Metrics, Flowchart, Exception Register)
- Standardization Orchestrator: Coordinates generation
- Outputs: JSON + DOCX formats

## 📊 5-Phase Methodology

```
Phase 1: STANDARDIZATION (✅ Complete - Stage 4)
  └─> SIPOC, Process Map, Baseline Metrics, Flowchart, Exception Register

Phase 2: OPTIMIZATION (🔄 Coming in Stage 5-7)
  └─> Waste Analysis, Value Stream Map, TO-BE Process

Phase 3: DIGITIZATION (🔄 Future)
  └─> System Integration Map, Data Flow Diagram

Phase 4: AUTOMATION (🔄 Future)
  └─> Automation Specification, ROI Analysis

Phase 5: AUTONOMIZATION (🔄 Future)
  └─> Decision Rules, Self-Healing Design
```

## 🗺️ Roadmap

### ✅ Completed
- [x] **Stage 1**: Foundation (Project Manager, CLI, Validators)
- [x] **Stage 2**: Knowledge Processing (File reading, LLM extraction)
- [x] **Stage 3**: Intelligent Conversation (Gap Analysis, Conversation Agent)
- [x] **Stage 4**: Full Standardization Phase (5 deliverable generators)
- [x] **Web Interface**: Browser-based UAT interface

### 🔄 In Progress
- [ ] **Stage 5**: Gate Review Agent (deliverable completeness evaluation)

### 📋 Planned
- [ ] **Stages 6-10**: Optimization, Digitization, Automation, Autonomization phases
- [ ] **User Authentication**: Multi-user project collaboration
- [ ] **Teams Integration**: Azure Bot Service integration
- [ ] **Real-time Updates**: WebSocket support
- [ ] **Advanced Visualizations**: Mermaid rendering in browser
- [ ] **Mobile App**: Native mobile interface

## 🧪 Testing

### Integration Tests
```bash
# Test Stages 1-3
python test_integration_1_to_3.py

# Test complete workflow (Stages 1-4)
python test_integration_1_to_4.py
```

### UAT Test Scenarios
See [web/README.md](web/README.md) for detailed UAT test scenarios.

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** — Project context and conventions
- **[system_architecture.md](system_architecture.md)** — System design
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** — Technical details
- **[PROJECT_JSON_SCHEMA.md](PROJECT_JSON_SCHEMA.md)** — Data schema
- **[web/README.md](web/README.md)** — Web interface guide

## 🔐 Security Features

- Input validation (project IDs, user roles, file paths)
- Path traversal prevention
- File type whitelisting
- Secure filename handling
- API key protection (not committed to git)
- Cost tracking and monitoring

## 💰 Cost Tracking

The system automatically tracks all API calls with:
- Token counts (input/output)
- Actual USD costs per model
- Per-agent cost breakdown
- Duration tracking
- Escalation logging

View costs in:
- Web dashboard (real-time)
- `projects/{project-id}/cost_log.json`

## 🐛 Troubleshooting

### Web Server Won't Start
- Verify Flask is installed: `pip install Flask`
- Check port 5000 is available
- Review terminal output for errors

### API Key Not Working
- Ensure `.env` file exists in root directory
- Verify API key format: `OPENAI_API_KEY=sk-proj-...`
- Check API key is active and has credits

### File Upload Fails
- Check file size (max 50MB)
- Verify file type is allowed
- Ensure `projects/` directory is writable

### Agent Not Responding
- Check internet connection
- Verify API key validity
- Review `cost_log.json` for API errors
- Check terminal for Python exceptions

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions, please:
- Open an issue on GitHub
- Check existing issues to see if your question has been answered
- Provide clear descriptions when reporting bugs

## Authors

Created as part of the Intelligent Automation Roadmap initiative.
