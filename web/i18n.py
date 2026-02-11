"""Lightweight i18n helper for the web UI.

Loads JSON translation files and provides a t() function
that resolves dot-separated keys for the active language.
"""

import json
from pathlib import Path
from typing import Dict

TRANSLATIONS_DIR = Path(__file__).parent / "translations"
SUPPORTED_LANGUAGES = ["en", "nl"]
DEFAULT_LANGUAGE = "en"

_cache: Dict[str, Dict[str, str]] = {}


def load_translations(lang: str) -> Dict[str, str]:
    """Load and cache translations for a language."""
    if lang in _cache:
        return _cache[lang]

    file_path = TRANSLATIONS_DIR / f"{lang}.json"
    if not file_path.exists():
        lang = DEFAULT_LANGUAGE
        file_path = TRANSLATIONS_DIR / f"{lang}.json"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _cache[lang] = data
    return data


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """Translate a key for the given language.

    Supports placeholder substitution via kwargs:
        t("api.project_not_found", lang="en", project_id="test")
        -> "Project 'test' not found"
    """
    translations = load_translations(lang)
    text = translations.get(key)

    # Fall back to English if key not found in target language
    if text is None and lang != DEFAULT_LANGUAGE:
        en_translations = load_translations(DEFAULT_LANGUAGE)
        text = en_translations.get(key)

    # Fall back to key itself if still not found
    if text is None:
        text = key

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text


def get_language_from_session(session) -> str:
    """Extract language preference from Flask session."""
    lang = session.get("lang", DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    return lang
