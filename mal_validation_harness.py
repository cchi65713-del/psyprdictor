"""MAL learning validation harness

Runs two consecutive insult events for the same person with MAL enabled
and reports meanings, evidence, states, and SystemMemory contents.
"""
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


def summarize_meanings(person):
    meanings = getattr(person, "meanings", []) or []
    out = []
    for m in meanings:
        out.append({
            "id": m.id,
            "interpretation": m.interpretation,
            "confidence": m.confidence,
            "supporting_memory_refs": getattr(m, "supporting_memory_refs", []),
            "provenance": getattr(m, "provenance", {}),
        })
    return out


def summarize_states(person):
    active = person.states.get("active", [])
    out = []
    for s in active:
        out.append({
            "id": s.id,
            "canonical_name": s.canonical_name,
            "dimensions": s.dimensions,
            "intensity": s.intensity,
            "evidence_refs": [e.ref for e in s.evidence],
        })
    return out


def main():
    sys_mem = SystemMemory()
    engine = DecisionEngine(system_memory=sys_mem, enable_mal=True)

    print("\n=== Event 1: first insult ===")
    person = make_person_for_insult("personX")
    res1 = engine.decide(person, person_id=person.person_id, current_context="public_challenge")

    meanings1 = summarize_meanings(person)
    states1 = summarize_states(person)

    print("Meanings generated (Event1):")
    for m in meanings1:
        print(m)

    print("\nStates created (Event1):")
    for s in states1:
        print(s)

    print("\nPerson.memory_refs (Event1):", getattr(person, "memory_refs", []))
    print("SystemMemory snapshot (Event1):", sys_mem.get_memory(person.person_id))

    print("\n=== Event 2: repeated insult ===")
    # Simulate later similar event with same PersonState and same SystemMemory
    # Trigger text can be identical to test for learning influence
    person.trigger = {
        "event_type": "verbal_attack",
        "text": "Someone publicly mocks the person again about not having money",
        "voice_volume": 75,
        "proximity": 0.8,
    }

    res2 = engine.decide(person, person_id=person.person_id, current_context="public_challenge")

    meanings2 = summarize_meanings(person)
    states2 = summarize_states(person)

    print("Meanings after Event2 (all attached meanings):")
    for m in meanings2:
        print(m)

    print("\nStates after Event2 (active):")
    for s in states2:
        print(s)

    print("\nPerson.memory_refs (after Event2):", getattr(person, "memory_refs", []))
    print("SystemMemory snapshot (after Event2):", sys_mem.get_memory(person.person_id))

    # Check whether SystemMemory provides find_related_meanings
    has_find = hasattr(sys_mem, "find_related_meanings")
    print("\nSystemMemory.find_related_meanings available?", has_find)

    # Basic conclusion printed for quick inspection
    influenced = any(m.get("supporting_memory_refs") for m in meanings2)
    print("\nDoes Event1 appear to have influenced Event2 meanings (supporting_memory_refs present)?", influenced)


if __name__ == "__main__":
    main()
