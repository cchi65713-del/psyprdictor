"""Canonical EFMSOMB ID <-> label registry.

Provides a single authoritative resolver between codes like `E4`, `F3`,
`M2` and their human-readable labels from the knowledge base. Also supports
basic lookup by label (case-insensitive) back to the canonical code.

The registry is intentionally lightweight and non-invasive: callers can use
`resolve_code(code)` to get structured info about a code, or
`label_to_code(label, category=None)` to find the canonical code for a label.
"""
from typing import Dict, List, Optional, Tuple

from knowledge import EMOTIONS, FEELINGS, MOODS, STATE_OF_MIND, BEHAVIORS


# Category -> list from knowledge.py
CATEGORIES: Dict[str, List[str]] = {
    "E": EMOTIONS,
    "F": FEELINGS,
    "M": MOODS,
    "S": STATE_OF_MIND,
    "B": BEHAVIORS,
}


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _split_code(code: str) -> Tuple[str, List[str]]:
    """Split a possibly nested code like 'E4.2.1' into ('E4', ['2','1'])."""
    if not code or len(code) < 2:
        raise ValueError("Invalid code")
    parts = code.split(".")
    base = parts[0]
    nested = parts[1:]
    return base.upper(), nested


def resolve_code(code: str) -> Dict[str, Optional[object]]:
    """Resolve a code like `E4` or `E4.2.1` to structured info.

    Returns a dict with keys: `category`, `base_code`, `nested`, `label`,
    `base_index` (0-based) and `canonical_code` (same as base_code).
    Raises KeyError for unknown mappings.
    """
    base_code, nested = _split_code(code)
    category = base_code[0]
    number = base_code[1:]
    if category not in CATEGORIES:
        raise KeyError(f"Unknown category: {category}")
    try:
        idx = int(number) - 1
    except Exception:
        raise KeyError(f"Invalid numeric part in code: {base_code}")

    options = CATEGORIES[category]
    if idx < 0 or idx >= len(options):
        raise KeyError(f"Code out of range: {base_code}")

    label = options[idx]
    return {
        "category": category,
        "base_code": base_code,
        "nested": nested,
        "label": label,
        "base_index": idx,
        "canonical_code": base_code,
    }


def code_to_label(code: str) -> str:
    """Return the human-readable label for a code like 'E4' or 'S5.1'."""
    info = resolve_code(code)
    return info["label"]


def label_to_code(label: str, category: Optional[str] = None) -> Optional[str]:
    """Find the canonical base code for a given label.

    If `category` is provided it must be one of 'E','F','M','S','B' and the
    lookup is limited to that list. When the label is ambiguous across
    categories, return None instead of silently choosing one.
    """
    target = _normalize(label)
    categories = [category.upper()] if category and category.upper() in CATEGORIES else list(CATEGORIES.keys())
    matches = []
    for cat in categories:
        for i, lab in enumerate(CATEGORIES[cat]):
            if _normalize(lab) == target:
                matches.append((cat, i + 1))
    if not matches:
        return None
    if len(matches) == 1:
        cat, idx = matches[0]
        return f"{cat}{idx}"
    return None


def all_codes_for_category(category: str) -> List[str]:
    category = category.upper()
    if category not in CATEGORIES:
        raise KeyError(f"Unknown category: {category}")
    return [f"{category}{i+1}" for i in range(len(CATEGORIES[category]))]


__all__ = [
    "resolve_code",
    "code_to_label",
    "label_to_code",
    "all_codes_for_category",
    "CATEGORIES",
]
