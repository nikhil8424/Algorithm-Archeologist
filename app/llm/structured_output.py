import json
import re
from typing import Any, Dict, Optional

def extract_json_payload(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extract structured JSON dictionary from model outputs."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        # Fallback: search for first { and last }
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None

def clean_python_code(raw_code: str) -> str:
    """Extract pristine Python code block from markdown or raw text."""
    raw_code = raw_code.strip()
    if "```python" in raw_code:
        parts = raw_code.split("```python")
        if len(parts) > 1:
            return parts[1].split("```")[0].strip()
    elif "```" in raw_code:
        parts = raw_code.split("```")
        if len(parts) > 1:
            return parts[1].strip()
    return raw_code
