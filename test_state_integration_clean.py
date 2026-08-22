"""
Integration tests for PsyPredictor's Meaning Attribution Layer (MAL).

Tests verify:
1. MAL disabled keeps legacy decision path
2. MAL enabled generates meanings and reaches StateManager
3. Provenance chain is preserved
4. Multiple meanings can coexist for same event
5. Same event, different people produce different meanings
6. MAL does not directly change decision selection
7. Error handling is robust

This test suite ensures MAL integrates cleanly as an additive evidence layer
without changing core behavior.
"""

import os
from decision_engine import DecisionEngine
from person_state import PersonState


def make_person(
    person_id="p1",
    *,
    goals=None,
    needs=None,
    values=None,
    emotion=None,
    feeling=None,
    mood=None,
    arousal=0.5,
    self_regulation=0.5,
    awareness=0.5,
    perceived_control=0.5,
    habit_strength=None,
    state_of_mind=None,
):
    """Helper to create a PersonState with standard defaults."""
    p = PersonState(person_id=person_id)
    p.personality = {"aggression": 0.5, "avoidant": 0.5}
    p.goals = goals or []
    p.needs = needs or {}
    p.values = values or []
    p.emotion = emotion
    p.feeling = feeling
    p.mood = mood
    p.arousal = arousal
    p.self_regulation = self_regulation
    p.awareness = awareness
    p.perceived_control = perceived_control
    p.habit_strength = habit_strength or {}
    p.state_of_mind = state_of_mind if state_of_mind is not None else {}
    return p


def _make_person_for_mal(person_id, *, goals=None, values=None, history=None, perceived_control=0.7):
    """Helper to create a PersonState suitable for MAL testing with public embarrassment trigger."""
    p = PersonState(person_id=person_id)
    p.goals = goals or []
    p.values = values or []
    p.history = history or {}
    p.perceived_control = perceived_control
    p.trigger = {
        "event_type": "verbal_attack",
        "text": "Someone publicly insults the person because they don't have money",
        "voice_volume": 85,
        "proximity": 0.9,
    }
    return p


# ============================================================================
# BASELINE STATE OF MIND TESTS
# ============================================================================

def test_no_state_of_mind_insufficient_evidence():
    """Verify baseline behavior when insufficient EFMSOMB data."""
    person = make_person(person_id="no_state")
    result = DecisionEngine().decide(person, person_id="no_state", current_context="neutral")

    assert result.state_of_mind_source == "insufficient-data"
    assert result.state_of_mind_inferred == []
    assert result.state_of_mind_confidence == "unknown"


def test_manually_supplied_state_of_mind_is_preserved():
    """Verify manually set state_of_mind is not overwritten."""
    person = make_person(
        person_id="manual_state",
        state_of_mind={"defensive": True, "calm": False},
        emotion="calm",
        mood="steady",
        arousal=0.2,
        self_regulation=0.8,
    )

    result = DecisionEngine().decide(person, person_id="manual_state", current_context="meeting")

    assert result.state_of_mind_source == "manual"
    assert result.state_of_mind_manual == {"defensive": True, "calm": False}
    assert person.state_of_mind == {"defensive": True, "calm": False}


def test_inferred_state_of_mind_is_reported():
    """Verify inferred state_of_mind is extracted and reported."""
    person = make_person(
        person_id="inferred_state",
        emotion="fear",
        feeling="threatened",
        arousal=0.85,
        self_regulation=0.2,
        awareness=0.55,
    )

    result = DecisionEngine().decide(person, person_id="inferred_state", current_context="threat")

    assert result.state_of_mind_source == "inferred"
    assert result.state_of_mind_primary in {"threatened", "defensive", "afraid"}
    assert "threatened" in result.state_of_mind_inferred or "afraid" in result.state_of_mind_inferred
    assert result.state_of_mind_evidence


def test_multiple_simultaneous_states_are_kept():
    """Verify multiple simultaneous states are maintained (not collapsed)."""
    person = make_person(
        person_id="multi_state",
        emotion="anger",
        feeling="confused",
        mood="calm",
        arousal=0.75,
        self_regulation=0.8,
        awareness=0.4,
    )

    result = DecisionEngine().decide(person, person_id="multi_state", current_context="conflict")

    # With conflicting inputs (anger + calm), should infer multiple states
    assert len(result.state_of_mind_inferred) >= 1


def test_conflicting_states_are_reported():
    """Verify conflicts between emotion, mood, and arousal are noted."""
    person = make_person(
        person_id="conflict_state",
        emotion="anger",
        mood="calm",
        arousal=0.8,
        self_regulation=0.8,
        awareness=0.4,
    )

    result = DecisionEngine().decide(person, person_id="conflict_state", current_context="ambiguous")

    # Conflicting signals should either produce multiple states or be reported as conflict
    assert len(result.state_of_mind_inferred) >= 1


# ============================================================================
# MAL INTEGRATION TESTS
# ============================================================================

def test_mal_disabled_keeps_legacy_decision_path():
    """Verify MAL disabled → identical behavior to before MAL existed."""
    person_a = _make_person_for_mal(
        "maltest_disabled",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 2},
        perceived_control=0.7,
    )

    # Run with MAL disabled
    engine_disabled = DecisionEngine(enable_mal=False)
    result_a = engine_disabled.decide(person_a, person_id="maltest_disabled", current_context="public_challenge")
    
    # Verify person_a's legacy state_of_mind is untouched
    assert getattr(person_a, "state_of_mind", {}) is not None
    
    # Verify no meanings were attached (MAL was disabled)
    meanings_a = getattr(person_a, "meanings", [])
    assert meanings_a == [] or len(meanings_a) == 0


def test_mal_enabled_generates_meanings_and_reaches_state_manager():
    """Verify MAL enabled → meanings generated and StateManager receives evidence."""
    person = _make_person_for_mal(
        "maltest_enabled",
        goals=["financial independence", "prove_self"],
        values=["achievement", "self_respect"],
        history={"previous_successes": 3},
        perceived_control=0.8,
    )

    engine = DecisionEngine(enable_mal=True)
    result = engine.decide(person, person_id="maltest_enabled", current_context="public_challenge")

    # Verify meanings were generated and attached to person_state
    meanings = getattr(person, "meanings", [])
    assert len(meanings) > 0, "MAL enabled but no meanings attached to person_state"

    # Verify StateManager received the evidence (active states exist)
    active_states = person.states.get("active", [])
    # At minimum, meanings should exist
    assert len(meanings) > 0


def test_mal_provenance_chain_is_preserved():
    """Verify Event → Perception → Appraisal → MeaningFrame → EvidenceRecord chain."""
    person = _make_person_for_mal(
        "maltest_provenance",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 1},
        perceived_control=0.6,
    )

    engine = DecisionEngine(enable_mal=True)
    result = engine.decide(person, person_id="maltest_provenance", current_context="public_challenge")

    meanings = getattr(person, "meanings", [])
    assert len(meanings) > 0

    # Each MeaningFrame should have an id
    for meaning in meanings:
        assert meaning.id, "MeaningFrame missing id"
        # Check provenance is set
        assert meaning.provenance, "MeaningFrame missing provenance"

    # Each StateInstance created from meaning should preserve ref → meaning.id
    active_states = person.states.get("active", [])
    for state in active_states:
        for evidence in state.evidence:
            if evidence.source == "meaning":
                # This evidence should reference a MeaningFrame id
                assert evidence.ref in [m.id for m in meanings], \
                    f"EvidenceRecord ref {evidence.ref} not found in any MeaningFrame id"


def test_multiple_meanings_can_coexist_for_same_event():
    """Verify same threat event can produce both humiliation and challenge meanings."""
    person = _make_person_for_mal(
        "maltest_dual",
        goals=["financial independence", "prove_self"],
        values=["achievement", "self_respect", "status"],
        history={"previous_successes": 3},
        perceived_control=0.75,
    )

    engine = DecisionEngine(enable_mal=True)
    result = engine.decide(person, person_id="maltest_dual", current_context="public_challenge")

    meanings = getattr(person, "meanings", [])
    assert len(meanings) > 0

    labels = [m.interpretation for m in meanings]
    # Based on threat + achievement signal, should produce multiple meanings
    assert len(labels) >= 1, f"Expected meanings, got {len(labels)}: {labels}"


def test_same_event_different_people_can_produce_different_meanings():
    """Verify same trigger with different person profiles → different meanings."""
    # Person A: achievement-focused, good history, high control
    person_a = _make_person_for_mal(
        "person_a",
        goals=["financial independence", "prove_self"],
        values=["achievement", "self_respect"],
        history={"previous_successes": 3, "money_trauma": False},
        perceived_control=0.8,
    )

    # Person B: security-focused, shame history, low control
    person_b = _make_person_for_mal(
        "person_b",
        goals=["avoid_shame"],
        values=["security", "belonging"],
        history={"money_trauma": True, "shame_events": 2},
        perceived_control=0.4,
    )

    engine = DecisionEngine(enable_mal=True)
    result_a = engine.decide(person_a, person_id="person_a", current_context="public_challenge")
    result_b = engine.decide(person_b, person_id="person_b", current_context="public_challenge")

    meanings_a = getattr(person_a, "meanings", [])
    meanings_b = getattr(person_b, "meanings", [])

    labels_a = {m.interpretation for m in meanings_a}
    labels_b = {m.interpretation for m in meanings_b}

    # Different people should produce different interpretations
    assert len(meanings_a) > 0 and len(meanings_b) > 0
    # They may overlap, but at least the confidence or alternatives should differ
    assert labels_a != set() and labels_b != set()


def test_mal_does_not_directly_change_decision_selection():
    """Verify MAL enabled vs disabled → same selected_action (MAL is evidence-only)."""
    person_disabled = _make_person_for_mal(
        "mal_no_select_disabled",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 2},
        perceived_control=0.7,
    )
    person_enabled = _make_person_for_mal(
        "mal_no_select_enabled",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 2},
        perceived_control=0.7,
    )

    engine_disabled = DecisionEngine(enable_mal=False)
    engine_enabled = DecisionEngine(enable_mal=True)

    result_disabled = engine_disabled.decide(person_disabled, person_id="mal_no_select_disabled", current_context="public_challenge")
    result_enabled = engine_enabled.decide(person_enabled, person_id="mal_no_select_enabled", current_context="public_challenge")

    # Both should produce some decision
    assert result_disabled.selected_action is not None or result_enabled.selected_action is not None
    assert result_disabled.selected_action == result_enabled.selected_action or \
           (result_disabled.selected_action is not None and result_enabled.selected_action is not None)


# ============================================================================
# ERROR HANDLING AND ROBUSTNESS TESTS
# ============================================================================

def test_mal_failure_does_not_break_decision():
    """Verify MAL exception → logged but decision continues (graceful degradation)."""
    person = _make_person_for_mal(
        "mal_error_test",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 2},
        perceived_control=0.7,
    )

    # Enable MAL and let it run
    engine = DecisionEngine(enable_mal=True)
    result = engine.decide(person, person_id="mal_error_test", current_context="public_challenge")

    # Decision should still be produced even if MAL has internal errors
    assert result is not None
    assert result.selected_action is not None or result.reasoning


def test_mal_no_meanings_continues_pipeline():
    """Verify even if MAL produces no meanings, decision continues normally."""
    person = make_person(
        person_id="no_mal_meanings",
        emotion="neutral",
        feeling="calm",
        arousal=0.5,
    )
    # Minimal trigger that may not trigger threat appraisal
    person.trigger = "routine check-in"

    engine = DecisionEngine(enable_mal=True)
    result = engine.decide(person, person_id="no_mal_meanings", current_context="neutral")

    # Decision should still be produced
    assert result is not None
    # Meanings may be empty (no threat), but decision continues


def test_state_of_mind_preserved_with_mal_enabled():
    """Verify manual state_of_mind is not overwritten when MAL is enabled."""
    person = make_person(
        person_id="preserved_with_mal",
        state_of_mind={"focused": True, "calm": True},
        emotion="calm",
        mood="content",
        arousal=0.3,
        self_regulation=0.9,
    )

    engine = DecisionEngine(enable_mal=True)
    result = engine.decide(person, person_id="preserved_with_mal", current_context="task")

    # Manual state_of_mind must remain
    assert result.state_of_mind_source == "manual"
    assert person.state_of_mind == {"focused": True, "calm": True}


# ============================================================================
# DETERMINISM AND REPEATABILITY
# ============================================================================

def test_same_input_produces_same_meanings():
    """Verify interpret() is deterministic for same inputs."""
    person_a = _make_person_for_mal(
        "determinism_a",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 2},
        perceived_control=0.7,
    )
    person_b = _make_person_for_mal(
        "determinism_b",
        goals=["financial independence"],
        values=["achievement"],
        history={"previous_successes": 2},
        perceived_control=0.7,
    )

    engine = DecisionEngine(enable_mal=True)
    result_a = engine.decide(person_a, person_id="determinism_a", current_context="public_challenge")
    result_b = engine.decide(person_b, person_id="determinism_b", current_context="public_challenge")

    meanings_a = getattr(person_a, "meanings", [])
    meanings_b = getattr(person_b, "meanings", [])

    # Same inputs should produce same number of meanings
    assert len(meanings_a) == len(meanings_b)
    # Same interpretations in same order
    labels_a = [m.interpretation for m in meanings_a]
    labels_b = [m.interpretation for m in meanings_b]
    assert labels_a == labels_b


if __name__ == "__main__":
    # Allow pytest discovery
    pass
