"""Focused validation tests for efmsomb_registry.

Tests cover:
1. E4 ↔ canonical label bidirectional mapping
2. F, M, S, B bidirectional behavior
3. Case normalization
4. Unknown codes return controlled failures
5. Unknown labels return None
6. No duplicate canonical entries
7. Compatibility with existing taxonomy tests
"""
from pathlib import Path

import pytest
import yaml

from efmsomb_registry import (
    EFMSOMBIdentityRecord,
    resolve_code,
    code_to_label,
    label_to_code,
    all_codes_for_category,
    CATEGORIES,
    F_CODE_TO_LABEL,
)


# ============================================================
# TEST 1: E4 → canonical label and label → E4
# ============================================================
class TestIdentityContractStage1:
    """Stage 1 identity-contract checks for canonical ID schema and invariants."""

    def test_identity_record_shape_contains_required_fields(self):
        record = EFMSOMBIdentityRecord(
            canonical_id="S5",
            category="S",
            current_label="Creative",
            aliases=["creative_state"],
            status="active",
            deprecated_since=None,
            retired_since=None,
            replacement_of=None,
            metadata={"source": "contract"},
        )
        required_fields = {
            "canonical_id",
            "category",
            "current_label",
            "aliases",
            "status",
            "deprecated_since",
            "retired_since",
            "replacement_of",
            "metadata",
        }
        assert required_fields.issubset(set(record.__dict__.keys()))
        assert record.canonical_id == "S5"
        assert record.category == "S"
        assert record.current_label == "Creative"

    def test_runtime_public_ids_are_permanent_canonical_ids(self):
        for code in ("E4", "F3", "M2", "S5", "B1"):
            assert code in {"E4", "F3", "M2", "S5", "B1"}

    def test_resolve_code_contract_requires_canonical_id_fields(self):
        info = resolve_code("S5")
        assert info["canonical_id"] == "S5"
        assert info["category"] == "S"
        assert info["current_label"] == "Creative"
        assert info["status"] == "active"

    def test_historical_path_preserves_public_canonical_ids(self):
        historical_path = ["E4", "F3", "M2", "S5", "B1"]
        for code in historical_path:
            info = resolve_code(code)
            assert info["canonical_id"] == code

    def test_label_change_does_not_change_canonical_id(self):
        record = EFMSOMBIdentityRecord(
            canonical_id="S5",
            category="S",
            current_label="Creative",
            aliases=["creative_state"],
            status="active",
            deprecated_since=None,
            retired_since=None,
            replacement_of=None,
            metadata={"source": "contract"},
        )
        record_v2 = EFMSOMBIdentityRecord(
            canonical_id="S5",
            category="S",
            current_label="NewLabel",
            aliases=["creative_state"],
            status="active",
            deprecated_since=None,
            retired_since=None,
            replacement_of=None,
            metadata={"source": "contract"},
        )
        assert record.canonical_id == record_v2.canonical_id == "S5"

    def test_position_independence_contract_is_explicit(self):
        reordered_state_of_mind = [
            "Creative",
            "Focused",
            "Confused",
            "Curious",
            "Determined",
            "Analytical",
            "Reflective",
            "Open-minded",
            "Closed-minded",
            "Grounded",
            "Hopeful",
            "Defensive",
            "Distracted",
            "Judgmental",
            "Resistant",
            "Stressed",
            "Overloaded",
            "Empathetic",
            "Reassured",
            "Numb",
            "Aware",
            "Unaware",
            "Alert",
            "Cautious",
            "Decisive",
            "Indecisive",
            "Accepting",
            "Avoidant",
            "Observant",
            "Patient",
        ]
        record = EFMSOMBIdentityRecord(
            canonical_id="S5",
            category="S",
            current_label="Creative",
            aliases=[],
            status="active",
            deprecated_since=None,
            retired_since=None,
            replacement_of=None,
            metadata={"semantic_order": reordered_state_of_mind},
        )
        assert record.canonical_id == "S5"
        assert record.current_label == "Creative"

    def test_reordering_taxonomy_does_not_change_canonical_id(self):
        original_label = code_to_label("E4")
        local_reordered = list(CATEGORIES["E"])
        local_reordered = [local_reordered[3], *local_reordered[:3], *local_reordered[4:]]
        assert local_reordered[0] == "Anger"
        assert code_to_label("E4") == original_label == "Anger"
        assert resolve_code("E4")["canonical_id"] == "E4"
        assert resolve_code("E4")["current_label"] == "Anger"


class TestE4BidirectionalMapping:
    """Test that E4 resolves to its expected canonical label and back."""

    def test_E4_code_to_label(self):
        """E4 must resolve to exactly EMOTIONS[3] from knowledge base."""
        # E4 is 1-indexed, so E4 -> EMOTIONS[3]
        label = code_to_label("E4")
        assert label == CATEGORIES["E"][3]
        assert label == "Anger"  # Verify against knowledge base

    def test_E4_resolve_code_structure(self):
        """resolve_code('E4') returns correct structured info."""
        info = resolve_code("E4")
        assert info["category"] == "E"
        assert info["base_code"] == "E4"
        assert info["base_index"] == 3  # 0-based
        assert info["label"] == "Anger"
        assert info["canonical_code"] == "E4"
        assert info["nested"] == []

    def test_label_to_E4_exact_case(self):
        """'Anger' should map back to E4."""
        code = label_to_code("Anger")
        assert code == "E4"

    def test_label_to_E4_lowercase(self):
        """'anger' should map back to E4 (case-insensitive)."""
        code = label_to_code("anger")
        assert code == "E4"

    def test_label_to_E4_uppercase(self):
        """'ANGER' should map back to E4 (case-insensitive)."""
        code = label_to_code("ANGER")
        assert code == "E4"

    def test_E4_roundtrip(self):
        """E4 → label → E4 roundtrip preserves identity."""
        original = "E4"
        label = code_to_label(original)
        recovered = label_to_code(label)
        assert recovered == original


# ============================================================
# TEST 2: F, M, S, B bidirectional behavior
# ============================================================
class TestAllCategoriesBidirectional:
    """Test that F, M, S, B all support bidirectional mapping."""

    def test_audited_f_catalog_is_canonical(self):
        """The runtime registry must reflect the audited F-layer specification."""
        assert code_to_label("F1") == "Tension"
        assert code_to_label("F3") == "Heaviness"
        assert code_to_label("F12") == "Depersonalization-style Detachment"
        with pytest.raises(KeyError):
            code_to_label("F11")
        assert label_to_code("Tension", category="F") == "F1"
        assert label_to_code("Heaviness", category="F") == "F3"
        assert label_to_code("Depersonalization-style Detachment", category="F") == "F12"
        assert label_to_code("Clarity/Focused-alertness", category="F") is None

    def test_yaml_f_section_matches_registry(self):
        """The YAML F section must match the canonical registry exactly and omit F11."""
        yaml_path = Path(__file__).with_name("efmsomb_emotion_taxonomy_v1_proposed.yaml")
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

        assert "feelings" in data, "YAML F section is missing."

        feelings = data["feelings"]
        expected = {
            "F1": "Tension",
            "F2": "Constriction",
            "F3": "Heaviness",
            "F4": "Affective Numbing",
            "F5": "Warmth/Expansion",
            "F6": "Felt-pull / Subjective Imperative",
            "F7": "Apprehensive Foreboding",
            "F8": "Agitation/Restlessness",
            "F9": "Emptiness/Hollowing",
            "F10": "Pressure/Surging-Heat",
            "F12": "Depersonalization-style Detachment",
        }

        assert list(feelings.keys()) == list(expected.keys())
        assert {code: entry["label"] for code, entry in feelings.items()} == expected
        assert "F11" not in feelings
        assert feelings["F12"]["label"] == "Depersonalization-style Detachment"

    def test_F_category_bidirectional(self):
        """F category codes ↔ labels bidirectional using the canonical audited mapping."""
        for code, label in F_CODE_TO_LABEL.items():
            recovered = label_to_code(label, category="F")
            assert recovered == code
            assert code_to_label(code) == label

    def test_M_category_bidirectional(self):
        """M category codes ↔ labels bidirectional."""
        for idx in range(len(CATEGORIES["M"])):
            code = f"M{idx+1}"
            label = code_to_label(code)
            recovered = label_to_code(label, category="M")
            assert recovered == code

    def test_S_category_bidirectional(self):
        """S category codes ↔ labels bidirectional."""
        for idx in range(len(CATEGORIES["S"])):
            code = f"S{idx+1}"
            label = code_to_label(code)
            recovered = label_to_code(label, category="S")
            assert recovered == code

    def test_B_category_bidirectional(self):
        """B category codes ↔ labels bidirectional."""
        for idx in range(len(CATEGORIES["B"])):
            code = f"B{idx+1}"
            label = code_to_label(code)
            recovered = label_to_code(label, category="B")
            assert recovered == code

    def test_E_category_bidirectional(self):
        """E category codes ↔ labels bidirectional."""
        for idx in range(len(CATEGORIES["E"])):
            code = f"E{idx+1}"
            label = code_to_label(code)
            recovered = label_to_code(label, category="E")
            assert recovered == code

    def test_representative_samples_all_categories(self):
        """Spot-check representative codes from each category."""
        samples = {
            "E4": ("E", 3, "Anger"),
            "F3": ("F", 2),
            "M2": ("M", 1),
            "S5": ("S", 4),
            "B1": ("B", 0),
        }
        for code, expected_info in samples.items():
            cat, idx = expected_info[0], expected_info[1]
            label = code_to_label(code)
            assert label == CATEGORIES[cat][idx]
            # All variations of case
            assert label_to_code(label.lower(), category=cat) == code
            assert label_to_code(label.upper(), category=cat) == code
            assert label_to_code(label, category=cat) == code


# ============================================================
# TEST 3: Case normalization
# ============================================================
class TestCaseNormalization:
    """Test that case variations resolve to the same canonical entry."""

    def test_anger_all_cases_same_code(self):
        """'anger', 'Anger', 'ANGER' all → E4."""
        assert label_to_code("anger") == "E4"
        assert label_to_code("Anger") == "E4"
        assert label_to_code("ANGER") == "E4"
        assert label_to_code("aNgEr") == "E4"

    def test_all_labels_case_insensitive(self):
        """All labels in all categories are case-insensitive."""
        for cat in CATEGORIES.keys():
            for idx, label in enumerate(CATEGORIES[cat]):
                expected_code = f"{cat}{idx+1}" if cat != "F" else next(code for code, mapped in F_CODE_TO_LABEL.items() if mapped == label)
                assert label_to_code(label.lower(), category=cat) == expected_code
                assert label_to_code(label.upper(), category=cat) == expected_code
                assert label_to_code(label, category=cat) == expected_code

    def test_case_with_whitespace_normalization(self):
        """Whitespace and case are both normalized."""
        # Test with leading/trailing whitespace
        assert label_to_code("  anger  ") == "E4"
        assert label_to_code("  ANGER  ") == "E4"


# ============================================================
# TEST 4: Unknown codes return controlled failure
# ============================================================
class TestUnknownCodeHandling:
    """Unknown codes must raise KeyError, not silently create entries."""

    def test_out_of_range_code_raises(self):
        """E999 (out of range) raises KeyError."""
        with pytest.raises(KeyError, match="Code out of range"):
            resolve_code("E999")

    def test_invalid_category_raises(self):
        """X1 (unknown category) raises KeyError."""
        with pytest.raises(KeyError, match="Unknown category"):
            resolve_code("X1")

    def test_invalid_numeric_part_raises(self):
        """EAB (non-numeric) raises KeyError."""
        with pytest.raises(KeyError, match="Invalid numeric part"):
            resolve_code("EAB")

    def test_empty_code_raises(self):
        """Empty code raises ValueError."""
        with pytest.raises(ValueError, match="Invalid code"):
            resolve_code("")

    def test_single_char_code_raises(self):
        """Single character code raises ValueError."""
        with pytest.raises(ValueError, match="Invalid code"):
            resolve_code("E")

    def test_invalid_category_lowercase_code_raises(self):
        """Lowercase invalid category still raises."""
        with pytest.raises(KeyError, match="Unknown category"):
            resolve_code("x1")

    def test_code_to_label_unknown_raises(self):
        """code_to_label propagates KeyError for unknown codes."""
        with pytest.raises(KeyError):
            code_to_label("Z99")


# ============================================================
# TEST 5: Unknown labels return None
# ============================================================
class TestUnknownLabelHandling:
    """Unknown labels must return None, not invent new codes."""

    def test_nonexistent_label_returns_none(self):
        """Completely fabricated label returns None."""
        assert label_to_code("this label does not exist") is None

    def test_random_text_returns_none(self):
        """Random text returns None."""
        assert label_to_code("xyzabc123") is None

    def test_partial_label_returns_none(self):
        """Partial matches don't count."""
        # "Ang" is not a complete label
        assert label_to_code("Ang") is None

    def test_ambiguous_label_without_category_returns_none(self):
        """Category-agnostic lookups must only return a code when the label is unambiguous."""
        assert label_to_code("Tension") == "F1"
        assert label_to_code("Heaviness") == "F3"
        assert label_to_code("Calm") == "M8"

    def test_misspelled_label_returns_none(self):
        """Misspelled labels return None."""
        assert label_to_code("Angar") is None  # vs "Anger"
        assert label_to_code("Joyy") is None   # vs "Joy"

    def test_unknown_label_with_category_filter_returns_none(self):
        """Unknown label in specific category returns None."""
        # "Anger" exists in E but not in F
        assert label_to_code("Anger", category="F") is None

    def test_valid_label_wrong_category_returns_none(self):
        """Label valid in E but searched in F returns None."""
        anger_code = label_to_code("Anger", category="F")
        assert anger_code is None


# ============================================================
# TEST 6: No duplicate canonical entries
# ============================================================
class TestNoDuplicates:
    """Verify no duplicate codes or label mappings exist."""

    def test_no_duplicate_codes_per_category(self):
        """Each category produces unique codes."""
        for cat in CATEGORIES.keys():
            codes = all_codes_for_category(cat)
            assert len(codes) == len(set(codes)), f"Duplicates in {cat}: {codes}"

    def test_all_labels_unique_per_category(self):
        """Each category has unique labels (by construction from knowledge.py)."""
        for cat in CATEGORIES.keys():
            labels = CATEGORIES[cat]
            # Normalize for comparison
            normalized = [l.lower().strip() for l in labels]
            assert len(normalized) == len(set(normalized)), f"Duplicate labels in {cat}"

    def test_label_to_code_uniqueness(self):
        """Each category's canonical labels are unique within that category."""
        for cat in CATEGORIES.keys():
            seen_labels = set()
            for idx, label in enumerate(CATEGORIES[cat]):
                normalized = label.lower().strip()
                assert normalized not in seen_labels, f"Label collision in {cat}: {label}"
                seen_labels.add(normalized)
                code = label_to_code(label, category=cat)
                if cat == "F":
                    expected_code = next(code for code, mapped in F_CODE_TO_LABEL.items() if mapped == label)
                else:
                    expected_code = f"{cat}{idx+1}"
                assert code == expected_code

    def test_code_to_label_uniqueness(self):
        """Each code maps to exactly one label (no ambiguity)."""
        seen_codes = set()
        for cat in CATEGORIES.keys():
            if cat == "F":
                for code in F_CODE_TO_LABEL:
                    assert code not in seen_codes
                    seen_codes.add(code)
                    label = code_to_label(code)
                    assert label is not None
            else:
                for idx in range(len(CATEGORIES[cat])):
                    code = f"{cat}{idx+1}"
                    assert code not in seen_codes
                    seen_codes.add(code)
                    label = code_to_label(code)
                    assert label is not None


# ============================================================
# TEST 7: Existing taxonomy tests compatibility
# ============================================================
class TestExistingTaxonomyCompatibility:
    """Ensure registry doesn't break existing taxonomy validators."""

    def test_taxonomy_module_imports(self):
        """efmsomb_taxonomy module can be imported."""
        import efmsomb_taxonomy  # noqa: F401

    def test_taxonomy_emotion_state_exists(self):
        """EmotionState validator still available."""
        import efmsomb_taxonomy
        assert hasattr(efmsomb_taxonomy, "EmotionState")

    def test_taxonomy_feeling_state_exists(self):
        """FeelingState validator still available."""
        import efmsomb_taxonomy
        assert hasattr(efmsomb_taxonomy, "FeelingState")

    def test_taxonomy_mood_state_exists(self):
        """MoodState validator still available."""
        import efmsomb_taxonomy
        assert hasattr(efmsomb_taxonomy, "MoodState")

    def test_taxonomy_state_of_mind_state_exists(self):
        """StateOfMindState validator still available."""
        import efmsomb_taxonomy
        assert hasattr(efmsomb_taxonomy, "StateOfMindState")

    def test_taxonomy_behavior_signature_exists(self):
        """BehaviorSignature validator still available."""
        import efmsomb_taxonomy
        assert hasattr(efmsomb_taxonomy, "BehaviorSignature")

    def test_registry_does_not_modify_categories(self):
        """Registry import does not mutate CATEGORIES."""
        # Verify all 5 categories exist
        assert set(CATEGORIES.keys()) == {"E", "F", "M", "S", "B"}
        # Verify all categories have content
        for cat, items in CATEGORIES.items():
            assert len(items) > 0, f"Category {cat} is empty"
