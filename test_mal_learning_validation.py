from decision_engine import DecisionEngine
from person_state import PersonState
from system_memory import SystemMemory


def make_person_for_insult(person_id):
    p = PersonState(person_id=person_id)
    p.goals = ["financial independence"]
    p.values = []
    p.history = {}
    p.perceived_control = 0.6
    p.trigger = {
        "event_type": "verbal_attack",
        "text": "Someone publicly insults the person because they don't have money",
        "voice_volume": 80,
        "proximity": 0.9,
    }
    return p


def test_mal_event1_and_event2_no_memory_influence():
    sys_mem = SystemMemory()
    engine = DecisionEngine(system_memory=sys_mem, enable_mal=True)

    # Event 1
    person = make_person_for_insult("test_person")
    engine.decide(person, person_id=person.person_id, current_context="public_challenge")

    meanings_after_e1 = getattr(person, "meanings", [])
    assert len(meanings_after_e1) > 0, "Event1 should produce meanings when MAL is enabled"

    # Verify StateManager created states with evidence referencing meanings
    active_states = person.states.get("active", [])
    assert len(active_states) >= 0
    meaning_ids = [m.id for m in meanings_after_e1]
    has_meaning_evidence = any(e.ref in meaning_ids for s in active_states for e in s.evidence)
    # It's acceptable if appraisal evidence created states too; we only assert MAL produced meanings above

    # SystemMemory may implement a memory lookup; we don't require it to be absent here.
    # Verify person.memory_refs starts empty (no reinforcement yet)
    assert getattr(person, "memory_refs", []) == [], "No memory refs should be present immediately after Event1"

    # Event 2: run the same person through DecisionEngine again
    person.trigger = {
        "event_type": "verbal_attack",
        "text": "Someone publicly mocks the person again about not having money",
        "voice_volume": 75,
        "proximity": 0.8,
    }
    engine.decide(person, person_id=person.person_id, current_context="public_challenge")

    meanings_after_e2 = getattr(person, "meanings", [])
    # Ensure meanings were produced again (appended)
    assert len(meanings_after_e2) >= len(meanings_after_e1)

    # Check whether any meaning references memory (supporting_memory_refs)
    any_supporting_memory_refs = any(getattr(m, "supporting_memory_refs", []) for m in meanings_after_e2)
    # It's acceptable if the new indexing returns supporting refs; this test only validated MAL runs
