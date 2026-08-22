from decision_engine import DecisionEngine
from person_state import PersonState
from system_memory import SystemMemory
from meaning_interpretation import meaning_to_evidence
from state_manager import EvidenceRecord


def test_meaning_to_memory_export_flow():
    # Setup system memory and engines
    sys_mem = SystemMemory()
    engine = DecisionEngine(system_memory=sys_mem, enable_mal=True)

    # Create person and trigger a MAL-enabled event
    person = PersonState(person_id='test_person_bridge')
    person.goals = ['financial independence']
    person.perceived_control = 0.6
    person.trigger = {
        'event_type': 'verbal_attack',
        'text': "Someone publicly insults the person because they don't have money",
        'voice_volume': 80,
        'proximity': 0.9,
    }

    # Run decision (MAL enabled) --> should produce MeaningFrames and feed StateManager
    decision = engine.decide(person, person_id=person.person_id, current_context='public_challenge')

    meanings = getattr(person, 'meanings', []) or []
    assert len(meanings) > 0, "MAL should produce MeaningFrames"

    # 1) MeaningFrame -> EvidenceRecord with ref == MeaningFrame.id
    evs = []
    for m in meanings:
        records = meaning_to_evidence(m)
        for r in records:
            assert r.ref == m.id
        evs.extend(records)

    assert len(evs) > 0, "MeaningFrames should convert into evidence records"

    # 2) Evidence reaches StateManager and creates/updates corresponding state
    manager = engine.state_manager
    active = person.states.get('active', [])
    assert len(active) > 0
    # find a state that has evidence.ref matching a meaning id
    linked = None
    linked_meaning_id = None
    for m in meanings:
        for s in active:
            if any(e.ref == m.id for e in s.evidence):
                linked = s
                linked_meaning_id = m.id
                break
        if linked:
            break

    assert linked is not None, "At least one StateInstance should be linked to a MeaningFrame via evidence.ref"

    # 3) Transient state should NOT be exported to SystemMemory initially
    exported_before = manager.export_memory_refs_to_system_memory(person.person_id, sys_mem)
    assert exported_before == 0
    mem_before = sys_mem.get_memory(person.person_id)
    assert mem_before.get('history', []) == []

    # 4) Simulate reinforcement by updating the linked state with similar evidence multiple times
    assert linked is not None and len(evs) > 0
    for _ in range(3):
        for e in evs:
            new_ev = EvidenceRecord.create(source=e.source, signal=e.signal, value=e.value, confidence=e.confidence, ref=e.ref)
            manager.update_state_with_evidence(linked, new_ev)
    # now evaluate persistence which should mark reinforced and append a memory_ref
    manager.evaluate_persistence(linked)

    # 5) After evaluate_persistence, memory_refs should contain a reinforced ref
    refs = getattr(person, 'memory_refs', [])
    assert any(isinstance(r, dict) and r.get('reinforced') for r in refs), "person.memory_refs must contain a reinforced reference"

    # 6) Export to SystemMemory and verify the exported event preserves the memory_ref
    exported = manager.export_memory_refs_to_system_memory(person.person_id, sys_mem)
    assert exported >= 1
    mem_after = sys_mem.get_memory(person.person_id)
    history = mem_after.get('history', [])
    assert any(isinstance(item, dict) and item.get('type') == 'state_learning' and isinstance(item.get('memory_ref'), dict) for item in history)

    # 7-8) MAL remains non-decisional: compare selected actions with MAL on vs off
    engine_no_mal = DecisionEngine(system_memory=sys_mem, enable_mal=False)
    person2 = PersonState(person_id='test_person_bridge_2')
    person2.goals = person.goals
    person2.trigger = person.trigger
    dec_on = decision.selected_action
    dec_off = engine_no_mal.decide(person2, person_id=person2.person_id, current_context='public_challenge').selected_action
    assert dec_on == dec_off, "MAL+bridge should not change the selected action in the decision pipeline"
