from action_selection import ActionSelector
from person_state import PersonState


def test_default_personality_profile_is_stable_and_person_specific():
    p1 = PersonState("P1")
    p2 = PersonState("P2")

    assert p1.personality == {"aggression": 0.5, "avoidant": 0.5}
    assert p2.personality == {"aggression": 0.5, "avoidant": 0.5}

    p1.set_personality_traits(aggression=0.9)

    assert p1.personality["aggression"] == 0.9
    assert p2.personality["aggression"] == 0.5
    assert p2.personality == {"aggression": 0.5, "avoidant": 0.5}


def test_personality_influences_preference_but_not_direct_action_selection():
    p_aggressive = PersonState("aggressive")
    p_avoidant = PersonState("avoidant")

    p_aggressive.set_personality_traits(aggression=1.0, avoidant=0.0)
    p_avoidant.set_personality_traits(aggression=0.0, avoidant=1.0)

    selector = ActionSelector()
    aggressive_scores = selector.score_actions(p_aggressive, current_pattern_id="p1")
    avoidant_scores = selector.score_actions(p_avoidant, current_pattern_id="p1")

    assert aggressive_scores["RespondImmediately"] > avoidant_scores["RespondImmediately"]
    assert avoidant_scores["WalkAway"] > aggressive_scores["WalkAway"]
    assert set(aggressive_scores) == set(selector.DEFAULT_ACTIONS)
    assert set(avoidant_scores) == set(selector.DEFAULT_ACTIONS)


def test_personality_cannot_bypass_reasoning_habits_or_arbitration():
    person = PersonState("P1")
    person.set_personality_traits(aggression=1.0, avoidant=1.0)
    person.habit_strength = {"p1": {"RespondImmediately": 4.0, "WalkAway": 3.0}}
    person.goals = ["avoid conflict"]

    selector = ActionSelector()
    scores = selector.score_actions(person, current_pattern_id="p1")

    assert all(action in selector.DEFAULT_ACTIONS for action in scores)
    assert sum(scores.values()) > 0
    assert scores["RespondImmediately"] >= 0.0
    assert scores["WalkAway"] >= 0.0
    assert "personality_override" not in scores
