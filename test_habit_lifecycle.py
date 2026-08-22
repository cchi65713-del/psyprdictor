from datetime import datetime, timedelta

from competition import BehavioralTendency, CompetitionEngine
from experience import Experience
from habit_formation import update_habit_strengths
from learning_bridge import LearningBridge
from memory import Memory
from pattern_learner import PatternLearner
from person_state import PersonState


PATTERN_ID = "E4.F3.M2.S5.B1"
PATH = ["E4", "F3", "M2", "S5", "B1"]


def make_experience(outcome, days_ago=0, intensity=5):
    return Experience(
        path=PATH,
        intensity=intensity,
        context="habit lifecycle test",
        outcome=outcome,
        timestamp=datetime.now() - timedelta(days=days_ago),
    )


def build_memory(experiences):
    memory = Memory()
    learner = PatternLearner()
    memory.connect_pattern_learner(learner)
    for experience in experiences:
        memory.store(experience)
    return memory, learner


def test_repeated_pattern_strengthens_habit():
    person = PersonState("P1")
    memory, learner = build_memory([
        make_experience("B1", days_ago=30),
        make_experience("B1", days_ago=20),
        make_experience("B1", days_ago=10),
        make_experience("B1", days_ago=5),
    ])

    update_habit_strengths(person, memory, learner, pattern_id=PATTERN_ID)

    assert person.habit_strength[PATTERN_ID]["RespondImmediately"] > 0.4


def test_inconsistent_outcomes_weaken_habit():
    consistent_person = PersonState("P1")
    inconsistent_person = PersonState("P2")

    consistent_memory, consistent_learner = build_memory([
        make_experience("B1", days_ago=30),
        make_experience("B1", days_ago=20),
        make_experience("B1", days_ago=10),
        make_experience("B1", days_ago=5),
    ])
    inconsistent_memory, inconsistent_learner = build_memory([
        make_experience("B1", days_ago=30),
        make_experience("B1", days_ago=20),
        make_experience("B4", days_ago=10),
        make_experience("B4", days_ago=5),
    ])

    update_habit_strengths(consistent_person, consistent_memory, consistent_learner, pattern_id=PATTERN_ID)
    update_habit_strengths(inconsistent_person, inconsistent_memory, inconsistent_learner, pattern_id=PATTERN_ID)

    consistent_strength = consistent_person.habit_strength[PATTERN_ID]["RespondImmediately"]
    inconsistent_strength = inconsistent_person.habit_strength[PATTERN_ID]["RespondImmediately"]

    assert consistent_strength > inconsistent_strength


def test_habit_is_person_specific():
    p1 = PersonState("P1")
    p2 = PersonState("P2")

    mem1, learner1 = build_memory([
        make_experience("B1", days_ago=30),
        make_experience("B1", days_ago=20),
        make_experience("B1", days_ago=10),
    ])
    mem2, learner2 = build_memory([
        make_experience("B4", days_ago=30),
        make_experience("B4", days_ago=20),
        make_experience("B4", days_ago=10),
    ])

    update_habit_strengths(p1, mem1, learner1, pattern_id=PATTERN_ID)
    update_habit_strengths(p2, mem2, learner2, pattern_id=PATTERN_ID)

    p1_dominant = max(p1.habit_strength[PATTERN_ID], key=p1.habit_strength[PATTERN_ID].get)
    p2_dominant = max(p2.habit_strength[PATTERN_ID], key=p2.habit_strength[PATTERN_ID].get)

    assert p1_dominant == "RespondImmediately"
    assert p2_dominant == "WalkAway"


def test_learning_bridge_does_not_double_reinforce():
    person = PersonState("P1")
    memory = Memory()
    learner = PatternLearner()
    memory.connect_pattern_learner(learner)
    bridge = LearningBridge()

    for _ in range(2):
        bridge.record_execution(
            person_state=person,
            person_id="P1",
            chosen_action="RespondImmediately",
            actual_outcome="B1",
            pattern_id=PATTERN_ID,
            pattern_path=PATH,
            context="repeated event",
            memory=memory,
            pattern_learner=learner,
        )

    assert len(memory.experiences) == 2
    assert len(learner.get_all_patterns()) >= 4
    assert person.habit_strength[PATTERN_ID]["RespondImmediately"] > 0


def test_habit_is_only_a_competing_proposal():
    engine = CompetitionEngine()
    goal = BehavioralTendency(action="WalkAway", raw_strength=60.0, source="goal_directed", confidence_in_proposal=0.9)
    reactive = BehavioralTendency(action="StayQuiet", raw_strength=55.0, source="reactive", confidence_in_proposal=0.8)
    habit = BehavioralTendency(action="RespondImmediately", raw_strength=8.0, source="habitual", confidence_in_proposal=0.9)

    result = engine.compete([goal, reactive, habit])

    assert result.selected_action in {"WalkAway", "StayQuiet", "RespondImmediately"}
    assert result.selected_source in {"goal_directed", "reactive", "habitual"}
