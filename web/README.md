# Process Document Agent - Web Interface

Browser-based interface for User Acceptance Testing (UAT) of the Intelligent Automation Roadmap Agent System.

## Quick Start

### 1. Install Dependencies

```bash
# Install core dependencies (if not already done)
pip install -r ../requirements.txt

# Install web-specific dependencies
pip install -r requirements_web.txt
```

### 2. Configure Environment

Make sure your `.env` file in the root directory has the required API keys:

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

# Optional: Anthropic API
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the Server

```bash
python server.py
```

The server will start at: **http://localhost:5000**

## Features

### Project Management
- ✅ Create new projects with name and description
- ✅ List all projects with status overview
- ✅ View project dashboard with metrics

### Knowledge Processing
- ✅ Upload files (PDF, DOCX, TXT, CSV, JSON, images)
- ✅ Extract structured knowledge via LLM
- ✅ View knowledge base facts and sources
- ✅ Incremental processing (no re-processing)

### Gap Analysis
- ✅ Identify missing deliverable fields
- ✅ Calculate completeness percentage
- ✅ Role-aware recommendations

### Conversational Interface
- ✅ Real-time chat with conversation agent
- ✅ Gap-guided intelligent questions
- ✅ Role selection (Process Owner, BA, SME, Developer)
- ✅ Session history logging
- ✅ Knowledge-first approach (never asks for info already in files)

### Deliverable Generation
- ✅ Generate all Stage 4 (Standardization) deliverables
- ✅ SIPOC table
- ✅ Process map
- ✅ Baseline metrics
- ✅ Flowchart (Mermaid)
- ✅ Exception register
- ✅ Download deliverables as JSON/DOCX

### Cost Tracking
- ✅ Real-time API call tracking
- ✅ Token usage monitoring
- ✅ Actual cost calculations per model
- ✅ Cost log with full audit trail

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/<id>` - Get project details

### Knowledge Management
- `POST /api/projects/<id>/upload` - Upload file
- `POST /api/projects/<id>/process` - Process uploaded files
- `GET /api/projects/<id>/knowledge` - Get knowledge base

### Analysis & Conversation
- `POST /api/projects/<id>/analyze` - Run gap analysis
- `POST /api/projects/<id>/chat` - Send message to agent

### Deliverables
- `POST /api/projects/<id>/generate` - Generate all deliverables
- `GET /api/projects/<id>/deliverables` - List deliverables
- `GET /api/projects/<id>/deliverables/<path>` - Download deliverable

### Cost Tracking
- `GET /api/projects/<id>/cost` - Get cost log

## Architecture

```
web/
├── server.py                  # Flask app with API routes
├── templates/
│   ├── base.html             # Base template with nav
│   ├── index.html            # Project list
│   ├── project.html          # Project dashboard
│   ├── chat.html             # Conversation interface
│   ├── deliverables.html    # Deliverables viewer
│   └── error.html            # Error page
├── static/
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   └── js/
│       └── app.js            # Client-side JavaScript
└── requirements_web.txt      # Flask dependencies
```

## Security Features

- ✅ File type validation (whitelist)
- ✅ File size limits (50MB max)
- ✅ Secure filename handling
- ✅ Path traversal prevention
- ✅ Project ID validation (no ../../../ attacks)
- ✅ User role validation

## UAT Test Scenarios

### Scenario 1: Create Project & Upload Files
1. Navigate to http://localhost:5000
2. Click "Create First Project"
3. Enter project name and description
4. Upload sample SOPs/documents
5. Verify files appear in uploaded count

### Scenario 2: Process Knowledge
1. Open project dashboard
2. Click "Process Files" button
3. Wait for extraction to complete
4. Verify knowledge base fact count increases

### Scenario 3: Analyze Gaps
1. Click "Run Gap Analysis"
2. Review completeness percentage
3. View missing fields per deliverable

### Scenario 4: Conversational Interview
1. Navigate to Chat interface
2. Select your role (e.g., Business Analyst)
3. Start conversation
4. Verify agent asks intelligent, role-aware questions
5. Verify agent doesn't ask for info already in files

### Scenario 5: Generate Deliverables
1. Return to project dashboard
2. Click "Generate All" button
3. Wait for generation to complete
4. Navigate to Deliverables page
5. View and download generated files

### Scenario 6: Cost Tracking
1. Note API call count and cost on dashboard
2. Perform actions (process, analyze, chat, generate)
3. Verify cost increases appropriately
4. Check cost breakdown per agent

## Troubleshooting

### Port Already in Use
If port 5000 is in use, edit `server.py` line 389:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001 or any available port
```

### API Keys Not Working
- Verify `.env` file is in the root directory (not in `web/`)
- Check API key format and validity
- Review terminal output for specific error messages

### File Upload Fails
- Check file size (max 50MB)
- Verify file type is in allowed list
- Ensure `projects/<project_id>/knowledge/uploaded/` directory exists

### Agent Not Responding
- Check API key is valid
- Verify internet connection
- Review cost log for API errors
- Check terminal for Python exceptions

## Production Considerations

**⚠️ This is a UAT interface, not production-ready:**

- Change `FLASK_SECRET_KEY` in production
- Add user authentication/authorization
- Use a production WSGI server (gunicorn, waitress)
- Add HTTPS/TLS
- Add rate limiting
- Add proper logging
- Add database for session management
- Add file upload virus scanning
- Add CORS configuration for APIs

## Next Steps After UAT

Based on UAT feedback, consider:
1. Add user authentication (login/logout)
2. Multi-user project collaboration
3. Real-time updates (WebSockets)
4. Enhanced deliverable preview (render Mermaid diagrams in browser)
5. Project export/import
6. Batch file upload with drag-and-drop
7. Mobile-responsive improvements
8. Dark mode toggle
