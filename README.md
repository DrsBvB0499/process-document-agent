# 🔍 Process Analysis Agent

**Intelligent Automation Roadmap — Standardization Checkpoint**

This agent guides teams through documenting the AS-IS state of a business process, ensuring it meets the Standardization checkpoint before progressing to Optimization.

## What It Produces

| Deliverable | Description |
|---|---|
| **SIPOC** | Suppliers, Inputs, Process, Outputs, Customers + enriched fields |
| **AS-IS Process Map** | Visual flowchart with swimlanes (PNG image) |
| **Baseline Measurement** | Time, cost, frequency, risk metrics |
| **Standardization Checkpoint Document** | Full Word document (.docx) with all deliverables |

## Project Structure

```
project-document-agent/
├── agent/
│   ├── process_agent.py         # Conversational agent (Claude API)
│   ├── flowchart_generator.py   # Process flow diagram generator (Pillow)
│   └── document_generator.py    # Word document generator (python-docx)
├── examples/
│   └── afkeurbewijzen_example.py  # Reference data format + runner
├── templates/                    # Document templates (coming soon)
├── outputs/                      # Generated files go here
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites
- **Python 3.9+** 
- **Node.js 14+** (optional, for flowchart rendering)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/process-document-agent.git
   cd process-document-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your actual API keys
   # For Anthropic (Claude):
   #   ANTHROPIC_API_KEY=sk-ant-...
   # For OpenAI (optional):
   #   OPENAI_API_KEY=sk-proj-...
   ```

5. **(Optional but recommended)** Install Mermaid CLI for flowchart image generation:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```
   Without this, flowcharts will be embedded as code text instead of PNG images in documents.

## Usage

### Run the conversational agent (CLI):
```bash
python agent/process_agent.py
```

### Generate documents from data (standalone):
```bash
cd agent
python document_generator.py
```
This generates both the process flow diagram (PNG) and the Word document (DOCX).

### Generate only the flowchart:
```bash
cd agent
python flowchart_generator.py
```

## How It Works

1. **process_agent.py** — Guides users through a structured conversation, asking one question at a time, tracking progress across three deliverables (SIPOC, Process Map, Baseline)
2. **flowchart_generator.py** — Takes process step data and generates a professional swimlane flowchart using Pillow (no external dependencies like Visio needed)
3. **document_generator.py** — Takes all collected data + the flowchart and produces a complete Standardization Checkpoint Word document with title page, TOC, tables, embedded diagram, gate assessment, and sign-off section

## Roadmap

- [x] Phase 1: Conversational agent with SIPOC, Process Map, Baseline
- [x] Phase 1b: Document generation (Word + visual flowchart)
- [ ] Phase 2: File reading (documents, whiteboard images, transcripts)
- [ ] Phase 3: Cloud integration (OneDrive/SharePoint)
- [ ] Phase 4: Teams chat integration
- [ ] Phase 5: Power Platform solution scanning

## Part of the Intelligent Automation Roadmap

```
STANDARDIZATION → OPTIMIZATION → DIGITIZATION → AUTOMATION → AUTONOMIZATION
     ↑ WE ARE HERE
```

## Troubleshooting

### Mermaid CLI Not Found
If you see "Mermaid CLI (mmdc) not found", install it:
```bash
npm install -g @mermaid-js/mermaid-cli
```

### API Key Not Found
Make sure your `.env` file exists and has the correct API key from `.env.example`.

### Virtual Environment Not Activated
Ensure your virtual environment is active before running the agent.

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
