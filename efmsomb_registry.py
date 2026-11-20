"""Canonical EFMSOMB ID <-> label registry.

Provides a single authoritative resolver between codes like `E4`, `F3`,
`M2` and their human-readable labels from the knowledge base. Also supports
basic lookup by label (case-insensitive) back to the canonical code.

The registry is intentionally lightweight and non-invasive: callers can use
`resolve_code(code)` to get structured info about a code, or
`label_to_code(label, category=None)` to find the canonical code for a label.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from knowledge import EMOTIONS, FEELINGS, LEGACY_FEELINGS, MOODS, STATE_OF_MIND, BEHAVIORS


@dataclass(frozen=True)
class EFMSOMBIdentityRecord:
    """Minimal canonical identity record for EFMSOMB IDs.

    This is intentionally a schema-only structure for Stage 1. It establishes the
    immutable canonical identity contract without implementing lifecycle mutation,
    alias mutation, registry migration, or historical ledger behavior.
    """
    canonical_id: str
    category: str
    current_label: str
    aliases: List[str] = field(default_factory=list)
    status: str = "active"
    deprecated_since: Optional[str] = None
    retired_since: Optional[str] = None
    replacement_of: Optional[List[str]] = None
    metadata: Dict[str, object] = field(default_factory=dict)


# Category -> list from knowledge.py
CATEGORIES: Dict[str, List[str]] = {
    "E": EMOTIONS,
    "F": FEELINGS,
    "M": MOODS,
    "S": STATE_OF_MIND,
    "B": BEHAVIORS,
}

F_CODE_TO_LABEL = {
    "F1": "Tension",
    "F2": "Constriction",
    "F3": "Heaviness",
    "F4": "Affective Numbing",
    "F5": "Warmth/Expansion",
    "F6": "Felt-pull / Subjective Imperative",
    "F7": "Apprehensive Foreboding",
    "F8": "Agitation/Restlessness",
    "F9": "Emptiness/Hollowing",
    "F10": "Pressure/Surging-Heat",
    "F12": "Depersonalization-style Detachment",
}

F_LABEL_TO_CODE = {label.lower(): code for code, label in F_CODE_TO_LABEL.items()}


def _build_identity_registry() -> Dict[str, EFMSOMBIdentityRecord]:
    """Build the explicit canonical identity registry from the current public vocabulary."""
    registry: Dict[str, EFMSOMBIdentityRecord] = {}

    for category, labels in CATEGORIES.items():
        if category == "F":
            continue
        for index, label in enumerate(labels, start=1):
            code = f"{category}{index}"
            registry[code] = EFMSOMBIdentityRecord(
                canonical_id=code,
                category=category,
                current_label=label,
                aliases=[],
                status="active",
                deprecated_since=None,
                retired_since=None,
                replacement_of=[],
                metadata={"source": "knowledge.py", "index": index - 1},
            )

    for code, label in F_CODE_TO_LABEL.items():
        registry[code] = EFMSOMBIdentityRecord(
            canonical_id=code,
            category="F",
            current_label=label,
            aliases=[],
            status="active",
            deprecated_since=None,
            retired_since=None,
            replacement_of=[],
            metadata={"source": "explicit_f_mapping", "index": int(code[1:]) - 1 if code[1:].isdigit() else -1},
        )

    return registry


IDENTITY_REGISTRY: Dict[str, EFMSOMBIdentityRecord] = _build_identity_registry()


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
    `base_index` (0-based), `canonical_id`, `current_label`, and `status`.
    Raises KeyError for unknown mappings.
    """
    base_code, nested = _split_code(code)
    category = base_code[0].upper()
    number = base_code[1:]
    if category not in CATEGORIES:
        raise KeyError(f"Unknown category: {category}")

    if not number.isdigit():
        raise KeyError(f"Invalid numeric part in code: {base_code}")

    if category == "F":
        if base_code == "F11":
            raise KeyError("F11 is reserved for S and is not a valid F node")
        record = IDENTITY_REGISTRY.get(base_code)
        if record is None:
            raise KeyError(f"Code out of range: {base_code}")
        base_index = int(number) - 1 if number.isdigit() else -1
        result = {
            "category": category,
            "base_code": base_code,
            "nested": nested,
            "label": record.current_label,
            "base_index": base_index,
            "canonical_code": base_code,
            "canonical_id": base_code,
            "current_label": record.current_label,
            "status": record.status,
        }
        return result

    if not number.isdigit():
        raise KeyError(f"Invalid numeric part in code: {base_code}")

    idx = int(number) - 1
    if idx < 0 or idx >= len(CATEGORIES[category]):
        raise KeyError(f"Code out of range: {base_code}")

    record = IDENTITY_REGISTRY.get(base_code)
    if record is None:
        raise KeyError(f"Code out of range: {base_code}")

    return {
        "category": category,
        "base_code": base_code,
        "nested": nested,
        "label": record.current_label,
        "base_index": idx,
        "canonical_code": base_code,
        "canonical_id": base_code,
        "current_label": record.current_label,
        "status": record.status,
    }


def code_to_label(code: str) -> str:
    """Return the human-readable label for a code like 'E4' or 'S5.1'."""
    info = resolve_code(code)
    return info["current_label"] if "current_label" in info else info["label"]


def label_to_code(label: str, category: Optional[str] = None) -> Optional[str]:
    """Find the canonical base code for a given label.

    If `category` is provided it must be one of 'E','F','M','S','B' and the
    lookup is limited to that list. When the label is ambiguous across
    categories, return None instead of silently choosing one.
    """
    target = _normalize(label)

    if category is not None:
        category = category.upper()
        if category not in CATEGORIES:
            return None
        categories = [category]
    else:
        categories = list(CATEGORIES.keys())

    matches = []
    for cat in categories:
        for code, record in IDENTITY_REGISTRY.items():
            if code.startswith(cat) and _normalize(record.current_label) == target:
                matches.append(code)

    # Keep explicit compatibility behavior for legacy recognized labels that are not
    # in the canonical identity registry.
    if not matches and category == "F":
        if target in {_normalize(v) for v in LEGACY_FEELINGS}:
            return None

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return None


def all_codes_for_category(category: str) -> List[str]:
    category = category.upper()
    if category not in CATEGORIES:
        raise KeyError(f"Unknown category: {category}")
    codes = [code for code in IDENTITY_REGISTRY if code.startswith(category)]
    return sorted(codes, key=lambda code: int(code[1:]) if code[1:].isdigit() else 0)


__all__ = [
    "EFMSOMBIdentityRecord",
    "resolve_code",
    "code_to_label",
    "label_to_code",
    "all_codes_for_category",
    "CATEGORIES",
]
