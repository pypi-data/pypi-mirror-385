"""Procedural fantasy name generation library."""

from .namegen import (
    generate,
    generate_batch,
    load_language_from_json,
    set_token,
    set_tokens,
)
from .pronounceability import (
    score_pronounceability,
    is_pronounceable,
)

__all__ = [
    "generate",
    "generate_batch",
    "load_language_from_json",
    "set_token",
    "set_tokens",
    "score_pronounceability",
    "is_pronounceable",
]
