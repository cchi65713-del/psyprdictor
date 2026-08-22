from person_state import PersonState
from perception_appraisal_expectations import (
    Appraisal,
    AppraisalFrame,
    Expectations,
    Prediction,
)
from state_inference import StateInferenceEngine


def test_sufficient_evidence():
    p = PersonState(person_id="A")
    p.emotion = "anger"
    p.feeling = "frustrated"
    p.mood = "tense"
    p.arousal = 0.9
    p.self_regulation = 0.2
    p.awareness = 0.6

    result = StateInferenceEngine().infer(p)
    print("TEST 1: sufficient evidence")
    print(result.inferred_states, result.primary_state, result.source)
    assert "threatened" in result.inferred_states
    assert result.primary_state == "threatened"
    assert result.source == "inferred"


def test_insufficient_evidence():
    p = PersonState(person_id="B")
    # Empty/default state should not force a guess.
    result = StateInferenceEngine().infer(p)
    print("\nTEST 2: insufficient evidence")
    print(result.source, result.insufficient_data)
    assert result.source == "insufficient-data"
    assert result.insufficient_data


def test_multiple_simultaneous_states():
    p = PersonState(person_id="C")
    p.emotion = "anger"
    p.feeling = "confused"
    p.mood = "calm"
    p.arousal = 0.7
    p.self_regulation = 0.8
    p.awareness = 0.4
    p.state_of_mind = {}

    result = StateInferenceEngine().infer(p)
    print("\nTEST 3: multiple simultaneous states")
    print(result.inferred_states)
    assert len(result.inferred_states) >= 2
    assert result.primary_state is not None


def test_manual_state_preservation():
    p = PersonState(person_id="D")
    p.state_of_mind = {"defensive": True, "calm": False}

    result = StateInferenceEngine().infer(p)
    print("\nTEST 4: manual state preservation")
    print(result.manual_state, result.source)
    assert result.source == "manual"
    assert p.state_of_mind == {"defensive": True, "calm": False}


def test_inferred_state_only():
    p = PersonState(person_id="E")
    p.emotion = "fear"
    p.arousal = 0.8
    p.self_regulation = 0.3
    p.awareness = 0.5

    result = StateInferenceEngine().infer(p)
    print("\nTEST 5: inferred state")
    print(result.inferred_states, result.primary_state)
    assert "threatened" in result.inferred_states
    assert result.source == "inferred"


def test_conflicting_evidence():
    p = PersonState(person_id="F")
    p.emotion = "anger"
    p.mood = "calm"
    p.arousal = 0.8
    p.self_regulation = 0.8
    p.awareness = 0.4

    result = StateInferenceEngine().infer(p)
    print("\nTEST 6: conflicting evidence")
    print(result.inferred_states)
    print(result.conflicts)
    assert result.conflicts or len(result.inferred_states) > 1


def test_explainability_and_evidence():
    p = PersonState(person_id="G")
    p.emotion = "fear"
    p.arousal = 0.8
    p.self_regulation = 0.3
    p.awareness = 0.6

    result = StateInferenceEngine().infer(p)
    print("\nTEST 7: explainability and evidence")
    print(result.evidence)
    assert result.evidence
    assert all("reason" in item for item in result.evidence)


def test_no_action_selection():
    p = PersonState(person_id="H")
    p.emotion = "anger"
    p.arousal = 0.9
    p.self_regulation = 0.2

    result = StateInferenceEngine().infer(p)
    print("\nTEST 8: no action selection")
    print(result.selected_action)
    assert result.selected_action is None


def test_threat_appraisal_supports_threatened_defensive_state():
    p = PersonState(person_id="I")
    p.awareness = 0.5
    p.arousal = 0.8
    p.self_regulation = 0.3
    p.appraisal = Appraisal(
        id="a1",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        frames=[
            AppraisalFrame(
                id="f1",
                label="threat",
                dimension_scores={"valence": -0.9, "goal_relevance": 0.8, "controllability": -0.5},
                supporting_perceptions=["p1"],
                evidence=[],
                confidence=0.8,
            )
        ],
        confidence=0.8,
        insufficient_data=False,
    )

    result = StateInferenceEngine().infer(p)
    assert "threatened" in result.inferred_states or "defensive" in result.inferred_states
    assert any(item.get("source") == "appraisal" for item in result.evidence)


def test_ambiguity_appraisal_supports_confused_inference():
    p = PersonState(person_id="J")
    p.awareness = 0.2
    p.arousal = 0.5
    p.self_regulation = 0.6
    p.appraisal = Appraisal(
        id="a2",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        frames=[
            AppraisalFrame(
                id="f2",
                label="ambiguity",
                dimension_scores={"valence": 0.0, "ambiguity": 0.9},
                supporting_perceptions=["p2"],
                evidence=[],
                confidence=0.7,
            )
        ],
        confidence=0.7,
        insufficient_data=False,
    )

    result = StateInferenceEngine().infer(p)
    assert "confused" in result.inferred_states
    assert any("ambiguity" in str(item.get("appraisal_labels", [])) for item in result.evidence)


def test_opportunity_appraisal_supports_confident_inference():
    p = PersonState(person_id="K")
    p.awareness = 0.8
    p.arousal = 0.4
    p.self_regulation = 0.75
    p.appraisal = Appraisal(
        id="a3",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        frames=[
            AppraisalFrame(
                id="f3",
                label="opportunity",
                dimension_scores={"valence": 0.8, "goal_relevance": 0.7, "controllability": 0.6},
                supporting_perceptions=["p3"],
                evidence=[],
                confidence=0.8,
            )
        ],
        confidence=0.8,
        insufficient_data=False,
    )

    result = StateInferenceEngine().infer(p)
    assert "confident" in result.inferred_states or "calm" in result.inferred_states
    assert any(item.get("source") == "appraisal" for item in result.evidence)


def test_expectations_add_evidence_for_state_inference():
    p = PersonState(person_id="L")
    p.mood = "tense"
    p.arousal = 0.7
    p.self_regulation = 0.4
    p.expectations = Expectations(
        id="e1",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        predictions=[
            Prediction(
                outcome_label="confrontation",
                probability=0.8,
                supporting_appraisals=["a4"],
                evidence=[],
            ),
            Prediction(
                outcome_label="clarify",
                probability=0.2,
                supporting_appraisals=["a4"],
                evidence=[],
            ),
        ],
        confidence=0.8,
        insufficient_data=False,
    )

    result = StateInferenceEngine().infer(p)
    assert "threatened" in result.inferred_states or "defensive" in result.inferred_states
    assert any(item.get("source") == "expectation" for item in result.evidence)


def test_multiple_appraisal_expectation_signals_can_coexist():
    p = PersonState(person_id="M")
    p.emotion = "fear"
    p.arousal = 0.8
    p.self_regulation = 0.5
    p.awareness = 0.4
    p.appraisal = Appraisal(
        id="a5",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        frames=[
            AppraisalFrame(id="f5", label="threat", dimension_scores={"valence": -0.8}, supporting_perceptions=["p5"], evidence=[], confidence=0.8),
            AppraisalFrame(id="f6", label="ambiguity", dimension_scores={"ambiguity": 0.8}, supporting_perceptions=["p6"], evidence=[], confidence=0.7),
        ],
        confidence=0.75,
        insufficient_data=False,
    )
    p.expectations = Expectations(
        id="e2",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        predictions=[
            Prediction(outcome_label="confrontation", probability=0.7, supporting_appraisals=["f5"], evidence=[]),
            Prediction(outcome_label="clarify", probability=0.3, supporting_appraisals=["f6"], evidence=[]),
        ],
        confidence=0.7,
        insufficient_data=False,
    )

    result = StateInferenceEngine().infer(p)
    assert "threatened" in result.inferred_states
    assert "confused" in result.inferred_states
    assert len(result.inferred_states) >= 2


def test_contradictory_appraisal_and_expectation_evidence_is_explainable():
    p = PersonState(person_id="N")
    p.awareness = 0.7
    p.arousal = 0.5
    p.self_regulation = 0.7
    p.appraisal = Appraisal(
        id="a6",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        frames=[
            AppraisalFrame(id="f7", label="threat", dimension_scores={"valence": -0.8}, supporting_perceptions=["p7"], evidence=[], confidence=0.8),
            AppraisalFrame(id="f8", label="opportunity", dimension_scores={"valence": 0.8}, supporting_perceptions=["p8"], evidence=[], confidence=0.8),
        ],
        confidence=0.8,
        insufficient_data=False,
    )
    p.expectations = Expectations(
        id="e3",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        predictions=[
            Prediction(outcome_label="confrontation", probability=0.6, supporting_appraisals=["f7"], evidence=[]),
            Prediction(outcome_label="cooperation", probability=0.4, supporting_appraisals=["f8"], evidence=[]),
        ],
        confidence=0.6,
        insufficient_data=False,
    )

    result = StateInferenceEngine().infer(p)
    assert result.conflicts or len(result.inferred_states) >= 2
    assert any(item.get("source") in {"appraisal", "expectation"} for item in result.evidence)


if __name__ == "__main__":
    test_sufficient_evidence()
    test_insufficient_evidence()
    test_multiple_simultaneous_states()
    test_manual_state_preservation()
    test_inferred_state_only()
    test_conflicting_evidence()
    test_explainability_and_evidence()
    test_no_action_selection()
    test_threat_appraisal_supports_threatened_defensive_state()
    test_ambiguity_appraisal_supports_confused_inference()
    test_opportunity_appraisal_supports_confident_inference()
    test_expectations_add_evidence_for_state_inference()
    test_multiple_appraisal_expectation_signals_can_coexist()
    test_contradictory_appraisal_and_expectation_evidence_is_explainable()
    print("\nAll state inference tests passed.")
