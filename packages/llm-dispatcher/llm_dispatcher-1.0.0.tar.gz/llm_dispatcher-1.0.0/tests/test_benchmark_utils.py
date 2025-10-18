"""
Test cases for LLM-Dispatcher benchmark utilities.

This module contains test cases for benchmark utility functions,
configuration validation, and helper functions.
"""

import pytest
import json
import csv
import tempfile
import os
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any

from llm_dispatcher.benchmarks.utils import (
    validate_benchmark_config,
    calculate_metrics,
    export_benchmark_data,
    format_duration,
    format_cost,
    format_latency,
    generate_benchmark_id,
    parse_benchmark_config,
    merge_benchmark_results,
    filter_benchmark_results,
    sort_benchmark_results,
    aggregate_benchmark_metrics,
    validate_test_cases,
    validate_test_prompts,
    create_benchmark_summary,
    export_to_excel,
    import_from_excel,
    benchmark_data_to_dict,
    dict_to_benchmark_data,
)


class TestBenchmarkConfiguration:
    """Test cases for benchmark configuration validation."""

    def test_validate_benchmark_config_valid(self):
        """Test validation of valid benchmark configuration."""
        valid_config = {
            "iterations": 10,
            "concurrent_requests": 5,
            "timeout": 30000,
            "max_retries": 3,
            "warmup_requests": 2,
            "cooldown_time": 1000,
        }

        assert validate_benchmark_config(valid_config) is True

    def test_validate_benchmark_config_invalid_iterations(self):
        """Test validation with invalid iterations."""
        invalid_config = {"iterations": -1, "concurrent_requests": 5, "timeout": 30000}

        with pytest.raises(ValueError, match="iterations must be positive"):
            validate_benchmark_config(invalid_config)

    def test_validate_benchmark_config_invalid_concurrent_requests(self):
        """Test validation with invalid concurrent requests."""
        invalid_config = {"iterations": 10, "concurrent_requests": 0, "timeout": 30000}

        with pytest.raises(ValueError, match="concurrent_requests must be positive"):
            validate_benchmark_config(invalid_config)

    def test_validate_benchmark_config_invalid_timeout(self):
        """Test validation with invalid timeout."""
        invalid_config = {
            "iterations": 10,
            "concurrent_requests": 5,
            "timeout": "invalid",
        }

        with pytest.raises(ValueError, match="timeout must be a positive number"):
            validate_benchmark_config(invalid_config)

    def test_validate_benchmark_config_missing_required(self):
        """Test validation with missing required fields."""
        incomplete_config = {
            "iterations": 10
            # Missing concurrent_requests and timeout
        }

        with pytest.raises(ValueError, match="Missing required configuration fields"):
            validate_benchmark_config(incomplete_config)

    def test_validate_benchmark_config_extra_fields(self):
        """Test validation with extra fields (should be allowed)."""
        config_with_extra = {
            "iterations": 10,
            "concurrent_requests": 5,
            "timeout": 30000,
            "extra_field": "extra_value",
        }

        assert validate_benchmark_config(config_with_extra) is True

    def test_parse_benchmark_config(self):
        """Test parsing benchmark configuration from file."""
        config_data = {
            "iterations": 15,
            "concurrent_requests": 8,
            "timeout": 45000,
            "max_retries": 5,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            parsed_config = parse_benchmark_config(config_file)
            assert parsed_config["iterations"] == 15
            assert parsed_config["concurrent_requests"] == 8
            assert parsed_config["timeout"] == 45000
            assert parsed_config["max_retries"] == 5
        finally:
            os.unlink(config_file)

    def test_parse_benchmark_config_invalid_file(self):
        """Test parsing invalid configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            config_file = f.name

        try:
            with pytest.raises(ValueError, match="Invalid configuration file"):
                parse_benchmark_config(config_file)
        finally:
            os.unlink(config_file)


class TestBenchmarkMetrics:
    """Test cases for benchmark metrics calculation."""

    def test_calculate_metrics_basic(self):
        """Test basic metrics calculation."""
        latencies = [1000, 1200, 800, 1500, 900]
        costs = [0.01, 0.012, 0.008, 0.015, 0.009]
        successes = [True, True, True, False, True]

        metrics = calculate_metrics(latencies, costs, successes)

        assert metrics["avg_latency"] == 1080.0  # (1000+1200+800+1500+900)/5
        assert metrics["min_latency"] == 800
        assert metrics["max_latency"] == 1500
        assert metrics["success_rate"] == 0.8  # 4/5
        assert metrics["avg_cost"] == 0.0108  # (0.01+0.012+0.008+0.015+0.009)/5
        assert metrics["total_cost"] == 0.054  # sum of costs
        assert metrics["cost_per_token"] > 0

    def test_calculate_metrics_empty_data(self):
        """Test metrics calculation with empty data."""
        latencies = []
        costs = []
        successes = []

        with pytest.raises(ValueError, match="Cannot calculate metrics for empty data"):
            calculate_metrics(latencies, costs, successes)

    def test_calculate_metrics_mismatched_lengths(self):
        """Test metrics calculation with mismatched data lengths."""
        latencies = [1000, 1200, 800]
        costs = [0.01, 0.012]
        successes = [True, True, True, False]

        with pytest.raises(ValueError, match="Data arrays must have the same length"):
            calculate_metrics(latencies, costs, successes)

    def test_calculate_metrics_all_failures(self):
        """Test metrics calculation with all failures."""
        latencies = [1000, 1200, 800]
        costs = [0.01, 0.012, 0.008]
        successes = [False, False, False]

        metrics = calculate_metrics(latencies, costs, successes)

        assert metrics["success_rate"] == 0.0
        assert metrics["failed_requests"] == 3
        assert metrics["total_requests"] == 3

    def test_calculate_metrics_percentiles(self):
        """Test metrics calculation with percentiles."""
        latencies = list(range(1, 101))  # 1 to 100
        costs = [0.01] * 100
        successes = [True] * 100

        metrics = calculate_metrics(latencies, costs, successes)

        assert metrics["avg_latency"] == 50.5  # Average latency
        assert metrics["min_latency"] == 1.0  # Min latency
        assert metrics["max_latency"] == 100.0  # Max latency
        assert metrics["total_cost"] == 1.0  # Total cost


class TestBenchmarkDataExport:
    """Test cases for benchmark data export functionality."""

    def test_export_benchmark_data_json(self):
        """Test exporting benchmark data as JSON."""
        data = {
            "performance": {
                "avg_latency": 1000,
                "throughput": 60,
                "success_rate": 0.95,
            },
            "cost": {"avg_cost": 0.01, "total_cost": 1.0},
            "quality": {"accuracy": 0.9, "quality_score": 8.5},
        }

        json_data = export_benchmark_data(data, format="json")

        assert json_data is not None
        assert isinstance(json_data, str)

        # Verify it's valid JSON
        parsed_data = json.loads(json_data)
        assert parsed_data["performance"]["avg_latency"] == 1000
        assert parsed_data["cost"]["avg_cost"] == 0.01
        assert parsed_data["quality"]["accuracy"] == 0.9

    def test_export_benchmark_data_csv(self):
        """Test exporting benchmark data as CSV."""
        data = {
            "performance": {
                "avg_latency": 1000,
                "throughput": 60,
                "success_rate": 0.95,
            },
            "cost": {"avg_cost": 0.01, "total_cost": 1.0},
        }

        csv_data = export_benchmark_data(data, format="csv")

        assert csv_data is not None
        assert isinstance(csv_data, str)

        # Verify CSV format
        lines = csv_data.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one data row
        assert "avg_latency" in lines[0]  # Header should contain field names

    def test_export_benchmark_data_invalid_format(self):
        """Test exporting with invalid format."""
        data = {"test": "data"}

        with pytest.raises(ValueError, match="Unsupported export format"):
            export_benchmark_data(data, format="invalid")

    def test_export_to_excel(self):
        """Test exporting benchmark data to Excel."""
        data = {
            "performance": {"avg_latency": 1000, "throughput": 60},
            "cost": {"avg_cost": 0.01, "total_cost": 1.0},
        }

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            excel_file = f.name

        try:
            result = export_to_excel(data, excel_file)
            assert result is not None
            assert os.path.exists(excel_file)
        finally:
            if os.path.exists(excel_file):
                os.unlink(excel_file)

    def test_import_from_excel(self):
        """Test importing benchmark data from Excel."""
        # First create an Excel file
        data = {"performance": {"avg_latency": 1000, "throughput": 60}}

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            excel_file = f.name

        try:
            export_to_excel(data, excel_file)

            # Now import it
            imported_data = import_from_excel(excel_file)
            assert imported_data is not None
            assert "performance" in imported_data
        finally:
            if os.path.exists(excel_file):
                os.unlink(excel_file)


class TestBenchmarkFormatting:
    """Test cases for benchmark data formatting."""

    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(1000) == "1.00s"
        assert format_duration(500) == "500.00ms"
        assert format_duration(60000) == "1.00m"
        assert format_duration(3600000) == "1.00h"

    def test_format_cost(self):
        """Test cost formatting."""
        assert format_cost(0.01) == "$0.01"
        assert format_cost(0.001) == "$0.001"
        assert format_cost(1.5) == "$1.50"
        assert format_cost(1000) == "$1,000.00"

    def test_format_latency(self):
        """Test latency formatting."""
        assert format_latency(1000) == "1,000ms"
        assert format_latency(500) == "500ms"
        assert format_latency(1500) == "1,500ms"
        assert format_latency(0.5) == "0.5ms"


class TestBenchmarkUtilities:
    """Test cases for benchmark utility functions."""

    def test_generate_benchmark_id(self):
        """Test benchmark ID generation."""
        benchmark_id = generate_benchmark_id()

        assert benchmark_id is not None
        assert isinstance(benchmark_id, str)
        assert len(benchmark_id) > 0

    def test_generate_benchmark_id_unique(self):
        """Test that generated benchmark IDs are unique."""
        ids = [generate_benchmark_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All IDs should be unique

    def test_merge_benchmark_results(self):
        """Test merging benchmark results."""
        results1 = {
            "performance": {"avg_latency": 1000, "throughput": 60},
            "cost": {"avg_cost": 0.01},
        }

        results2 = {
            "performance": {"avg_latency": 1200, "throughput": 50},
            "cost": {"avg_cost": 0.012},
        }

        merged = merge_benchmark_results([results1, results2])

        assert merged is not None
        assert "performance" in merged
        assert "cost" in merged
        # Should have combined metrics
        assert merged["performance"]["total_requests"] == 2

    def test_filter_benchmark_results(self):
        """Test filtering benchmark results."""
        results = {
            "performance": {"avg_latency": 1000, "success_rate": 0.95},
            "cost": {"avg_cost": 0.01},
            "quality": {"accuracy": 0.9},
        }

        # Filter by success rate
        filtered = filter_benchmark_results(results, {"success_rate": 0.9})
        assert filtered is not None

        # Filter by cost
        filtered = filter_benchmark_results(results, {"max_cost": 0.02})
        assert filtered is not None

    def test_sort_benchmark_results(self):
        """Test sorting benchmark results."""
        results = [
            {"performance": {"avg_latency": 1200}},
            {"performance": {"avg_latency": 800}},
            {"performance": {"avg_latency": 1000}},
        ]

        sorted_results = sort_benchmark_results(results, "avg_latency")

        assert len(sorted_results) == 3
        assert sorted_results[0]["performance"]["avg_latency"] == 800
        assert sorted_results[1]["performance"]["avg_latency"] == 1000
        assert sorted_results[2]["performance"]["avg_latency"] == 1200

    def test_aggregate_benchmark_metrics(self):
        """Test aggregating benchmark metrics."""
        metrics_list = [
            {"avg_latency": 1000, "throughput": 60, "success_rate": 0.95},
            {"avg_latency": 1200, "throughput": 50, "success_rate": 0.90},
            {"avg_latency": 800, "throughput": 70, "success_rate": 0.98},
        ]

        aggregated = aggregate_benchmark_metrics(metrics_list)

        assert aggregated is not None
        assert "avg_latency" in aggregated
        assert "throughput" in aggregated
        assert "success_rate" in aggregated

        # Should have calculated averages
        assert aggregated["avg_latency"] == 1000  # (1000+1200+800)/3
        assert aggregated["throughput"] == 60  # (60+50+70)/3
        assert aggregated["success_rate"] == 0.943  # (0.95+0.90+0.98)/3


class TestBenchmarkValidation:
    """Test cases for benchmark data validation."""

    def test_validate_test_cases_valid(self):
        """Test validation of valid test cases."""
        test_cases = [
            {
                "prompt": "What is AI?",
                "expected": "Artificial Intelligence",
                "type": "factual",
            },
            {
                "prompt": "Write a poem",
                "expected": "creative content",
                "type": "creative",
            },
        ]

        assert validate_test_cases(test_cases) is True

    def test_validate_test_cases_missing_fields(self):
        """Test validation with missing required fields."""
        test_cases = [
            {
                "prompt": "What is AI?",
                # Missing expected and type
            }
        ]

        with pytest.raises(ValueError, match="Missing required fields"):
            validate_test_cases(test_cases)

    def test_validate_test_cases_empty(self):
        """Test validation with empty test cases."""
        with pytest.raises(ValueError, match="Test cases cannot be empty"):
            validate_test_cases([])

    def test_validate_test_prompts_valid(self):
        """Test validation of valid test prompts."""
        prompts = ["Write a story", "Explain AI", "Generate code"]

        assert validate_test_prompts(prompts) is True

    def test_validate_test_prompts_empty(self):
        """Test validation with empty prompts."""
        with pytest.raises(ValueError, match="Test prompts cannot be empty"):
            validate_test_prompts([])

    def test_validate_test_prompts_invalid_type(self):
        """Test validation with invalid prompt types."""
        with pytest.raises(ValueError, match="All prompts must be strings"):
            validate_test_prompts(["valid prompt", 123, "another valid prompt"])


class TestBenchmarkSummary:
    """Test cases for benchmark summary generation."""

    def test_create_benchmark_summary(self):
        """Test creating benchmark summary."""
        results = {
            "performance": {
                "avg_latency": 1000,
                "throughput": 60,
                "success_rate": 0.95,
            },
            "cost": {"avg_cost": 0.01, "total_cost": 1.0},
            "quality": {"accuracy": 0.9, "quality_score": 8.5},
        }

        summary = create_benchmark_summary(results)

        assert summary is not None
        assert isinstance(summary, str)
        assert "Performance" in summary
        assert "Cost" in summary
        assert "Quality" in summary
        assert "1000" in summary  # Should contain latency
        assert "0.01" in summary  # Should contain cost

    def test_create_benchmark_summary_minimal(self):
        """Test creating summary with minimal data."""
        results = {"performance": {"avg_latency": 1000}}

        summary = create_benchmark_summary(results)

        assert summary is not None
        assert isinstance(summary, str)
        assert "Performance" in summary


class TestBenchmarkDataConversion:
    """Test cases for benchmark data conversion."""

    def test_benchmark_data_to_dict(self):
        """Test converting benchmark data to dictionary."""
        # Mock benchmark data object
        mock_data = MagicMock()
        mock_data.performance = MagicMock()
        mock_data.performance.avg_latency = 1000
        mock_data.performance.throughput = 60
        mock_data.cost = MagicMock()
        mock_data.cost.avg_cost = 0.01
        mock_data.quality = MagicMock()
        mock_data.quality.accuracy = 0.9

        data_dict = benchmark_data_to_dict(mock_data)

        assert isinstance(data_dict, dict)
        assert "performance" in data_dict
        assert "cost" in data_dict
        assert "quality" in data_dict
        assert data_dict["performance"]["avg_latency"] == 1000

    def test_dict_to_benchmark_data(self):
        """Test converting dictionary to benchmark data."""
        data_dict = {
            "performance": {"avg_latency": 1000, "throughput": 60},
            "cost": {"avg_cost": 0.01},
        }

        benchmark_data = dict_to_benchmark_data(data_dict)

        assert benchmark_data is not None
        assert hasattr(benchmark_data, "performance")
        assert hasattr(benchmark_data, "cost")
        assert benchmark_data.performance.avg_latency == 1000
        assert benchmark_data.cost.avg_cost == 0.01


class TestBenchmarkErrorHandling:
    """Test cases for benchmark error handling."""

    def test_validate_benchmark_config_with_none(self):
        """Test configuration validation with None values."""
        config_with_none = {
            "iterations": None,
            "concurrent_requests": 5,
            "timeout": 30000,
        }

        with pytest.raises(ValueError, match="iterations must be a positive number"):
            validate_benchmark_config(config_with_none)

    def test_calculate_metrics_with_none_values(self):
        """Test metrics calculation with None values."""
        latencies = [1000, None, 800]
        costs = [0.01, 0.012, 0.008]
        successes = [True, True, True]

        with pytest.raises(
            ValueError, match="Cannot calculate metrics with None values"
        ):
            calculate_metrics(latencies, costs, successes)

    def test_export_benchmark_data_with_none(self):
        """Test exporting data with None values."""
        data = {"performance": {"avg_latency": None, "throughput": 60}}

        # Should handle None values gracefully
        json_data = export_benchmark_data(data, format="json")
        assert json_data is not None
        assert "null" in json_data  # None should be serialized as null

    def test_merge_benchmark_results_with_invalid_data(self):
        """Test merging results with invalid data."""
        results1 = {"performance": {"avg_latency": 1000}}
        results2 = "invalid_data"

        with pytest.raises(ValueError, match="All results must be dictionaries"):
            merge_benchmark_results([results1, results2])


if __name__ == "__main__":
    pytest.main([__file__])
