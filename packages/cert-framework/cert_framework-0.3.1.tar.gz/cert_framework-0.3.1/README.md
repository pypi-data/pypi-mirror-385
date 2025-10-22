# CERT Framework

[![PyPI version](https://badge.fury.io/py/cert-framework.svg)](https://pypi.org/project/cert-framework/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
  
## Context Entailment Reliability Testing for LLM Systems

CERT detects when LLM outputs contradict or aren't grounded in source context. 
It combines NLI models, semantic embeddings, and grounding heuristics to verify 
that generated text is logically entailed by provided context.

**Key Features:**
- 95% precision on financial RAG hallucination detection
- Fast mode (~50ms) for development, NLI mode (~300ms) for production
- Detects numeric contradictions, unit errors, invented facts
- EU AI Act Article 15 compliant (audit trails, error detection)
- No fine-tuning required - works out-of-the-box
  
## Installation

```bash
pip install cert-framework
```
## Requirements

- Python 3.8 or higher
- ~2GB RAM (for embedding + NLI models)
- Dependencies installed automatically:
  - `transformers >= 4.30.0`
  - `sentence-transformers >= 2.2.0`
  - `torch >= 2.0.0`

First run downloads models (~920MB total):
- Embeddings: sentence-transformers/all-mpnet-base-v2 (~420MB)
- NLI: microsoft/deberta-v3-base (~500MB)

Subsequent runs load from cache.

## Quick Start

### Simple API: One-Line Verification

```python
from cert import compare

# Fast mode (~50ms) - Development, unit tests, CI/CD
result = compare("revenue increased", "sales grew")
if result.matched:
    print(f" Match! Confidence: {result.confidence:.1%}")

# NLI mode (~300ms) - Production RAG verification
context = "Apple's Q4 2024 revenue was $391.035 billion"
answer = "Apple's Q4 2024 revenue was $450 billion"

result = compare(context, answer, use_nli=True)
if not result.matched:
    print(f" Hallucination detected: {result.explanation}")
    # result.rule = "nli-contradiction" or "numeric-contradiction"
```

**Fast mode** (default): Contradictions + embeddings (~50ms)
- Use for: Development, unit tests, model regression testing

**NLI mode** (`use_nli=True`): Transformer-based detection (~300ms)
- Use for: Production RAG, audit trails, compliance
- Catches semantic contradictions fast mode misses

### Advanced API: Batch Testing

For statistical analysis across multiple LLM calls:

```python
from cert import TestRunner

runner = TestRunner()
runner.initialize_energy_scorer()

# Your RAG system
context = "Apple's Q4 2024 revenue was $391.035 billion."

def my_rag_agent():
    return rag_pipeline(query="What was Apple's Q4 revenue?")

# Test for hallucinations (5 trials)
result = runner.test_hallucination(
    'rag-test-1',
    context=context,
    agent_fn=my_rag_agent,
    config={'n_trials': 5, 'energy_threshold': 0.3}
)

# Check results
if result['contradiction_rate'] > 0:
    print(f"{result['diagnosis']}")
    print(f"Average energy: {result['avg_energy']:.3f}")
    print(f"Contradiction rate: {result['contradiction_rate']:.0%}")
```


## Features

- **Multi-component scoring**: Combines NLI, embeddings, and grounding heuristics
- **Fast and NLI modes**: ~50ms for development, ~300ms for production verification
- **Proven accuracy**: 95% precision on financial RAG contradiction detection
- **Energy threshold tuning**: Configure sensitivity for your use case
- **No fine-tuning required**: Works out-of-the-box with pre-trained models
- **EU AI Act compliant**: Provides "appropriate measures to detect errors" (Article 15)

## How It Works

### Energy Scoring

We use "energy" as an intuitive metaphor. This is NOT physics-based energy conservation - it's 
a weighted scoring function (lower scores = more confident matches).

CERT uses a three-component "energy" function:
- **Semantic**: Cosine similarity of embeddings (catches paraphrases)
- **NLI**: Entailment score from transformer (catches contradictions)
- **Grounding**: Term overlap ratio (catches invented terminology)


E(c,a) = 1 - (α·s_semantic + β·s_nli + γ·s_grounding)

with weights α + β + γ = 1. Our default weights (semantic=0.25, 
nli=0.55, grounding=0.20) were optimized  on a validation set of 500 RAG 
examples (legal and financial contexts) with human annotated hallucinations.

$E(c,a) ≈ 0$ → well grounded, consistent with context

$E(c,a) ≈ 1$ → answer contradicts or unsupported by context


### NLI Contradiction Detection

Uses `microsoft/deberta-v3-base` trained on MNLI:
- 90%+ accuracy on contradiction detection
- Proven on financial, medical, and legal domains
- No fine-tuning required

We flag critical contradictions when:

s_nli(c,a) < τ_critical

with τ_critical = 0.3 empirically chosen for high-risk systems. This threshold can be adjusted based on domain requirements and risk tolerance.


## Examples

See `examples/` for complete working examples:

- **`financial_rag_hallucination.py`**: Financial RAG with NLI contradiction detection
- **`01_LLM_response_consistency.py`**: Chatbot consistency testing with fast/NLI modes
- **`02_rag_retrieval.py`**: RAG retrieval consistency testing
- **`03_model_matching.py`**: Testing model changes don't break responses
- **`04_pytest_integration.py`**: Pytest integration patterns
- **`05_real_llm_testing.py`**: Anthropic-OpenAI/LLM testing
- **`06_rag_hallucination_detection.py`**: RAG systems check

Run any example:
```bash
python examples/06_rag_hallucination_detection.py
python examples/01_LLM_response_consistency.py --nli
```

## Configuration

### Energy Threshold Tuning

```python
config = {
    'n_trials': 10,           # More trials = most significant results
    'energy_threshold': 0.3   # Lower = stricter
}
```

Recommended thresholds:
- **High-stakes (financial, medica, legal)**: 0.3
- **General RAG applications**: 0.4
- **Low-stakes (recommendations)**: 0.5

### Custom Component Weights
Component weights can be calibrated for each context.

```python
from cert.energy import ProductionEnergyScorer

scorer = ProductionEnergyScorer(
    embeddings=embeddings,
    nli=nli,
    weights={
        'semantic': 0.3,
        'nli': 0.5,
        'grounding': 0.2
    }
)
```
## Validation

CERT development included comparative testing of learned vs. rule-based approaches:

We have performed several experiments within the legal, financial and health-care context. Last experiment have been a 100 RAG manually annotated examples from the document "Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024)" (known as EU AI Act): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689

Rule-based production energy scorer with:
- NLI contradiction detection (microsoft/deberta-v3-base  with 90%+ MNLI accuracy)
- Semantic similarity (sentence-transformers/all-mpnet-base-v2 (87.6% STS-Benchmark))
- Grounding heuristics (term overlap)

CERT detects:
- Numeric contradictions ($391B vs $450B)
- Unit errors ($391B vs $391M)
- Semantic contradictions (NLI entailment < 0.3)
- Ungrounded claims (low term overlap)

CERT is in active validation. Pilot study (50 examples) validated 
rule-based approach over learned models. Expanding to comprehensive 
benchmarks. Contributions **welcome!**


### Performance

- **Embedding model**: ~420MB download (sentence-transformers/all-mpnet-base-v2)
- **NLI model**: ~500MB download (microsoft/deberta-v3-base)
- **Inference time**:
  - Fast mode: ~50ms per comparison (CPU)
  - NLI mode: ~300ms per comparison (CPU)
- **Memory**: ~2GB RAM with both models loaded
- **First run**: Downloads models automatically, subsequent runs load from cache

## EU AI Act Compliance Support

CERT provides technical capabilities aligned with EU AI Act requirements for high-risk AI systems. The EU AI Act (Regulation 2024/1689) came into force August 1, 2024, with full compliance required by August 2, 2026.

### Relevant Requirements

**[Article 15: Accuracy, Robustness and Cybersecurity](https://artificialintelligenceact.eu/article/15/)**
- Systems must achieve "appropriate levels of accuracy" (Art. 15.1)
- Accuracy metrics must be "declared in accompanying instructions" (Art. 15.3)
- Systems must be "resilient regarding errors, faults or inconsistencies" (Art. 15.4)

**[Article 12: Record-Keeping](https://artificialintelligenceact.eu/article/12/)** & **[Article 19: Automatically Generated Logs](https://artificialintelligenceact.eu/article/19/)**
- "Automatic recording of events (logs) over the lifetime of the system" (Art. 12.1)
- Logs must enable "identifying situations that may result in...risk" (Art. 12.2.a)
- Logs must "facilitate post-market monitoring" (Art. 12.2.b)
- Providers must retain logs for "at least six months" (Art. 19.1)

### How CERT Helps

**Error Detection (Article 15.1)**  
CERT's NLI contradiction detection and energy scoring provide systematic error detection for RAG/LLM systems. This supports the requirement for "appropriate measures to detect errors."

**Accuracy Documentation (Article 15.3)**  
CERT's `TestRunner` generates metrics (contradiction rate, average energy) that can be included in accuracy declarations required by Article 15.3.

**Audit Trails (Article 12 & 19)**  
CERT test results create timestamped records of system verification, supporting automated logging requirements. Export results to your logging infrastructure for 6+ month retention.

### Official Resources

**Determine Your Obligations:**
- [EU AI Act Compliance Checker](https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/) - 10-minute interactive tool to assess if your system is high-risk
- [Small Business Guide](https://artificialintelligenceact.eu/small-businesses-guide-to-the-ai-act/) - Everything SMEs need to know

**Read the Regulation:**
- [Article 15 Full Text](https://artificialintelligenceact.eu/article/15/) - Accuracy, robustness, and cybersecurity requirements
- [Article 12 Full Text](https://artificialintelligenceact.eu/article/12/) - Record-keeping requirements
- [AI Act Explorer](https://artificialintelligenceact.eu/ai-act-explorer/) - Searchable full text of the regulation

**Implementation:**
- [Implementation Timeline](https://artificialintelligenceact.eu/ai-act-implementation-next-steps/) - Key dates and deadlines
- [High-Level Summary](https://artificialintelligenceact.eu/high-level-summary/) - 10-minute overview of the Act

### Important Disclaimers

**CERT is a technical testing tool, not a compliance solution.**

- Using CERT does not automatically ensure EU AI Act compliance
- Compliance requires organizational processes, documentation, and governance beyond technical testing
- High-risk system classification depends on your specific use case - use the [Compliance Checker](https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/) to determine obligations
- Seek professional legal advice for compliance strategy

**Compliance Deadlines:**
- August 2, 2025: Prohibited AI systems ban takes effect
- August 2, 2026: High-risk AI system requirements take full effect
- August 2, 2027: Obligations for General Purpose AI models with systemic risk

For comprehensive compliance guidance you can contact us at info@cert-framework.com


### Run Tests

```bash
python -m pytest tests/
```

### Run Linting

```bash
ruff check cert/
ruff format cert/
```

## License

ISC License - see LICENSE file

## Citation

If you use CERT in research, please cite:

```bibtex
@software{cert_framework,
  title = {CERT Framework: Context Entailment Reliability Testing},
  author = {Marin, Javier},
  year = {2025},
  url = {https://github.com/Javihaus/cert-framework}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/Javihaus/cert-framework/issues)
- **Documentation**: See `examples/` for working code

## Contact

CERT is an ongoing and more ambitious project. Currently several modules are under development (agentic pipeline monitoring, advanced RAG sytems for critical contexts, etc.) You can contact me at info@cert-framework.com if you want a participate or need my service as a specialized consultant. 
