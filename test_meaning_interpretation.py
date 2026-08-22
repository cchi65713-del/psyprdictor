from meaning_interpretation import interpret, meaning_to_evidence, _memory_support_score
from perception_appraisal_expectations import Appraisal, AppraisalFrame, EvidenceRecord as PercepEvidence, Expectations, Prediction
from person_state import PersonState
from system_memory import SystemMemory
from decision_engine import DecisionEngine


class StubMemory:
    def __init__(self, matches=None):
        self._matches = matches or []

    def find_related_meanings(self, tags, person_id, time_window_seconds=None, limit=5, current_dimensions=None):
        return self._matches[:limit]


def make_threat_appraisal():
    frame = AppraisalFrame(
        id="app-frm-1",
        label="threat",
        dimension_scores={"social_threat": 0.95, "goal_relevance": 0.8, "valence": -0.9},
        supporting_perceptions=["per-1"],
        evidence=[PercepEvidence(field="utterance", value="You always act like you're broke and useless", source="trigger", note="insult")],
        confidence=0.85,
        manual=False,
    )
    return Appraisal(id="app-1", timestamp="t", source="trigger", frames=[frame], confidence=0.85)


def test_public_money_embarrassment_personA():
    appraisal = make_threat_appraisal()
    expectations = Expectations(id="ex-1", timestamp="t", source="trigger", predictions=[], confidence=0.0)

    p = PersonState(person_id="A")
    p.goals = ["financial independence"]
    p.values = []

    result = interpret(appraisal, expectations, p, system_memory=None)

    labels = [m.interpretation for m in result.meaning_frames]
    assert "humiliation" in labels
    assert "challenge" in labels

    # challenge should include motivation suggestion
    chal = next((m for m in result.meaning_frames if m.interpretation == "challenge"), None)
    assert chal is not None
    ds = chal.derived_state_suggestions
    assert "motivation" in ds.get("activate", [])

    # provenance preserved
    hum = next((m for m in result.meaning_frames if m.interpretation == "humiliation"), None)
    assert hum is not None
    assert hum.provenance and hum.provenance.get("appraisal_frame_ids")


def test_public_money_embarrassment_personB_with_memory():
    appraisal = make_threat_appraisal()
    expectations = Expectations(id="ex-1", timestamp="t", source="trigger", predictions=[], confidence=0.0)

    p = PersonState(person_id="B")
    p.goals = []
    p.values = []

    # memory indicates past shaming events
    stub = StubMemory(matches=[{"memory_id": "m-shame-1", "matching_tags": ["threat"], "timestamp": "old", "relevance_score": 0.9}])

    result = interpret(appraisal, expectations, p, system_memory=stub)
    labels = [m.interpretation for m in result.meaning_frames]

    assert "humiliation" in labels
    # humiliation confidence should be relatively high when memory matches
    hum = next((m for m in result.meaning_frames if m.interpretation == "humiliation"), None)
    assert hum is not None
    assert hum.supporting_memory_refs
    assert hum.confidence > 0


def test_memory_influences_meaningframe_without_becoming_decisional():
    appraisal = make_threat_appraisal()
    expectations = Expectations(id="ex-1", timestamp="t", source="trigger", predictions=[], confidence=0.0)

    no_memory_person = PersonState(person_id="C")
    no_memory_person.goals = []
    no_memory_person.values = []

    memory_person = PersonState(person_id="C")
    memory_person.goals = []
    memory_person.values = []
    stub = StubMemory(matches=[
        {"memory_id": "m-shame-1", "matching_tags": ["threat"], "timestamp": "old", "relevance_score": 0.9},
        {"memory_id": "m-shame-2", "matching_tags": ["threat"], "timestamp": "older", "relevance_score": 0.75},
    ])

    no_memory_result = interpret(appraisal, expectations, no_memory_person, system_memory=None)
    memory_result = interpret(appraisal, expectations, memory_person, system_memory=stub)

    hum_no_memory = next((m for m in no_memory_result.meaning_frames if m.interpretation == "humiliation"), None)
    hum_with_memory = next((m for m in memory_result.meaning_frames if m.interpretation == "humiliation"), None)

    assert hum_no_memory is not None
    assert hum_with_memory is not None
    assert hum_with_memory.supporting_memory_refs
    assert hum_with_memory.personal_relevance > hum_no_memory.personal_relevance
    assert hum_with_memory.confidence > hum_no_memory.confidence
    assert hum_with_memory.persistence_hint == "sustained"
    assert hum_with_memory.provenance.get("memory_influence", 0.0) > 0.0
    assert any(value > 0.5 for value in hum_with_memory.derived_state_suggestions.get("dims", {}).values())


def test_memory_support_score_is_bounded_and_stable_after_cap():
    strong_matches = [
        {"memory_id": f"m-cap-{i}", "matching_tags": ["threat"], "timestamp": "old", "relevance_score": 0.95}
        for i in range(10)
    ]

    support_3 = _memory_support_score(strong_matches[:3])
    support_10 = _memory_support_score(strong_matches)
    assert 0.0 <= support_3 <= 1.0
    assert 0.0 <= support_10 <= 1.0
    assert abs(support_10 - support_3) < 1e-9
    assert support_10 == 1.0

    appraisal = make_threat_appraisal()
    expectations = Expectations(id="ex-1", timestamp="t", source="trigger", predictions=[], confidence=0.0)
    person = PersonState(person_id="cap")
    person.goals = []
    person.values = []

    result = interpret(appraisal, expectations, person, system_memory=StubMemory(matches=strong_matches))
    hum = next((m for m in result.meaning_frames if m.interpretation == "humiliation"), None)
    assert hum is not None
    assert 0.0 <= hum.personal_relevance <= 1.0
    assert 0.0 <= hum.confidence <= 1.0
    assert 0.0 <= hum.provenance.get("memory_influence", 0.0) <= 1.0
    dims = hum.derived_state_suggestions.get("dims", {})
    assert dims
    assert all(0.0 <= float(v) <= 1.0 for v in dims.values())


def test_weak_or_unrelated_memory_does_not_significantly_strengthen_interpretation():
    appraisal = make_threat_appraisal()
    expectations = Expectations(id="ex-1", timestamp="t", source="trigger", predictions=[], confidence=0.0)

    base_person = PersonState(person_id="base")
    base_person.goals = []
    base_person.values = []
    base_result = interpret(appraisal, expectations, base_person, system_memory=None)
    base_hum = next((m for m in base_result.meaning_frames if m.interpretation == "humiliation"), None)
    assert base_hum is not None

    weak_person = PersonState(person_id="weak")
    weak_person.goals = []
    weak_person.values = []
    weak_stub = StubMemory(matches=[{"memory_id": "m-weak", "matching_tags": ["threat"], "timestamp": "old", "relevance_score": 0.12}])
    weak_result = interpret(appraisal, expectations, weak_person, system_memory=weak_stub)
    weak_hum = next((m for m in weak_result.meaning_frames if m.interpretation == "humiliation"), None)
    assert weak_hum is not None
    assert weak_hum.supporting_memory_refs
    assert weak_hum.personal_relevance <= base_hum.personal_relevance + 0.25
    assert weak_hum.confidence <= base_hum.confidence + 0.20
    assert weak_hum.provenance.get("memory_influence", 0.0) < 0.45

    unrelated_memory = SystemMemory()
    unrelated_memory.add_history("other_person", {
        "type": "state_learning",
        "memory_id": "unrelated-memory",
        "canonical_name": "unrelated",
        "memory_ref": {"state_id": "unrelated-memory", "reinforced": True},
    })
    unrelated_result = interpret(appraisal, expectations, PersonState(person_id="current"), system_memory=unrelated_memory)
    unrelated_hum = next((m for m in unrelated_result.meaning_frames if m.interpretation == "humiliation"), None)
    assert unrelated_hum is not None
    assert not unrelated_hum.supporting_memory_refs
    assert unrelated_hum.provenance.get("memory_influence", 0.0) == 0.0


def test_memory_influence_is_non_decisional_for_action_selection():
    appraisal = make_threat_appraisal()
    expectations = Expectations(id="ex-1", timestamp="t", source="trigger", predictions=[], confidence=0.0)

    memory_store = SystemMemory()
    memory_store.add_history("person_mem", {
        "type": "state_learning",
        "memory_id": "m-decide-1",
        "canonical_name": "threat",
        "memory_ref": {"state_id": "m-decide-1", "reinforced": True},
    })

    person_mem = PersonState(person_id="person_mem")
    person_mem.goals = ["financial independence"]
    person_mem.values = []
    person_mem.trigger = {'event_type': 'verbal_attack', 'text': "You never had money and you are useless", 'voice_volume': 80, 'proximity': 0.9}

    mem_engine = DecisionEngine(system_memory=memory_store, enable_mal=True)
    mem_decision = mem_engine.decide(person_mem, person_id=person_mem.person_id, current_context='public_challenge')
    mem_meanings = getattr(person_mem, 'meanings', []) or []
    assert any(getattr(m, 'supporting_memory_refs', []) for m in mem_meanings)
    assert len(mem_decision.all_proposals) > 0

    person_base = PersonState(person_id="person_mem")
    person_base.goals = ["financial independence"]
    person_base.values = []
    person_base.trigger = person_mem.trigger

    no_mem_engine = DecisionEngine(system_memory=SystemMemory(), enable_mal=False)
    no_mem_decision = no_mem_engine.decide(person_base, person_id=person_base.person_id, current_context='public_challenge')

    assert mem_decision.selected_action == no_mem_decision.selected_action
    assert len(no_mem_decision.all_proposals) > 0


def test_meaning_to_evidence_preserves_ref():
    appraisal = make_threat_appraisal()
    p = PersonState(person_id="A")
    p.goals = ["financial independence"]
    res = interpret(appraisal, None, p)
    mf = next((m for m in res.meaning_frames if m.interpretation == "challenge"), None)
    assert mf is not None
    evs = meaning_to_evidence(mf)
    assert evs
    for e in evs:
        assert e.ref == mf.id


def _build_person_a():
    p = PersonState(person_id="A")
    p.goals = ["financial independence", "prove_self", "status"]
    p.values = ["achievement", "self_respect"]
    p.history = {"previous_successes": 3, "money_trauma": False}
    p.perceived_control = 0.8
    return p


def _build_person_b():
    p = PersonState(person_id="B")
    p.goals = ["avoid_shame"]
    p.values = ["security", "belonging"]
    p.history = {"money_trauma": True, "shame_events": 4}
    p.perceived_control = 0.2
    return p


def test_same_event_different_people_produce_different_meanings():
    appraisal = make_threat_appraisal()
    person_a = _build_person_a()
    person_b = _build_person_b()

    result_a = interpret(appraisal, None, person_a)
    result_b = interpret(appraisal, None, person_b)

    labels_a = {item.interpretation for item in result_a.meaning_frames}
    labels_b = {item.interpretation for item in result_b.meaning_frames}

    assert "challenge" in labels_a
    assert "opportunity" in labels_a or "need_to_prove_self" in labels_a
    assert "humiliation" in labels_b
    assert "rejection" in labels_b or "inadequacy" in labels_b
    assert labels_a != labels_b


def test_mixed_meanings_can_coexist():
    appraisal = make_threat_appraisal()
    person = _build_person_a()
    result = interpret(appraisal, None, person)

    labels = {item.interpretation for item in result.meaning_frames}
    assert "humiliation" in labels
    assert "challenge" in labels

    challenge = next(item for item in result.meaning_frames if item.interpretation == "challenge")
    humiliation = next(item for item in result.meaning_frames if item.interpretation == "humiliation")

    challenge_suggests = set(challenge.derived_state_suggestions.get("activate", []))
    humiliation_suggests = set(humiliation.derived_state_suggestions.get("activate", []))
    assert "motivation" in challenge_suggests
    assert "sadness" in humiliation_suggests or "embarrassment" in humiliation_suggests


def test_meaning_decay_over_time():
    from meaning_interpretation import decay_meaning_influence

    appraisal = make_threat_appraisal()
    person = _build_person_a()
    result = interpret(appraisal, None, person)
    challenge = next(item for item in result.meaning_frames if item.interpretation == "challenge")

    original = challenge.personal_relevance * challenge.confidence
    decayed = decay_meaning_influence(challenge, elapsed_seconds=86400, half_life_seconds=43200)
    assert decayed < original
    assert decayed > 0.0


def test_self_report_is_supporting_evidence_not_absolute_truth():
    appraisal = make_threat_appraisal()
    person = _build_person_a()
    person.self_reports = ["I felt embarrassed but it motivated me."]

    result = interpret(appraisal, None, person)
    challenge = next(item for item in result.meaning_frames if item.interpretation == "challenge")
    evidence = challenge.evidence
    self_report = next((entry for entry in evidence if isinstance(entry, dict) and entry.get("source") == "self_report"), None)
    assert self_report is not None
    assert self_report.get("accepted_as_truth") is False
    assert challenge.provenance.get("meaning_frame_id") == challenge.id


def test_explainability_chain_preserves_provenance_and_ref():
    appraisal = make_threat_appraisal()
    person = _build_person_a()
    result = interpret(appraisal, None, person)
    challenge = next(item for item in result.meaning_frames if item.interpretation == "challenge")

    assert challenge.provenance.get("perception_ids")
    assert challenge.provenance.get("appraisal_frame_ids")
    assert challenge.provenance.get("meaning_frame_id") == challenge.id

    evs = meaning_to_evidence(challenge)
    assert evs
    for ev in evs:
        assert ev.ref == challenge.id
        assert ev.source == "meaning"


if __name__ == "__main__":
    test_public_money_embarrassment_personA()
    test_public_money_embarrassment_personB_with_memory()
    test_meaning_to_evidence_preserves_ref()
    test_same_event_different_people_produce_different_meanings()
    test_mixed_meanings_can_coexist()
    test_meaning_decay_over_time()
    test_self_report_is_supporting_evidence_not_absolute_truth()
    test_explainability_chain_preserves_provenance_and_ref()
    print("meaning_interpretation tests passed")
