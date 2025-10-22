"""
Example 3: Model Matching Testing

Problem: Upgrading models (GPT-3.5 → GPT-4, model version bumps) can break outputs.
Solution: CERT validates new model outputs match old model on test cases.

This is critical before deploying model upgrades to production.
"""

from cert import compare
from typing import List, Tuple

# Test cases: (input, expected_output_from_old_model)
test_cases = [
    (
        "Summarize: The company's Q4 revenue was $10M, up 20% YoY.",
        "Q4 revenue increased 20% year-over-year to $10 million.",
    ),
    (
        "Extract: Founded in 2020, the company has 50 employees.",
        "Company founded: 2020. Employee count: 50.",
    ),
    (
        "Classify sentiment: This product exceeded my expectations!",
        "Positive",
    ),
]


def simulate_model_output(input_text: str, model: str) -> str:
    """Simulate model output (replace with actual LLM API call).

    In production:
        return openai.ChatCompletion.create(model=model, messages=[...])
    """
    # For demo: simulate slight variations between models
    if model == "old":
        return test_cases[[t[0] for t in test_cases].index(input_text)][1]
    else:  # "new" model
        # Simulate new model with slightly different wording
        outputs = {
            test_cases[0][
                0
            ]: "The company's Q4 revenue reached $10M, a 20% increase YoY.",
            test_cases[1][0]: "Founded: 2020. Employees: 50 people.",
            test_cases[2][0]: "Sentiment: Positive",
        }
        return outputs.get(input_text, "")


def run_regression_tests(
    test_cases: List[Tuple[str, str]],
    old_model: str,
    new_model: str,
    threshold: float = 0.85,
) -> dict:
    """Run regression tests comparing old vs new model outputs.

    Args:
        test_cases: List of (input, expected_output) tuples
        old_model: Name of baseline model
        new_model: Name of new model to test
        threshold: Similarity threshold (higher for regressions)

    Returns:
        Dict with test results
    """
    results = {"passed": [], "failed": []}

    for input_text, expected_output in test_cases:
        new_output = simulate_model_output(input_text, new_model)
        result = compare(expected_output, new_output, threshold=threshold)

        test_result = {
            "input": input_text,
            "expected": expected_output,
            "actual": new_output,
            "confidence": result.confidence,
            "matched": result.matched,
        }

        if result.matched:
            results["passed"].append(test_result)
        else:
            results["failed"].append(test_result)

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("MODEL REGRESSION TESTING")
    print("=" * 70)
    print(f"\nComparing: old_model → new_model")
    print(f"Test cases: {len(test_cases)}\n")

    results = run_regression_tests(test_cases, "old", "new", threshold=0.85)

    print(
        f"Results: {len(results['passed'])} passed, {len(results['failed'])} failed\n"
    )

    if results["passed"]:
        print("✓ PASSED TESTS:")
        for test in results["passed"]:
            print(f"  Input: '{test['input']}'")
            print(f"  Confidence: {test['confidence']:.0%}\n")

    if results["failed"]:
        print("✗ FAILED TESTS (outputs differ):")
        for test in results["failed"]:
            print(f"  Input: '{test['input']}'")
            print(f"  Expected: '{test['expected']}'")
            print(f"  Actual:   '{test['actual']}'")
            print(f"  Confidence: {test['confidence']:.0%} (below threshold 85%)")
            print(f"  → Review: Is this an acceptable change?\n")

    print("=" * 70)
    print("REGRESSION TESTING WORKFLOW")
    print("=" * 70)
    print("Before deploying model upgrades:")
    print("  1. Build test suite from production examples")
    print("  2. Run old model, save outputs")
    print("  3. Run new model, compare with CERT")
    print("  4. Review failures - bugs or improvements?")
    print("  5. Update test suite, deploy confidently")
    print()
    print("Use higher thresholds (0.85-0.90) for regressions")
    print("→ Small changes in wording are OK, semantic changes are not")
