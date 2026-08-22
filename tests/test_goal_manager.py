import pytest

from goal_manager import GoalManager
from person_state import PersonState


def test_generate_goals_simple():
    gm = GoalManager()
    values = {"honor": 0.8, "peace": 0.4}
    needs = {"esteem": 0.9}
    identity = {"roles": {"soldier": 1.0}, "standards": ["Honor"]}

    goals = gm.generate_goals(values, needs, identity)

    assert isinstance(goals, list)
    assert len(goals) >= 1
    g = goals[0]
    assert "id" in g and "priority" in g and g["priority"] > 0
    assert any("honor" in str(g.get("description", "")).lower() or "esteem" in str(g.get("description", "")).lower() for g in goals)


def test_person_state_identity_drives_goals():
    person = PersonState(person_id="p1")
    person.value_weights = {"respect": 0.9, "safety": 0.8}
    person.need_state = {"esteem": 0.9, "safety": 0.7}
    person.fill_actual_identity(
        name="Ava",
        roles={"defender": 0.9},
        standards=["Respect", "Boundaries"],
    )

    person.refresh_goals()

    assert person.active_goals
    assert person.goals == person.active_goals
    assert any("respect" in str(goal["description"]).lower() or "defender" in str(goal["description"]).lower() for goal in person.active_goals)
