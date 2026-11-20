from efmsomb_taxonomy import EmotionState, FeelingState, MoodState, StateOfMindState, BehaviorSignature
from person_state import PersonState


def test_readable_label_resolves_to_code_and_updates_legacy_field():
    p = PersonState("Test")
    res = p.apply_efmsomb_taxonomy(
        emotion_state=EmotionState(label="anger", intensity=0.5, valence="negative", confidence=0.6)
    )
    assert p.efmsomb["emotion"]["label"] == "anger"
    assert p.efmsomb["emotion"]["code"] == "E4"
    assert p.emotion == "anger"
    assert res["resolved"]["emotion"]["code"] == "E4"


def test_canonical_code_resolves_to_label():
    p = PersonState("Test2")
    res = p.apply_efmsomb_taxonomy(
        emotion_state=EmotionState(label="E4", intensity=0.7, valence="negative", confidence=0.7)
    )
    assert p.efmsomb["emotion"]["code"] == "E4"
    assert p.efmsomb["emotion"]["label"].lower() == "anger"
    assert p.emotion.lower() == "anger"
    assert res["resolved"]["emotion"]["code"] == "E4"


def test_unknown_label_is_tolerant_and_diagnosed():
    p = PersonState("Test3")
    res = p.apply_efmsomb_taxonomy(
        emotion_state=EmotionState(label="not_an_emotion", intensity=0.3, valence="neutral", confidence=0.2)
    )
    assert p.efmsomb["emotion"]["label"] == "not_an_emotion"
    assert p.efmsomb["emotion"]["code"] is None
    assert isinstance(res["warnings"], list)
    assert any("Unknown label" in w or "Invalid code" in w for w in res["warnings"]) 


def test_full_dimensions_map_and_sync():
    p = PersonState("Test4")
    res = p.apply_efmsomb_taxonomy(
        emotion_state=EmotionState(label="anger", intensity=0.82, valence="negative", confidence=0.78),
        feeling_state=FeelingState(quality="disrespected", texture="sharp", intensity=0.75, salience=0.8),
        mood_state=MoodState(tone="irritation", intensity=0.64, drift=0.25, decay=0.12),
        state_of_mind_state=StateOfMindState(frame="defensive", regulation_mode="redirect", control_level=0.46, flexibility=0.58, cognitive_bias="self-protective"),
        behavior_state=BehaviorSignature(signature="respond_immediately", mode="selected", confidence=0.9, intensity=0.8)
    )
    # Check keys present
    for dim in ("emotion", "feeling", "mood", "state_of_mind", "behavior"):
        assert dim in p.efmsomb
        assert "label" in p.efmsomb[dim]
        # code may be None for some if unmapped; ensure presence
        assert "code" in p.efmsomb[dim]
    # Legacy fields reflect labels
    assert p.emotion == p.efmsomb["emotion"]["label"]
    assert p.feeling == p.efmsomb["feeling"]["label"]
    assert p.mood == p.efmsomb["mood"]["label"]
    assert p.state_of_mind.get("frame") == p.efmsomb["state_of_mind"]["label"]
    assert p.behavior == p.efmsomb["behavior"]["label"]
    # Contract sync
    assert p.person_model.dynamic.get("efmsomb") == p.efmsomb
