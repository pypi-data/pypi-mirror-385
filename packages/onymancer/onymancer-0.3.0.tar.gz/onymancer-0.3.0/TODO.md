# Onymancer Enhancement Roadmap

This document outlines planned improvements to make the onymancer fantasy name generator significantly more powerful and realistic.

## 🎯 Priority 1: Core Quality Improvements (High Impact, Low Effort)

### 1.1 Cultural Token Sets

- [x] Create Elvish token set (liquid consonants l/r, soft vowels, melodic patterns)
- [x] Create Dwarvish token set (hard consonants k/g/d, short vowels, compound structures)
- [ ] Create Orcish token set (gutturals kh/gr, harsh sounds, simple syllables)
- [ ] Create Draconic token set (sibilants s/z/sh, rolling r's, complex clusters)
- [x] Add language selection parameter to `generate()` function

### 1.2 Batch Generation with Constraints

- [x] Implement `generate_batch()` function with count parameter
- [x] Add length constraints (min_length, max_length)
- [x] Add character restrictions (starts_with, ends_with, contains)
- [ ] Add pattern avoidance (avoid consecutive consonants, etc.)
- [ ] Add uniqueness guarantee within batch

### 1.3 Quality Control & Filtering

- [x] Implement pronounceability scoring algorithm
- [ ] Add profanity filtering system
- [ ] Create name validation functions (length, character sets, patterns)
- [ ] Add quality metrics (memorability, readability scores)

## 🧠 Priority 2: Phonetic Intelligence (Medium Impact, Medium Effort)

### 2.1 Markov Chain Syllable Transitions

- [ ] Analyze existing token sets for transition probabilities
- [ ] Implement Markov chain for syllable-to-syllable transitions
- [ ] Add support for phoneme-level transitions (consonant → vowel → consonant)
- [ ] Create transition matrix generation from training data

### 2.2 Stress Patterns & Rhythm

- [ ] Add stress markers to pattern syntax (`'` for primary, `,` for secondary)
- [ ] Implement syllable stress assignment rules
- [ ] Add rhythmic pattern templates (iambic, trochaic, etc.)
- [ ] Create stress-aware token selection

### 2.3 Real Language Inspiration

- [ ] Research and implement Celtic-inspired patterns
- [ ] Add Norse-inspired syllable structures
- [ ] Create Arabic-inspired consonant patterns
- [ ] Implement Japanese-inspired mora-based generation

## 🎲 Priority 3: Advanced Generation Modes (High Impact, Medium Effort)

### 3.1 Name Families & Relationships

- [ ] Implement sibling name generation (shared phonetic elements)
- [ ] Create clan/family name generators with common roots
- [ ] Add name evolution (diminutives, formal versions, nicknames)
- [ ] Implement compound name generation with proper joining

### 3.2 Thematic Generation

- [ ] Create theme-based token sets (noble, peasant, magical, warrior)
- [ ] Add context-aware generation (setting-specific names)
- [ ] Implement era-specific naming conventions
- [ ] Add cultural archetype support

### 3.3 Name Blending & Variation

- [ ] Create name combination algorithms
- [ ] Implement morphological variation (prefixes, suffixes, infixes)
- [ ] Add name mutation with controlled randomness
- [ ] Create name hybridization between different styles

## 🔧 Priority 4: Extensibility & Architecture (Low Impact, High Effort)

### 4.1 Plugin System

- [ ] Design plugin architecture for custom generators
- [ ] Create plugin interface for token providers
- [ ] Implement validator plugin system
- [ ] Add custom pattern syntax extensions

### 4.2 Advanced Token System

- [ ] Implement context-aware tokens (change based on neighbors)
- [ ] Add weighted random selection for tokens
- [ ] Create conditional token rules ("if A then prefer B")
- [ ] Implement token metadata (frequency, rarity, context)

### 4.3 Template System

- [ ] Create pattern template storage and retrieval
- [ ] Add template composition (combine multiple patterns)
- [ ] Implement template parameterization
- [ ] Add template validation and testing

## 📊 Priority 5: Analytics & Insights (Medium Impact, Low Effort)

### 5.1 Generation Statistics

- [ ] Track token usage frequency
- [ ] Monitor name length distributions
- [ ] Record generation performance metrics
- [ ] Create usage analytics dashboard

### 5.2 Name Analysis Tools

- [ ] Implement phonetic breakdown analysis
- [ ] Add syllable structure reporting
- [ ] Create name similarity comparison
- [ ] Add linguistic pattern recognition

### 5.3 Quality Reporting

- [ ] Generate quality assessment reports
- [ ] Create diversity metrics for name sets
- [ ] Add cultural authenticity scoring
- [ ] Implement memorability testing

## 🚀 Priority 6: Performance & Scalability (Low Impact, Medium Effort)

### 6.1 Optimization

- [ ] Implement token caching system
- [ ] Add lazy loading for large token sets
- [ ] Create pre-compiled pattern optimization
- [ ] Optimize random number generation

### 6.2 Parallel Processing

- [ ] Add multi-threaded batch generation
- [ ] Implement async generation for web services
- [ ] Create distributed generation support
- [ ] Add GPU acceleration for large batches

## 🌐 Priority 7: Integration & Ecosystem (Medium Impact, High Effort)

### 7.1 Web API

- [ ] Create RESTful web service
- [ ] Add OpenAPI/Swagger documentation
- [ ] Implement rate limiting and authentication
- [ ] Create web-based name generator interface

### 7.2 Data Integration

- [ ] Add database storage for generated names
- [ ] Create export formats (JSON, CSV, XML)
- [ ] Implement name collection management
- [ ] Add import from external name databases

### 7.3 Developer Tools

- [ ] Create name generation benchmarking suite
- [ ] Add token set creation and validation tools
- [ ] Implement pattern testing framework
- [ ] Create development and debugging utilities

## 🧪 Priority 8: Research & Innovation (High Impact, Variable Effort)

### 8.1 Linguistic Research

- [ ] Study real language phonotactics for authenticity
- [ ] Research fantasy name patterns from literature
- [ ] Analyze successful constructed languages (Esperanto, Dothraki)
- [ ] Implement machine learning approaches for name quality

### 8.2 User Experience Research

- [ ] Conduct user studies on name preferences
- [ ] Analyze memorability and pronounceability metrics
- [ ] Study cultural associations with different sounds
- [ ] Create A/B testing framework for name quality

---

## Implementation Guidelines

### Task Breakdown

- Each [ ] item should be a single, actionable task
- Tasks should be independently implementable
- Include acceptance criteria for each task

### Testing Strategy

- Unit tests for all new functionality
- Integration tests for complex features
- Performance benchmarks for optimization tasks
- User acceptance testing for quality features

### Version Planning

- **v0.2.0**: Cultural token sets + batch generation
- **v0.3.0**: Phonetic intelligence + quality control
- **v0.4.0**: Advanced generation modes
- **v0.5.0**: Analytics and performance improvements
- **v1.0.0**: Plugin system + web API

### Success Metrics

- Name quality scores (pronounceability, memorability)
- Generation performance (names/second)
- User satisfaction ratings
- Cultural authenticity assessments
