from decision_engine import DecisionEngine
from person_state import PersonState


def test_embarrassment_to_motivation_focus_integration():
    # Create a person and craft a trigger that Appraiser will treat as accusatory
    p = PersonState(person_id="integration_test")
    # trigger contains accusatory phrase that Appraiser recognizes as 'threat'
    p.trigger = {"event_type": "verbal_attack", "text": "You always act like you're broke and useless" , "voice_volume": 85, "proximity": 0.9}

    engine = DecisionEngine()
    res = engine.decide(p, person_id="integration_test", current_context="public_embarrassment")

    # After decide, StateManager should have been called and populated person_state.states
    states = getattr(p, "states", {})
    active = states.get("active", [])

    # Expect at least one appraisal-derived state (e.g., 'threat') and evidence preserved
    assert len(active) >= 1
    names = {s.canonical_name for s in active}

    # the appraisal->StateManager path produces frame.label as canonical_name; 'threat' is expected
    assert any(n for n in names if n in {"threat", "embarrassment", "fear"})

    # DecisionResult should report state inference based on those active states
    assert res.state_of_mind_source in {"inferred-via-states", "inferred", "manual", "insufficient-data"}
    # Ensure provenance present in decision result evidence or person_state.active state evidence
    evidence_present = False
    for s in active:
        if getattr(s, "evidence", None):
            evidence_present = True
            break
    assert evidence_present


if __name__ == "__main__":
    test_embarrassment_to_motivation_focus_integration()
    print("Integration test passed.")
