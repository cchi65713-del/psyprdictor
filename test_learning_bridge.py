from datetime import datetime, timedelta

from experience import Experience
from learning_bridge import LearningBridge
from memory import Memory
from pattern_learner import PatternLearner
from person_state import PersonState


def test_learning_bridge_records_execution_and_updates_habit_strength():
    person = PersonState("P1")
    memory = Memory()
    learner = PatternLearner()
    memory.connect_pattern_learner(learner)

    bridge = LearningBridge()
    result = bridge.record_execution(
        person_state=person,
        person_id="P1",
        chosen_action="RespondImmediately",
        actual_outcome="B1",
        pattern_id="E4.F3.M2.S5.B1",
        pattern_path=["E4", "F3", "M2", "S5", "B1"],
        context="Repeated conflict",
        memory=memory,
    )

    assert result["outcome"] == "B1"
    assert len(memory.experiences) == 1
    assert memory.experiences[0].outcome == "B1"
    assert person.habit_strength["E4.F3.M2.S5.B1"]["RespondImmediately"] > 0
    assert learner.get_pattern(["E4", "F3", "M2", "S5", "B1"]) is not None


def test_learning_bridge_preserves_manual_learning_pattern_without_changing_habit_algorithm():
    person = PersonState("P1")
    memory = Memory()
    learner = PatternLearner()
    memory.connect_pattern_learner(learner)

    # simulate the old manual flow exactly in a bridge-backed call
    outcome = "B1"
    pattern_path = ["E4", "F3", "M2", "S5", "B1"]
    pattern_id = ".".join(pattern_path)

    bridge = LearningBridge()
    diag = bridge.record_execution(
        person_state=person,
        person_id="P1",
        chosen_action="RespondImmediately",
        actual_outcome=outcome,
        pattern_id=pattern_id,
        pattern_path=pattern_path,
        context="manual flow",
        memory=memory,
    )

    assert diag["pattern_id"] == pattern_id
    assert diag["outcome"] == outcome
    assert diag["memory_updated"] is True
    assert diag["habit_strength_updated"] is True
    assert len(learner.get_all_patterns()) >= 1
