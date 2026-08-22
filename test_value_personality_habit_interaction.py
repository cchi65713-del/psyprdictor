from person_state import PersonState
from action_selection import propose_integrated


def top_action(scores):
    return max(scores.items(), key=lambda t: t[1])[0]


def test_same_event_different_people():
    # Shared event: same context and pattern
    context = "conflict_discussion"
    pattern_id = "conflict.discussion"

    # Person A: values harmony, low aggression, low habit
    a = PersonState(person_id="A")
    a.values = ["harmony"]
    a.goals = ["preserve relationships"]
    a.personality = {"aggression": 0.1, "avoidant": 0.3}
    a.habit_strength = {pattern_id: {"Negotiation": 0.0, "RespondImmediately": 0.0, "WalkAway": 0.0}}

    # Person B: values self-respect, high aggression, potential habit to respond
    b = PersonState(person_id="B")
    b.values = ["self respect"]
    b.goals = ["defend reputation"]
    b.personality = {"aggression": 0.9, "avoidant": 0.1}
    b.habit_strength = {pattern_id: {"RespondImmediately": 1.5}}

    res_a = propose_integrated(a, current_context=context, current_pattern_id=pattern_id)
    res_b = propose_integrated(b, current_context=context, current_pattern_id=pattern_id)

    top_a = top_action(res_a.scores)
    top_b = top_action(res_b.scores)

    assert top_a != top_b, f"Expected different top actions for different people, got both {top_a}"

    # Also ensure RespondImmediately score higher for B than A
    assert res_b.scores.get("RespondImmediately", 0.0) > res_a.scores.get("RespondImmediately", 0.0)
