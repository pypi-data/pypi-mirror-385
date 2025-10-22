"""
Example 4: pytest Integration with CERT

Shows how to integrate CERT into your pytest test suite.
This is how you'd actually use CERT in production.

Run with: pytest examples/test_llm_consistency.py -v
"""

import pytest
from cert import compare


# Simulated LLM outputs for testing
def get_summarization_output(input_text: str, run: int) -> str:
    """Simulate LLM summarization (replace with actual API call)."""
    # In production: return openai.ChatCompletion.create(...)

    summaries = {
        1: "The article discusses machine learning applications in healthcare.",
        2: "Machine learning is being applied to healthcare problems.",
        3: "Healthcare is benefiting from ML applications.",  # Consistent
        4: "The article is about cooking recipes.",  # INCONSISTENT - wrong topic!
    }
    return summaries.get(run, "")


class TestLLMConsistency:
    """Test suite for LLM output consistency."""

    @pytest.fixture
    def input_text(self):
        """Sample input for testing."""
        return "Machine learning is transforming healthcare..."

    def test_summarization_consistency(self, input_text):
        """Test that repeated summarizations are semantically equivalent."""
        # Run LLM multiple times
        output_1 = get_summarization_output(input_text, 1)
        output_2 = get_summarization_output(input_text, 2)
        output_3 = get_summarization_output(input_text, 3)

        # All outputs should be semantically similar
        result_1_2 = compare(output_1, output_2, threshold=0.80)
        result_1_3 = compare(output_1, output_3, threshold=0.80)

        assert result_1_2.matched, (
            f"Run 2 inconsistent with run 1 (confidence: {result_1_2.confidence:.2f})"
        )
        assert result_1_3.matched, (
            f"Run 3 inconsistent with run 1 (confidence: {result_1_3.confidence:.2f})"
        )

    def test_summarization_catches_hallucination(self, input_text):
        """Test that CERT catches completely wrong outputs."""
        output_good = get_summarization_output(input_text, 1)
        output_bad = get_summarization_output(input_text, 4)  # Wrong topic

        result = compare(output_good, output_bad, threshold=0.80)

        # Should NOT match - different topics
        assert not result.matched, "CERT should catch outputs on different topics"
        assert result.confidence < 0.50, (
            f"Confidence too high for unrelated content: {result.confidence:.2f}"
        )


class TestRAGConsistency:
    """Test suite for RAG system consistency."""

    @pytest.fixture
    def query_variations(self):
        """Semantically equivalent queries."""
        return [
            "What are the benefits of exercise?",
            "Why is exercise good for you?",
            "What are the advantages of working out?",
        ]

    def test_retrieval_consistency_across_queries(self, query_variations):
        """Test that similar queries retrieve similar documents."""

        # Simulate retrieval (replace with actual RAG system)
        def retrieve(query):
            # Mock retrieval - in production, this is your vector search
            return (
                "Regular exercise improves cardiovascular health and mental wellbeing."
            )

        baseline = retrieve(query_variations[0])

        for query in query_variations[1:]:
            retrieved = retrieve(query)
            result = compare(baseline, retrieved, threshold=0.75)

            assert result.matched, (
                f"Query '{query}' retrieved different docs (confidence: {result.confidence:.2f})"
            )


# You can also use pytest-cert plugin (if installed):
# @pytest.mark.cert_consistency(threshold=0.80)
# def test_with_cert_plugin():
#     ...
