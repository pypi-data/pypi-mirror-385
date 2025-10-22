"""
RAG Hallucination Detection Example in Financial Context

Demonstrates using CERT to detect when a RAG system hallucinates
financial data by contradicting source documents.

This example shows two approaches:
1. Simple API: compare(use_nli=True) - one-line verification
2. Advanced API: TestRunner with batch testing

For most use cases, the simple API is recommended.

Run: python examples/financial_rag_hallucination.py
"""

from cert import compare, TestRunner
import random


# Simulated RAG context (retrieved from Apple 10-K)
CONTEXT = """
Apple Inc. Q4 2024 Financial Results:
- Total net sales: $391.035 billion
- Operating income: $122.847 billion
- Net income: $96.995 billion
- Diluted EPS: $6.08
- Gross margin: 46.2%
"""


def simulated_rag_agent():
    """Simulates RAG responses with varying accuracy.

    In a real system, this would be your RAG pipeline that:
    1. Retrieves context from vector DB
    2. Passes context + query to LLM
    3. Returns LLM-generated answer

    This simulation includes common hallucination patterns:
    - Correct facts (grounded)
    - Wrong numbers (contradiction)
    - Wrong units ($M vs $B - catastrophic)
    - Abbreviated but correct ($391B)
    """
    responses = [
        # Correct responses
        "$391.035 billion",
        "$391.035 billion in total net sales",
        "Apple's Q4 2024 revenue was $391B",
        "Total sales were $391.035 billion",
        # HALLUCINATIONS - Wrong numbers
        "$450 billion",  # Contradiction
        "$350.5 billion",  # Contradiction
        # HALLUCINATIONS - Wrong units (catastrophic!)
        "$391.035 million",  # Off by 1000x
        "$391 thousand",  # Off by 1,000,000x
        # HALLUCINATIONS - Invented data
        "$391B with 50% growth YoY",  # Growth not in context
    ]
    return random.choice(responses)


def simple_api_example():
    """Demonstrate simple compare() API with NLI."""
    print("=" * 70)
    print("APPROACH 1: SIMPLE API - compare(use_nli=True)")
    print("=" * 70)
    print()
    print("For single comparisons, use the simple API:")
    print()

    # Example 1: Correct paraphrase
    print("Example 1: Correct paraphrase")
    print("-" * 70)
    result = compare(
        "Apple's Q4 2024 total net sales: $391.035 billion",
        "Apple's Q4 2024 revenue was $391B",
        use_nli=True,
    )
    print(f"Context:  'Apple's Q4 2024 total net sales: $391.035 billion'")
    print(f"Answer:   'Apple's Q4 2024 revenue was $391B'")
    print(f"Result:   {result.matched} ({result.rule})")
    print(f"Explanation: {result.explanation}")
    print()

    # Example 2: Numeric contradiction
    print("Example 2: Numeric contradiction")
    print("-" * 70)
    result = compare(
        "Apple's Q4 2024 total net sales: $391.035 billion",
        "Apple's Q4 2024 revenue was $450 billion",
        use_nli=True,
    )
    print(f"Context:  'Apple's Q4 2024 total net sales: $391.035 billion'")
    print(f"Answer:   'Apple's Q4 2024 revenue was $450 billion'")
    print(f"Result:   {result.matched} ({result.rule})")
    print(f"Explanation: {result.explanation}")
    print()

    # Example 3: Unit contradiction (catastrophic!)
    print("Example 3: Unit contradiction (catastrophic!)")
    print("-" * 70)
    result = compare(
        "Apple's Q4 2024 total net sales: $391.035 billion",
        "Apple's Q4 2024 revenue was $391 million",
        use_nli=True,
    )
    print(f"Context:  'Apple's Q4 2024 total net sales: $391.035 billion'")
    print(f"Answer:   'Apple's Q4 2024 revenue was $391 million'")
    print(f"Result:   {result.matched} ({result.rule})")
    print(f"Explanation: {result.explanation}")
    print()

    print("✓ Simple API is perfect for:")
    print("  - Single verification checks")
    print("  - Production RAG pipelines")
    print("  - Real-time hallucination detection")
    print()
    print("=" * 70)
    print()


def advanced_api_example():
    """Demonstrate advanced TestRunner API for batch testing."""
    print("=" * 70)
    print("APPROACH 2: ADVANCED API - TestRunner.test_hallucination()")
    print("=" * 70)
    print()
    print("For batch testing and statistical analysis:")
    print()

    # Step 1: Initialize test runner
    print("Step 1: Initializing CERT test runner...")
    runner = TestRunner()
    print("✓ Test runner initialized")
    print()

    # Step 2: Load NLI model for hallucination detection
    print("Step 2: Loading NLI model (microsoft/deberta-v3-base)")
    print("(First run downloads ~500MB model, subsequent runs load from cache)")
    print()
    runner.initialize_energy_scorer()
    print()
    print("✓ Energy scorer ready")
    print()

    # Step 3: Display test setup
    print("=" * 70)
    print("TEST SETUP")
    print("=" * 70)
    print()
    print("Context (retrieved from Apple 10-K):")
    print("-" * 70)
    print(CONTEXT)
    print("-" * 70)
    print()
    print("Query: 'What was Apple's Q4 2024 total revenue?'")
    print()
    print("Testing 20 RAG responses for hallucinations...")
    print()

    # Step 4: Run hallucination test
    result = runner.test_hallucination(
        "apple-revenue-test",
        context=CONTEXT,
        agent_fn=simulated_rag_agent,
        config={"n_trials": 20, "energy_threshold": 0.3},
    )

    # Step 5: Display results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Test ID:            {result['test_id']}")
    print(f"Status:             {result['status'].upper()}")
    print(f"Average Energy:     {result['avg_energy']:.3f}")
    print(f"Contradiction Rate: {result['contradiction_rate']:.0%}")
    print()
    print(f"Diagnosis: {result['diagnosis']}")
    print()

    # Step 6: Show examples of failures
    if result["contradiction_rate"] > 0:
        print("=" * 70)
        print("DETECTED HALLUCINATIONS")
        print("=" * 70)
        print()
        print("The following responses contradicted the source context:")
        print()

        for i, (output, energy) in enumerate(
            zip(result["outputs"], result["energies"])
        ):
            if energy.contradiction:
                print(f"Trial {i + 1}: '{output}'")
                print(f"  Energy:     {energy.total_energy:.3f}")
                print(f"  Semantic:   {energy.semantic:.3f}")
                print(f"  NLI:        {energy.nli:.3f} (< 0.3 = contradiction)")
                print(f"  Grounding:  {energy.grounding:.3f}")
                print()

    # Step 7: Show examples of passes
    good_responses = [
        (output, energy)
        for output, energy in zip(result["outputs"], result["energies"])
        if not energy.contradiction
    ]

    if good_responses:
        print("=" * 70)
        print("WELL-GROUNDED RESPONSES (Sample)")
        print("=" * 70)
        print()
        print("These responses were entailed by the context:")
        print()

        for output, energy in good_responses[:3]:  # Show first 3
            print(f"Response: '{output}'")
            print(f"  Energy:    {energy.total_energy:.3f}")
            print(f"  NLI:       {energy.nli:.3f} (> 0.7 = entailed)")
            print()

    # Step 8: Explain why this matters
    print("=" * 70)
    print("WHY THIS MATTERS")
    print("=" * 70)
    print()
    print("For Financial RAG Systems:")
    print("  • Contradictions can cause regulatory compliance violations")
    print("  • Wrong units ($M vs $B) can cause catastrophic investment decisions")
    print("  • NLI detection catches these before they reach users")
    print()
    print("For EU AI Act Compliance (Article 15):")
    print("  • Demonstrates 'appropriate measures to detect errors'")
    print("  • Provides audit trail of verification")
    print("  • Satisfies high-risk system requirements for financial applications")
    print()
    print("Production Deployment:")
    print("  • Set energy_threshold=0.3 for high-stakes applications")
    print("  • Alert on any contradiction_rate > 0")
    print("  • Log all energy components for debugging")
    print()
    print("=" * 70)
    print()

    # Step 9: Return status code
    return 0 if result["status"] == "pass" else 1


def main():
    """Run both simple and advanced examples."""
    print()
    print("╔" + "=" * 68 + "╗")
    print(
        "║"
        + " " * 10
        + "CERT FRAMEWORK - RAG HALLUCINATION DETECTION"
        + " " * 4
        + "║"
    )
    print("╚" + "=" * 68 + "╝")
    print()

    # Show simple API first (recommended for most users)
    simple_api_example()

    # Show advanced API for batch testing
    return advanced_api_example()


if __name__ == "__main__":
    import sys

    sys.exit(main())
