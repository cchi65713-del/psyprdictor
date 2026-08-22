from person_state import PersonState


def test_person_state_populates_actual_identity():
    person = PersonState(person_id="p1")
    person.value_weights = {"respect": 0.9, "safety": 0.8}
    person.beliefs = {"explicit": ["Respect must be defended"]}
    person.identity["relationships"] = ["Difficult relationship"]

    identity = person.fill_actual_identity(
        name="Ava",
        roles={"defender": 0.9, "student": 0.6},
        standards=["Respect", "Boundaries"],
    )

    assert identity["person_id"] == "p1"
    assert identity["name"] == "Ava"
    assert identity["roles"]["defender"] == 0.9
    assert identity["standards"] == ["Respect", "Boundaries"]
    assert identity["values"] == ["respect", "safety"]
    assert identity["beliefs"] == ["Respect must be defended"]
    assert identity["relationships"] == ["Difficult relationship"]
    assert person.identity_schema is person.identity
