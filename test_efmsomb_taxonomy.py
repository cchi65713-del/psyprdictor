import pytest

from efmsomb_taxonomy import (
    BehaviorSignature,
    EmotionState,
    FeelingState,
    MoodState,
    StateOfMindState,
    validate_behavior_signature,
    validate_emotion_state,
    validate_feeling_state,
    validate_mood_state,
    validate_state_of_mind_state,
)
from person_state import PersonState


def test_valid_emotion_state_passes():
    state = EmotionState(label="anger", intensity=0.8, valence="negative", confidence=0.7)
    validated = validate_emotion_state(state)
    assert validated.label == "anger"
    assert validated.intensity == 0.8
    assert validated.valence == "negative"


def test_invalid_emotion_label_raises():
    with pytest.raises(ValueError):
        validate_emotion_state(EmotionState(label="mystery", intensity=0.5, valence="neutral"))


def test_valid_feeling_state_passes():
    state = FeelingState(quality="disrespected", texture="sharp", intensity=0.65, salience=0.9)
    validated = validate_feeling_state(state)
    assert validated.quality == "disrespected"
    assert validated.texture == "sharp"


def test_valid_mood_state_passes():
    state = MoodState(tone="tense", intensity=0.6, drift=0.2, decay=0.1)
    validated = validate_mood_state(state)
    assert validated.tone == "tense"
    assert validated.decay == 0.1


def test_valid_state_of_mind_state_passes():
    state = StateOfMindState(frame="defensive", regulation_mode="withdraw_then_counter", control_level=0.4, flexibility=0.3)
    validated = validate_state_of_mind_state(state)
    assert validated.frame == "defensive"
    assert validated.control_level == 0.4


def test_valid_behavior_signature_passes():
    state = BehaviorSignature(signature="walk_away", mode="selected", confidence=0.7, intensity=0.8)
    validated = validate_behavior_signature(state)
    assert validated.signature == "walk_away"
    assert validated.mode == "selected"


def test_invalid_float_is_rejected():
    with pytest.raises(ValueError):
        validate_mood_state(MoodState(tone="calm", intensity=1.5, drift=0.0, decay=0.0))


def test_person_state_adapter_maps_taxonomy_to_dynamic_fields():
    person = PersonState("tester")

    emotion = EmotionState(label="anger", intensity=0.8, valence="negative", confidence=0.7)
    feeling = FeelingState(quality="disrespected", texture="sharp", intensity=0.7, salience=0.8)
    mood = MoodState(tone="tense", intensity=0.6, drift=0.2, decay=0.1)
    som = StateOfMindState(frame="defensive", regulation_mode="withdraw_then_counter", control_level=0.4, flexibility=0.3)
    behavior = BehaviorSignature(signature="walk_away", mode="selected", confidence=0.8, intensity=0.7)

    result = person.apply_efmsomb_taxonomy(
        emotion_state=emotion,
        feeling_state=feeling,
        mood_state=mood,
        state_of_mind_state=som,
        behavior_state=behavior,
    )

    assert result["emotion"] == "anger"
    assert result["feeling"] == "disrespected"
    assert result["mood"] == "tense"
    assert result["behavior"] == "walk_away"
    assert result["state_emotion"][0]["label"] == "anger"
    assert result["state_appraisal"]["felt_quality"] == "disrespected"
    assert result["state_regulation"] == 0.4
    assert person.state_of_mind["frame"] == "defensive"
    assert person.behavior == "walk_away"
