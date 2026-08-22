from person_state import PersonState
from efmsomb_taxonomy import (
    BehaviorSignature,
    EmotionState,
    FeelingState,
    MoodState,
    StateOfMindState,
)


def test_conflict_scenario_maps_to_dynamic_state():
    person = PersonState("scenario_conflict")

    emotion = EmotionState(label="anger", intensity=0.82, valence="negative", confidence=0.72)
    feeling = FeelingState(quality="disrespected", texture="sharp", intensity=0.74, salience=0.8)
    mood = MoodState(tone="tense", intensity=0.58, drift=0.2, decay=0.1)
    state_of_mind = StateOfMindState(
        frame="defensive",
        regulation_mode="withdraw_then_counter",
        cognitive_bias="threat_focus",
        control_level=0.42,
        flexibility=0.3,
    )
    behavior = BehaviorSignature(signature="walk_away", mode="selected", confidence=0.8, intensity=0.7)

    result = person.apply_efmsomb_taxonomy(
        emotion_state=emotion,
        feeling_state=feeling,
        mood_state=mood,
        state_of_mind_state=state_of_mind,
        behavior_state=behavior,
    )

    assert result["emotion"] == "anger"
    assert result["feeling"] == "disrespected"
    assert result["mood"] == "tense"
    assert result["behavior"] == "walk_away"

    assert result["state_emotion"][0]["label"] == "anger"
    assert result["state_appraisal"]["felt_quality"] == "disrespected"
    assert result["state_regulation"] == 0.42
    assert person.state_of_mind["frame"] == "defensive"
    assert person.behavior == "walk_away"

    # The scenario should leave the decision layer untouched while updating state.
    assert person.action_tendencies.get("behavior_signature") == "walk_away"
