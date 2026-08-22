from decision_engine import DecisionEngine
from person_state import PersonState
from system_memory import SystemMemory
from meaning_interpretation import meaning_to_evidence
from state_manager import EvidenceRecord


def test_memory_indexing_two_event_flow_and_isolation():
    sys_mem = SystemMemory()
    engine = DecisionEngine(system_memory=sys_mem, enable_mal=True)

    # Event 1: produce meaning and reinforce
    person = PersonState(person_id='p_index')
    person.goals = ['financial independence']
    person.trigger = {'event_type': 'verbal_attack', 'text': "Insult about money", 'voice_volume': 80, 'proximity': 0.9}

    dec1 = engine.decide(person, person_id=person.person_id, current_context='public_challenge')
    meanings1 = getattr(person, 'meanings', []) or []
    assert len(meanings1) > 0

    # find linked state
    manager = engine.state_manager
    active = person.states.get('active', [])
    linked = None
    for m in meanings1:
        for s in active:
            if any(e.ref == m.id for e in s.evidence):
                linked = s
                linked_meaning = m
                break
        if linked:
            break
    assert linked is not None

    # create a transient (non-reinforced) state to ensure it does not get exported/retrieved
    transient_ev = EvidenceRecord.create(source=linked_meaning.id, signal='transient_signal', value={'threat': 0.2}, confidence=0.5, ref=linked_meaning.id)
    transient_state = manager.create_state_from_trigger('transient_state', transient_ev)
    assert transient_state.reinforced is False

    # ensure no memory exported yet
    assert sys_mem.get_memory(person.person_id).get('history', []) == []

    # reinforce via repeated evidence and evaluate persistence, then export
    evs = []
    for m in meanings1:
        evs.extend(meaning_to_evidence(m))
    for _ in range(3):
        for e in evs:
            new_ev = EvidenceRecord.create(source=e.source, signal=e.signal, value=e.value, confidence=e.confidence, ref=e.ref)
            manager.update_state_with_evidence(linked, new_ev)
    manager.evaluate_persistence(linked)
    # now export
    exported = manager.export_memory_refs_to_system_memory(person.person_id, sys_mem)
    assert exported >= 1
    hist = sys_mem.get_memory(person.person_id).get('history', [])
    assert any(it.get('type') == 'state_learning' for it in hist)

    # Inspect the exported memory for provenance: should reference the linked state's id
    learned_events = [it for it in hist if it.get('type') == 'state_learning']
    assert learned_events, "No learned events were exported"
    learned = learned_events[0]
    learned_mem_id = learned.get('memory_id') or (learned.get('memory_ref') or {}).get('state_id')
    assert learned_mem_id == linked.id, f"Exported memory_id {learned_mem_id} should match reinforced state id {linked.id}"
    # transient state must not be exported
    assert all((learned.get('memory_ref') or {}).get('state_id') != transient_state.id for learned in learned_events)

    # Event 2: same person, similar trigger
    person.trigger = {'event_type': 'verbal_attack', 'text': "Someone mocks about not having money", 'voice_volume': 70, 'proximity': 0.8}
    dec2 = engine.decide(person, person_id=person.person_id, current_context='public_challenge')
    meanings2 = getattr(person, 'meanings', []) or []
    # check that at least one meaning gained supporting_memory_refs
    supportive = [m for m in meanings2 if getattr(m, 'supporting_memory_refs', [])]
    assert len(supportive) > 0, "At least one MeaningFrame should reference prior reinforced memory"

    # Verify supporting references point back to the exported memory and provenance links
    found_match = False
    for m in supportive:
        # supporting_memory_refs may contain dicts with memory_id or state_id
        for ref in getattr(m, 'supporting_memory_refs', []):
            if isinstance(ref, str):
                mid = ref
            elif isinstance(ref, dict):
                mid = ref.get('memory_id') or ref.get('state_id') or ref.get('memory_ref') or None
                if isinstance(mid, dict):
                    mid = mid.get('state_id') or mid.get('memory_id')
            else:
                mid = None
            if mid == learned_mem_id:
                found_match = True
        # provenance should record memory_refs linking to system memory
        prov_mem_refs = []
        if getattr(m, 'provenance', None):
            prov_mem_refs = m.provenance.get('memory_refs') or []
        # each provenance entry may be a string id or a dict; verify at least one valid identifier exists when entries present
        for r in prov_mem_refs:
            if isinstance(r, str):
                continue
            assert isinstance(r, dict), "provenance.memory_refs entries must be dicts or strings"
            assert (r.get('memory_id') or r.get('state_id') or (r.get('memory_ref') or {}).get('state_id')) , "provenance.memory_refs must contain memory identifiers if present"
    assert found_match, "No supporting_memory_refs referred back to the exported learned memory"

    # Isolation: person B should not be influenced by person A's memory
    person_b = PersonState(person_id='p_index_b')
    person_b.goals = person.goals
    person_b.trigger = person.trigger
    dec_b = engine.decide(person_b, person_id=person_b.person_id, current_context='public_challenge')
    meanings_b = getattr(person_b, 'meanings', []) or []
    assert all(not getattr(m, 'supporting_memory_refs', []) for m in meanings_b), "Person B should not be influenced by Person A's memory"

    # Unrelated memory: create a memory for a different person (should not influence)
    # Simulate by adding a fake history entry for a different person id with canonical_name 'unrelated'
    sys_mem.add_history(person.person_id + '_other', {'type': 'state_learning', 'memory_id': 'fake1', 'canonical_name': 'unrelated', 'memory_ref': {'state_id': 'fake1', 'reinforced': True}})
    person.trigger = {'event_type': 'verbal_attack', 'text': "Insult about money again", 'voice_volume': 75, 'proximity': 0.9}
    dec3 = engine.decide(person, person_id=person.person_id, current_context='public_challenge')
    # ensure at least one meaning still references the original memory (not the unrelated fake)
    meanings3 = getattr(person, 'meanings', []) or []
    assert any(getattr(m, 'supporting_memory_refs', []) for m in meanings3)
    # ensure none of the supporting refs point only to the unrelated fake
    for m in meanings3:
        for r in getattr(m, 'supporting_memory_refs', []) or []:
            if isinstance(r, str):
                assert r != 'fake1'
            else:
                assert r.get('memory_id') != 'fake1' and (r.get('memory_ref', {}) or {}).get('state_id') != 'fake1'

    # MAL remains non-decisional: compare with MAL off
    engine_no_mal = DecisionEngine(system_memory=sys_mem, enable_mal=False)
    person2 = PersonState(person_id='p_index_2')
    person2.goals = person.goals
    person2.trigger = person.trigger
    dec_no_mal = engine_no_mal.decide(person2, person_id=person2.person_id, current_context='public_challenge')
    # Memory influence should not directly decide the final action (action selection unchanged)
    assert dec3.selected_action == dec_no_mal.selected_action

    # provenance chain check: MeaningFrame -> Evidence.ref -> StateInstance -> SystemMemory.memory_id -> supporting_memory_refs
    # Find an Event1 meaning and ensure its id appears in linked state's evidence refs
    e1_meaning_ids = [m.id for m in meanings1]
    ev_refs = [e.ref for e in linked.evidence]
    assert any(mid in ev_refs for mid in e1_meaning_ids), "At least one Event1 Meaning.id must appear in the linked state's evidence refs"
    # Confirm the state's id appears as memory_id in system memory history
    assert any((learned.get('memory_id') == linked.id) or ((learned.get('memory_ref') or {}).get('state_id') == linked.id) for learned in learned_events)


def test_find_related_meanings_returns_empty_on_no_history():
    sm = SystemMemory()
    res = sm.find_related_meanings(['threat'], 'no_one')
    assert res == []
