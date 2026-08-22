from state_manager import StateManager, EvidenceRecord
from person_state import PersonState


def make_manager(person_id="p1"):
    person = PersonState(person_id=person_id)
    person.states["baseline"]["dimensions"] = {
        "motivation": 0.25,
        "attention": 0.45,
        "sadness": 0.10,
        "confidence": 0.40,
        "threat": 0.10,
    }
    return person, StateManager(person_state=person)


def evidence(source, signal, value, confidence=1.0, ref=None):
    return EvidenceRecord.create(source=source, signal=signal, value=value, confidence=confidence, ref=ref)


def test_multiple_simultaneous_states_are_independent():
    person, manager = make_manager("multi")

    sadness = manager.create_state_from_trigger(
        "sadness",
        evidence("appraisal", "sadness", {"sadness": 0.85, "coherence": 0.30}, 0.9),
        {"sadness": 0.85, "coherence": 0.30},
    )
    optimism = manager.create_state_from_trigger(
        "optimism",
        evidence("appraisal", "optimism", {"optimism": 0.75, "confidence": 0.70}, 0.8),
        {"optimism": 0.75, "confidence": 0.70},
    )
    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("self_reflection", "motivation", {"motivation": 0.82, "goal_relevance": 0.70}, 0.9),
        {"motivation": 0.82, "goal_relevance": 0.70},
    )
    focus = manager.create_state_from_trigger(
        "focus",
        evidence("plan", "focus", {"attention": 0.83, "goal_relevance": 0.88}, 0.9),
        {"attention": 0.83, "goal_relevance": 0.88},
    )

    assert len(person.states["active"]) >= 4
    assert {state.canonical_name for state in person.states["active"]} >= {"sadness", "optimism", "motivation", "focus"}
    assert sadness.intensity != optimism.intensity
    assert motivation.intensity > 0.0
    assert focus.intensity > 0.0


def test_cross_state_influence_embarrassment_to_motivation_to_focus():
    person, manager = make_manager("influence")

    embarrassment = manager.create_state_from_trigger(
        "embarrassment",
        evidence("appraisal", "embarrassment", {"threat": 0.8, "arousal": 0.8, "shame": 0.9}, 0.95),
        {"threat": 0.8, "arousal": 0.8, "shame": 0.9},
    )
    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("goal", "motivation", {"motivation": 0.30, "goal_relevance": 0.40}, 0.8),
        {"motivation": 0.30, "goal_relevance": 0.40},
    )
    focus = manager.create_state_from_trigger(
        "focus",
        evidence("goal", "focus", {"attention": 0.35, "goal_relevance": 0.45}, 0.8),
        {"attention": 0.35, "goal_relevance": 0.45},
    )

    manager.propagate_influence(embarrassment, motivation, {"motivation": 0.55, "goal_relevance": 0.25})
    manager.propagate_influence(motivation, focus, {"attention": 0.60, "goal_relevance": 0.50})

    assert motivation.dimensions["motivation"] > 0.30
    assert focus.dimensions["attention"] > 0.35
    assert embarrassment.id in motivation.influenced_by
    assert motivation.id in focus.influenced_by
    assert motivation.id in embarrassment.influences
    assert focus.id in motivation.influences
    assert 0.0 <= motivation.intensity <= 1.0
    assert 0.0 <= focus.intensity <= 1.0


def test_different_lifetimes_decay_independently():
    person, manager = make_manager("lifetimes")

    embarrassment = manager.create_state_from_trigger(
        "embarrassment",
        evidence("appraisal", "embarrassment", {"threat": 0.85, "arousal": 0.75}, 0.9),
        {"threat": 0.85, "arousal": 0.75},
    )
    sadness = manager.create_state_from_trigger(
        "sadness",
        evidence("appraisal", "sadness", {"sadness": 0.75, "coherence": 0.25}, 0.8),
        {"sadness": 0.75, "coherence": 0.25},
    )
    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("goal", "motivation", {"motivation": 0.80, "goal_relevance": 0.75}, 0.9),
        {"motivation": 0.80, "goal_relevance": 0.75},
    )
    focus = manager.create_state_from_trigger(
        "focus",
        evidence("goal", "focus", {"attention": 0.82, "goal_relevance": 0.88}, 0.9),
        {"attention": 0.82, "goal_relevance": 0.88},
    )

    embarrassment.decay_rate = 0.014
    sadness.decay_rate = 0.009
    motivation.decay_rate = 0.0008
    focus.decay_rate = 0.0008

    before = {"embarrassment": embarrassment.intensity, "sadness": sadness.intensity, "motivation": motivation.intensity, "focus": focus.intensity}
    for state in (embarrassment, sadness, motivation, focus):
        manager.decay_step(state, elapsed_seconds=1800)

    assert embarrassment.intensity < before["embarrassment"]
    assert sadness.intensity < before["sadness"]
    assert motivation.intensity > 0.10
    assert focus.intensity > 0.10
    assert len(person.states["active"]) + len(person.states["recent"]) >= 3
    assert embarrassment in person.states["active"] or embarrassment in person.states["recent"]


def test_trigger_disappearance_does_not_control_other_states():
    person, manager = make_manager("trigger")

    embarrassment = manager.create_state_from_trigger(
        "embarrassment",
        evidence("appraisal", "embarrassment", {"threat": 0.85, "arousal": 0.70, "shame": 0.90}, 0.9),
        {"threat": 0.85, "arousal": 0.70, "shame": 0.90},
    )
    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("goal", "motivation", {"motivation": 0.80, "goal_relevance": 0.75}, 0.9),
        {"motivation": 0.80, "goal_relevance": 0.75},
    )
    focus = manager.create_state_from_trigger(
        "focus",
        evidence("goal", "focus", {"attention": 0.80, "goal_relevance": 0.90}, 0.9),
        {"attention": 0.80, "goal_relevance": 0.90},
    )

    motivation.maintaining_factors = ["financial_stability_goal"]
    focus.maintaining_factors = ["financial_stability_goal"]
    manager.decay_step(embarrassment, elapsed_seconds=86400)

    assert motivation in person.states["active"] or motivation in person.states["recent"]
    assert focus in person.states["active"] or focus in person.states["recent"]
    assert motivation.intensity > 0.0
    assert focus.intensity > 0.0
    assert person.states["baseline"]["dimensions"]["motivation"] < motivation.dimensions.get("motivation", 0.0)


def test_return_toward_baseline_without_deleting_states():
    person, manager = make_manager("baseline")

    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("goal", "motivation", {"motivation": 0.95, "goal_relevance": 0.90}, 0.9),
        {"motivation": 0.95, "goal_relevance": 0.90},
    )
    focus = manager.create_state_from_trigger(
        "focus",
        evidence("goal", "focus", {"attention": 0.90, "goal_relevance": 0.92}, 0.9),
        {"attention": 0.90, "goal_relevance": 0.92},
    )

    before_motivation = motivation.dimensions["motivation"]
    before_attention = focus.dimensions["attention"]
    manager.return_toward_baseline(motivation, elapsed_seconds=300)
    manager.return_toward_baseline(focus, elapsed_seconds=300)

    assert motivation.dimensions["motivation"] < before_motivation
    assert focus.dimensions["attention"] < before_attention
    assert motivation in person.states["active"]
    assert focus in person.states["active"]


def test_reinforcement_increases_recurrence_and_reduces_decay():
    person, manager = make_manager("reinforcement")

    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("experience", "motivation", {"motivation": 0.70, "goal_relevance": 0.75}, 0.9),
        {"motivation": 0.70, "goal_relevance": 0.75},
    )

    original_decay = motivation.decay_rate
    for _ in range(3):
        manager.update_state_with_evidence(
            motivation,
            evidence("experience", "goal_pursuit", {"motivation": 0.60, "goal_relevance": 0.70}, 0.9),
        )

    manager.evaluate_persistence(motivation)

    assert motivation.recurrence_count >= 4
    assert motivation.reinforced is True
    assert motivation.decay_rate <= original_decay
    assert motivation.manual is False
    assert motivation.origin["cause_type"] == "experience" or motivation.origin["cause_type"] == "goal"


def test_coexisting_and_contradictory_state_pairs_are_valid():
    person, manager = make_manager("coexistence")

    sadness = manager.create_state_from_trigger(
        "sadness",
        evidence("reflection", "sadness", {"sadness": 0.80, "coherence": 0.20}, 0.9),
        {"sadness": 0.80, "coherence": 0.20},
    )
    optimism = manager.create_state_from_trigger(
        "optimism",
        evidence("reflection", "optimism", {"optimism": 0.80, "confidence": 0.75}, 0.9),
        {"optimism": 0.80, "confidence": 0.75},
    )
    threat = manager.create_state_from_trigger(
        "threat",
        evidence("threat", "fear", {"threat": 0.80, "arousal": 0.85}, 0.9),
        {"threat": 0.80, "arousal": 0.85},
    )
    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("goal", "motivation", {"motivation": 0.85, "goal_relevance": 0.80}, 0.9),
        {"motivation": 0.85, "goal_relevance": 0.80},
    )
    low_mood = manager.create_state_from_trigger(
        "low_mood",
        evidence("appraisal", "low_mood", {"sadness": 0.65, "motivation": 0.20}, 0.8),
        {"sadness": 0.65, "motivation": 0.20},
    )
    high_goal_motivation = manager.create_state_from_trigger(
        "high_goal_motivation",
        evidence("appraisal", "high_goal_motivation", {"motivation": 0.90, "goal_relevance": 0.85}, 0.9),
        {"motivation": 0.90, "goal_relevance": 0.85},
    )

    assert sadness in person.states["active"]
    assert optimism in person.states["active"]
    assert threat in person.states["active"]
    assert motivation in person.states["active"]
    assert low_mood in person.states["active"]
    assert high_goal_motivation in person.states["active"]


def test_temporal_provenance_and_label_derivation():
    person, manager = make_manager("provenance")

    embarrassment = manager.create_state_from_trigger(
        "embarrassment",
        evidence("appraisal", "embarrassment", {"threat": 0.80, "arousal": 0.75}, 0.9, ref="money_lack_event"),
        {"threat": 0.80, "arousal": 0.75},
    )
    embarrassment.maintaining_factors.append("financial_stability_goal")
    manager.update_state_with_evidence(
        embarrassment,
        evidence("memory", "supporting_evidence", {"shame": 0.70}, 0.8, ref="repeated_reminder"),
    )
    manager.propagate_influence(embarrassment, embarrassment, {"threat": 0.10})

    focus = manager.create_state_from_trigger(
        "focus",
        evidence("goal", "focus", {"attention": 0.88, "goal_relevance": 0.90, "motivation": 0.82}, 0.9),
        {"attention": 0.88, "goal_relevance": 0.90, "motivation": 0.82},
    )
    motivated = manager.create_state_from_trigger(
        "motivated",
        evidence("goal", "motivation", {"motivation": 0.88, "goal_relevance": 0.86}, 0.9),
        {"motivation": 0.88, "goal_relevance": 0.86},
    )
    optimistic = manager.create_state_from_trigger(
        "optimistic",
        evidence("self_reflection", "optimism", {"optimism": 0.80, "confidence": 0.85}, 0.9),
        {"optimism": 0.80, "confidence": 0.85},
    )
    sad = manager.create_state_from_trigger(
        "sad",
        evidence("reflection", "sadness", {"sadness": 0.82, "coherence": 0.20}, 0.9),
        {"sadness": 0.82, "coherence": 0.20},
    )
    defensive = manager.create_state_from_trigger(
        "defensive",
        evidence("threat", "defense", {"threat": 0.75, "arousal": 0.80}, 0.9),
        {"threat": 0.75, "arousal": 0.80},
    )

    labels = {
        label
        for state in (focus, motivated, optimistic, sad, defensive)
        for label in manager.derive_labels_from_dimensions(state)
    }

    assert embarrassment.origin["cause_ref"] == "money_lack_event"
    assert len(embarrassment.evidence) >= 2
    assert "financial_stability_goal" in embarrassment.maintaining_factors
    assert "focused" in labels or "motivated" in labels or "optimistic" in labels or "sad" in labels or "defensive" in labels


def test_state_manager_has_no_decision_logic():
    person, manager = make_manager("no_decision")

    assert not hasattr(manager, "select_action")
    assert not hasattr(manager, "rank_proposals")
    assert not hasattr(manager, "compete_tendencies")
    assert not hasattr(manager, "arbitrate")
    assert callable(manager.create_state_from_trigger)
    assert callable(manager.update_state_with_evidence)


def test_complete_money_scenario_is_deterministic():
    person, manager = make_manager("money")

    embarrassment = manager.create_state_from_trigger(
        "embarrassment",
        evidence("appraisal", "embarrassment", {"threat": 0.85, "arousal": 0.8, "shame": 0.9}, 0.96, ref="lack_of_money"),
        {"threat": 0.85, "arousal": 0.8, "shame": 0.9},
    )
    sadness = manager.create_state_from_trigger(
        "sadness",
        evidence("appraisal", "sadness", {"sadness": 0.75, "coherence": 0.25}, 0.9),
        {"sadness": 0.75, "coherence": 0.25},
    )
    optimism = manager.create_state_from_trigger(
        "optimism",
        evidence("self_reflection", "optimism", {"optimism": 0.85, "confidence": 0.8}, 0.9),
        {"optimism": 0.85, "confidence": 0.8},
    )
    motivation = manager.create_state_from_trigger(
        "motivation",
        evidence("goal", "financial_goal", {"motivation": 0.65, "goal_relevance": 0.82}, 0.9),
        {"motivation": 0.65, "goal_relevance": 0.82},
    )
    focus = manager.create_state_from_trigger(
        "focus",
        evidence("goal", "financial_focus", {"attention": 0.7, "goal_relevance": 0.88}, 0.9),
        {"attention": 0.7, "goal_relevance": 0.88},
    )

    manager.propagate_influence(embarrassment, motivation, {"motivation": 0.45, "goal_relevance": 0.35})
    manager.propagate_influence(motivation, focus, {"attention": 0.52, "goal_relevance": 0.45})

    before = motivation.intensity
    manager.decay_step(embarrassment, elapsed_seconds=86400)
    manager.decay_step(sadness, elapsed_seconds=43200)
    assert embarrassment.intensity < before
    assert sadness.intensity > 0.0
    assert motivation.intensity > 0.0
    assert focus.intensity > 0.0

    motivation.maintaining_factors.append("money_goal")
    focus.maintaining_factors.append("money_goal")
    manager.return_toward_baseline(motivation, elapsed_seconds=300)
    manager.return_toward_baseline(focus, elapsed_seconds=300)

    for _ in range(3):
        manager.update_state_with_evidence(
            motivation,
            evidence("experience", "financial_goal", {"motivation": 0.70, "goal_relevance": 0.80}, 0.9),
        )
    manager.evaluate_persistence(motivation)

    assert motivation.recurrence_count >= 4
    assert motivation.reinforced is True
    assert focus in person.states["active"] or focus in person.states["recent"]
    assert optimism in person.states["active"]
    assert sadness in person.states["active"] or sadness in person.states["recent"]


if __name__ == "__main__":
    test_multiple_simultaneous_states_are_independent()
    test_cross_state_influence_embarrassment_to_motivation_to_focus()
    test_different_lifetimes_decay_independently()
    test_trigger_disappearance_does_not_control_other_states()
    test_return_toward_baseline_without_deleting_states()
    test_reinforcement_increases_recurrence_and_reduces_decay()
    test_coexisting_and_contradictory_state_pairs_are_valid()
    test_temporal_provenance_and_label_derivation()
    test_state_manager_has_no_decision_logic()
    test_complete_money_scenario_is_deterministic()
    print("State manager scenario tests passed.")
