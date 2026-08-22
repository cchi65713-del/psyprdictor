from perception_appraisal_expectations import (
    Appraisal,
    AppraisalFrame,
    EvidenceRecord,
    Expectations,
    ExpectationsGenerator,
    Observation,
    Perception,
    Perceptor,
    Appraiser,
)


def test_strong_threat_generates_threat_and_confrontation():
    trigger = {
        "event_type": "verbal_attack",
        "text": "You always screw things up!",
        "voice_volume": 90,
        "proximity": 0.9,
    }

    perception = Perceptor.process(trigger, person_state=None)
    assert perception.insufficient_data is False
    assert any(obs.type == "utterance" for obs in perception.observations)

    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.7})())
    labels = {frame.label for frame in appraisal.frames}
    assert "threat" in labels

    expectations = ExpectationsGenerator.update(appraisal, person_state=None)
    assert any(pred.outcome_label == "confrontation" for pred in expectations.predictions)
    assert expectations.insufficient_data is False
    assert expectations.confidence > 0.0


def test_neutral_input_produces_insufficient_appraisal_and_expectations():
    trigger = {"event_type": "neutral", "text": "please pass the salt"}
    perception = Perceptor.process(trigger, person_state=None)
    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.7})())
    expectations = ExpectationsGenerator.update(appraisal, person_state=None)

    assert appraisal.insufficient_data is True
    assert appraisal.frames == []
    assert expectations.insufficient_data is True
    assert expectations.predictions == []
    assert appraisal.confidence == 0.0
    assert expectations.confidence == 0.0


def test_threat_plus_ambiguity_are_both_present_for_mixed_signal_case():
    trigger = {
        "event_type": "mixed_signal",
        "text": "I am fine, but this is very intense.",
        "voice_volume": 80,
        "proximity": 0.8,
    }
    perception = Perceptor.process(trigger, person_state=None)
    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.2})())

    labels = {frame.label for frame in appraisal.frames}
    assert "threat" in labels
    assert "ambiguity" in labels
    assert appraisal.conflicts


def test_opportunity_plus_caution_is_supported_for_mixed_positive_signal():
    trigger = {
        "event_type": "offer",
        "text": "I can help you with that.",
        "voice_volume": 55,
        "proximity": 0.3,
    }
    perception = Perceptor.process(trigger, person_state=None)
    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.8})())

    labels = {frame.label for frame in appraisal.frames}
    assert "opportunity" in labels

    expectations = ExpectationsGenerator.update(appraisal, person_state=None)
    assert any(pred.outcome_label in {"cooperation", "acceptance"} for pred in expectations.predictions)


def test_contradictory_cues_are_recorded_as_conflicts():
    trigger = {
        "event_type": "contradictory",
        "text": "I am calm, but I am furious.",
        "voice_volume": 90,
        "proximity": 0.9,
    }
    perception = Perceptor.process(trigger, person_state=None)
    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.4})())

    assert "ambiguity" in {frame.label for frame in appraisal.frames}
    assert appraisal.conflicts


def test_insufficient_data_produces_valid_empty_result_objects():
    perception = Perceptor.process(None, person_state=None)
    assert perception.insufficient_data is True
    assert perception.observations == []
    assert perception.confidence == 0.0

    appraisal = Appraiser.evaluate(perception, person_state=None)
    assert appraisal.insufficient_data is True
    assert appraisal.frames == []
    assert appraisal.confidence == 0.0

    expectations = ExpectationsGenerator.update(appraisal, person_state=None)
    assert expectations.insufficient_data is True
    assert expectations.predictions == []
    assert expectations.confidence == 0.0


def test_manual_state_of_mind_is_preserved_by_inference_contract():
    # This module does not change state inference logic, but the design contract
    # requires manual state to remain authoritative. We validate the layer keeps
    # the result object shape and explicit provenance metadata.
    trigger = {"event_type": "manual_override", "text": "You never listen"}
    perception = Perceptor.process(trigger, person_state=None)
    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.6})())

    assert appraisal.frames
    for frame in appraisal.frames:
        assert frame.evidence
        assert all(isinstance(item, EvidenceRecord) for item in frame.evidence)


def test_evidence_and_provenance_are_present_for_generated_interpretations():
    trigger = {"event_type": "threat",
               "text": "You always ruin everything",
               "voice_volume": 85,
               "proximity": 0.8}
    perception = Perceptor.process(trigger, person_state=None)
    appraisal = Appraiser.evaluate(perception, person_state=type("State", (), {"awareness": 0.7})())

    assert appraisal.frames
    for frame in appraisal.frames:
        assert frame.evidence
        assert frame.supporting_perceptions

    expectations = ExpectationsGenerator.update(appraisal, person_state=None)
    assert expectations.predictions
    for prediction in expectations.predictions:
        assert prediction.evidence


def test_empty_appraisal_and_expectations_remain_backward_compatible():
    empty_appraisal = Appraisal(
        id="a-empty",
        timestamp="2026-01-01T00:00:00Z",
        source="trigger",
        frames=[],
        confidence=0.0,
        insufficient_data=True,
    )
    expectations = ExpectationsGenerator.update(empty_appraisal, person_state=None)
    assert expectations.insufficient_data is True
    assert expectations.predictions == []
