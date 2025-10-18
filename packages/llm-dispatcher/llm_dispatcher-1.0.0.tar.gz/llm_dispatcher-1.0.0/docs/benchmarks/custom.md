# Custom Benchmarks

Create your own benchmark criteria and evaluation metrics to test specific aspects of LLM performance that matter to your use case.

## Overview

Custom benchmarks allow you to:

- **Define custom evaluation criteria** - Create metrics specific to your domain
- **Implement custom evaluators** - Build evaluation logic tailored to your needs
- **Test specific scenarios** - Focus on use cases relevant to your application
- **Combine multiple metrics** - Create composite scores from different evaluation dimensions
- **Integrate with existing systems** - Connect with your current evaluation pipelines

## Basic Custom Benchmarking

### Simple Custom Benchmark

```python
from llm_dispatcher.benchmarks import CustomBenchmark

# Define custom evaluation function
def custom_evaluator(response: str, expected: str) -> float:
    """Custom evaluation function that returns a score between 0 and 1."""
    # Simple example: check if expected text is in response
    if expected.lower() in response.lower():
        return 1.0
    else:
        return 0.0

# Create custom benchmark
benchmark = CustomBenchmark(
    test_cases=[
        {
            "prompt": "What is the capital of France?",
            "expected": "Paris",
            "evaluator": custom_evaluator
        },
        {
            "prompt": "What is 2+2?",
            "expected": "4",
            "evaluator": custom_evaluator
        }
    ],
    iterations=5
)

# Run benchmark
results = await benchmark.run()
print(f"Custom score: {results.custom_score:.2f}")
```

### Multiple Custom Evaluators

```python
# Define multiple custom evaluators
def accuracy_evaluator(response: str, expected: str) -> float:
    """Evaluate accuracy."""
    return 1.0 if expected.lower() in response.lower() else 0.0

def length_evaluator(response: str, expected: str) -> float:
    """Evaluate response length appropriateness."""
    # Assume expected length is 50 characters
    expected_length = 50
    actual_length = len(response)
    return 1.0 - abs(actual_length - expected_length) / expected_length

def creativity_evaluator(response: str, expected: str) -> float:
    """Evaluate creativity (simple heuristic)."""
    # Count unique words as a proxy for creativity
    unique_words = len(set(response.lower().split()))
    total_words = len(response.split())
    return unique_words / total_words if total_words > 0 else 0.0

# Create benchmark with multiple evaluators
benchmark = CustomBenchmark(
    test_cases=[
        {
            "prompt": "Write a creative story about a robot",
            "expected": "creative narrative",
            "evaluators": {
                "accuracy": accuracy_evaluator,
                "length": length_evaluator,
                "creativity": creativity_evaluator
            }
        }
    ],
    iterations=5
)

results = await benchmark.run()
print(f"Accuracy score: {results.evaluator_scores['accuracy']:.2f}")
print(f"Length score: {results.evaluator_scores['length']:.2f}")
print(f"Creativity score: {results.evaluator_scores['creativity']:.2f}")
```

## Advanced Custom Benchmarking

### Domain-Specific Benchmarks

```python
from llm_dispatcher.benchmarks import DomainSpecificBenchmark

# Medical domain evaluator
def medical_accuracy_evaluator(response: str, expected: str) -> float:
    """Evaluate medical accuracy."""
    # Check for medical terminology and accuracy
    medical_terms = ["diagnosis", "treatment", "symptoms", "patient", "medical"]
    term_count = sum(1 for term in medical_terms if term in response.lower())
    return min(term_count / len(medical_terms), 1.0)

def medical_safety_evaluator(response: str, expected: str) -> float:
    """Evaluate medical safety (no harmful advice)."""
    harmful_phrases = ["self-diagnose", "ignore symptoms", "skip treatment"]
    for phrase in harmful_phrases:
        if phrase in response.lower():
            return 0.0
    return 1.0

# Legal domain evaluator
def legal_accuracy_evaluator(response: str, expected: str) -> float:
    """Evaluate legal accuracy."""
    legal_terms = ["law", "legal", "statute", "regulation", "court"]
    term_count = sum(1 for term in legal_terms if term in response.lower())
    return min(term_count / len(legal_terms), 1.0)

def legal_disclaimer_evaluator(response: str, expected: str) -> float:
    """Evaluate presence of legal disclaimers."""
    disclaimer_phrases = ["not legal advice", "consult attorney", "general information"]
    for phrase in disclaimer_phrases:
        if phrase in response.lower():
            return 1.0
    return 0.0

# Create domain-specific benchmarks
medical_benchmark = DomainSpecificBenchmark(
    domain="medical",
    test_cases=[
        {
            "prompt": "What are the symptoms of diabetes?",
            "expected": "medical information",
            "evaluators": {
                "accuracy": medical_accuracy_evaluator,
                "safety": medical_safety_evaluator
            }
        }
    ],
    iterations=5
)

legal_benchmark = DomainSpecificBenchmark(
    domain="legal",
    test_cases=[
        {
            "prompt": "What are the requirements for a valid contract?",
            "expected": "legal information",
            "evaluators": {
                "accuracy": legal_accuracy_evaluator,
                "disclaimer": legal_disclaimer_evaluator
            }
        }
    ],
    iterations=5
)

# Run domain-specific benchmarks
medical_results = await medical_benchmark.run()
legal_results = await legal_benchmark.run()

print(f"Medical accuracy: {medical_results.evaluator_scores['accuracy']:.2f}")
print(f"Medical safety: {medical_results.evaluator_scores['safety']:.2f}")
print(f"Legal accuracy: {legal_results.evaluator_scores['accuracy']:.2f}")
print(f"Legal disclaimer: {legal_results.evaluator_scores['disclaimer']:.2f}")
```

### Composite Score Benchmarks

```python
from llm_dispatcher.benchmarks import CompositeScoreBenchmark

# Define individual evaluators
def accuracy_evaluator(response: str, expected: str) -> float:
    """Evaluate accuracy."""
    return 1.0 if expected.lower() in response.lower() else 0.0

def relevance_evaluator(response: str, expected: str) -> float:
    """Evaluate relevance."""
    # Simple relevance check based on keyword overlap
    response_words = set(response.lower().split())
    expected_words = set(expected.lower().split())
    overlap = len(response_words.intersection(expected_words))
    return overlap / len(expected_words) if expected_words else 0.0

def completeness_evaluator(response: str, expected: str) -> float:
    """Evaluate completeness."""
    # Check if response addresses all aspects of the prompt
    return min(len(response) / 100, 1.0)  # Simple length-based completeness

# Define composite score function
def composite_score(evaluator_scores: dict) -> float:
    """Calculate composite score from individual evaluator scores."""
    weights = {
        "accuracy": 0.4,
        "relevance": 0.3,
        "completeness": 0.3
    }

    weighted_sum = sum(weights[key] * score for key, score in evaluator_scores.items())
    return weighted_sum

# Create composite score benchmark
benchmark = CompositeScoreBenchmark(
    test_cases=[
        {
            "prompt": "Explain machine learning",
            "expected": "technical explanation",
            "evaluators": {
                "accuracy": accuracy_evaluator,
                "relevance": relevance_evaluator,
                "completeness": completeness_evaluator
            },
            "composite_score_function": composite_score
        }
    ],
    iterations=5
)

results = await benchmark.run()
print(f"Composite score: {results.composite_score:.2f}")
print(f"Individual scores: {results.evaluator_scores}")
```

### A/B Testing Benchmarks

```python
from llm_dispatcher.benchmarks import ABTestBenchmark

# Define A/B test evaluator
def ab_test_evaluator(response_a: str, response_b: str, expected: str) -> str:
    """Compare two responses and return the better one."""
    # Simple comparison based on length and keyword presence
    score_a = len(response_a) + (1 if expected.lower() in response_a.lower() else 0)
    score_b = len(response_b) + (1 if expected.lower() in response_b.lower() else 0)

    return "A" if score_a > score_b else "B"

# Create A/B test benchmark
benchmark = ABTestBenchmark(
    test_cases=[
        {
            "prompt": "Write a story about a robot",
            "expected": "creative narrative",
            "evaluator": ab_test_evaluator
        }
    ],
    iterations=10,
    providers_a=["openai"],
    models_a=["gpt-3.5-turbo"],
    providers_b=["anthropic"],
    models_b=["claude-3-haiku"]
)

results = await benchmark.run()
print(f"A wins: {results.a_wins}")
print(f"B wins: {results.b_wins}")
print(f"Winner: {results.winner}")
print(f"Confidence: {results.confidence:.2f}")
```

## Custom Evaluation Classes

### Creating Custom Evaluator Classes

```python
from llm_dispatcher.benchmarks.evaluation import BaseEvaluator

class CustomEvaluator(BaseEvaluator):
    """Custom evaluator class."""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.config = config or {}

    def evaluate(self, response: str, expected: str, context: dict = None) -> float:
        """Evaluate response against expected output."""
        # Implement your custom evaluation logic
        score = 0.0

        # Example: Check for keyword presence
        if self.config.get("check_keywords", True):
            keywords = self.config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in response.lower():
                    score += 0.2

        # Example: Check response length
        if self.config.get("check_length", True):
            min_length = self.config.get("min_length", 10)
            max_length = self.config.get("max_length", 1000)
            if min_length <= len(response) <= max_length:
                score += 0.3

        # Example: Check for specific format
        if self.config.get("check_format", True):
            format_type = self.config.get("format_type", "text")
            if format_type == "json" and response.strip().startswith("{"):
                score += 0.5
            elif format_type == "text":
                score += 0.5

        return min(score, 1.0)

    def get_metrics(self) -> dict:
        """Get evaluation metrics."""
        return {
            "evaluator_type": "custom",
            "config": self.config
        }

# Use custom evaluator
custom_evaluator = CustomEvaluator({
    "check_keywords": True,
    "keywords": ["important", "key", "main"],
    "check_length": True,
    "min_length": 20,
    "max_length": 500,
    "check_format": True,
    "format_type": "text"
})

benchmark = CustomBenchmark(
    test_cases=[
        {
            "prompt": "Summarize the key points",
            "expected": "summary with key points",
            "evaluator": custom_evaluator
        }
    ],
    iterations=5
)

results = await benchmark.run()
print(f"Custom evaluation score: {results.custom_score:.2f}")
```

### Multi-Metric Evaluator

```python
class MultiMetricEvaluator(BaseEvaluator):
    """Evaluator that combines multiple metrics."""

    def __init__(self, metrics: list, weights: dict = None):
        super().__init__()
        self.metrics = metrics
        self.weights = weights or {metric: 1.0 for metric in metrics}

    def evaluate(self, response: str, expected: str, context: dict = None) -> dict:
        """Evaluate response using multiple metrics."""
        scores = {}

        for metric in self.metrics:
            if metric == "accuracy":
                scores[metric] = self._accuracy_score(response, expected)
            elif metric == "relevance":
                scores[metric] = self._relevance_score(response, expected)
            elif metric == "completeness":
                scores[metric] = self._completeness_score(response, expected)
            elif metric == "coherence":
                scores[metric] = self._coherence_score(response, expected)

        # Calculate weighted average
        weighted_sum = sum(self.weights[metric] * score for metric, score in scores.items())
        total_weight = sum(self.weights.values())
        scores["overall"] = weighted_sum / total_weight if total_weight > 0 else 0.0

        return scores

    def _accuracy_score(self, response: str, expected: str) -> float:
        """Calculate accuracy score."""
        return 1.0 if expected.lower() in response.lower() else 0.0

    def _relevance_score(self, response: str, expected: str) -> float:
        """Calculate relevance score."""
        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())
        overlap = len(response_words.intersection(expected_words))
        return overlap / len(expected_words) if expected_words else 0.0

    def _completeness_score(self, response: str, expected: str) -> float:
        """Calculate completeness score."""
        return min(len(response) / 100, 1.0)

    def _coherence_score(self, response: str, expected: str) -> float:
        """Calculate coherence score."""
        # Simple coherence check based on sentence structure
        sentences = response.split(".")
        return min(len(sentences) / 5, 1.0)

# Use multi-metric evaluator
multi_evaluator = MultiMetricEvaluator(
    metrics=["accuracy", "relevance", "completeness", "coherence"],
    weights={"accuracy": 0.4, "relevance": 0.3, "completeness": 0.2, "coherence": 0.1}
)

benchmark = CustomBenchmark(
    test_cases=[
        {
            "prompt": "Explain machine learning",
            "expected": "technical explanation",
            "evaluator": multi_evaluator
        }
    ],
    iterations=5
)

results = await benchmark.run()
print(f"Overall score: {results.evaluator_scores['overall']:.2f}")
print(f"Accuracy: {results.evaluator_scores['accuracy']:.2f}")
print(f"Relevance: {results.evaluator_scores['relevance']:.2f}")
print(f"Completeness: {results.evaluator_scores['completeness']:.2f}")
print(f"Coherence: {results.evaluator_scores['coherence']:.2f}")
```

## Integration with External Systems

### Custom Data Sources

```python
from llm_dispatcher.benchmarks import ExternalDataBenchmark

# Load test cases from external source
def load_test_cases_from_file(file_path: str) -> list:
    """Load test cases from external file."""
    import json
    with open(file_path, 'r') as f:
        return json.load(f)

# Load test cases from database
def load_test_cases_from_db(connection_string: str) -> list:
    """Load test cases from database."""
    # Implementation depends on your database
    pass

# Create benchmark with external data
benchmark = ExternalDataBenchmark(
    data_source="file",
    data_config={"file_path": "test_cases.json"},
    evaluator=custom_evaluator,
    iterations=5
)

results = await benchmark.run()
```

### Custom Reporting

```python
from llm_dispatcher.benchmarks.reports import CustomReporter

class CustomReporter(CustomReporter):
    """Custom reporter for specific needs."""

    def generate_custom_report(self, results, output_file: str):
        """Generate custom report format."""
        # Implement your custom reporting logic
        with open(output_file, 'w') as f:
            f.write("# Custom Benchmark Report\n\n")
            f.write(f"Overall Score: {results.overall_score:.2f}\n\n")

            for test_case, score in results.test_case_scores.items():
                f.write(f"Test Case: {test_case}\n")
                f.write(f"Score: {score:.2f}\n\n")

    def generate_dashboard_data(self, results) -> dict:
        """Generate data for custom dashboard."""
        return {
            "overall_score": results.overall_score,
            "test_case_scores": results.test_case_scores,
            "evaluator_scores": results.evaluator_scores,
            "trends": results.trends
        }

# Use custom reporter
reporter = CustomReporter(results)
reporter.generate_custom_report("custom_report.md")
dashboard_data = reporter.generate_dashboard_data()
```

## Best Practices

### 1. **Define Clear Evaluation Criteria**

```python
# Good: Clear, specific evaluation criteria
def medical_accuracy_evaluator(response: str, expected: str) -> float:
    """Evaluate medical accuracy based on specific criteria."""
    criteria = [
        "contains medical terminology",
        "avoids harmful advice",
        "includes appropriate disclaimers",
        "provides accurate information"
    ]

    score = 0.0
    for criterion in criteria:
        if self._check_criterion(response, criterion):
            score += 0.25

    return score

# Avoid: Vague evaluation criteria
def vague_evaluator(response: str, expected: str) -> float:
    """Evaluate response quality."""
    return 0.5  # Too vague
```

### 2. **Use Multiple Evaluation Dimensions**

```python
# Good: Multiple evaluation dimensions
evaluator = MultiMetricEvaluator(
    metrics=["accuracy", "relevance", "completeness", "coherence"],
    weights={"accuracy": 0.4, "relevance": 0.3, "completeness": 0.2, "coherence": 0.1}
)

# Avoid: Single evaluation dimension
def single_metric_evaluator(response: str, expected: str) -> float:
    return 1.0 if expected in response else 0.0
```

### 3. **Validate Your Evaluators**

```python
# Good: Validate evaluators with known examples
def validate_evaluator(evaluator, test_cases):
    """Validate evaluator with known examples."""
    for test_case in test_cases:
        score = evaluator.evaluate(test_case["response"], test_case["expected"])
        expected_score = test_case["expected_score"]
        assert abs(score - expected_score) < 0.1, f"Evaluator validation failed for {test_case}"

# Avoid: Using unvalidated evaluators
# No validation
```

### 4. **Document Your Evaluation Logic**

```python
# Good: Well-documented evaluation logic
class DocumentedEvaluator(BaseEvaluator):
    """
    Custom evaluator for technical documentation.

    Evaluation criteria:
    1. Accuracy (40%): Correctness of technical information
    2. Clarity (30%): How well the information is explained
    3. Completeness (20%): Coverage of all required topics
    4. Structure (10%): Logical organization of information
    """

    def evaluate(self, response: str, expected: str, context: dict = None) -> float:
        """Evaluate technical documentation quality."""
        # Implementation with clear documentation
        pass

# Avoid: Undocumented evaluation logic
class UndocumentedEvaluator(BaseEvaluator):
    def evaluate(self, response: str, expected: str, context: dict = None) -> float:
        # No documentation
        return 0.5
```

### 5. **Test Your Benchmarks**

```python
# Good: Test your benchmarks
def test_custom_benchmark():
    """Test custom benchmark with known data."""
    benchmark = CustomBenchmark(
        test_cases=[
            {
                "prompt": "What is 2+2?",
                "expected": "4",
                "evaluator": accuracy_evaluator
            }
        ],
        iterations=1
    )

    results = await benchmark.run()
    assert results.custom_score > 0.8, "Benchmark test failed"

# Avoid: Not testing benchmarks
# No testing
```

## Next Steps

- [:octicons-chart-line-24: Benchmark Overview](overview.md) - Comprehensive benchmarking guide
- [:octicons-chart-line-24: Performance Benchmarks](performance.md) - Performance testing and optimization
- [:octicons-dollar-sign-24: Cost Benchmarks](cost.md) - Cost analysis and optimization
- [:octicons-star-24: Quality Benchmarks](quality.md) - Quality assessment and evaluation
