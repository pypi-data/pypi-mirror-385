"""Tests for name generator."""

import json
import os
import tempfile

from onymancer import (
    generate,
    generate_batch,
    load_language_from_json,
    set_token,
    set_tokens,
    score_pronounceability,
    is_pronounceable,
)


def test_generate_simple() -> None:
    """Test simple name generation."""
    name = generate("s", seed=42)
    assert isinstance(name, str)
    assert len(name) > 0


def test_generate_with_literal() -> None:
    """Test generation with literals."""
    name = generate("s(dim)", seed=42)
    assert "dim" in name


def test_generate_with_capitalization() -> None:
    """Test generation with capitalization."""
    name = generate("!s", seed=42)
    assert name[0].isupper()


def test_generate_with_groups() -> None:
    """Test generation with groups."""
    name = generate("<s|v>", seed=42)
    assert isinstance(name, str)


def test_generate_empty_pattern() -> None:
    """Test generation with empty pattern."""
    name = generate("", seed=42)
    assert name == ""


def test_set_token() -> None:
    """Test setting a token."""
    set_token("x", ["test"])
    name = generate("x", seed=42)
    assert name == "test"


def test_set_tokens() -> None:
    """Test setting multiple tokens."""
    tokens = {"y": ["hello"], "z": ["world"]}
    set_tokens(tokens)
    name1 = generate("y", seed=42)
    name2 = generate("z", seed=42)
    assert name1 == "hello"
    assert name2 == "world"


def test_generate_reproducibility() -> None:
    """Test that same seed produces same result."""
    name1 = generate("s!v", seed=123)
    name2 = generate("s!v", seed=123)
    assert name1 == name2


def test_generate_complex_pattern() -> None:
    """Test complex pattern generation."""
    pattern = "!s<v|c>!C"
    name = generate(pattern, seed=456)
    assert isinstance(name, str)
    assert len(name) > 0


def test_generate_batch_basic() -> None:
    """Test basic batch generation."""
    names = generate_batch("s", count=3, seed=42)
    assert isinstance(names, list)
    assert len(names) == 3
    for name in names:
        assert isinstance(name, str)
        assert len(name) > 0


def test_generate_batch_reproducibility() -> None:
    """Test batch generation reproducibility with seed."""
    names1 = generate_batch("s!v", count=5, seed=123)
    names2 = generate_batch("s!v", count=5, seed=123)
    assert names1 == names2


def test_generate_batch_no_seed() -> None:
    """Test batch generation without seed."""
    names = generate_batch("s", count=2)
    assert len(names) == 2
    for name in names:
        assert isinstance(name, str)


def test_generate_batch_count_zero() -> None:
    """Test batch generation with count 0."""
    names = generate_batch("s", count=0, seed=42)
    assert names == []


def test_generate_batch_min_length() -> None:
    """Test batch generation with minimum length constraint."""
    names = generate_batch("s", count=5, seed=42, min_length=3)
    assert len(names) == 5
    for name in names:
        assert len(name) >= 3


def test_generate_batch_max_length() -> None:
    """Test batch generation with maximum length constraint."""
    names = generate_batch("s!v!c", count=5, seed=42, max_length=5)
    assert len(names) == 5
    for name in names:
        assert len(name) <= 5


def test_generate_batch_length_range() -> None:
    """Test batch generation with both min and max length constraints."""
    names = generate_batch("s!v!c", count=5, seed=42, min_length=2, max_length=8)
    assert len(names) == 5
    for name in names:
        assert 2 <= len(name) <= 8


def test_generate_batch_impossible_constraints() -> None:
    """Test batch generation with impossible length constraints."""
    # Try to get 5 names with min_length=100 (very unlikely)
    names = generate_batch("s", count=5, seed=42, min_length=100)
    # Should return fewer than 5 names if constraints can't be met
    assert len(names) <= 5
    # But any names returned should meet the constraint
    for name in names:
        assert len(name) >= 100


def test_generate_batch_starts_with() -> None:
    """Test batch generation with starts_with constraint."""
    # Use a more common starting letter that should appear in syllables
    names = generate_batch("s!v!c", count=5, seed=42, starts_with="A")
    # May not get exactly 5 names if constraint is restrictive
    assert len(names) <= 5
    for name in names:
        assert name.startswith("A")


def test_generate_batch_ends_with() -> None:
    """Test batch generation with ends_with constraint."""
    # Use a common ending consonant
    names = generate_batch("s!v!c", count=5, seed=42, ends_with="n")
    assert len(names) <= 5
    for name in names:
        assert name.endswith("n")


def test_generate_batch_contains() -> None:
    """Test batch generation with contains constraint."""
    # Use a common vowel
    names = generate_batch("s!v!c", count=5, seed=42, contains="a")
    assert len(names) <= 5
    for name in names:
        assert "a" in name.lower()


def test_generate_batch_multiple_constraints() -> None:
    """Test batch generation with multiple character constraints."""
    # Use constraints that might be possible together
    names = generate_batch("s!v!c", count=5, seed=42, 
                          starts_with="A", ends_with="n", contains="e")
    assert len(names) <= 5
    for name in names:
        assert name.startswith("A")
        assert name.endswith("n")
        assert "e" in name.lower()


def test_generate_batch_combined_constraints() -> None:
    """Test batch generation with both length and character constraints."""
    names = generate_batch("s!v!c", count=5, seed=42,
                          min_length=4, max_length=8,
                          starts_with="A", contains="a")
    assert len(names) <= 5
    for name in names:
        assert 4 <= len(name) <= 8
        assert name.startswith("A")
        assert "a" in name.lower()


def test_generate_batch_impossible_character_constraints() -> None:
    """Test batch generation with impossible character constraints."""
    # Try to get names starting with 'X' - very unlikely with current tokens
    names = generate_batch("s!v!c", count=5, seed=42, starts_with="X")
    # Should return fewer than 5 names or empty list if impossible
    assert len(names) <= 5
    # But any names returned should meet the constraint
    for name in names:
        assert name.startswith("X")


def test_generate_elvish() -> None:
    """Test generation with Elvish language."""
    name = generate("s!v!c", seed=42, language="elvish")
    assert isinstance(name, str)
    assert len(name) > 0
    # Elvish names should contain more liquid consonants
    assert any(char in name.lower() for char in "lr")


def test_generate_elvish_batch() -> None:
    """Test batch generation with Elvish language."""
    names = generate_batch("s!v", count=3, seed=123, language="elvish")
    assert len(names) == 3
    for name in names:
        assert isinstance(name, str)
        assert len(name) > 0


def test_generate_default_language() -> None:
    """Test that default language works."""
    name1 = generate("s", seed=42, language="default")
    name2 = generate("s", seed=42)  # Should be same as default
    assert name1 == name2


def test_generate_unknown_language() -> None:
    """Test generation with unknown language falls back to default."""
    name = generate("s", seed=42, language="unknown")
    assert isinstance(name, str)
    assert len(name) > 0


def test_load_language_from_json() -> None:
    """Test loading a custom language from JSON."""
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"s": ["test"]}, f)
        temp_file = f.name

    try:
        success = load_language_from_json("test_lang", temp_file)
        assert success
        name = generate("s", seed=42, language="test_lang")
        assert name == "test"
    finally:
        os.unlink(temp_file)


def test_load_language_from_json_invalid() -> None:
    """Test loading invalid JSON for language."""
    result = load_language_from_json("test", "nonexistent.json")
    assert result is False


def test_score_pronounceability() -> None:
    """Test pronounceability scoring."""
    # Highly pronounceable names
    assert score_pronounceability("Eldrin") > 0.6
    assert score_pronounceability("Thalia") > 0.7
    assert score_pronounceability("Borogar") > 0.6

    # Moderately pronounceable names
    assert 0.3 < score_pronounceability("Quartz") < 0.8
    assert 0.3 < score_pronounceability("Zephyr") < 0.8

    # Low pronounceability names
    assert score_pronounceability("Brrrgh") < 0.5
    assert score_pronounceability("Xxxzzz") < 0.5
    assert score_pronounceability("Xyzzyx") < 0.2
    assert score_pronounceability("") == 0.0
    assert score_pronounceability("a") == 0.0


def test_is_pronounceable() -> None:
    """Test pronounceability threshold checking."""
    assert is_pronounceable("Eldrin")  # Default threshold 0.6
    assert is_pronounceable("Thalia", threshold=0.8)  # High threshold
    assert not is_pronounceable("Xxxzzz")  # Low score
    assert not is_pronounceable("Xxxzzz", threshold=0.1)  # Low threshold


def test_generate_batch_with_pronounceability() -> None:
    """Test batch generation with pronounceability filtering."""
    # Generate names with high pronounceability requirement
    names = generate_batch("!svs", count=5, seed=42, min_pronounceability=0.7)
    assert len(names) == 5

    # All names should meet the threshold
    for name in names:
        assert score_pronounceability(name) >= 0.7

    # Test with very high threshold (might not find enough names)
    names_strict = generate_batch("!svs", count=10, seed=42, min_pronounceability=0.95)
    # May return fewer than requested if constraints are too strict
    assert len(names_strict) <= 10
    for name in names_strict:
        assert score_pronounceability(name) >= 0.95
