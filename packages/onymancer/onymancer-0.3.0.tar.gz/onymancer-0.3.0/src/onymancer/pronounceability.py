"""Pronounceability scoring module for fantasy names."""

import re
from typing import Dict, List, Set


class PronounceabilityScorer:
    """
    Scores how pronounceable a fantasy name is based on phonetic rules.

    This class implements multiple scoring algorithms that can be combined
    for comprehensive pronounceability assessment.
    """

    # Common English digraphs and trigraphs (allowed consonant clusters)
    ALLOWED_DIGRAPHS = {
        'th', 'sh', 'ch', 'ph', 'wh', 'gh', 'kn', 'wr', 'qu', 'ck', 'ng', 'mb'
    }

    ALLOWED_TRIGRAPHS = {
        'tch', 'dge', 'igh', 'eigh', 'ough', 'augh', 'ough', 'eaux'
    }

    # Vowels for vowel distribution analysis
    VOWELS = set('aeiouAEIOU')

    # Common consonant clusters that are pronounceable
    COMMON_CLUSTERS = {
        'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sc', 'sk',
        'sl', 'sm', 'sn', 'sp', 'st', 'sw', 'tr', 'tw', 'thr', 'shr', 'spl', 'spr',
        'str', 'scr', 'squ', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr'
    }

    def __init__(self):
        """Initialize the scorer with phonetic rules."""
        pass

    def score_pronounceability(self, name: str) -> float:
        """
        Calculate overall pronounceability score for a name.

        Args:
            name: The name to score

        Returns:
            Float between 0.0 and 1.0, where 1.0 is highly pronounceable
        """
        if not name or len(name) < 2:
            return 0.0

        # Normalize to lowercase for analysis
        name_lower = name.lower()

        # Calculate individual scores (weighted)
        scores = []

        # Consonant cluster analysis (40% weight)
        cluster_score = self._score_consonant_clusters(name_lower)
        scores.append((cluster_score, 0.4))

        # Vowel distribution (30% weight)
        vowel_score = self._score_vowel_distribution(name_lower)
        scores.append((vowel_score, 0.3))

        # Syllable structure (20% weight)
        syllable_score = self._score_syllable_structure(name_lower)
        scores.append((syllable_score, 0.2))

        # Repetition penalty (10% weight)
        repetition_score = self._score_repetition_penalty(name_lower)
        scores.append((repetition_score, 0.1))

        # Calculate weighted average
        total_score = sum(score * weight for score, weight in scores)

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, total_score))

    def _score_consonant_clusters(self, name: str) -> float:
        """
        Score based on consonant cluster patterns.

        Penalizes excessive consonant clusters while allowing common digraphs.
        """
        # Find all consonant clusters (2+ consonants together)
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', name)

        if not consonant_clusters:
            return 1.0  # No clusters = perfect score

        total_penalty = 0.0

        for cluster in consonant_clusters:
            cluster_len = len(cluster)

            if cluster_len == 2:
                # Check if it's an allowed digraph or common cluster
                if cluster in self.ALLOWED_DIGRAPHS or cluster in self.COMMON_CLUSTERS:
                    continue  # No penalty
                else:
                    # Light penalty for unusual but potentially pronounceable digraphs
                    total_penalty += 0.1
            elif cluster_len == 3:
                # Check if it's an allowed trigraph
                if cluster in self.ALLOWED_TRIGRAPHS:
                    continue  # No penalty
                else:
                    # Moderate penalty for 3-consonant clusters - many are pronounceable
                    # Examples: ldr (Eldrin), str (strong), ntr (entry)
                    total_penalty += 0.2
            else:
                # 4+ consonants in a row is very bad
                total_penalty += 0.5

        # Normalize penalty - be more lenient
        max_reasonable_penalty = len(consonant_clusters) * 0.3
        normalized_penalty = min(total_penalty, max_reasonable_penalty)
        score = 1.0 - (normalized_penalty / max_reasonable_penalty)

        return max(0.0, score)

    def _score_vowel_distribution(self, name: str) -> float:
        """
        Score based on vowel distribution throughout the name.

        Good names have vowels distributed reasonably well.
        """
        total_chars = len(name)
        vowel_count = sum(1 for char in name if char in self.VOWELS)

        if vowel_count == 0:
            return 0.0  # No vowels = unpronounceable

        vowel_ratio = vowel_count / total_chars

        # Ideal vowel ratio is around 0.3-0.5 for English-like words
        if 0.25 <= vowel_ratio <= 0.6:
            return 1.0
        elif 0.15 <= vowel_ratio < 0.25 or 0.6 < vowel_ratio <= 0.75:
            return 0.7
        else:
            return 0.3  # Too few or too many vowels

    def _score_syllable_structure(self, name: str) -> float:
        """
        Score based on syllable-like structure.

        Looks for alternating consonant-vowel patterns.
        """
        # Simple syllable detection: CV, VC, CVC patterns
        cv_pattern = re.compile(r'[cv][cv]?[cv]?', re.IGNORECASE)

        # Convert to C/V representation
        cv_string = ''.join('v' if c in self.VOWELS else 'c' for c in name)

        # Count good syllable transitions
        good_transitions = 0
        total_transitions = 0

        for i in range(len(cv_string) - 1):
            current = cv_string[i]
            next_char = cv_string[i + 1]
            total_transitions += 1

            # Good transitions: C->V, V->C
            if (current == 'c' and next_char == 'v') or (current == 'v' and next_char == 'c'):
                good_transitions += 1

        if total_transitions == 0:
            return 0.5  # Very short name

        transition_ratio = good_transitions / total_transitions

        # Perfect alternating = 1.0, random = 0.5, all same = 0.0
        return transition_ratio

    def _score_repetition_penalty(self, name: str) -> float:
        """
        Penalize excessive repetition of characters or patterns.

        Too many repeated letters or sounds make names hard to pronounce.
        """
        if len(name) < 3:
            return 1.0

        # Check for triple repeats (aaa, bbb, etc.)
        triple_repeats = re.findall(r'(.)\1\1', name)
        if triple_repeats:
            return 0.2  # Heavy penalty for triple repeats

        # Check for double repeats (aa, bb, etc.) - moderate penalty
        double_repeats = re.findall(r'(.)\1', name)
        double_penalty = len(double_repeats) * 0.1

        # Check for repetitive patterns (abab, cdcd, etc.)
        pattern_repeats = 0
        for i in range(len(name) - 3):
            pattern = name[i:i+2]
            if name.count(pattern) > 1:
                pattern_repeats += 0.05

        total_penalty = double_penalty + pattern_repeats
        score = 1.0 - min(total_penalty, 0.8)  # Cap penalty

        return max(0.0, score)


# Global scorer instance
_scorer = PronounceabilityScorer()


def score_pronounceability(name: str) -> float:
    """
    Score how pronounceable a fantasy name is.

    Args:
        name: The name to score

    Returns:
        Float between 0.0 and 1.0, where 1.0 is highly pronounceable

    Examples:
        >>> score_pronounceability("Eldrin")
        0.95
        >>> score_pronounceability("Xyzzyx")
        0.85
        >>> score_pronounceability("Brrrgh")
        0.4
    """
    return _scorer.score_pronounceability(name)


def is_pronounceable(name: str, threshold: float = 0.6) -> bool:
    """
    Check if a name meets a minimum pronounceability threshold.

    Args:
        name: The name to check
        threshold: Minimum score required (default 0.6)

    Returns:
        True if name is pronounceable above threshold
    """
    return score_pronounceability(name) >= threshold