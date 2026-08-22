from competition import BehavioralTendency, CompetitionEngine


def test_unanimous():
    # All systems propose the same action -> unanimous
    t1 = BehavioralTendency(action="Negotiation", raw_strength=50, source="goal_directed")
    t2 = BehavioralTendency(action="Negotiation", raw_strength=40, source="reactive")
    t3 = BehavioralTendency(action="Negotiation", raw_strength=4, source="habitual")

    engine = CompetitionEngine()
    res = engine.compete([t1, t2, t3])
    print("TEST 1: Unanimous")
    print(res.conflict_info)
    assert res.conflict_info["type"] == "unanimous"
    assert res.conflict_info["exists"] is False


def test_direct_opposition():
    # Goal -> WalkAway, Reactive -> RespondImmediately
    goal = BehavioralTendency(action="WalkAway", raw_strength=45, source="goal_directed")
    reactive = BehavioralTendency(action="RespondImmediately", raw_strength=70, source="reactive")

    engine = CompetitionEngine()
    res = engine.compete([goal, reactive])
    print("TEST 2: Direct opposition")
    print(res.conflict_info)
    assert res.conflict_info["type"] == "direct_opposition"
    assert res.conflict_info["exists"] is True


def test_coalition_override():
    # Goal -> WalkAway, Reactive+Habit -> RespondImmediately
    goal = BehavioralTendency(action="WalkAway", raw_strength=45, source="goal_directed")
    reactive = BehavioralTendency(action="RespondImmediately", raw_strength=70, source="reactive")
    habit = BehavioralTendency(action="RespondImmediately", raw_strength=3.2, source="habitual")

    engine = CompetitionEngine()
    res = engine.compete([goal, reactive, habit])
    print("TEST 3: Coalition override")
    print(res.conflict_info)
    assert res.conflict_info["type"] == "coalition_override"
    assert res.conflict_info["exists"] is True


def test_close_competition():
    # Two actions with nearly equal pressure
    a1 = BehavioralTendency(action="A", raw_strength=50, source="goal_directed")
    a2 = BehavioralTendency(action="B", raw_strength=49.5, source="reactive")

    engine = CompetitionEngine()
    res = engine.compete([a1, a2])
    print("TEST 4: Close competition")
    print(res.conflict_info)
    assert res.conflict_info["type"] == "close_competition"
    assert res.conflict_info["exists"] is True


if __name__ == "__main__":
    test_unanimous()
    test_direct_opposition()
    test_coalition_override()
    test_close_competition()
    print("\nConflict type tests completed.")
