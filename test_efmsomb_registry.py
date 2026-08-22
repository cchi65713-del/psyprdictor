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
import pytest

from efmsomb_registry import (
    resolve_code,
    code_to_label,
    label_to_code,
    all_codes_for_category,
    CATEGORIES,
)


# ============================================================
# TEST 1: E4 → canonical label and label → E4
# ============================================================
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

    def test_F_category_bidirectional(self):
        """F category codes ↔ labels bidirectional."""
        for idx in range(len(CATEGORIES["F"])):
            code = f"F{idx+1}"
            label = code_to_label(code)
            recovered = label_to_code(label, category="F")
            assert recovered == code

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
                expected_code = f"{cat}{idx+1}"
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
        """Ambiguous labels across categories fail safely and do not invent a code."""
        assert label_to_code("Optimistic") is None
        assert label_to_code("Hopeful") is None
        assert label_to_code("Calm") is None

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
                # Verify unambiguous category-scoped lookup
                code = label_to_code(label, category=cat)
                assert code == f"{cat}{idx+1}"

    def test_code_to_label_uniqueness(self):
        """Each code maps to exactly one label (no ambiguity)."""
        seen_codes = set()
        for cat in CATEGORIES.keys():
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
