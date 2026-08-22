"""
Habit formation utilities for PsyPredictor.

Compute and update `PersonState.habit_strength` from Memory and PatternLearner traces.

Algorithm (heuristic):
- For each active pattern (or provided pattern_id):
  - Gather experiences from Memory that match the pattern.
  - Map experience outcomes to actions using a provided map.
  - Compute supporting weight per action using Experience.get_weight()
  - Compute contradictory weight (sum weights of other actions).
  - Consistency = support_weight / total_weight
  - New habit strength = EMA(prev_strength, support_norm) with separate learning rates
    for strengthening and weakening; include recency via Experience.get_recency_weight.
- Keep habit strength in `PersonState.habit_strength[pattern_id] = { action: strength }
- Diagnostic prints for each updated habit entry.

This module intentionally keeps habit strength separate from outcome probability.
"""
from typing import Dict, List, Optional


def _pattern_habit_signal(support_norm: float, repetition_count: int, contradictory_count: int, total_experiences: int) -> float:
    """Compute the growth/decay signal for a pattern-based habit.

    The signal is intentionally simple and explicit:
    - repeated experiences raise the signal
    - contradictory evidence reduces the signal
    - a pattern with stable support grows faster than an inconsistent one
    """
    if total_experiences <= 0:
        return 0.0

    repetition_bonus = 1.0 + min(max(repetition_count - 1, 0), 10) * 0.10
    contradiction_ratio = contradictory_count / total_experiences

    if support_norm >= 0.5:
        # Keep single-event reinforcement real but bounded; do not let a lone
        # positive outcome create a near-max habit signal on its own.
        signal = support_norm * repetition_bonus * (0.6 + support_norm)
    else:
        signal = support_norm * repetition_bonus * 0.35

    return max(0.0, signal * (1.0 - contradiction_ratio * 0.5))


def default_outcome_to_action_map():
    # Default mapping used by main.py; external callers can pass a different map
    return {
        "B1": "RespondImmediately",
        "B4": "WalkAway",
        # add more mappings if project grows
    }


def update_habit_strengths(
    person_state,
    memory,
    pattern_learner=None,
    pattern_id: Optional[str] = None,
    outcome_to_action_map: Optional[Dict[str, str]] = None,
    positive_lr: float = 0.2,
    negative_lr: float = 0.1,
    min_strength: float = 0.0,
    max_strength: float = 5.0,
):
    """Update `person_state.habit_strength` for the given pattern(s).

    If `pattern_id` is None, update for all `person_state.active_patterns`.

    Returns a diagnostics dict for prints.
    """

    if outcome_to_action_map is None:
        outcome_to_action_map = default_outcome_to_action_map()

    diagnostics = {}

    # Determine which patterns to update
    patterns = []
    if pattern_id:
        patterns = [pattern_id]
    else:
        patterns = getattr(person_state, "active_patterns", []) or []

    for pid in patterns:
        experiences = memory.get_by_pattern_id(pid)

        # Compute support weights per action
        support_weights = {}
        total_weight = 0.0

        for exp in experiences:
            act = outcome_to_action_map.get(exp.outcome)
            if not act:
                continue
            w = exp.get_weight()
            support_weights[act] = support_weights.get(act, 0.0) + w
            total_weight += w

        # If there are no experiences, skip
        if total_weight <= 0:
            continue

        # Determine the top action by support
        sorted_actions = sorted(support_weights.items(), key=lambda t: t[1], reverse=True)

        # Prepare habit_strength entry
        habit_entry = person_state.habit_strength.get(pid, {}) if isinstance(person_state.habit_strength, dict) else {}

        diagnostics[pid] = []

        for action, support in sorted_actions:
            prev_strength = habit_entry.get(action, 0.0)

            # Normalized support in [0,1]
            support_norm = support / total_weight

            # Diagnostics: count supporting and contradictory experiences
            supporting_count = sum(1 for e in experiences if outcome_to_action_map.get(e.outcome) == action)
            contradictory_count = len(experiences) - supporting_count
            pattern_signal = _pattern_habit_signal(
                support_norm=support_norm,
                repetition_count=len(experiences),
                contradictory_count=contradictory_count,
                total_experiences=len(experiences),
            )

            # Strengthen or weaken depending on relative support and repeated-pattern evidence.
            if support_norm >= 0.5:
                new_strength = prev_strength * (1 - positive_lr) + pattern_signal * positive_lr
            else:
                new_strength = prev_strength * (1 - negative_lr) + pattern_signal * negative_lr

            # Clip
            if new_strength < min_strength:
                new_strength = min_strength
            if new_strength > max_strength:
                new_strength = max_strength

            # Save
            habit_entry[action] = new_strength

            diagnostics[pid].append({
                "action": action,
                "previous_strength": prev_strength,
                "new_strength": new_strength,
                "support_weight": support,
                "supporting_count": supporting_count,
                "contradictory_count": contradictory_count,
                "pattern_signal": pattern_signal,
                "repetition_count": len(experiences),
            })

        # Decay actions not present in current supports slightly
        for existing_action in list(habit_entry.keys()):
            if existing_action not in support_weights:
                prev = habit_entry[existing_action]
                decayed = prev * (1 - negative_lr)
                if decayed < min_strength:
                    decayed = min_strength
                habit_entry[existing_action] = decayed
                diagnostics[pid].append({
                    "action": existing_action,
                    "previous_strength": prev,
                    "new_strength": decayed,
                    "support_weight": 0.0,
                    "supporting_count": 0,
                    "contradictory_count": len(experiences),
                })

        # Write back
        if isinstance(person_state.habit_strength, dict):
            person_state.habit_strength[pid] = habit_entry

    # Print diagnostics in a human-friendly format
    for pid, entries in diagnostics.items():
        print(f"\n--- Habit update for pattern: {pid} ---")
        for e in entries:
            print(f"Action: {e['action']}")
            print(f"  Previous strength: {e['previous_strength']:.3f}")
            print(f"  New strength:      {e['new_strength']:.3f}")
            print(f"  Supporting weight: {e['support_weight']:.3f}")
            print(f"  Supporting exps:   {e['supporting_count']}")
            print(f"  Contradictory exps:{e['contradictory_count']}")
            # Habitual proposal generated
            print(f"  Habitual proposal (from strength): {e['action']} -> {e['new_strength']:.3f}")

    return diagnostics
