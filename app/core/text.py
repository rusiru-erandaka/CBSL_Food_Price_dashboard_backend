from __future__ import annotations

import re


def humanize_label(value: str) -> str:
    cleaned = re.sub(r"[_\s]+", " ", value).strip()
    if not cleaned:
        return cleaned
    return cleaned.title()


def normalize_key(value: str) -> str:
    return re.sub(r"[_\s]+", " ", value).strip().lower()
