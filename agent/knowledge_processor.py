"""Knowledge Processor Agent — reads and extracts knowledge from uploaded files.

This agent:
1. Scans projects/<project_id>/knowledge/uploaded/ for new files
2. Reads each file (PDF, DOCX, TXT, images, etc.)
3. Uses the LLM to extract structured information
4. Consolidates findings into knowledge_base.json
5. Logs analysis per source in analysis_log.json

The agent is knowledge-first: it learns everything available before
any conversation happens, giving subsequent agents a complete picture
of what's already known.

Usage:
    from agent.knowledge_processor import KnowledgeProcessor
    
    kp = KnowledgeProcessor()
    project = kp.process_project("sd-light-invoicing")
    knowledge_base = project.get("knowledge_base", {})
    
    print(f"Extracted {len(knowledge_base.get('facts', []))} facts")
    print(f"Analyzed {len(knowledge_base.get('sources', []))} sources")
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import mimetypes

from agent.llm import call_model
from agent.validators import validate_project_id
from agent.hybrid_security import HybridSecurityChecker
from agent.security_logger import SecurityLogger


class KnowledgeProcessor:
    """Scans, reads, and extracts knowledge from uploaded project files."""

    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize the Knowledge Processor.

        Args:
            projects_root: Root directory for projects.
                          Defaults to ./projects/
        """
        self.projects_root = Path(projects_root or (Path(__file__).parent.parent / "projects"))
        self.security_checker = HybridSecurityChecker(self.projects_root)
        self.security_logger = SecurityLogger(self.projects_root)

    def process_project(self, project_id: str) -> Dict[str, Any]:
        """Process all uploaded files for a project.

        Scans knowledge/uploaded/, reads each file, extracts structured
        information, and updates knowledge_base.json and analysis_log.json.

        Args:
            project_id: The project ID to process

        Returns:
            Dictionary with keys: knowledge_base, analysis_log, status
        """
        # Validate project_id to prevent path traversal attacks
        if not validate_project_id(project_id):
            return {
                "knowledge_base": {},
                "analysis_log": [],
                "status": "invalid_project_id",
                "error": f"Invalid project ID '{project_id}'. Must contain only lowercase letters, numbers, and hyphens.",
            }

        project_path = self.projects_root / project_id
        uploaded_path = project_path / "knowledge" / "uploaded"
        extracted_path = project_path / "knowledge" / "extracted"

        if not uploaded_path.exists():
            return {
                "knowledge_base": {},
                "analysis_log": [],
                "status": "no_uploaded_files",
            }

        extracted_path.mkdir(parents=True, exist_ok=True)

        # Load existing knowledge base and analysis log
        knowledge_base = self._load_knowledge_base(extracted_path)
        analysis_log = self._load_analysis_log(extracted_path)

        # Find files that haven't been processed
        processed_files = {entry.get("source_file") for entry in analysis_log}
        files_to_process = [
            f
            for f in uploaded_path.iterdir()
            if f.is_file() and f.name not in processed_files
        ]

        # Process each new file
        for file_path in files_to_process:
            try:
                analysis = self._process_file(
                    project_id, file_path, uploaded_path
                )
                if analysis:
                    analysis_log.append(analysis)
                    # Merge extracted facts and sources
                    if "facts" in analysis.get("extraction", {}):
                        knowledge_base.setdefault("facts", []).extend(
                            analysis["extraction"]["facts"]
                        )
                    if "sources" in analysis.get("extraction", {}):
                        knowledge_base.setdefault("sources", []).extend(
                            analysis["extraction"]["sources"]
                        )
            except Exception as e:
                # Log error but continue processing
                analysis_log.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source_file": file_path.name,
                    "file_type": file_path.suffix,
                    "status": "error",
                    "error": str(e),
                    "extraction": {},
                })

        # Deduplicate facts and sources
        knowledge_base["facts"] = self._deduplicate_facts(
            knowledge_base.get("facts", [])
        )
        knowledge_base["sources"] = self._deduplicate_sources(
            knowledge_base.get("sources", [])
        )
        knowledge_base["last_updated"] = datetime.utcnow().isoformat() + "Z"

        # Save updated files
        self._save_knowledge_base(extracted_path, knowledge_base)
        self._save_analysis_log(extracted_path, analysis_log)

        return {
            "knowledge_base": knowledge_base,
            "analysis_log": analysis_log,
            "status": "success",
            "files_processed": len(files_to_process),
        }

    def _process_file(
        self, project_id: str, file_path: Path, uploaded_path: Path
    ) -> Optional[Dict[str, Any]]:
        """Process a single uploaded file.

        Reads the file, calls the LLM to extract information,
        and returns an analysis entry.
        """
        # Read file content
        file_content = self._read_file(file_path)
        if not file_content:
            return None

        # SECURITY: Check file content for injection attempts (limit check to first 5000 chars for performance)
        content_preview = file_content[:5000]
        security_check = self.security_checker.check_input(
            user_input=content_preview,
            project_id=project_id,
            context="file_upload"
        )

        # Log if suspicious
        if not security_check.is_safe:
            self.security_logger.log_event(
                event_type="suspicious_file_content",
                project_id=project_id,
                user_id="file_upload",
                risk_level=security_check.risk_level,
                threats=security_check.threats_detected,
                details={
                    "filename": file_path.name,
                    "file_type": file_path.suffix,
                    "file_size": file_path.stat().st_size,
                    "check_method": security_check.check_method
                }
            )

        # Block critical threats in uploaded files
        if security_check.risk_level == "critical":
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source_file": file_path.name,
                "file_type": file_path.suffix,
                "status": "blocked",
                "error": "File content blocked due to security concerns",
                "extraction": {}
            }

        # Determine file type
        file_type = file_path.suffix.lower()
        if not file_type:
            file_type = mimetypes.guess_extension(file_path.name) or "unknown"

        # Build extraction prompt
        prompt = self._build_extraction_prompt(file_path.name, file_content, file_type)

        # Call LLM to extract information
        result = call_model(
            project_id=project_id,
            agent="knowledge_processor",
            prompt=prompt,
        )

        # Parse extracted information
        text = result.get("text", "")
        extraction = self._parse_extraction(text)

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source_file": file_path.name,
            "file_type": file_type,
            "file_size_bytes": file_path.stat().st_size,
            "status": "success",
            "model": result.get("model"),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "cost_usd": result.get("cost_usd", 0.0),
            "extraction": extraction,
        }

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read file content based on type."""
        try:
            suffix = file_path.suffix.lower()

            # Plain text files
            if suffix in {".txt", ".md", ".log"}:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

            # JSON files
            elif suffix == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)

            # CSV (simple read as text)
            elif suffix == ".csv":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

            # DOCX (basic extraction)
            elif suffix in {".docx", ".doc"}:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    return "\n".join([para.text for para in doc.paragraphs])
                except Exception:
                    return None

            # PDF (basic text extraction)
            elif suffix == ".pdf":
                try:
                    import PyPDF2
                    with open(file_path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        return text
                except Exception:
                    return None

            # Images (OCR if available, otherwise skip)
            elif suffix in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
                try:
                    from PIL import Image
                    import pytesseract
                    img = Image.open(file_path)
                    return pytesseract.image_to_string(img)
                except Exception:
                    # OCR not available; return placeholder
                    return f"[Image file: {file_path.name}]"

            else:
                # Unknown file type; try as text
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

        except Exception:
            return None

    def _build_extraction_prompt(
        self, filename: str, content: str, file_type: str
    ) -> str:
        """Build a prompt for the LLM to extract structured information."""
        # Increased from 4000 to 50000 chars to capture more content
        # This allows ~12,500 tokens, suitable for gpt-4o
        truncated_content = content[:50000]

        return f"""You are analyzing a process documentation file to extract ALL relevant information.

File: {filename}
Type: {file_type}

Content:
{truncated_content}

{"..." if len(content) > 50000 else ""}

CRITICAL INSTRUCTIONS:
1. **EXTRACT EVERYTHING** - Do not skip tables, labeled fields, or structured data
2. **PROCESS OWNER** - If there's a field/cell labeled "process owner", "owner", or similar, extract the name!
3. **TEAMS & ROLES** - Extract all team names, roles, and responsibilities mentioned
4. **SIPOC ELEMENTS** - Specifically look for:
   - Suppliers: Who provides information/materials to start the process?
   - Inputs: What information/materials are needed?
   - Outputs: What is produced/delivered?
   - Customers: Who receives the outputs?
5. **PROCESS STEPS** - Extract each step with:
   - Step name/description
   - Who performs it (performer/role)
   - What systems are used
   - Any decisions or branching logic
6. **METRICS** - Extract numbers, measurements, volumes, times, costs
7. **TABLES** - Extract data from tables row by row with labels
8. **EXCEPTIONS** - Any special cases, errors, or edge cases mentioned

Extract and return ONLY a valid JSON object (no markdown, no code block) with this exact schema:
{{
  "facts": [
    {{"category": "process_owner", "fact": "Owner name: [SPECIFIC NAME FROM DOCUMENT]", "confidence": 1.0}},
    {{"category": "suppliers", "fact": "[WHO] provides [WHAT]", "confidence": 0.9}},
    {{"category": "inputs", "fact": "[SPECIFIC INPUT] from [SOURCE]", "confidence": 0.9}},
    {{"category": "outputs", "fact": "[SPECIFIC OUTPUT] to [DESTINATION]", "confidence": 0.9}},
    {{"category": "customers", "fact": "[WHO] receives [WHAT]", "confidence": 0.9}},
    {{"category": "process_steps", "fact": "Step X: [ACTION] by [PERFORMER] using [SYSTEM]", "confidence": 0.8}},
    {{"category": "teams", "fact": "[TEAM NAME]: [RESPONSIBILITY]", "confidence": 0.9}},
    {{"category": "systems", "fact": "[SYSTEM NAME]", "confidence": 0.9}},
    {{"category": "metrics", "fact": "[METRIC NAME]: [VALUE] [UNIT]", "confidence": 0.8}},
    {{"category": "decisions", "fact": "Decision: [CONDITION] then [ACTION]", "confidence": 0.7}},
    {{"category": "constraints", "fact": "[CONSTRAINT DESCRIPTION]", "confidence": 0.7}}
  ],
  "sources": [
    {{"system": "[SYSTEM/TEAM NAME]", "description": "[WHAT THEY DO]"}}
  ],
  "exceptions": ["[EXCEPTION CASE]"],
  "unknowns": ["[WHAT'S UNCLEAR]"]
}}

IMPORTANT:
- Be SPECIFIC - extract actual names, values, and details from the document
- Don't skip tables or structured data!
- If you see a labeled field (like "Process Owner: John Smith"), extract it!
- Extract team names mentioned anywhere in the document
- Return ONLY the JSON object, no other text.
"""

    def _parse_extraction(self, text: str) -> Dict[str, Any]:
        """Parse the LLM response as JSON extraction."""
        try:
            # Try to extract JSON from the response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: return empty extraction
        return {
            "facts": [],
            "sources": [],
            "exceptions": [],
            "unknowns": [],
        }

    def _deduplicate_facts(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate facts based on category + fact text."""
        seen = set()
        unique = []
        for fact in facts:
            key = (fact.get("category"), fact.get("fact"))
            if key not in seen:
                seen.add(key)
                unique.append(fact)
        return unique

    def _deduplicate_sources(
        self, sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on system name."""
        seen = set()
        unique = []
        for source in sources:
            system = source.get("system")
            if system not in seen:
                seen.add(system)
                unique.append(source)
        return unique

    def _load_knowledge_base(self, extracted_path: Path) -> Dict[str, Any]:
        """Load existing knowledge_base.json or return empty."""
        kb_path = extracted_path / "knowledge_base.json"
        if kb_path.exists():
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"facts": [], "sources": [], "exceptions": [], "unknowns": []}

    def _load_analysis_log(self, extracted_path: Path) -> List[Dict[str, Any]]:
        """Load existing analysis_log.json or return empty."""
        log_path = extracted_path / "analysis_log.json"
        if log_path.exists():
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_knowledge_base(
        self, extracted_path: Path, knowledge_base: Dict[str, Any]
    ) -> None:
        """Save knowledge_base.json."""
        kb_path = extracted_path / "knowledge_base.json"
        try:
            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            # Log error but don't crash the entire process
            print(f"Warning: Failed to save knowledge_base.json: {e}")

    def _save_analysis_log(
        self, extracted_path: Path, analysis_log: List[Dict[str, Any]]
    ) -> None:
        """Save analysis_log.json."""
        log_path = extracted_path / "analysis_log.json"
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(analysis_log, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            # Log error but don't crash the entire process
            print(f"Warning: Failed to save analysis_log.json: {e}")


if __name__ == "__main__":
    # Quick test: process a project
    kp = KnowledgeProcessor()
    try:
        result = kp.process_project("test-project")
        print(f"Status: {result['status']}")
        print(f"Files processed: {result.get('files_processed', 0)}")
        print(f"Facts extracted: {len(result['knowledge_base'].get('facts', []))}")
        print(f"Sources identified: {len(result['knowledge_base'].get('sources', []))}")
    except Exception as e:
        print(f"Error: {e}")
