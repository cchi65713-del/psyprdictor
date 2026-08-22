from person_state import PersonState


def test_person_state_has_canonical_fields():
    p = PersonState("test")
    # trait prefix
    assert hasattr(p, "trait_personality")
    # value/need canonical
    assert hasattr(p, "value_weights")
    assert hasattr(p, "need_state")
    # state splits
    assert hasattr(p, "state_appraisal")
    assert hasattr(p, "state_emotion")
    assert hasattr(p, "state_regulation")
    assert hasattr(p, "state_meta_confidence")
