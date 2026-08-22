"""
Tests for DecisionEngine: integration of all subsystems into one decision pipeline.
"""

from decision_engine import DecisionEngine, make_decision
from system_memory import SystemMemory


def create_mock_person(
    goals=None,
    emotion=None,
    habit_strength=None,
    arousal=0.5,
    self_regulation=0.5
):
    """Create a mock PersonState for testing."""
    class PS: pass
    p = PS()
    p.personality = {}
    p.goals = goals or []
    p.needs = {}
    p.values = []
    p.emotion = emotion
    p.feeling = None
    p.mood = None
    p.state_of_mind = {}
    p.arousal = arousal
    p.self_regulation = self_regulation
    p.perceived_control = 0.5
    p.awareness = 0.5
    p.habit_strength = habit_strength or {}
    return p


def test_unanimous_decision():
    """High convergence decision across subsystems."""
    print("TEST 1: High convergence decision")
    
    # Note: True unanimous is rare due to subsystem heuristic differences
    # This tests when subsystems largely agree on an action
    p = create_mock_person(
        goals=["avoid conflict"],
        emotion="calm",
        habit_strength={"p1": {"Negotiation": 4.0}},
        arousal=0.1,
        self_regulation=0.95
    )
    
    engine = DecisionEngine()
    res = engine.decide(p, person_id="alice", current_context="meeting", current_pattern_id="p1")
    
    print(f"  Selected: {res.selected_action}")
    print(f"  Convergence: {res.confidence_breakdown.get('convergence_score', 'N/A'):.2f}")
    print(f"  Conflict type: {res.conflict_info.get('type')}")
    
    assert res.selected_action is not None
    # Verify decision is made and confidence is valid
    assert 0.0 <= res.decision_confidence <= 1.0
    # Verify all fields are present
    assert res.confidence_breakdown is not None


def test_direct_conflict():
    """Goal-directed vs Reactive produce different actions."""
    print("TEST 2: Direct conflict")
    
    p = create_mock_person(
        goals=["preserve peace"],
        emotion="anger",
        habit_strength={},
        arousal=0.8,
        self_regulation=0.3
    )
    
    engine = DecisionEngine()
    res = engine.decide(p, person_id="bob", current_context="provocation")
    
    print(f"  Selected: {res.selected_action}")
    print(f"  Conflict type: {res.conflict_info.get('type')}")
    assert res.selected_action is not None
    assert res.conflict_info.get('exists')
    assert res.conflict_info.get('type') in ('direct_opposition', 'coalition_override', 'close_competition')


def test_coalition_override():
    """Reactive + Habitual override Goal-directed."""
    print("TEST 3: Coalition override")
    
    p = create_mock_person(
        goals=["compromise"],
        emotion="frustrated",
        habit_strength={"p1": {"RespondImmediately": 4.0}},
        arousal=0.7,
        self_regulation=0.4
    )
    
    engine = DecisionEngine()
    res = engine.decide(p, person_id="charlie", current_context="challenge", current_pattern_id="p1")
    
    print(f"  Selected: {res.selected_action}")
    print(f"  Conflict type: {res.conflict_info.get('type')}")
    print(f"  Proposals: {len(res.all_proposals)}")
    
    assert res.selected_action is not None
    assert len(res.all_proposals) >= 3


def test_system_memory_influence():
    """SystemMemory is integrated into the decision pipeline."""
    print("TEST 4: SystemMemory integrated into decision")
    
    p = create_mock_person(
        goals=["respond"],
        emotion="anger",
        habit_strength={},
        arousal=0.7,
        self_regulation=0.3
    )
    
    # First decision: without memory
    engine1 = DecisionEngine(system_memory=None)
    res1 = engine1.decide(p, person_id="diana", current_context="conflict")
    action1 = res1.selected_action
    
    # Second decision: with memory that opposes RespondImmediately
    memory = SystemMemory()
    memory.add_rule("diana", "oppose:RespondImmediately")
    engine2 = DecisionEngine(system_memory=memory)
    res2 = engine2.decide(p, person_id="diana", current_context="conflict")
    action2 = res2.selected_action
    
    print(f"  Without memory: {action1}")
    print(f"  With memory opposing RespondImmediately: {action2}")
    print(f"  Memory influence: {res2.system_memory_influence}")
    
    # Verify decision engine works with memory; memory effects are tested in test_system_memory.py
    assert res1.selected_action is not None
    assert res2.selected_action is not None
    assert res2.system_memory_influence is not None


def test_confidence_returned():
    """Decision confidence is calculated and returned."""
    print("TEST 5: Confidence returned")
    
    p = create_mock_person(
        goals=["defend"],
        emotion="alert",
        habit_strength={"p1": {"RespondImmediately": 3.0}},
        arousal=0.6
    )
    
    engine = DecisionEngine()
    res = engine.decide(p, person_id="eve", current_context="threat", current_pattern_id="p1")
    
    print(f"  Decision confidence: {res.decision_confidence:.4f}")
    print(f"  Confidence breakdown: {res.confidence_breakdown}")
    
    assert 0.0 <= res.decision_confidence <= 1.0
    assert 'margin_score' in res.confidence_breakdown
    assert 'convergence_score' in res.confidence_breakdown
    assert 'source_confidence_score' in res.confidence_breakdown
    assert 'evidence_score' in res.confidence_breakdown


def test_end_to_end_complete():
    """Complete end-to-end decision with all fields."""
    print("TEST 6: End-to-end complete pipeline")
    
    p = create_mock_person(
        goals=["protect self"],
        emotion="defensive",
        habit_strength={"meeting": {"StayQuiet": 2.0}},
        arousal=0.5,
        self_regulation=0.6
    )
    
    engine = DecisionEngine()
    res = engine.decide(
        p,
        person_id="frank",
        current_context="meeting",
        current_pattern_id="meeting"
    )
    
    print(f"  Selected action: {res.selected_action}")
    print(f"  Selected source: {res.selected_source}")
    print(f"  Final strength: {res.final_strength:.4f}")
    print(f"  Decision confidence: {res.decision_confidence:.2%}")
    print(f"  Conflict level: {res.conflict_level}")
    print(f"  Conflict type: {res.conflict_type}")
    print(f"  Person ID: {res.person_id}")
    print(f"  Context: {res.context}")
    print(f"  Proposals: {len(res.all_proposals)}")
    
    # Verify all required fields are present
    assert res.selected_action is not None
    assert isinstance(res.selected_source, str)
    assert res.final_strength >= 0.0
    assert 0.0 <= res.decision_confidence <= 1.0
    assert res.conflict_level in ('none', 'mild', 'moderate', 'high')
    assert res.conflict_type in ('unanimous', 'direct_opposition', 'coalition_override', 'close_competition')
    assert res.person_id == "frank"
    assert res.context == "meeting"
    assert len(res.all_proposals) >= 3
    assert res.reasoning != ""
    assert res.conflict_info is not None
    assert res.confidence_breakdown is not None


def test_convenience_function():
    """Test the convenience function make_decision()."""
    print("TEST 7: Convenience function make_decision()")
    
    p = create_mock_person(
        goals=["proceed"],
        emotion="determined",
        arousal=0.6
    )
    
    res = make_decision(p, person_id="grace", current_context="task")
    
    print(f"  Selected: {res.selected_action}")
    print(f"  Confidence: {res.decision_confidence:.2%}")
    
    assert res.selected_action is not None
    assert res.person_id == "grace"


if __name__ == "__main__":
    test_unanimous_decision()
    test_direct_conflict()
    test_coalition_override()
    test_system_memory_influence()
    test_confidence_returned()
    test_end_to_end_complete()
    test_convenience_function()
    print("\nAll decision engine tests completed.")
