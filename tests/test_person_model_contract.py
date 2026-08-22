from person_state import PersonState
from person_model_contract import PersonModelContract


def test_person_model_contract_exposes_canonical_layers():
    model = PersonModelContract()

    assert set(model.layers.keys()) == {"stable", "semi_stable", "dynamic", "learning", "meta"}
    assert "identity" in model.layers["stable"]
    assert "values" in model.layers["stable"]
    assert "needs" in model.layers["semi_stable"]
    assert "appraisal" in model.layers["dynamic"]
    assert "habits" in model.layers["learning"]
    assert "confidence" in model.layers["meta"]


def test_person_state_uses_person_model_contract():
    p = PersonState("p1")

    assert hasattr(p, "person_model")
    assert isinstance(p.person_model, PersonModelContract)
    assert p.person_model.stable["identity"] is p.identity
    assert p.person_model.semi_stable["goals"] is p.active_goals
    assert p.person_model.dynamic["appraisal"] is p.appraisal
