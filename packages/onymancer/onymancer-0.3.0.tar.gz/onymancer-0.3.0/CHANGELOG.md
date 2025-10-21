# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-20

### Added

- Pronounceability scoring algorithm and API (`score_pronounceability`,
  `is_pronounceable`) for quality filtering in `generate_batch()` (9caab39)
- Dwarvish language token set with authentic guttural syllables (14a01a1)
- `--min-pronounceability` CLI option and integration with `generate_batch()` (9caab39)
- Expanded elven name patterns with 12 diverse melodic combinations (47e0d52)
- Character restrictions (`starts_with`, `ends_with`, `contains`) to `generate_batch()` (7f124e8)
- Length constraints (`min_length`, `max_length`) to `generate_batch()` (b925230)
- Language support to CLI presets (8c228fd)

### Changed

- Refactored constraint checking to a fail-early pattern for clarity and
  maintainability (b5be6df)

### Fixed

- Updated tests and docs to cover pronounceability scoring and dwarvish
  language support

## [0.2.0] - 2025-10-20

### Added

- `generate_batch()` function for generating multiple names at once (68c020c)
- Elvish language token set with liquid consonants and melodic patterns (68c020c)
- Language selection parameter in `generate()` and `generate_batch()` (68c020c)
- `load_language_from_json()` for loading custom language token sets (b2ac18e)
- Token data moved to JSON files for better maintainability (b2ac18e)

### Changed

- Refactored internal code with dataclasses and improved random handling (68c020c)
- Removed disruptive `load_tokens_from_json()` function (b2ac18e)
- Enhanced docstrings and type hints (68c020c)

### Fixed

- Improved token processing and language switching (68c020c)

## [0.1.0] - 2025-10-17

### Added

- Initial release of Onymancer library
- Procedural fantasy name generation using pattern-based tokens
- Support for various tokens: syllables, vowels, consonants, titles, etc.
- Pattern features: literals with (), groups with <>, capitalization with !
- JSON token loading for custom token sets
- Seeded random generation for reproducibility
- Comprehensive test suite
- Example scripts
- Modern Python packaging with pyproject.toml

### Features

- Token system with predefined fantasy name tokens
- Customizable token sets via JSON or API
- Complex pattern support with grouping and capitalization
- Type hints and documentation
- Ported from C++ namegen library to Python
