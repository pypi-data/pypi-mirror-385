"""
Utility functions for LLM-Dispatcher benchmarks.

This module provides utility functions for benchmark configuration validation,
data processing, formatting, and helper functions.
"""

import json
import csv
import uuid
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import statistics


def validate_benchmark_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate benchmark configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    required_fields = ["test_prompts", "iterations"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate test_prompts
    if "test_prompts" in config:
        test_prompts = config["test_prompts"]
        if not isinstance(test_prompts, list):
            errors.append("test_prompts must be a list")
        elif len(test_prompts) == 0:
            errors.append("test_prompts cannot be empty")
        else:
            for i, prompt in enumerate(test_prompts):
                if not isinstance(prompt, str) or not prompt.strip():
                    errors.append(f"test_prompts[{i}] must be a non-empty string")

    # Validate iterations
    if "iterations" in config:
        iterations = config["iterations"]
        if not isinstance(iterations, int) or iterations <= 0:
            errors.append("iterations must be a positive integer")

    # Validate concurrent_requests if present
    if "concurrent_requests" in config:
        concurrent_requests = config["concurrent_requests"]
        if not isinstance(concurrent_requests, int) or concurrent_requests <= 0:
            errors.append("concurrent_requests must be a positive integer")

    # Validate timeout if present
    if "timeout" in config:
        timeout = config["timeout"]
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("timeout must be a positive number")

    # Validate providers if present
    if "providers" in config:
        providers = config["providers"]
        if not isinstance(providers, list):
            errors.append("providers must be a list")
        elif len(providers) == 0:
            errors.append("providers cannot be empty")
        else:
            for i, provider in enumerate(providers):
                if not isinstance(provider, str) or not provider.strip():
                    errors.append(f"providers[{i}] must be a non-empty string")

    # Validate models if present
    if "models" in config:
        models = config["models"]
        if not isinstance(models, list):
            errors.append("models must be a list")
        elif len(models) == 0:
            errors.append("models cannot be empty")
        else:
            for i, model in enumerate(models):
                if not isinstance(model, str) or not model.strip():
                    errors.append(f"models[{i}] must be a non-empty string")

    return len(errors) == 0, errors


def calculate_metrics(
    latencies: List[float], costs: List[float], successes: List[bool]
) -> Dict[str, float]:
    """
    Calculate statistical metrics for benchmark data.

    Args:
        latencies: List of latency values in milliseconds
        costs: List of cost values
        successes: List of success/failure boolean values

    Returns:
        Dictionary containing statistical metrics
    """
    if not latencies or not costs or not successes:
        return {
            "avg_latency": 0.0,
            "min_latency": 0.0,
            "max_latency": 0.0,
            "avg_cost": 0.0,
            "min_cost": 0.0,
            "max_cost": 0.0,
            "total_cost": 0.0,
            "cost_per_token": 0.0,
            "success_rate": 0.0,
            "total_requests": 0,
            "failed_requests": 0,
        }

    # Calculate latency metrics
    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    # Calculate cost metrics
    avg_cost = statistics.mean(costs)
    min_cost = min(costs)
    max_cost = max(costs)
    total_cost = sum(costs)

    # Calculate success metrics
    total_requests = len(successes)
    successful_requests = sum(successes)
    failed_requests = total_requests - successful_requests
    success_rate = successful_requests / total_requests if total_requests > 0 else 0.0

    # Calculate cost per token (assuming average tokens per request)
    avg_tokens_per_request = 100  # Default assumption
    cost_per_token = (
        total_cost / (total_requests * avg_tokens_per_request)
        if total_requests > 0
        else 0.0
    )

    return {
        "avg_latency": avg_latency,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "avg_cost": avg_cost,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "total_cost": total_cost,
        "cost_per_token": cost_per_token,
        "success_rate": success_rate,
        "total_requests": total_requests,
        "failed_requests": failed_requests,
    }


def export_benchmark_data(data: Dict[str, Any], format: str = "json") -> str:
    """
    Export benchmark data in specified format.

    Args:
        data: Benchmark data dictionary
        format: Export format ("json", "csv")

    Returns:
        String representation of the data in specified format
    """
    if format.lower() == "json":
        return json.dumps(data, indent=2, default=str)
    elif format.lower() == "csv":
        if not data:
            return ""

        # Convert dict to CSV format
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(data.keys())

        # Write data (flatten nested dicts)
        row = []
        for value in data.values():
            if isinstance(value, dict):
                row.append(json.dumps(value))
            else:
                row.append(str(value))
        writer.writerow(row)

        return output.getvalue()
    else:
        raise ValueError(f"Unsupported format: {format}")


def format_duration(milliseconds: float) -> str:
    """
    Format duration in milliseconds to human-readable string.

    Args:
        milliseconds: Duration in milliseconds

    Returns:
        Formatted duration string
    """
    if milliseconds < 1000:
        return f"{milliseconds:.2f}ms"
    elif milliseconds < 60000:
        seconds = milliseconds / 1000
        return f"{seconds:.2f}s"
    elif milliseconds < 3600000:
        minutes = milliseconds / 60000
        return f"{minutes:.2f}m"
    else:
        hours = milliseconds / 3600000
        return f"{hours:.2f}h"


def format_cost(cost: float) -> str:
    """
    Format cost value to human-readable string.

    Args:
        cost: Cost value

    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        return f"${cost:.3f}"
    elif cost < 1:
        return f"${cost:.2f}"
    elif cost < 1000:
        return f"${cost:.2f}"
    else:
        return f"${cost:,.2f}"


def format_latency(latency_ms: float) -> str:
    """
    Format latency in milliseconds to human-readable string.

    Args:
        latency_ms: Latency in milliseconds

    Returns:
        Formatted latency string
    """
    if latency_ms < 1:
        return f"{latency_ms:.1f}ms"
    else:
        return f"{latency_ms:,.0f}ms"


def generate_benchmark_id() -> str:
    """
    Generate a unique benchmark ID.

    Returns:
        Unique benchmark ID string
    """
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"benchmark_{timestamp}_{unique_id}"


def parse_benchmark_config(config_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Parse benchmark configuration from file.

    Args:
        config_file: Path to configuration file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_file)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, "r") as f:
        if config_file.suffix.lower() == ".json":
            return json.load(f)
        else:
            raise ValueError(
                f"Unsupported configuration file format: {config_file.suffix}"
            )


def merge_benchmark_results(
    results_list: List[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Merge multiple benchmark result lists.

    Args:
        results_list: List of benchmark result lists

    Returns:
        Merged benchmark results
    """
    merged = []
    for results in results_list:
        merged.extend(results)
    return merged


def filter_benchmark_results(
    results: List[Dict[str, Any]], filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Filter benchmark results based on criteria.

    Args:
        results: List of benchmark results
        filters: Filter criteria

    Returns:
        Filtered benchmark results
    """
    filtered = []

    for result in results:
        include = True

        for key, value in filters.items():
            if key not in result:
                include = False
                break

            if isinstance(value, list):
                if result[key] not in value:
                    include = False
                    break
            else:
                if result[key] != value:
                    include = False
                    break

        if include:
            filtered.append(result)

    return filtered


def sort_benchmark_results(
    results: List[Dict[str, Any]], sort_key: str, reverse: bool = False
) -> List[Dict[str, Any]]:
    """
    Sort benchmark results by specified key.

    Args:
        results: List of benchmark results
        sort_key: Key to sort by
        reverse: Whether to sort in reverse order

    Returns:
        Sorted benchmark results
    """
    return sorted(results, key=lambda x: x.get(sort_key, 0), reverse=reverse)


def aggregate_benchmark_metrics(
    results: List[Dict[str, Any]], group_by: str = "provider"
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate benchmark metrics by grouping key.

    Args:
        results: List of benchmark results
        group_by: Key to group by

    Returns:
        Aggregated metrics by group
    """
    groups = {}

    for result in results:
        group_key = result.get(group_by, "unknown")

        if group_key not in groups:
            groups[group_key] = {
                "count": 0,
                "latency_ms": [],
                "success_rate": [],
                "total_cost": [],
                "tokens_per_dollar": [],
            }

        groups[group_key]["count"] += 1

        # Collect metrics
        if "latency_ms" in result:
            groups[group_key]["latency_ms"].append(result["latency_ms"])
        if "success_rate" in result:
            groups[group_key]["success_rate"].append(result["success_rate"])
        if "total_cost" in result:
            groups[group_key]["total_cost"].append(result["total_cost"])
        if "tokens_per_dollar" in result:
            groups[group_key]["tokens_per_dollar"].append(result["tokens_per_dollar"])

    # Calculate aggregated metrics
    aggregated = {}
    for group_key, data in groups.items():
        aggregated[group_key] = {
            "count": data["count"],
            "avg_latency_ms": (
                statistics.mean(data["latency_ms"]) if data["latency_ms"] else 0.0
            ),
            "avg_success_rate": (
                statistics.mean(data["success_rate"]) if data["success_rate"] else 0.0
            ),
            "avg_total_cost": (
                statistics.mean(data["total_cost"]) if data["total_cost"] else 0.0
            ),
            "avg_tokens_per_dollar": (
                statistics.mean(data["tokens_per_dollar"])
                if data["tokens_per_dollar"]
                else 0.0
            ),
        }

    return aggregated


def validate_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Validate test cases for custom benchmarks.

    Args:
        test_cases: List of test cases to validate

    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(test_cases, list):
        raise ValueError("test_cases must be a list")

    if len(test_cases) == 0:
        raise ValueError("Test cases cannot be empty")

    for i, test_case in enumerate(test_cases):
        if not isinstance(test_case, dict):
            raise ValueError(f"test_cases[{i}] must be a dictionary")

        # Check required fields
        if "prompt" not in test_case:
            raise ValueError(f"test_cases[{i}] missing required field: prompt")
        elif (
            not isinstance(test_case["prompt"], str) or not test_case["prompt"].strip()
        ):
            raise ValueError(f"test_cases[{i}] prompt must be a non-empty string")

        # Check evaluator, expected_output, or expected
        if (
            "evaluator" not in test_case
            and "expected_output" not in test_case
            and "expected" not in test_case
        ):
            raise ValueError("Missing required fields")

        # Validate evaluator if present
        if "evaluator" in test_case and not callable(test_case["evaluator"]):
            raise ValueError(f"test_cases[{i}] evaluator must be callable")

        # Validate expected_output if present
        if "expected_output" in test_case and not isinstance(
            test_case["expected_output"], str
        ):
            raise ValueError(f"test_cases[{i}] expected_output must be a string")

        # Validate expected if present
        if "expected" in test_case and not isinstance(test_case["expected"], str):
            raise ValueError(f"test_cases[{i}] expected must be a string")

    return True


def validate_test_prompts(test_prompts: List[str]) -> bool:
    """
    Validate test prompts for benchmarks.

    Args:
        test_prompts: List of test prompts to validate

    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(test_prompts, list):
        raise ValueError("test_prompts must be a list")

    if len(test_prompts) == 0:
        raise ValueError("Test prompts cannot be empty")

    for i, prompt in enumerate(test_prompts):
        if not isinstance(prompt, str):
            raise ValueError("All prompts must be strings")
        elif not prompt.strip():
            raise ValueError(f"test_prompts[{i}] cannot be empty")
        elif len(prompt) > 10000:  # Reasonable limit
            raise ValueError(f"test_prompts[{i}] is too long (max 10000 characters)")

    return True


def create_benchmark_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a summary of benchmark results.

    Args:
        results: List of benchmark results

    Returns:
        Summary dictionary
    """
    if not results:
        return {
            "total_benchmarks": 0,
            "providers": [],
            "models": [],
            "total_duration": 0.0,
            "total_requests": 0,
            "total_errors": 0,
        }

    providers = set()
    models = set()
    total_duration = 0.0
    total_requests = 0
    total_errors = 0

    for result in results:
        if "provider" in result:
            providers.add(result["provider"])
        if "model" in result:
            models.add(result["model"])
        if "duration" in result:
            total_duration += result["duration"]
        if "total_requests" in result:
            total_requests += result["total_requests"]
        if "error_count" in result:
            total_errors += result["error_count"]

    return {
        "total_benchmarks": len(results),
        "providers": sorted(list(providers)),
        "models": sorted(list(models)),
        "total_duration": total_duration,
        "total_requests": total_requests,
        "total_errors": total_errors,
        "success_rate": (
            (total_requests - total_errors) / total_requests
            if total_requests > 0
            else 0.0
        ),
    }


def normalize_benchmark_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize benchmark results to ensure consistent structure.

    Args:
        results: List of benchmark results

    Returns:
        Normalized benchmark results
    """
    normalized = []

    for result in results:
        normalized_result = {
            "provider": result.get("provider", "unknown"),
            "model": result.get("model", "unknown"),
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "latency_ms": result.get("latency_ms", 0.0),
            "success_rate": result.get("success_rate", 0.0),
            "total_requests": result.get("total_requests", 0),
            "error_count": result.get("error_count", 0),
            "total_cost": result.get("total_cost", 0.0),
            "tokens_per_dollar": result.get("tokens_per_dollar", 0.0),
            "metadata": result.get("metadata", {}),
        }
        normalized.append(normalized_result)

    return normalized


def compare_benchmark_results(
    results1: List[Dict[str, Any]], results2: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare two sets of benchmark results.

    Args:
        results1: First set of benchmark results
        results2: Second set of benchmark results

    Returns:
        Comparison results
    """
    # Normalize both result sets
    norm1 = normalize_benchmark_results(results1)
    norm2 = normalize_benchmark_results(results2)

    # Calculate metrics for each set
    metrics1 = calculate_metrics([r["latency_ms"] for r in norm1])
    metrics2 = calculate_metrics([r["latency_ms"] for r in norm2])

    # Calculate improvement percentages
    latency_improvement = (
        ((metrics1["mean"] - metrics2["mean"]) / metrics1["mean"] * 100)
        if metrics1["mean"] > 0
        else 0
    )

    success_rate1 = (
        statistics.mean([r["success_rate"] for r in norm1]) if norm1 else 0.0
    )
    success_rate2 = (
        statistics.mean([r["success_rate"] for r in norm2]) if norm2 else 0.0
    )
    success_rate_improvement = (
        ((success_rate2 - success_rate1) / success_rate1 * 100)
        if success_rate1 > 0
        else 0
    )

    return {
        "results1_count": len(norm1),
        "results2_count": len(norm2),
        "latency_improvement_percent": latency_improvement,
        "success_rate_improvement_percent": success_rate_improvement,
        "results1_avg_latency": metrics1["mean"],
        "results2_avg_latency": metrics2["mean"],
        "results1_avg_success_rate": success_rate1,
        "results2_avg_success_rate": success_rate2,
        "better_performance": "results2" if latency_improvement > 0 else "results1",
        "better_reliability": (
            "results2" if success_rate_improvement > 0 else "results1"
        ),
    }


def export_to_excel(
    results: List[Dict[str, Any]],
    filepath: Union[str, Path],
    sheet_name: str = "Benchmark Results",
) -> None:
    """
    Export benchmark data to Excel file.

    Args:
        results: List of benchmark results
        filepath: Path to save the Excel file
        sheet_name: Name of the Excel sheet
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for Excel export. Install with: pip install pandas openpyxl"
        )

    if not results:
        return

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Save to Excel
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def import_from_excel(
    filepath: Union[str, Path], sheet_name: str = "Benchmark Results"
) -> List[Dict[str, Any]]:
    """
    Import benchmark data from Excel file.

    Args:
        filepath: Path to the Excel file
        sheet_name: Name of the Excel sheet

    Returns:
        List of benchmark results
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for Excel import. Install with: pip install pandas openpyxl"
        )

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    # Read Excel file
    df = pd.read_excel(filepath, sheet_name=sheet_name)

    # Convert to list of dictionaries
    return df.to_dict("records")


def benchmark_data_to_dict(benchmark_data: Any) -> Dict[str, Any]:
    """
    Convert benchmark data to dictionary format.

    Args:
        benchmark_data: Benchmark data object

    Returns:
        Dictionary representation of benchmark data
    """
    if isinstance(benchmark_data, dict):
        return benchmark_data
    elif hasattr(benchmark_data, "__dict__"):
        return benchmark_data.__dict__
    elif hasattr(benchmark_data, "_asdict"):  # namedtuple
        return benchmark_data._asdict()
    else:
        # Try to convert to dict using vars()
        try:
            return vars(benchmark_data)
        except TypeError:
            return {"data": str(benchmark_data)}


def dict_to_benchmark_data(data: Dict[str, Any], data_type: str = "dict") -> Any:
    """
    Convert dictionary to benchmark data object.

    Args:
        data: Dictionary data
        data_type: Type of object to create ("dict", "namedtuple", "dataclass")

    Returns:
        Benchmark data object
    """
    if data_type == "dict":
        return data
    elif data_type == "namedtuple":
        from collections import namedtuple

        # Create a dynamic namedtuple
        keys = list(data.keys())
        BenchmarkData = namedtuple("BenchmarkData", keys)
        return BenchmarkData(**data)
    else:
        # Default to dict
        return data
