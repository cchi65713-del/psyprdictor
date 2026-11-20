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


def test_experience_accepts_optional_efmsomb_snapshot():
    efmsomb = {
        "emotion": {"label": "anger", "code": "E4"},
        "feeling": {"label": "disrespected", "code": "F3"},
    }
    exp = Experience(
        path=["E4", "F3", "M2"],
        intensity=8,
        context="snapshot test",
        outcome="B1",
        efmsomb=efmsomb,
    )

    assert exp.efmsomb == efmsomb
    assert exp.path == ["E4", "F3", "M2"]
    assert exp.outcome == "B1"


def test_learning_bridge_records_optional_efmsomb_snapshot():
    person = PersonState("P2")
    person.efmsomb = {
        "emotion": {"label": "anger", "code": "E4"},
        "feeling": {"label": "disrespected", "code": "F3"},
        "mood": {"label": "irritated", "code": "M2"},
        "state_of_mind": {"label": "defensive", "code": "S5"},
        "behavior": {"label": "respond_immediately", "code": "B1"},
    }
    memory = Memory()
    learner = PatternLearner()
    memory.connect_pattern_learner(learner)
    bridge = LearningBridge()

    diag = bridge.record_execution(
        person_state=person,
        person_id="P2",
        chosen_action="RespondImmediately",
        actual_outcome="B1",
        pattern_id="E4.F3.M2.S5.B1",
        pattern_path=["E4", "F3", "M2", "S5", "B1"],
        context="snapshot flow",
        memory=memory,
    )

    assert len(memory.experiences) == 1
    assert memory.experiences[0].efmsomb == person.efmsomb
    assert memory.experiences[0].path == ["E4", "F3", "M2", "S5", "B1"]
    assert diag["outcome"] == "B1"
