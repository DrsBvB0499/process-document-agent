"""LLM helper: model map, fallback escalation, and cost logging.

Provides a single entrypoint `call_model(...)` used by agents to invoke
an LLM according to the configured MODEL_MAP. Handles automatic
escalation to a premium model on low-confidence results and appends a
cost entry to `projects/<project_id>/cost_log.json`.

The module supports a dry-run mode when no API keys are present so
unit tests and local development can run without secrets.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_MODEL_MAP = {
    "knowledge_processor": "gpt-4o-mini",  # Upgraded from gpt-3.5-turbo-16k for better extraction
    "gap_analyzer": "gpt-3.5-turbo",
    "conversation_agent": "gpt-4o",
    "document_generator": "gpt-4o-mini",
    "gate_review_agent": "gpt-4o",
    "mermaid_generator": "gpt-4o-mini",
}


def _load_model_map() -> Dict[str, str]:
    """Load model map from env overrides or default."""
    model_map = DEFAULT_MODEL_MAP.copy()
    for key in list(model_map.keys()):
        env_key = f"MODEL_{key.upper()}"
        if env_key in os.environ:
            model_map[key] = os.environ[env_key]
    return model_map


def _get_escalation_threshold() -> float:
    try:
        return float(os.environ.get("MODEL_ESCALATION_CONFIDENCE", "0.7"))
    except Exception:
        return 0.7


def _project_cost_log_path(projects_root: Path, project_id: str) -> Path:
    p = projects_root / project_id / "cost_log.json"
    return p


def append_cost_log(projects_root: Path, project_id: str, entry: Dict[str, Any]) -> None:
    """Append a cost log entry to the project's cost_log.json.

    Creates the file if missing and keeps a list of entries.
    """
    path = _project_cost_log_path(projects_root, project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    logs = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    logs.append(entry)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception:
        # Silently fail on cost logging errors to avoid disrupting the main flow
        pass


def _mock_model_response(prompt: str) -> Tuple[str, int, int, float, float]:
    """Return a mock response (text, input_tokens, output_tokens, cost, confidence)."""
    # Simple heuristics for mock token counts
    input_tokens = max(1, len(prompt) // 4)
    output_tokens = min(512, max(1, len(prompt) // 6))
    text = "[MOCK RESPONSE] " + (prompt[:200] + ("..." if len(prompt) > 200 else ""))
    cost = 0.0
    confidence = 0.95
    return text, input_tokens, output_tokens, cost, confidence


def call_model(
    project_id: str,
    agent: str,
    prompt: str,
    projects_root: Optional[Path] = None,
    escalate_on_low_confidence: bool = True,
    preferred_model: Optional[str] = None,
) -> Dict[str, Any]:
    """Call a model according to the model map and log cost.

    Returns a dictionary with keys: `text`, `model`, `input_tokens`,
    `output_tokens`, `cost_usd`, `confidence`, `escalated`, `duration_ms`.

    If no API keys are configured the function returns a mocked response
    and still writes a cost log entry with `cost_usd` 0.0.
    """
    start = time.time()
    model_map = _load_model_map()
    model = preferred_model or model_map.get(agent, "gpt-4o-mini")
    projects_root = Path(projects_root or (Path(__file__).parent.parent / "projects"))

    # Determine whether we have an OpenAI key (simple dry-run guard)
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))

    # For now implement a simple call: if no keys, return mock response
    if not (has_openai or has_anthropic):
        text, in_toks, out_toks, cost, confidence = _mock_model_response(prompt)
        duration_ms = int((time.time() - start) * 1000)
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "project_id": project_id,
            "agent": agent,
            "model": model,
            "phase": None,
            "deliverable": None,
            "input_tokens": in_toks,
            "output_tokens": out_toks,
            "cost_usd": cost,
            "escalated": False,
            "duration_ms": duration_ms,
        }
        try:
            append_cost_log(projects_root, project_id, entry)
        except Exception:
            pass

        return {
            "text": text,
            "model": model,
            "input_tokens": in_toks,
            "output_tokens": out_toks,
            "cost_usd": cost,
            "confidence": confidence,
            "escalated": False,
            "duration_ms": duration_ms,
        }

    # Real API call path (simplified): use OpenAI for models containing 'gpt',
    # and Anthropic for models containing 'claude'. Implement light parsing of response
    # and compute a crude confidence signal.
    text = ""
    in_toks = 0
    out_toks = 0
    cost = 0.0
    confidence = 0.0
    escalated = False

    # Minimal implementation to avoid importing heavy SDKs here.
    # If OPENAI_API_KEY is present and model name contains 'gpt', call OpenAI.
    if "gpt" in model and has_openai:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.environ.get("OPENAI_TEMPERATURE", "0.2")),
            )
            text = resp.choices[0].message.content
            # token accounting: modern API provides usage in response
            in_toks = resp.usage.prompt_tokens if resp.usage else 0
            out_toks = resp.usage.completion_tokens if resp.usage else 0

            # Calculate actual cost based on model pricing (as of 2026)
            if "gpt-4o" in model:
                # gpt-4o: $5/1M input, $15/1M output
                cost = (in_toks / 1_000_000 * 5.0) + (out_toks / 1_000_000 * 15.0)
            elif "gpt-3.5-turbo" in model:
                # gpt-3.5-turbo: $0.50/1M input, $1.50/1M output
                cost = (in_toks / 1_000_000 * 0.5) + (out_toks / 1_000_000 * 1.5)
            else:
                cost = 0.0

            confidence = 0.9
        except Exception as e:
            # Fall back to mock if API call fails
            text, in_toks, out_toks, cost, confidence = _mock_model_response(prompt)

    elif "claude" in model and has_anthropic:
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            # Use modern Messages API instead of deprecated Completions API
            resp = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text if resp.content else ""
            # Modern API provides usage information
            in_toks = resp.usage.input_tokens if resp.usage else 0
            out_toks = resp.usage.output_tokens if resp.usage else 0

            # Calculate actual cost based on Claude pricing (as of 2026)
            if "claude-3-5-sonnet" in model or "claude-sonnet" in model:
                # Claude Sonnet 3.5: $3/1M input, $15/1M output
                cost = (in_toks / 1_000_000 * 3.0) + (out_toks / 1_000_000 * 15.0)
            elif "claude-3-opus" in model or "claude-opus" in model:
                # Claude Opus: $15/1M input, $75/1M output
                cost = (in_toks / 1_000_000 * 15.0) + (out_toks / 1_000_000 * 75.0)
            elif "claude-3-haiku" in model or "claude-haiku" in model:
                # Claude Haiku: $0.25/1M input, $1.25/1M output
                cost = (in_toks / 1_000_000 * 0.25) + (out_toks / 1_000_000 * 1.25)
            else:
                cost = 0.0

            confidence = 0.88
        except Exception:
            text, in_toks, out_toks, cost, confidence = _mock_model_response(prompt)

    else:
        # Unknown model or provider; return mock response
        text, in_toks, out_toks, cost, confidence = _mock_model_response(prompt)

    duration_ms = int((time.time() - start) * 1000)

    # If confidence low and escalation enabled, escalate once
    if escalate_on_low_confidence and confidence < _get_escalation_threshold():
        escalated = True
        premium = os.environ.get("MODEL_FALLBACK", "gpt-4o")
        # recursive call but avoid infinite recursion by disabling escalation
        premium_result = call_model(project_id, agent, prompt, projects_root, escalate_on_low_confidence=False, preferred_model=premium)
        # merge results: use premium result but log that escalation happened
        premium_result["escalated"] = True
        try:
            # also record the original low-confidence call
            append_cost_log(projects_root, project_id, {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "project_id": project_id,
                "agent": agent,
                "model": model,
                "phase": None,
                "deliverable": None,
                "input_tokens": in_toks,
                "output_tokens": out_toks,
                "cost_usd": cost,
                "escalated": True,
                "duration_ms": duration_ms,
            })
        except Exception:
            pass
        return premium_result

    # Log the successful call
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "project_id": project_id,
        "agent": agent,
        "model": model,
        "phase": None,
        "deliverable": None,
        "input_tokens": in_toks,
        "output_tokens": out_toks,
        "cost_usd": cost,
        "escalated": escalated,
        "duration_ms": duration_ms,
    }
    try:
        append_cost_log(projects_root, project_id, entry)
    except Exception:
        pass

    return {
        "text": text,
        "model": model,
        "input_tokens": in_toks,
        "output_tokens": out_toks,
        "cost_usd": cost,
        "confidence": confidence,
        "escalated": escalated,
        "duration_ms": duration_ms,
    }


if __name__ == "__main__":
    # Quick manual test: will run in mock mode if keys are absent
    res = call_model("test-project", "knowledge_processor", "Extract suppliers and customers from the SOP.")
    print("Test call result:", res)
