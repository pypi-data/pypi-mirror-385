"""Fantasy name generator module."""

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

from .pronounceability import score_pronounceability

# Global token map
_token_map: dict[str, list[str]] = {}

# Data directory
_data_dir = Path(__file__).parent / "data"

# Load language token sets from JSON files
_language_tokens: dict[str, dict[str, list[str]]] = {}
for lang_file in _data_dir.glob("*.json"):
    lang = lang_file.stem
    with open(lang_file, encoding="utf-8") as f:
        _language_tokens[lang] = json.load(f)

# Initialize with default tokens
_token_map.update(_language_tokens["default"])


@dataclass
class _OptionT:
    """
    Struct that encapsulates all the state options.

    Attributes:
        capitalize (bool):
            Whether to capitalize the next character.
        emit_literal (bool):
            Whether to emit characters as literals.
        inside_group (bool):
            Whether currently inside a group.
        current_option (str):
            The current option being built.
        options (list[str]):
            The list of options in the current group.
        language (str):
            The language token set to use.

    """

    capitalize: bool = field(
        default=False,
        metadata={"description": "Whether to capitalize the next character."},
    )
    emit_literal: bool = field(
        default=False,
        metadata={"description": "Whether to emit characters as literals."},
    )
    inside_group: bool = field(
        default=False, metadata={"description": "Whether currently inside a group."}
    )
    current_option: str = field(
        default="", metadata={"description": "The current option being built."}
    )
    options: list[str] = field(
        default_factory=list,
        metadata={"description": "The list of options in the current group."},
    )
    language: str = field(
        default="default",
        metadata={"description": "The language token set to use."},
    )


def _capitalize_and_clear(options: _OptionT, character: str) -> str:
    """
    Capitalize the given character if capitalize is True.

    Args:
        options:
            The current state options.
        character:
            The input character.

    Returns:
        str:
            The capitalized character if capitalize is True, else the original.

    """
    if options.capitalize:
        options.capitalize = False
        return character.upper()
    return character


def _process_token(options: _OptionT, buffer: list[str], key: str) -> bool:
    """
    Process a token based on the provided key and append it to the buffer.

    Args:
        options:
            The current state options.
        buffer:
            The string buffer where the processed token will be appended.
        key:
            The key representing the type of token to process.

    Returns:
        bool:
            True on success, False otherwise.

    """
    if options.language == "default":
        tokens = _token_map.get(key, [])
    else:
        token_map = _language_tokens.get(options.language, {})
        tokens = token_map.get(key, [])
    if not tokens:
        buffer.append(_capitalize_and_clear(options, key))
    else:
        token = random.choice(tokens)
        it = iter(token)
        first_char = next(it, "")
        buffer.append(_capitalize_and_clear(options, first_char))
        buffer.extend(it)
    return True


def _process_character(
    options: _OptionT,
    buffer: list[str],
    character: str,
) -> bool:
    """
    Process a character from the pattern and append it to the buffer.

    Args:
        options:
            The current state options.
        buffer:
            The string buffer where the processed character will be appended.
        character:
            The character to process.

    Returns:
        bool:
            True on success, False otherwise.

    """
    if character == "(":
        if options.inside_group:
            options.current_option += character
        else:
            options.emit_literal = True
    elif character == ")":
        if options.inside_group:
            options.current_option += character
        else:
            options.emit_literal = False
    elif character == "<":
        options.inside_group = True
        options.options.clear()
        options.current_option = ""
    elif character == "|":
        options.options.append(options.current_option)
        options.current_option = ""
    elif character == ">":
        options.inside_group = False
        options.options.append(options.current_option)
        options.current_option = ""
        # Ensure there's at least one option in the group.
        if not options.options:
            return False
        # Randomly pick an option.
        option = random.choice(options.options)
        # Process and append the selected option.
        for token in option:
            if not _process_character(options, buffer, token):
                return False
        # Clear options after processing the group.
        options.options.clear()
    elif character == "!":
        if options.inside_group:
            options.current_option += character
        else:
            options.capitalize = True
    elif options.inside_group:
        options.current_option += character
    elif options.emit_literal:
        buffer.append(_capitalize_and_clear(options, character))
    elif not _process_token(options, buffer, character):
        return False
    return True


def load_language_from_json(language: str, filename: str) -> bool:
    """
    Load a custom language token set from a JSON file.

    Args:
        language:
            The name of the language to load.
        filename:
            The path to the JSON file containing the token set.

    Returns:
        bool:
            True if the loading was successful, False otherwise.

    """
    try:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False
        _language_tokens[language] = data
        return True
    except (OSError, json.JSONDecodeError):
        return False


def set_token(key: str, tokens: list[str]) -> None:
    """
    Set the token list of a given key in the global token map.

    Args:
        key:
            The key for which to set the token list.
        tokens:
            The list of tokens (strings) to associate with the key.

    """
    _token_map[key] = tokens


def set_tokens(tokens: dict[str, list[str]]) -> None:
    """
    Set a given list of key-value pairs in the global token map.

    Args:
        tokens:
            A map where each key is a character and the value is a list of
            strings (tokens).

    """
    _token_map.update(tokens)


def generate(
    pattern: str,
    seed: int | None = None,
    language: str = "default",
) -> str:
    """
    Generate a random name based on the provided pattern and seed.

    Args:
        pattern (str):
            The pattern defining the structure of the name.
        seed (int | None):
            The seed for random number generation.
        language (str):
            The language token set to use ("default" or "elvish").

    Returns:
        str:
            The generated name.

    """
    # If a seed is provided, seed the random generator.
    if seed is not None:
        random.seed(seed)
    options = _OptionT(language=language)
    buffer: list[str] = []
    for c in pattern:
        if not _process_character(options, buffer, c):
            return ""
    return "".join(buffer)


def generate_batch(
    pattern: str,
    count: int,
    seed: int | None = None,
    language: str = "default",
    min_length: int | None = None,
    max_length: int | None = None,
    starts_with: str | None = None,
    ends_with: str | None = None,
    contains: str | None = None,
    min_pronounceability: float | None = None,
) -> list[str]:
    """
    Generate multiple names using the given pattern.

    Args:
        pattern:
            The pattern to use for generation.
        count:
            Number of names to generate.
        seed:
            Optional seed for reproducibility. If provided, each name uses seed
            + i.
        language:
            The language token set to use ("default" or "elvish").
        min_length:
            Minimum length constraint for generated names. If None, no minimum.
        max_length:
            Maximum length constraint for generated names. If None, no maximum.
        starts_with:
            String that generated names must start with. If None, no restriction.
        ends_with:
            String that generated names must end with. If None, no restriction.
        contains:
            String that generated names must contain. If None, no restriction.
        min_pronounceability:
            Minimum pronounceability score (0.0-1.0) for generated names.
            If None, no pronounceability filtering is applied.

    Returns:
        list[str]:
            List of generated names that meet all specified constraints.
            May return fewer than 'count' names if constraints cannot be satisfied
            within reasonable attempts (to prevent infinite loops).

    Note:
        If character constraints are incompatible with the pattern or token set,
        the function may return fewer names than requested or an empty list.
        For example, requiring names to start with 'X' when the pattern generates
        names starting with syllables that never begin with 'X'.
    """
    # If a seed is provided, seed the random generator.
    if seed is not None:
        random.seed(seed)
    names = []
    attempts = 0
    max_attempts = count * 10  # Prevent infinite loops
    while len(names) < count and attempts < max_attempts:
        # We already seeded the random generator above.
        name = generate(pattern, None, language)
        
        # Check constraints with fail-early pattern
        name_len = len(name)
        
        # Length constraints
        min_violated = min_length is not None and name_len < min_length
        max_violated = max_length is not None and name_len > max_length
        if min_violated or max_violated:
            attempts += 1
            continue
        
        # Character constraints
        if starts_with is not None and not name.startswith(starts_with):
            attempts += 1
            continue
        if ends_with is not None and not name.endswith(ends_with):
            attempts += 1
            continue
        if contains is not None and contains not in name:
            attempts += 1
            continue
        
        # Pronounceability constraint
        if min_pronounceability is not None and \
           score_pronounceability(name) < min_pronounceability:
            attempts += 1
            continue
        
        # All constraints passed
        names.append(name)
        attempts += 1
    return names
