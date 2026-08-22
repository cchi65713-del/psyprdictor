#!/usr/bin/env python3
"""Manual test runner for efmsomb_registry tests (when pytest is unavailable).

This script imports and runs the test functions directly, printing results.
"""
import sys
import traceback

# Import the registry
from efmsomb_registry import (
    resolve_code,
    code_to_label,
    label_to_code,
    all_codes_for_category,
    CATEGORIES,
)

# Counter
passed = 0
failed = 0
errors = []

def run_test(test_name, test_func):
    """Run a single test and report results."""
    global passed, failed, errors
    try:
        test_func()
        print(f"[OK] {test_name}")
        passed += 1
    except AssertionError as e:
        print(f"[FAIL] {test_name}: {e}")
        failed += 1
        errors.append((test_name, e))
    except Exception as e:
        print(f"[FAIL] {test_name}: {type(e).__name__}: {e}")
        failed += 1
        errors.append((test_name, e))

# ============================================================
# TEST 1: E4 → canonical label and label → E4
# ============================================================
def test_E4_code_to_label():
    label = code_to_label("E4")
    assert label == CATEGORIES["E"][3], f"Expected {CATEGORIES['E'][3]}, got {label}"
    assert label == "Anger", f"Expected 'Anger', got {label}"

def test_E4_resolve_code_structure():
    info = resolve_code("E4")
    assert info["category"] == "E"
    assert info["base_code"] == "E4"
    assert info["base_index"] == 3
    assert info["label"] == "Anger"
    assert info["canonical_code"] == "E4"
    assert info["nested"] == []

def test_label_to_E4_exact_case():
    code = label_to_code("Anger")
    assert code == "E4", f"Expected E4, got {code}"

def test_label_to_E4_lowercase():
    code = label_to_code("anger")
    assert code == "E4", f"Expected E4, got {code}"

def test_label_to_E4_uppercase():
    code = label_to_code("ANGER")
    assert code == "E4", f"Expected E4, got {code}"

def test_E4_roundtrip():
    original = "E4"
    label = code_to_label(original)
    recovered = label_to_code(label)
    assert recovered == original

# ============================================================
# TEST 2: All categories bidirectional
# ============================================================
def test_F_category_bidirectional():
    for idx in range(min(3, len(CATEGORIES["F"]))):  # Sample first 3
        code = f"F{idx+1}"
        label = code_to_label(code)
        recovered = label_to_code(label, category="F")
        assert recovered == code, f"F category: {code} -> {label} -> {recovered}"

def test_M_category_bidirectional():
    for idx in range(min(3, len(CATEGORIES["M"]))):
        code = f"M{idx+1}"
        label = code_to_label(code)
        recovered = label_to_code(label, category="M")
        assert recovered == code

def test_S_category_bidirectional():
    for idx in range(min(3, len(CATEGORIES["S"]))):
        code = f"S{idx+1}"
        label = code_to_label(code)
        recovered = label_to_code(label, category="S")
        assert recovered == code

def test_B_category_bidirectional():
    for idx in range(min(3, len(CATEGORIES["B"]))):
        code = f"B{idx+1}"
        label = code_to_label(code)
        recovered = label_to_code(label, category="B")
        assert recovered == code

def test_representative_samples_all_categories():
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
        assert label == CATEGORIES[cat][idx], f"{code}: {label} != {CATEGORIES[cat][idx]}"
        assert label_to_code(label.lower(), category=cat) == code
        assert label_to_code(label.upper(), category=cat) == code
        assert label_to_code(label, category=cat) == code

# ============================================================
# TEST 3: Case normalization
# ============================================================
def test_anger_all_cases_same_code():
    assert label_to_code("anger") == "E4"
    assert label_to_code("Anger") == "E4"
    assert label_to_code("ANGER") == "E4"
    assert label_to_code("aNgEr") == "E4"

def test_case_with_whitespace_normalization():
    assert label_to_code("  anger  ") == "E4"
    assert label_to_code("  ANGER  ") == "E4"

# ============================================================
# TEST 4: Unknown codes raise KeyError
# ============================================================
def test_out_of_range_code_raises():
    try:
        resolve_code("E999")
        raise AssertionError("Should have raised KeyError")
    except KeyError as e:
        assert "out of range" in str(e).lower()

def test_invalid_category_raises():
    try:
        resolve_code("X1")
        raise AssertionError("Should have raised KeyError")
    except KeyError as e:
        assert "unknown category" in str(e).lower()

def test_invalid_numeric_part_raises():
    try:
        resolve_code("EAB")
        raise AssertionError("Should have raised KeyError")
    except KeyError as e:
        assert "invalid" in str(e).lower()

def test_empty_code_raises():
    try:
        resolve_code("")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "invalid code" in str(e).lower()

def test_single_char_code_raises():
    try:
        resolve_code("E")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "invalid code" in str(e).lower()

# ============================================================
# TEST 5: Unknown labels return None
# ============================================================
def test_nonexistent_label_returns_none():
    assert label_to_code("this label does not exist") is None

def test_random_text_returns_none():
    assert label_to_code("xyzabc123") is None

def test_partial_label_returns_none():
    assert label_to_code("Ang") is None

def test_misspelled_label_returns_none():
    assert label_to_code("Angar") is None

def test_unknown_label_with_category_filter_returns_none():
    assert label_to_code("Anger", category="F") is None

# ============================================================
# TEST 6: No duplicates
# ============================================================
def test_no_duplicate_codes_per_category():
    for cat in CATEGORIES.keys():
        codes = all_codes_for_category(cat)
        unique_codes = set(codes)
        assert len(codes) == len(unique_codes), f"Duplicates in {cat}"

def test_all_labels_unique_per_category():
    for cat in CATEGORIES.keys():
        labels = CATEGORIES[cat]
        normalized = [l.lower().strip() for l in labels]
        unique = set(normalized)
        assert len(normalized) == len(unique), f"Duplicate labels in {cat}"

def test_code_to_label_uniqueness():
    for cat in CATEGORIES.keys():
        for idx, label in enumerate(CATEGORIES[cat]):
            code = label_to_code(label, category=cat)
            assert code == f"{cat}{idx+1}", f"Collision: {label}"

# ============================================================
# TEST 7: Compatibility
# ============================================================
def test_taxonomy_module_imports():
    import efmsomb_taxonomy
    assert hasattr(efmsomb_taxonomy, "EmotionState")

def test_registry_does_not_modify_categories():
    assert set(CATEGORIES.keys()) == {"E", "F", "M", "S", "B"}
    for cat, items in CATEGORIES.items():
        assert len(items) > 0

# ============================================================
# RUN ALL TESTS
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("EFMSOMB Registry Manual Test Runner")
    print("="*60)
    print()

    test_groups = [
        ("E4 Bidirectional Mapping", [
            ("E4 code_to_label", test_E4_code_to_label),
            ("E4 resolve_code structure", test_E4_resolve_code_structure),
            ("label_to_E4 exact case", test_label_to_E4_exact_case),
            ("label_to_E4 lowercase", test_label_to_E4_lowercase),
            ("label_to_E4 uppercase", test_label_to_E4_uppercase),
            ("E4 roundtrip", test_E4_roundtrip),
        ]),
        ("All Categories Bidirectional", [
            ("F category bidirectional", test_F_category_bidirectional),
            ("M category bidirectional", test_M_category_bidirectional),
            ("S category bidirectional", test_S_category_bidirectional),
            ("B category bidirectional", test_B_category_bidirectional),
            ("Representative samples", test_representative_samples_all_categories),
        ]),
        ("Case Normalization", [
            ("Anger all cases", test_anger_all_cases_same_code),
            ("Whitespace normalization", test_case_with_whitespace_normalization),
        ]),
        ("Unknown Code Handling", [
            ("Out of range raises", test_out_of_range_code_raises),
            ("Invalid category raises", test_invalid_category_raises),
            ("Invalid numeric raises", test_invalid_numeric_part_raises),
            ("Empty code raises", test_empty_code_raises),
            ("Single char raises", test_single_char_code_raises),
        ]),
        ("Unknown Label Handling", [
            ("Nonexistent label None", test_nonexistent_label_returns_none),
            ("Random text None", test_random_text_returns_none),
            ("Partial label None", test_partial_label_returns_none),
            ("Misspelled label None", test_misspelled_label_returns_none),
            ("Wrong category None", test_unknown_label_with_category_filter_returns_none),
        ]),
        ("No Duplicates", [
            ("No duplicate codes", test_no_duplicate_codes_per_category),
            ("All labels unique", test_all_labels_unique_per_category),
            ("Code to label unique", test_code_to_label_uniqueness),
        ]),
        ("Compatibility", [
            ("Taxonomy imports", test_taxonomy_module_imports),
            ("Categories unchanged", test_registry_does_not_modify_categories),
        ]),
    ]

    for group_name, tests in test_groups:
        print(f"\n{group_name}")
        print("-" * 60)
        for test_name, test_func in tests:
            run_test(test_name, test_func)

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    if failed > 0:
        print("\nFailed tests:")
        for test_name, error in errors:
            print(f"  - {test_name}: {error}")
        sys.exit(1)
    else:
        sys.exit(0)
