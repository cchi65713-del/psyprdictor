from action_selection import propose_goal_directed, propose_reactive, propose_habitual
from competition import CompetitionEngine


def test_goal_produces_tendency():
    class PS: pass
    p = PS()
    p.personality = {}
    p.goals = ["avoid conflict"]
    res = propose_goal_directed(p)
    print("TEST 1: Goal-directed produces tendencies")
    assert hasattr(res, 'tendencies')
    assert len(res.tendencies) > 0


def test_reactive_produces_tendency():
    class PS: pass
    p = PS()
    p.personality = {}
    p.emotion = "anger"
    p.feeling = "irritated"
    res = propose_reactive(p)
    print("TEST 2: Reactive produces tendencies")
    assert hasattr(res, 'tendencies')
    assert len(res.tendencies) > 0


def test_habitual_produces_tendency():
    class PS: pass
    p = PS()
    p.personality = {}
    p.habit_strength = {"p1": {"RespondImmediately": 3.0}}
    res = propose_habitual(p, current_pattern_id="p1")
    print("TEST 3: Habitual produces tendencies")
    assert hasattr(res, 'tendencies')
    assert len(res.tendencies) > 0


def test_raw_and_normalized():
    class PS: pass
    p = PS()
    p.personality = {}
    p.goals = ["defend self"]
    res = propose_goal_directed(p)
    t = res.tendencies[0]
    print("TEST 4: Raw and normalized preserved")
    assert hasattr(t, 'raw_before_norm')
    assert t.raw_strength == t.raw_before_norm
    assert 0.0 <= t.normalized_strength <= 1.0


def test_source_and_confidence():
    class PS: pass
    p = PS()
    p.personality = {}
    p.emotion = "anger"
    res = propose_reactive(p)
    t = res.tendencies[0]
    print("TEST 5: Source and confidence present")
    assert t.source == "reactive"
    assert 0.0 <= t.confidence_in_proposal <= 1.0


def test_identity_goal_priority_biases_action_selection():
    class PS: pass
    p = PS()
    p.personality = {}
    p.active_goals = [{
        "description": "Maintain personal standards and autonomy",
        "priority": 3.5,
        "origin": {"need": "esteem", "value": "respect"},
    }]
    p.goals = p.active_goals
    p.values = []
    p.needs = {}
    p.identity = {"roles": {"defender": 0.9}, "standards": ["Respect", "Boundaries"]}

    res = propose_goal_directed(p, current_context="insult")
    print("TEST 6: identity-driven goals bias action selection")
    assert res.scores["RespondImmediately"] > res.scores["WalkAway"]
    assert any("priority" in r.lower() or "goal" in r.lower() for r in res.reasons["RespondImmediately"])


def test_identity_goal_relevance_is_context_specific():
    class PS: pass
    p = PS()
    p.personality = {}
    p.active_goals = [{
        "description": "Practice patience and stay calm",
        "priority": 3.5,
        "origin": {"need": "esteem", "value": "calm"},
    }]
    p.goals = p.active_goals
    p.values = []
    p.needs = {}
    p.identity = {"roles": {"teacher": 0.9}, "standards": ["Patience", "Calm"]}

    res = propose_goal_directed(p, current_context="morning meeting")
    print("TEST 7: identity relevance does not create a hidden confrontation rule")
    assert res.scores["RespondImmediately"] <= res.scores["WalkAway"] + 0.05
    assert not any("identity" in r.lower() and "goal" in r.lower() for r in res.reasons["RespondImmediately"])


def test_end_to_end_competition():
    # Use one tendency from each subsystem run through CompetitionEngine
    class PS: pass
    p = PS()
    p.personality = {}
    p.goals = ["avoid conflict"]
    p.emotion = "anger"
    p.habit_strength = {"p1": {"RespondImmediately": 3.0}}

    gd = propose_goal_directed(p).tendencies
    re = propose_reactive(p).tendencies
    ha = propose_habitual(p, current_pattern_id="p1").tendencies

    # pick top tendency from each
    proposals = [gd[0], re[0], ha[0]]

    engine = CompetitionEngine()
    res = engine.compete(proposals)
    print("TEST 6: End-to-end competition")
    print(res.selected_action)
    assert res.selected_action is not None


if __name__ == "__main__":
    test_goal_produces_tendency()
    test_reactive_produces_tendency()
    test_habitual_produces_tendency()
    test_raw_and_normalized()
    test_source_and_confidence()
    test_end_to_end_competition()
    print('\nAction selection tests completed.')
