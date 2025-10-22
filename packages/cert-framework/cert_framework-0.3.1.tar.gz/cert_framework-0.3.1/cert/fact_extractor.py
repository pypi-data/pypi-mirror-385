"""
Fact extraction for detecting numeric and factual contradictions.

Embeddings compress meaning into vectors and may miss specific factual details
like "30 days vs 90 days". This module extracts structured facts for comparison.
"""

import re
from typing import Set, Dict, Tuple, Optional


def extract_numbers(text: str) -> Set[Tuple[float, str]]:
    """Extract numbers with their units/context from text.

    Returns set of (value, unit) tuples:
    - (30.0, "day") from "30-day" or "30 days"
    - (90.0, "day") from "90 days"
    - (100.0, "percent") from "100%"
    - (50.0, "currency") from "$50" or "$50.00"

    Args:
        text: Text to extract numbers from

    Returns:
        Set of (value, unit) tuples

    Example:
        >>> extract_numbers("30-day money-back guarantee")
        {(30.0, 'day')}
        >>> extract_numbers("$50 or 100%")
        {(50.0, 'currency'), (100.0, 'percent')}
    """
    patterns = [
        # Time periods
        (r"(\d+)-day", "day"),  # "30-day"
        (r"(\d+)\s*days?", "day"),  # "30 days" or "30 day"
        (r"(\d+)\s*weeks?", "week"),  # "4 weeks"
        (r"(\d+)\s*months?", "month"),  # "3 months"
        (r"(\d+)\s*years?", "year"),  # "1 year"
        # Percentages
        (r"(\d+(?:\.\d+)?)\s*%", "percent"),  # "100%" or "99.5%"
        (r"(\d+(?:\.\d+)?)\s*percent", "percent"),  # "100 percent"
        # Currency
        (r"\$\s*(\d+(?:\.\d+)?)", "currency"),  # "$50" or "$50.00"
        (r"(\d+(?:\.\d+)?)\s*dollars?", "currency"),  # "50 dollars"
        # Quantities
        (r"(\d+(?:\.\d+)?)\s*(?:items?|units?|pieces?)", "quantity"),
        # Hours/minutes
        (r"(\d+(?:\.\d+)?)\s*hours?", "hour"),
        (r"(\d+(?:\.\d+)?)\s*minutes?", "minute"),
    ]

    results = set()
    text_lower = text.lower()

    for pattern, unit in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                value = float(match.group(1))
                results.add((value, unit))
            except (ValueError, IndexError):
                continue

    return results


def check_numeric_contradiction(
    text1: str, text2: str, tolerance: float = 0.0
) -> Tuple[bool, Optional[str]]:
    """Check if two texts contain contradictory numbers for the same unit.

    Args:
        text1: First text to compare
        text2: Second text to compare
        tolerance: Relative tolerance for numeric differences (0.0-1.0)
                  e.g., 0.1 = 10% difference allowed

    Returns:
        Tuple of (has_contradiction, explanation)
        - has_contradiction: True if texts have contradictory numbers
        - explanation: Human-readable explanation of the contradiction

    Example:
        >>> check_numeric_contradiction(
        ...     "30-day refund policy",
        ...     "90-day refund policy"
        ... )
        (True, "Numeric contradiction: day (30.0 vs 90.0)")

        >>> check_numeric_contradiction(
        ...     "30-day refund",
        ...     "We offer refunds within 30 days"
        ... )
        (False, None)
    """
    nums1 = extract_numbers(text1)
    nums2 = extract_numbers(text2)

    # Group by unit
    units1: Dict[str, Set[float]] = {}
    for value, unit in nums1:
        if unit not in units1:
            units1[unit] = set()
        units1[unit].add(value)

    units2: Dict[str, Set[float]] = {}
    for value, unit in nums2:
        if unit not in units2:
            units2[unit] = set()
        units2[unit].add(value)

    # Check for contradictions in shared units
    for unit in units1.keys() & units2.keys():
        values1 = units1[unit]
        values2 = units2[unit]

        # Check if any values differ significantly
        for v1 in values1:
            for v2 in values2:
                # Check if values differ beyond tolerance
                if v1 == v2:
                    continue

                max_val = max(v1, v2)
                if max_val == 0:
                    continue

                relative_diff = abs(v1 - v2) / max_val
                if relative_diff > tolerance:
                    return (True, f"Numeric contradiction: {unit} ({v1} vs {v2})")

    return (False, None)


def extract_named_entities(text: str) -> Set[str]:
    """Extract potential named entities (capitalized words/phrases).

    This is a simple heuristic for detecting contradictory proper nouns
    like company names, product names, or locations.

    Args:
        text: Text to extract entities from

    Returns:
        Set of potential entity strings

    Example:
        >>> extract_named_entities("Contact Apple or Microsoft")
        {'Apple', 'Microsoft'}
    """
    # Find capitalized words that aren't at sentence start
    pattern = r"(?<!^)(?<!\. )\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
    entities = set(re.findall(pattern, text))

    # Filter out common non-entities
    common_words = {
        "The",
        "A",
        "An",
        "This",
        "That",
        "These",
        "Those",
        "We",
        "You",
        "I",
        "He",
        "She",
        "It",
        "They",
    }
    entities = {e for e in entities if e not in common_words}

    return entities


def check_entity_contradiction(text1: str, text2: str) -> Tuple[bool, Optional[str]]:
    """Check if texts contain contradictory named entities.

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        Tuple of (has_contradiction, explanation)

    Example:
        >>> check_entity_contradiction(
        ...     "Contact Apple support",
        ...     "Contact Microsoft support"
        ... )
        (True, "Entity contradiction: {Apple} vs {Microsoft}")
    """
    entities1 = extract_named_entities(text1)
    entities2 = extract_named_entities(text2)

    # If one text has entities and the other doesn't, check if they differ
    if entities1 and entities2 and not (entities1 & entities2):
        # They have entities but no overlap
        return (True, f"Entity contradiction: {entities1} vs {entities2}")

    return (False, None)


def check_factual_contradiction(
    text1: str, text2: str, numeric_tolerance: float = 0.0, check_entities: bool = False
) -> Tuple[bool, Optional[str]]:
    """Check for any factual contradictions between two texts.

    Combines numeric and entity contradiction detection.

    Args:
        text1: First text to compare
        text2: Second text to compare
        numeric_tolerance: Relative tolerance for numeric differences
        check_entities: Whether to check for entity contradictions

    Returns:
        Tuple of (has_contradiction, explanation)

    Example:
        >>> check_factual_contradiction(
        ...     "30-day refund from Apple",
        ...     "90-day refund from Microsoft"
        ... )
        (True, "Numeric contradiction: day (30.0 vs 90.0)")
    """
    # Check numeric contradictions first (most common)
    has_numeric_contradiction, numeric_explanation = check_numeric_contradiction(
        text1, text2, tolerance=numeric_tolerance
    )

    if has_numeric_contradiction:
        return (True, numeric_explanation)

    # Optionally check entity contradictions
    if check_entities:
        has_entity_contradiction, entity_explanation = check_entity_contradiction(
            text1, text2
        )
        if has_entity_contradiction:
            return (True, entity_explanation)

    return (False, None)
