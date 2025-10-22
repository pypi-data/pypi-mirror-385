"""Test runner for CERT framework."""

import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from .types import (
    GroundTruth,
    TestResult,
    TestConfig,
    TestStatus,
    Evidence,
)
from .consistency import measure_consistency, autodiagnose_variance
from .semantic import SemanticComparator


class ConsistencyError(Exception):
    """Raised when a consistency check fails."""

    def __init__(self, diagnosis: str, suggestions: List[str]):
        super().__init__(f"Consistency check failed: {diagnosis}")
        self.diagnosis = diagnosis
        self.suggestions = suggestions


class AccuracyError(Exception):
    """Raised when an accuracy check fails."""

    def __init__(self, diagnosis: str, expected: str, actual: str):
        super().__init__(f"Accuracy check failed: {diagnosis}")
        self.diagnosis = diagnosis
        self.expected = expected
        self.actual = actual


class TestRunner:
    """
    Test runner with pluggable semantic comparison.

    Enforces testing order: retrieval → accuracy → consistency

    Args:
        semantic_comparator: Optional custom comparator. Defaults to SemanticComparator
                           with rule-based matching. Can be replaced with EmbeddingComparator
                           or LLMJudgeComparator for different tradeoffs.

    Example:
        # Default rule-based comparison
        runner = TestRunner()

        # Embedding-based comparison (slower, better semantic matching)
        from cert.embeddings import EmbeddingComparator
        runner = TestRunner(semantic_comparator=EmbeddingComparator())

        # LLM-as-judge (slowest, most robust)
        from cert.llm_judge import LLMJudgeComparator
        runner = TestRunner(semantic_comparator=LLMJudgeComparator(client=client))
    """

    __test__ = False  # Tell pytest this is not a test class

    def __init__(self, semantic_comparator: Optional[Any] = None):
        """Initialize test runner with optional custom comparator."""
        self.ground_truths: Dict[str, GroundTruth] = {}
        self.results: List[TestResult] = []
        self.passed_accuracy: set[str] = set()
        self.comparator = semantic_comparator or SemanticComparator()
        self.energy_scorer = None
        self.nli_detector = None

    def add_ground_truth(self, ground_truth: GroundTruth) -> None:
        """Register ground truth for a test."""
        self.ground_truths[ground_truth.id] = ground_truth

    def _must_have_passed_accuracy(self, test_id: str) -> None:
        """Enforce that accuracy test passed before consistency testing."""
        if test_id not in self.passed_accuracy:
            raise ValueError(
                f"Cannot test consistency for '{test_id}' before accuracy validation. "
                "Run test_accuracy() first to ensure outputs are correct."
            )

    async def test_accuracy(
        self,
        test_id: str,
        agent_fn: Callable[[], Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> TestResult:
        """
        Test accuracy against ground truth.

        Args:
            test_id: ID of test (must match ground truth ID)
            agent_fn: Async function that produces output
            config: Optional configuration

        Returns:
            TestResult with accuracy metrics
        """
        if test_id not in self.ground_truths:
            raise ValueError(f"No ground truth found for test ID: {test_id}")

        ground_truth = self.ground_truths[test_id]
        threshold = config.get("threshold", 0.8) if config else 0.8

        # Execute agent
        actual = await (
            agent_fn()
            if asyncio.iscoroutinefunction(agent_fn)
            else asyncio.to_thread(agent_fn)
        )

        # Compare with ground truth
        comparison = self.comparator.compare(str(ground_truth.expected), str(actual))

        # Check equivalents if no match
        if not comparison.matched and ground_truth.equivalents:
            for equivalent in ground_truth.equivalents:
                comparison = self.comparator.compare(equivalent, str(actual))
                if comparison.matched:
                    break

        # Determine result
        passed = comparison.matched and comparison.confidence >= threshold
        status = TestStatus.PASS if passed else TestStatus.FAIL

        result = TestResult(
            test_id=test_id,
            status=status,
            timestamp=datetime.now(),
            accuracy=comparison.confidence if comparison.matched else 0.0,
            diagnosis=None
            if passed
            else (
                f"Output '{actual}' does not match expected '{ground_truth.expected}'"
            ),
            suggestions=None
            if passed
            else [
                "Check if the agent is retrieving correct context",
                "Verify prompt clearly specifies expected output format",
                "Consider adding equivalents to ground truth",
            ],
        )

        if passed:
            self.passed_accuracy.add(test_id)

        self.results.append(result)
        return result

    async def test_consistency(
        self, test_id: str, agent_fn: Callable[[], Any], config: TestConfig
    ) -> TestResult:
        """
        Test consistency across multiple runs.

        Args:
            test_id: ID of test
            agent_fn: Async function to test
            config: Test configuration

        Returns:
            TestResult with consistency metrics
        """
        # Layer enforcement
        self._must_have_passed_accuracy(test_id)

        # Measure consistency
        consistency_result = await measure_consistency(agent_fn, config)

        # Determine pass/fail
        passed = consistency_result.consistency >= config.consistency_threshold
        status = TestStatus.PASS if passed else TestStatus.FAIL

        # Build result
        result = TestResult(
            test_id=test_id,
            status=status,
            timestamp=datetime.now(),
            consistency=consistency_result.consistency,
            evidence=Evidence(
                outputs=[str(o) for o in consistency_result.outputs],
                unique_count=consistency_result.unique_count,
                examples=consistency_result.evidence,
            )
            if not passed
            else None,
            diagnosis=autodiagnose_variance(consistency_result) if not passed else None,
            suggestions=[
                "Set temperature=0 if not already",
                "Check for non-deterministic data sources (timestamps, random sampling)",
                "Review prompt for ambiguous instructions",
                "Consider using semantic comparison if outputs are semantically equivalent",
            ]
            if not passed
            else None,
        )

        self.results.append(result)
        return result

    def get_results(self, test_id: Optional[str] = None) -> List[TestResult]:
        """
        Get test results.

        Args:
            test_id: Optional filter by test ID

        Returns:
            List of test results
        """
        if test_id:
            return [r for r in self.results if r.test_id == test_id]
        return self.results

    def initialize_energy_scorer(self) -> None:
        """Initialize NLI and energy components for hallucination detection.

        This loads the NLI model (~500MB first time) and sets up the
        production energy scorer. Call this once before using test_hallucination().

        Example:
            >>> runner = TestRunner()
            >>> runner.initialize_energy_scorer()  # One-time setup
            Loading NLI model: microsoft/deberta-v3-base...
            ✓ NLI model loaded
            >>> # Now ready for hallucination testing
        """
        from .nli import NLIDetector
        from .energy import ProductionEnergyScorer
        from .embeddings import EmbeddingComparator

        # Initialize NLI detector
        self.nli_detector = NLIDetector()

        # Initialize embeddings if not already set
        if not hasattr(self, "embeddings") or self.embeddings is None:
            print("Initializing embedding model...")
            self.embeddings = EmbeddingComparator()

        # Initialize energy scorer
        self.energy_scorer = ProductionEnergyScorer(
            embeddings=self.embeddings, nli=self.nli_detector
        )

    def test_hallucination(
        self,
        test_id: str,
        context: str,
        agent_fn: Callable[[], Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Test for hallucinations using production energy scorer.

        This is the main method for detecting when RAG systems generate
        answers that contradict or aren't grounded in the provided context.

        Args:
            test_id: Identifier for this test
            context: Source context (e.g., retrieved document)
            agent_fn: Function that generates answers (no args)
            config: Configuration with:
                - n_trials: Number of times to run agent (default: 5)
                - energy_threshold: Max acceptable energy (default: 0.3)

        Returns:
            Dict with:
                - test_id: Test identifier
                - status: 'pass' or 'fail'
                - avg_energy: Average energy across trials
                - contradiction_rate: Fraction of contradictory responses
                - diagnosis: Human-readable diagnosis
                - energies: List of EnergyComponents for each trial
                - outputs: List of agent outputs

        Example:
            >>> runner = TestRunner()
            >>> runner.initialize_energy_scorer()
            >>>
            >>> context = "Apple's Q4 revenue was $391B"
            >>> def agent():
            ...     return my_rag_system("What was Apple's Q4 revenue?")
            >>>
            >>> result = runner.test_hallucination(
            ...     'rag-test-1',
            ...     context=context,
            ...     agent_fn=agent,
            ...     config={'n_trials': 10, 'energy_threshold': 0.3}
            ... )
            >>>
            >>> if result['contradiction_rate'] > 0:
            ...     print(f"WARNING: {result['diagnosis']}")
        """
        if self.energy_scorer is None:
            raise RuntimeError(
                "Energy scorer not initialized. Call initialize_energy_scorer() first."
            )

        n_trials = config.get("n_trials", 5)
        threshold = config.get("energy_threshold", 0.3)

        outputs = []
        energies = []

        # Run multiple trials
        for _ in range(n_trials):
            answer = agent_fn()
            energy = self.energy_scorer.compute_energy(context, str(answer))
            outputs.append(str(answer))
            energies.append(energy)

        # Compute aggregate metrics
        avg_energy = sum(e.total_energy for e in energies) / len(energies)
        contradictions = sum(1 for e in energies if e.contradiction)
        contradiction_rate = contradictions / n_trials

        # Determine pass/fail
        status = "pass" if avg_energy <= threshold else "fail"

        # Generate diagnosis
        diagnosis = self._diagnose_hallucination(energies)

        return {
            "test_id": test_id,
            "status": status,
            "avg_energy": avg_energy,
            "contradiction_rate": contradiction_rate,
            "diagnosis": diagnosis,
            "energies": energies,
            "outputs": outputs,
        }

    def _diagnose_hallucination(self, energies: List[Any]) -> str:
        """Generate human-readable diagnosis from energy components.

        Args:
            energies: List of EnergyComponents from trials

        Returns:
            Diagnosis string explaining the issue
        """
        avg_nli = sum(e.nli for e in energies) / len(energies)
        avg_semantic = sum(e.semantic for e in energies) / len(energies)
        avg_grounding = sum(e.grounding for e in energies) / len(energies)

        # Priority: contradiction > grounding > semantic
        if avg_nli < 0.4:
            return "CRITICAL: Answers contradict provided context (NLI detection)"

        if avg_grounding < 0.4:
            return "WARNING: Answers not well-grounded in context (invented terms/entities)"

        if avg_semantic < 0.6:
            return "WARNING: Answers semantically distant from context"

        return "PASS: Answers well-grounded and entailed by context"
