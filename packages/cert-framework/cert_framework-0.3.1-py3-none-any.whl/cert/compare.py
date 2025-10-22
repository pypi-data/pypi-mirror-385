"""Simple API for document comparison.

This module provides a simple, one-function interface to CERT:

    from cert import compare

    result = compare("revenue increased", "sales grew")
    if result:
        print(f"Match! Confidence: {result.confidence:.1%}")

Progressive disclosure: simple by default, configurable for advanced use.
"""

from typing import Optional
from cert.embeddings import EmbeddingComparator, ComparisonResult
from cert.fact_extractor import check_factual_contradiction

# Global comparator with lazy initialization
_default_comparator: Optional[EmbeddingComparator] = None


def compare(
    text1: str, text2: str, threshold: Optional[float] = None, use_nli: bool = False
) -> ComparisonResult:
    """Compare two texts for semantic similarity with optional NLI contradiction detection.

    This is the simplest way to use CERT. One function call, immediate value.

    Args:
        text1: First text to compare
        text2: Second text to compare
        threshold: Optional custom threshold (0-1). If None, uses default 0.80
        use_nli: If True, use NLI-based contradiction detection (~300ms).
                 If False (default), use fast regex + embeddings (~50ms).
                 Recommended True for production RAG verification.

    Returns:
        ComparisonResult with matched (bool) and confidence (float) attributes

    Raises:
        TypeError: If text1 or text2 are not strings
        ValueError: If texts are empty or threshold is out of range

    Example:
        Fast comparison (development):
            result = compare("revenue increased", "sales grew")
            print(result.matched)  # True
            print(result.confidence)  # 0.847

        Production verification (with NLI):
            result = compare("Revenue: $30M", "Revenue: $90M", use_nli=True)
            print(result.matched)  # False - NLI detects contradiction
            print(result.explanation)  # "CRITICAL: Answers contradict..."

        As boolean:
            if compare("profit up", "earnings rose"):
                print("Match!")

        Custom threshold:
            result = compare("good", "great", threshold=0.90)

    Note:
        Fast mode (use_nli=False):
          - Regex contradiction check + embeddings
          - ~50-100ms per comparison
          - Good for development, unit tests, model regression

        NLI mode (use_nli=True):
          - Transformer-based semantic contradiction detection
          - ~300ms per comparison (first call downloads ~500MB model)
          - Recommended for production RAG verification, audit trails

        First call downloads embedding model (~420MB). With use_nli=True,
        also downloads NLI model (~500MB). Models cached after first use.
    """
    # Validate inputs
    if not isinstance(text1, str) or not isinstance(text2, str):
        raise TypeError(
            f"Both texts must be strings. Got {type(text1).__name__} and {type(text2).__name__}"
        )

    if not text1.strip() or not text2.strip():
        raise ValueError(
            "Cannot compare empty texts. Both text1 and text2 must contain content."
        )

    if threshold is not None and not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

    # CRITICAL: Check for factual contradictions BEFORE embeddings
    # Embeddings can miss specific facts like "30 days vs 90 days"
    has_contradiction, explanation = check_factual_contradiction(text1, text2)
    if has_contradiction:
        return ComparisonResult(
            matched=False,
            rule="numeric-contradiction",
            confidence=0.0,
            explanation=explanation,
        )

    global _default_comparator

    # Lazy initialization: load model on first use
    if _default_comparator is None:
        print("Loading semantic model (one-time, ~5 seconds)...")
        _default_comparator = EmbeddingComparator()

    # NLI mode: Use ProductionEnergyScorer for comprehensive contradiction detection
    if use_nli:
        # Lazy initialization of NLI components
        if not hasattr(_default_comparator, "_nli_detector"):
            print("Loading NLI model (one-time, ~10 seconds)...")
            from cert.nli import NLIDetector
            from cert.energy import ProductionEnergyScorer

            _default_comparator._nli_detector = NLIDetector()
            _default_comparator._energy_scorer = ProductionEnergyScorer(
                embeddings=_default_comparator, nli=_default_comparator._nli_detector
            )

        # Use energy scorer for comprehensive check
        energy = _default_comparator._energy_scorer.compute_energy(text1, text2)

        # Convert to ComparisonResult
        if energy.contradiction:
            # Hard contradiction detected by NLI
            return ComparisonResult(
                matched=False,
                rule="nli-contradiction",
                confidence=0.0,
                explanation=f"NLI detected contradiction (entailment score: {energy.nli:.2f})",
            )
        elif energy.total_energy > 0.5:
            # High energy = likely hallucination
            return ComparisonResult(
                matched=False,
                rule="nli-hallucination",
                confidence=1.0 - energy.total_energy,
                explanation=f"High hallucination energy: {energy.total_energy:.2f} (semantic: {energy.semantic:.2f}, nli: {energy.nli:.2f}, grounding: {energy.grounding:.2f})",
            )
        else:
            # Low energy = well-grounded match
            return ComparisonResult(
                matched=True,
                rule="nli-verified",
                confidence=1.0 - energy.total_energy,
                explanation=f"NLI-verified match (energy: {energy.total_energy:.2f})",
            )

    # Custom threshold for this comparison
    if threshold is not None:
        old_threshold = _default_comparator.threshold
        _default_comparator.threshold = threshold
        result = _default_comparator.compare(text1, text2)
        _default_comparator.threshold = old_threshold
        return result

    return _default_comparator.compare(text1, text2)


def configure(
    model_name: str = "sentence-transformers/all-mpnet-base-v2", threshold: float = 0.80
) -> None:
    """Configure the default comparison model and threshold.

    Call this once at application startup if you want to use a different
    model or threshold for all comparisons.

    Args:
        model_name: Sentence transformer model to use
        threshold: Similarity threshold (0-1)

    Example:
        # Use faster but less accurate model
        configure(model_name="all-MiniLM-L6-v2", threshold=0.75)

        # Then all compare() calls use these settings
        result = compare("text1", "text2")

    Note:
        This replaces the global comparator, so any cached embeddings are lost.
    """
    global _default_comparator
    _default_comparator = EmbeddingComparator(
        model_name=model_name, threshold=threshold
    )


def reset() -> None:
    """Reset the global comparator (mainly for testing)."""
    global _default_comparator
    _default_comparator = None
