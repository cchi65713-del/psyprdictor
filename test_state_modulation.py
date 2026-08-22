from competition import BehavioralTendency
from state_modulation import StateModulator


def make_person_state(state_of_mind=None, emotion=None, feeling=None, mood=None):
    class PersonState: pass
    p = PersonState()
    p.state_of_mind = state_of_mind or {}
    p.emotion = emotion
    p.feeling = feeling
    p.mood = mood
    return p


def test_neutral_state():
    modulator = StateModulator()
    tendency = BehavioralTendency(
        action="WalkAway",
        raw_strength=45.0,
        source="goal_directed",
        confidence_in_proposal=0.8,
    )
    tendency.normalized_strength = 0.45

    person = make_person_state(state_of_mind={}, emotion="calm", feeling="steady", mood="neutral")
    modified = modulator.modulate(tendency, person)

    print("TEST 1: Neutral state")
    print(modified.state_modulation_factor)
    assert modified.state_modulation_factor == 1.0
    assert modified.post_state_strength == 0.45


def test_recognized_state_modifies_tendency():
    modulator = StateModulator()
    tendency = BehavioralTendency(
        action="RespondImmediately",
        raw_strength=70.0,
        source="reactive",
        confidence_in_proposal=0.9,
    )
    tendency.normalized_strength = 0.70

    person = make_person_state(state_of_mind={"defensive": True}, emotion="anger", feeling="threatened", mood="tense")
    modified = modulator.modulate(tendency, person)

    print("\nTEST 2: Recognized state modifies tendency")
    print(modified.state_modulation_factor)
    print(modified.post_state_strength)
    assert modified.state_modulation_factor > 1.0
    assert modified.post_state_strength > modified.normalized_strength


def test_modulator_does_not_select_winner():
    modulator = StateModulator()
    tendency = BehavioralTendency(
        action="Negotiation",
        raw_strength=50.0,
        source="goal_directed",
        confidence_in_proposal=0.8,
    )
    tendency.normalized_strength = 0.50

    person = make_person_state(state_of_mind={"confused": True})
    modified = modulator.modulate(tendency, person)

    print("\nTEST 3: State modulator does not choose winner")
    print(modified.state_modulation_factor)
    assert modified.action == "Negotiation"
    assert modified.state_modulation_factor < 1.0
    assert modified.post_state_strength == modified.normalized_strength * modified.state_modulation_factor


def test_original_tendency_information_preserved():
    modulator = StateModulator()
    tendency = BehavioralTendency(
        action="WalkAway",
        raw_strength=45.0,
        source="goal_directed",
        confidence_in_proposal=0.85,
        supporting_evidence=["avoid conflict"],
        reason="Goal is to avoid conflict.",
    )
    tendency.normalized_strength = 0.45

    person = make_person_state(state_of_mind={"threatened": True})
    modified = modulator.modulate(tendency, person)

    print("\nTEST 4: Preserve original information")
    print(modified.raw_strength, modified.normalized_strength, modified.state_modulation_factor)
    assert modified.raw_strength == 45.0
    assert modified.normalized_strength == 0.45
    assert modified.reason == "Goal is to avoid conflict."
    assert modified.supporting_evidence == ["avoid conflict"]


def test_multiple_tendencies_independently_modulated():
    modulator = StateModulator()
    person = make_person_state(state_of_mind={"threatened": True})

    t1 = BehavioralTendency(action="WalkAway", raw_strength=45.0, source="goal_directed", confidence_in_proposal=0.8)
    t1.normalized_strength = 0.45
    t2 = BehavioralTendency(action="RespondImmediately", raw_strength=70.0, source="reactive", confidence_in_proposal=0.9)
    t2.normalized_strength = 0.70

    m1 = modulator.modulate(t1, person)
    m2 = modulator.modulate(t2, person)

    print("\nTEST 5: Multiple tendencies independently modulated")
    print(m1.state_modulation_factor, m2.state_modulation_factor)
    print(m1.post_state_strength, m2.post_state_strength)
    assert m1.state_modulation_factor == 1.15
    assert m2.state_modulation_factor == 1.15
    assert m1.post_state_strength != m2.post_state_strength


if __name__ == "__main__":
    test_neutral_state()
    test_recognized_state_modifies_tendency()
    test_modulator_does_not_select_winner()
    test_original_tendency_information_preserved()
    test_multiple_tendencies_independently_modulated()
    print("\nAll state modulation tests passed.")
