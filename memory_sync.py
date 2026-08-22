"""
Utilities to synchronize beliefs/values and simple memory fields
between SystemMemory and PersonState.

This module provides two small helpers:
- `sync_system_to_person(system_memory, person_state, person_id)` — merge
  system-level memory into the runtime `PersonState` for a person.
- `sync_person_to_system(person_state, system_memory, person_id)` — push
  short-term updates from `PersonState` back into `SystemMemory`.

The functions are intentionally conservative and idempotent: they merge
lists without duplicating entries and avoid clobbering complex structures.
"""
from typing import Any


def _ensure_list(container: dict, key: str):
    if key not in container or not isinstance(container[key], list):
        container[key] = []


def _merge_list(dest: list, src: list):
    if not src:
        return dest
    for it in src:
        if it not in dest:
            dest.append(it)
    return dest


def sync_system_to_person(system_memory: Any, person_state: Any, person_id: str):
    """Merge simple memory fields from SystemMemory into `person_state`.

    - Adds beliefs into `person_state.beliefs['explicit']` (creates key if missing)
    - Merges values into `person_state.values` (list)
    - Copies environment/history/relationships/rules into similarly named
      attributes on `person_state` when present.
    """
    # Beliefs
    beliefs = system_memory.beliefs.get(person_id, []) if hasattr(system_memory, "beliefs") else []
    if isinstance(person_state.beliefs, dict):
        _ensure_list(person_state.beliefs, "explicit")
        _merge_list(person_state.beliefs["explicit"], beliefs)
    else:
        # fallback: set to list
        person_state.beliefs = {"explicit": list(beliefs)}

    # Values: prefer canonical `value_weights` list if present, else `values`
    values = system_memory.values.get(person_id, []) if hasattr(system_memory, "values") else []
    if hasattr(person_state, "value_weights") and isinstance(person_state.value_weights, list):
        _merge_list(person_state.value_weights, values)
    else:
        if not isinstance(person_state.values, list):
            person_state.values = []
        _merge_list(person_state.values, values)

    # Environment
    if hasattr(system_memory, "environment"):
        env = system_memory.environment.get(person_id)
        if env is not None:
            # only set if person_state.environment is empty or different
            if not person_state.environment:
                person_state.environment = env

    # History / relationships / rules — merge where sensible
    if hasattr(system_memory, "history"):
        hist = system_memory.history.get(person_id, [])
        if hist:
            if not hasattr(person_state, "history") or person_state.history is None:
                person_state.history = {}
            # store under a simple key
            person_state.history.setdefault("system_events", [])
            _merge_list(person_state.history["system_events"], hist)

    if hasattr(system_memory, "relationships"):
        rel = system_memory.relationships.get(person_id, [])
        if rel:
            if not hasattr(person_state, "identity") or person_state.identity is None:
                person_state.identity = {}
            person_state.identity.setdefault("relationships", [])
            _merge_list(person_state.identity["relationships"], rel)

    if hasattr(system_memory, "rules"):
        rules = system_memory.rules.get(person_id, [])
        if rules:
            if not hasattr(person_state, "preferences") or person_state.preferences is None:
                person_state.preferences = {}
            person_state.preferences.setdefault("rules", [])
            _merge_list(person_state.preferences["rules"], rules)


def sync_person_to_system(person_state: Any, system_memory: Any, person_id: str):
    """Push simple lists from `person_state` into `system_memory`.

    This does minimal merging and avoids creating duplicate entries.
    """
    # Ensure underlying dicts exist
    if not hasattr(system_memory, "beliefs"):
        system_memory.beliefs = {}
    if not hasattr(system_memory, "values"):
        system_memory.values = {}

    # Values: prefer canonical `value_weights` list if present
    if hasattr(person_state, "value_weights") and isinstance(person_state.value_weights, list):
        src_values = person_state.value_weights
    else:
        src_values = person_state.values if isinstance(person_state.values, list) else []
    dest_values = system_memory.values.get(person_id, [])
    for v in src_values:
        if v not in dest_values:
            dest_values.append(v)
    system_memory.values[person_id] = dest_values

    # Beliefs (from person_state.beliefs['explicit'] when available)
    src_beliefs = []
    if isinstance(person_state.beliefs, dict):
        src_beliefs = person_state.beliefs.get("explicit", [])
    elif isinstance(person_state.beliefs, list):
        src_beliefs = person_state.beliefs

    dest_beliefs = system_memory.beliefs.get(person_id, [])
    for b in src_beliefs:
        if b not in dest_beliefs:
            dest_beliefs.append(b)
    system_memory.beliefs[person_id] = dest_beliefs

    # Environment
    try:
        if hasattr(person_state, "environment") and person_state.environment:
            system_memory.environment[person_id] = person_state.environment
    except Exception:
        pass

    # History/relationships/rules — push simple additions if present
    try:
        if hasattr(person_state, "history") and isinstance(person_state.history, dict):
            events = person_state.history.get("system_events", [])
            if events:
                system_memory.history.setdefault(person_id, [])
                _merge_list(system_memory.history[person_id], events)
    except Exception:
        pass

    try:
        if hasattr(person_state, "identity") and isinstance(person_state.identity, dict):
            rels = person_state.identity.get("relationships", [])
            if rels:
                system_memory.relationships.setdefault(person_id, [])
                _merge_list(system_memory.relationships[person_id], rels)
    except Exception:
        pass

    try:
        prefs = getattr(person_state, "preferences", {}) or {}
        rules = prefs.get("rules", []) if isinstance(prefs, dict) else []
        if rules:
            system_memory.rules.setdefault(person_id, [])
            _merge_list(system_memory.rules[person_id], rules)
    except Exception:
        pass
