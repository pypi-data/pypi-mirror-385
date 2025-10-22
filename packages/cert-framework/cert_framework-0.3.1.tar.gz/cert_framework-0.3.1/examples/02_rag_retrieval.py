"""
Example 2: Testing RAG System Retrieval Consistency

Problem: Similar queries should retrieve similar documents.
Solution: CERT validates retrieval consistency across query variations.

Tests whether your RAG system retrieves consistent documents when users
ask the same question in different ways.

Note: This example uses fast mode (default) since we're testing retrieval
consistency, not answer verification. For answer verification, use
compare(use_nli=True) as shown in financial_rag_hallucination.py
"""

from cert import compare
from typing import List, Dict

# Knowledge base (simplified - real systems have hundreds/thousands)
knowledge_base = [
    "Python is a high-level programming language known for readability",
    "JavaScript is primarily used for web development and runs in browsers",
    "Java is a statically-typed language commonly used in enterprise applications",
    "C++ offers low-level memory control and high performance",
    "Ruby emphasizes programmer productivity and elegant syntax",
]


def simulate_rag_retrieval(query: str, k: int = 2) -> List[str]:
    """Simulate RAG retrieval (in production, this is your vector search).

    For demo purposes, we'll use simple keyword matching.
    In production, this would be your actual RAG implementation.
    """
    # Simplified retrieval - in production use vector search
    scores = []
    for doc in knowledge_base:
        # Simple keyword overlap (replace with actual RAG)
        overlap = len(set(query.lower().split()) & set(doc.lower().split()))
        scores.append((doc, overlap))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scores[:k]]


def test_retrieval_consistency(
    query_variations: List[str], threshold: float = 0.75
) -> Dict:
    """Test that query variations retrieve semantically similar documents.

    Args:
        query_variations: Different ways of asking the same question
        threshold: Similarity threshold for document equivalence

    Returns:
        Dict with consistency results
    """
    # Get baseline retrieval
    baseline_docs = simulate_rag_retrieval(query_variations[0])
    baseline_text = " ".join(baseline_docs)

    inconsistencies = []

    for query in query_variations[1:]:
        retrieved_docs = simulate_rag_retrieval(query)
        retrieved_text = " ".join(retrieved_docs)

        result = compare(baseline_text, retrieved_text, threshold=threshold)

        if not result.matched:
            inconsistencies.append(
                {
                    "query": query,
                    "docs": retrieved_docs,
                    "confidence": result.confidence,
                }
            )

    return {
        "baseline_query": query_variations[0],
        "baseline_docs": baseline_docs,
        "inconsistencies": inconsistencies,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("RAG RETRIEVAL CONSISTENCY TEST")
    print("=" * 70)

    # Query variations - different ways users ask the same thing
    queries = [
        "What programming language is good for beginners?",
        "Which language should I learn first for coding?",
        "Best programming language for someone starting out?",
    ]

    print(f"\nTesting {len(queries)} query variations:\n")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. '{q}'")

    results = test_retrieval_consistency(queries)

    print(f"\nBaseline retrieval (Query 1):")
    for doc in results["baseline_docs"]:
        print(f"  - {doc}")

    if not results["inconsistencies"]:
        print("\n✓ All query variations retrieve consistent documents")
    else:
        print(f"\n✗ Found {len(results['inconsistencies'])} inconsistent retrievals:\n")

        for issue in results["inconsistencies"]:
            print(f"  Query: '{issue['query']}'")
            print(f"  Retrieved:")
            for doc in issue["docs"]:
                print(f"    - {doc}")
            print(f"  Confidence: {issue['confidence']:.0%} vs baseline")
            print(f"  → Different docs for semantically equivalent query\n")

    print("=" * 70)
    print("WHY THIS MATTERS FOR RAG SYSTEMS")
    print("=" * 70)
    print("Inconsistent retrieval means:")
    print("  - Different answers for the same question")
    print("  - Poor user experience")
    print("  - Unreliable system behavior")
    print()
    print("Use CERT to test:")
    print("  - Query understanding robustness")
    print("  - Embedding model quality")
    print("  - Chunking strategy effectiveness")
