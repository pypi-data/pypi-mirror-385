from typing import Dict, Optional


def headers(
    api_key: Optional[str], extra: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    h = {"content-type": "application/json", "maniac-apikey": api_key or ""}
    if api_key:
        h["authorization"] = f"Bearer {api_key}"
    if extra:
        h.update(extra)
    return h
