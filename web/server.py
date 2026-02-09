"""Flask web server for Process Document Agent.

Provides browser-based interface for project management, knowledge processing,
gap analysis, conversation, and deliverable generation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename

# Add parent directory to path to import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.project_manager import ProjectManager
from agent.knowledge_processor import KnowledgeProcessor
from agent.gap_analyzer import GapAnalyzer
from agent.conversation_agent import ConversationAgent
from agent.standardization_deliverables import StandardizationDeliverablesOrchestrator

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize agents
pm = ProjectManager()
kp = KnowledgeProcessor()
ga = GapAnalyzer()
ca = ConversationAgent()
sdo = StandardizationDeliverablesOrchestrator()

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv', '.json', '.png', '.jpg', '.jpeg'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


# ==================== WEB PAGES ====================

@app.route('/')
def index():
    """Home page with project list."""
    projects = pm.list_projects()
    return render_template('index.html', projects=projects)


@app.route('/project/<project_id>')
def project_dashboard(project_id: str):
    """Project dashboard showing status, actions, and deliverables."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return render_template('error.html', message=f"Project '{project_id}' not found"), 404

        # Get knowledge stats
        kb_path = pm.config.projects_root / project_id / "knowledge" / "extracted" / "knowledge_base.json"
        kb_facts = 0
        if kb_path.exists():
            try:
                with open(kb_path, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
                    kb_facts = len(kb.get('facts', []))
            except Exception:
                pass

        # Get uploaded files count
        upload_dir = pm.config.projects_root / project_id / "knowledge" / "uploaded"
        uploaded_files = list(upload_dir.glob('*.*')) if upload_dir.exists() else []

        # Get cost log summary
        cost_path = pm.config.projects_root / project_id / "cost_log.json"
        total_cost = 0.0
        api_calls = 0
        if cost_path.exists():
            try:
                with open(cost_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    api_calls = len(logs)
                    total_cost = sum(log.get('cost_usd', 0.0) for log in logs)
            except Exception:
                pass

        return render_template(
            'project.html',
            project=project,
            project_id=project_id,
            kb_facts=kb_facts,
            uploaded_files=len(uploaded_files),
            api_calls=api_calls,
            total_cost=total_cost
        )
    except Exception as e:
        return render_template('error.html', message=str(e)), 500


@app.route('/project/<project_id>/chat')
def chat_interface(project_id: str):
    """Conversational interface for gap-guided interviews."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return render_template('error.html', message=f"Project '{project_id}' not found"), 404

        # Load conversation history from today's session
        session_dir = pm.config.projects_root / project_id / "knowledge" / "sessions"
        today = datetime.now().strftime("%Y-%m-%d")
        session_file = session_dir / f"session_{today}.json"

        messages = []
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    messages = session_data.get('turns', [])
            except Exception:
                pass

        return render_template(
            'chat.html',
            project=project,
            project_id=project_id,
            messages=messages
        )
    except Exception as e:
        return render_template('error.html', message=str(e)), 500


@app.route('/project/<project_id>/deliverables')
def view_deliverables(project_id: str):
    """View and download deliverables."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return render_template('error.html', message=f"Project '{project_id}' not found"), 404

        # Scan deliverables directory
        deliverables_dir = pm.config.projects_root / project_id / "deliverables"
        deliverables = []

        if deliverables_dir.exists():
            for phase_dir in sorted(deliverables_dir.iterdir()):
                if phase_dir.is_dir():
                    phase_name = phase_dir.name
                    for file in sorted(phase_dir.glob('*.*')):
                        deliverables.append({
                            'phase': phase_name,
                            'name': file.name,
                            'path': str(file.relative_to(pm.config.projects_root / project_id)),
                            'size': file.stat().st_size,
                            'modified': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })

        return render_template(
            'deliverables.html',
            project=project,
            project_id=project_id,
            deliverables=deliverables
        )
    except Exception as e:
        return render_template('error.html', message=str(e)), 500


# ==================== API ENDPOINTS ====================

@app.route('/api/projects', methods=['GET'])
def api_list_projects():
    """List all projects."""
    try:
        projects = pm.list_projects()
        return jsonify([p.to_dict() for p in projects])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects', methods=['POST'])
def api_create_project():
    """Create a new project."""
    try:
        data = request.get_json()
        project_name = data.get('project_name')
        description = data.get('description', '')

        if not project_name:
            return jsonify({'error': 'project_name is required'}), 400

        project = pm.create_project(project_name, description)
        return jsonify(project.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['GET'])
def api_get_project(project_id: str):
    """Get project details."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404
        return jsonify(project.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/upload', methods=['POST'])
def api_upload_file(project_id: str):
    """Upload a file to the project's knowledge folder."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        filename = secure_filename(file.filename)
        upload_dir = pm.config.projects_root / project_id / "knowledge" / "uploaded"
        upload_dir.mkdir(parents=True, exist_ok=True)

        filepath = upload_dir / filename
        file.save(str(filepath))

        return jsonify({
            'message': f'File "{filename}" uploaded successfully',
            'filename': filename,
            'path': str(filepath.relative_to(pm.config.projects_root / project_id))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/process', methods=['POST'])
def api_process_knowledge(project_id: str):
    """Process uploaded files and extract knowledge."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        result = kp.process_project(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/analyze', methods=['POST'])
def api_analyze_gaps(project_id: str):
    """Analyze gaps in knowledge base."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        result = ga.analyze_project(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/chat', methods=['POST'])
def api_send_message(project_id: str):
    """Send a message to the conversation agent."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'web-user')
        user_role = data.get('user_role', 'business_analyst')

        if not message:
            return jsonify({'error': 'message is required'}), 400

        response = ca.handle_message(message, user_id, user_role, project_id)

        return jsonify({
            'response': response,
            'user_message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/generate', methods=['POST'])
def api_generate_deliverables(project_id: str):
    """Generate all standardization deliverables."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        results = sdo.generate_all_deliverables(project_id)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/deliverables', methods=['GET'])
def api_list_deliverables(project_id: str):
    """List all deliverables for a project."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        deliverables_dir = pm.config.projects_root / project_id / "deliverables"
        deliverables = []

        if deliverables_dir.exists():
            for phase_dir in sorted(deliverables_dir.iterdir()):
                if phase_dir.is_dir():
                    phase_name = phase_dir.name
                    for file in sorted(phase_dir.glob('*.*')):
                        deliverables.append({
                            'phase': phase_name,
                            'name': file.name,
                            'path': str(file.relative_to(pm.config.projects_root / project_id)),
                            'size': file.stat().st_size,
                            'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat() + 'Z'
                        })

        return jsonify(deliverables)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/deliverables/<path:filepath>', methods=['GET'])
def api_download_deliverable(project_id: str, filepath: str):
    """Download a specific deliverable file."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        file_path = pm.config.projects_root / project_id / filepath

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        # Security check: ensure file is within project directory
        if not str(file_path.resolve()).startswith(str((pm.config.projects_root / project_id).resolve())):
            return jsonify({'error': 'Access denied'}), 403

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/cost', methods=['GET'])
def api_get_cost_log(project_id: str):
    """Get cost log for a project."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        cost_path = pm.config.projects_root / project_id / "cost_log.json"

        if not cost_path.exists():
            return jsonify([])

        with open(cost_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)

        # Calculate summary
        total_cost = sum(log.get('cost_usd', 0.0) for log in logs)
        total_input_tokens = sum(log.get('input_tokens', 0) for log in logs)
        total_output_tokens = sum(log.get('output_tokens', 0) for log in logs)

        return jsonify({
            'logs': logs,
            'summary': {
                'total_cost_usd': round(total_cost, 4),
                'total_input_tokens': total_input_tokens,
                'total_output_tokens': total_output_tokens,
                'total_calls': len(logs)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/knowledge', methods=['GET'])
def api_get_knowledge_base(project_id: str):
    """Get knowledge base for a project."""
    try:
        project = pm.get_project(project_id)
        if not project:
            return jsonify({'error': f"Project '{project_id}' not found"}), 404

        kb_path = pm.config.projects_root / project_id / "knowledge" / "extracted" / "knowledge_base.json"

        if not kb_path.exists():
            return jsonify({'facts': [], 'sources': [], 'exceptions': [], 'unknowns': []})

        with open(kb_path, 'r', encoding='utf-8') as f:
            kb = json.load(f)

        return jsonify(kb)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('error.html', message='Internal server error'), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("🚀 Starting Process Document Agent Web Server")
    print("📂 Projects directory:", pm.config.projects_root)
    print("🌐 Server running at: http://localhost:5000")
    print("\n✅ Ready for UAT!")

    app.run(debug=True, host='0.0.0.0', port=5000)
