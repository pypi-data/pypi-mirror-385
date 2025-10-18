"""
Benchmark reporter for generating comprehensive reports from benchmark results.

This module provides reporting capabilities for benchmark results including
HTML reports, JSON exports, and summary visualizations.
"""

import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import base64

from .performance_benchmark import BenchmarkResult
from .cost_benchmark import CostBenchmarkResult
from .custom_benchmark import CustomBenchmarkResult
from .benchmark_analyzer import BenchmarkAnalyzer


@dataclass
class ReportConfig:
    """Configuration for benchmark reports."""

    include_performance: bool = True
    include_cost: bool = True
    include_custom: bool = True
    include_statistics: bool = True
    include_recommendations: bool = True
    include_charts: bool = True
    output_format: str = "html"  # html, json, markdown
    title: str = "LLM Benchmark Report"
    description: str = "Comprehensive benchmark analysis report"


class BenchmarkReporter:
    """
    Comprehensive reporter for benchmark results.

    This class provides various reporting formats and visualizations
    for benchmark analysis results.
    """

    def __init__(self, results: List[Any], config: Optional[ReportConfig] = None):
        """
        Initialize benchmark reporter.

        Args:
            results: List of benchmark results to report on
            config: Report configuration options
        """
        self.results = results
        self.config = config or ReportConfig()
        self.analyzer = BenchmarkAnalyzer(results)

    def generate_html_report(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """
        Generate comprehensive HTML report.

        Args:
            filepath: Optional file path to save the report

        Returns:
            HTML content as string
        """
        html_content = self._generate_html_template()

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

        return html_content

    def generate_json_report(
        self, filepath: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON report with all benchmark data and analysis.

        Args:
            filepath: Optional file path to save the report

        Returns:
            Report data as dictionary
        """
        report_data = {
            "metadata": {
                "title": self.config.title,
                "description": self.config.description,
                "generated_at": datetime.now().isoformat(),
                "total_benchmarks": len(self.results),
            },
            "results": self._serialize_results(),
            "analysis": self._generate_analysis_data(),
            "summary": self._generate_summary_data(),
        }

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)

        return report_data

    def generate_markdown_report(
        self, filepath: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Generate Markdown report.

        Args:
            filepath: Optional file path to save the report

        Returns:
            Markdown content as string
        """
        md_content = self._generate_markdown_content()

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)

        return md_content

    def _generate_html_template(self) -> str:
        """Generate the main HTML template."""
        insights = self.analyzer.get_performance_insights()
        comparison = self.analyzer.compare_providers()

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{self.config.title}</h1>
            <p class="description">{self.config.description}</p>
            <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <nav class="toc">
            <h2>Table of Contents</h2>
            <ul>
                <li><a href="#summary">Executive Summary</a></li>
                <li><a href="#performance">Performance Analysis</a></li>
                <li><a href="#cost">Cost Analysis</a></li>
                <li><a href="#custom">Custom Benchmark Analysis</a></li>
                <li><a href="#comparison">Provider Comparison</a></li>
                <li><a href="#recommendations">Recommendations</a></li>
                <li><a href="#detailed-results">Detailed Results</a></li>
            </ul>
        </nav>
        
        <main>
            {self._generate_summary_section(insights)}
            {self._generate_performance_section() if self.config.include_performance else ''}
            {self._generate_cost_section() if self.config.include_cost else ''}
            {self._generate_custom_section() if self.config.include_custom else ''}
            {self._generate_comparison_section(comparison)}
            {self._generate_recommendations_section(comparison) if self.config.include_recommendations else ''}
            {self._generate_detailed_results_section()}
        </main>
        
        <footer>
            <p>Report generated by LLM-Dispatcher Benchmark Reporter</p>
        </footer>
    </div>
</body>
</html>
        """

        return html

    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .description {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .timestamp {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-top: 1rem;
        }
        
        .toc {
            background: #f8f9fa;
            padding: 1.5rem 2rem;
            border-bottom: 1px solid #dee2e6;
        }
        
        .toc h2 {
            margin-bottom: 1rem;
            color: #495057;
        }
        
        .toc ul {
            list-style: none;
        }
        
        .toc li {
            margin-bottom: 0.5rem;
        }
        
        .toc a {
            color: #007bff;
            text-decoration: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .toc a:hover {
            background-color: #e9ecef;
        }
        
        main {
            padding: 2rem;
        }
        
        section {
            margin-bottom: 3rem;
        }
        
        h2 {
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        h3 {
            color: #6c757d;
            margin-bottom: 1rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .table-container {
            overflow-x: auto;
            margin-bottom: 2rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .recommendation {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .recommendation h4 {
            color: #155724;
            margin-bottom: 0.5rem;
        }
        
        .recommendation p {
            color: #155724;
            margin: 0;
        }
        
        footer {
            background: #f8f9fa;
            padding: 1.5rem 2rem;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
        
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        """

    def _generate_summary_section(self, insights: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        total_benchmarks = insights.get("total_benchmarks", 0)

        html = f"""
        <section id="summary">
            <h2>Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_benchmarks}</div>
                    <div class="metric-label">Total Benchmarks</div>
                </div>
        """

        if "performance_insights" in insights:
            perf = insights["performance_insights"]
            html += f"""
                <div class="metric-card">
                    <div class="metric-value">{perf.get('avg_latency_ms', 0):.1f}ms</div>
                    <div class="metric-label">Average Latency</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{perf.get('avg_success_rate', 0):.1%}</div>
                    <div class="metric-label">Average Success Rate</div>
                </div>
            """

        if "cost_insights" in insights:
            cost = insights["cost_insights"]
            html += f"""
                <div class="metric-card">
                    <div class="metric-value">${cost.get('avg_total_cost', 0):.4f}</div>
                    <div class="metric-label">Average Total Cost</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cost.get('avg_tokens_per_dollar', 0):.0f}</div>
                    <div class="metric-label">Tokens per Dollar</div>
                </div>
            """

        html += """
            </div>
        </section>
        """

        return html

    def _generate_performance_section(self) -> str:
        """Generate performance analysis section."""
        performance_results = [
            r for r in self.results if isinstance(r, BenchmarkResult)
        ]

        if not performance_results:
            return ""

        html = """
        <section id="performance">
            <h2>Performance Analysis</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Model</th>
                            <th>Latency (ms)</th>
                            <th>Success Rate</th>
                            <th>Tokens/sec</th>
                            <th>Requests/sec</th>
                            <th>Total Requests</th>
                            <th>Errors</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for result in performance_results:
            html += f"""
                        <tr>
                            <td>{result.provider}</td>
                            <td>{result.model}</td>
                            <td>{result.metrics.latency_ms:.2f}</td>
                            <td>{result.metrics.success_rate:.2%}</td>
                            <td>{result.metrics.tokens_per_second:.2f}</td>
                            <td>{result.metrics.requests_per_second:.2f}</td>
                            <td>{result.metrics.total_requests}</td>
                            <td>{result.metrics.error_count}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>
        </section>
        """

        return html

    def _generate_cost_section(self) -> str:
        """Generate cost analysis section."""
        cost_results = [r for r in self.results if isinstance(r, CostBenchmarkResult)]

        if not cost_results:
            return ""

        html = """
        <section id="cost">
            <h2>Cost Analysis</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Model</th>
                            <th>Total Cost</th>
                            <th>Cost per Token</th>
                            <th>Cost per Request</th>
                            <th>Tokens per Dollar</th>
                            <th>Total Tokens</th>
                            <th>Total Requests</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for result in cost_results:
            html += f"""
                        <tr>
                            <td>{result.provider}</td>
                            <td>{result.model}</td>
                            <td>${result.metrics.total_cost:.4f}</td>
                            <td>${result.metrics.cost_per_token:.6f}</td>
                            <td>${result.metrics.cost_per_request:.4f}</td>
                            <td>{result.metrics.tokens_per_dollar:.0f}</td>
                            <td>{result.metrics.total_tokens}</td>
                            <td>{result.metrics.total_requests}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>
        </section>
        """

        return html

    def _generate_custom_section(self) -> str:
        """Generate custom benchmark analysis section."""
        custom_results = [
            r for r in self.results if isinstance(r, CustomBenchmarkResult)
        ]

        if not custom_results:
            return ""

        html = """
        <section id="custom">
            <h2>Custom Benchmark Analysis</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Model</th>
                            <th>Average Score</th>
                            <th>Success Rate</th>
                            <th>Total Tests</th>
                            <th>Passed Tests</th>
                            <th>Failed Tests</th>
                            <th>Avg Latency (ms)</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for result in custom_results:
            html += f"""
                        <tr>
                            <td>{result.provider}</td>
                            <td>{result.model}</td>
                            <td>{result.metrics.avg_score:.3f}</td>
                            <td>{result.metrics.success_rate:.2%}</td>
                            <td>{result.metrics.total_tests}</td>
                            <td>{result.metrics.passed_tests}</td>
                            <td>{result.metrics.failed_tests}</td>
                            <td>{result.metrics.avg_latency_ms:.2f}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>
        </section>
        """

        return html

    def _generate_comparison_section(self, comparison) -> str:
        """Generate provider comparison section."""
        html = f"""
        <section id="comparison">
            <h2>Provider Comparison</h2>
            <h3>Overall Rankings</h3>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Provider</th>
                            <th>Overall Score</th>
                            <th>Performance Score</th>
                            <th>Cost Efficiency Score</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        # Sort providers by rank
        sorted_providers = sorted(
            comparison.provider_rankings.items(), key=lambda x: x[1]
        )

        for provider, rank in sorted_providers:
            overall_score = comparison.overall_scores.get(provider, 0.0)
            perf_score = comparison.performance_scores.get(provider, 0.0)
            cost_score = comparison.cost_efficiency_scores.get(provider, 0.0)

            html += f"""
                        <tr>
                            <td>{rank}</td>
                            <td>{provider}</td>
                            <td>{overall_score:.3f}</td>
                            <td>{perf_score:.3f}</td>
                            <td>{cost_score:.3f}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>
        </section>
        """

        return html

    def _generate_recommendations_section(self, comparison) -> str:
        """Generate recommendations section."""
        html = """
        <section id="recommendations">
            <h2>Recommendations</h2>
        """

        for recommendation in comparison.recommendations:
            html += f"""
            <div class="recommendation">
                <h4>Recommendation</h4>
                <p>{recommendation}</p>
            </div>
            """

        html += """
        </section>
        """

        return html

    def _generate_detailed_results_section(self) -> str:
        """Generate detailed results section."""
        html = """
        <section id="detailed-results">
            <h2>Detailed Results</h2>
            <p>This section contains detailed information about each benchmark run.</p>
        """

        # Add detailed results for each type
        for i, result in enumerate(self.results):
            html += f"""
            <h3>Benchmark {i+1}: {type(result).__name__}</h3>
            <div class="table-container">
                <table>
                    <tbody>
            """

            if isinstance(result, BenchmarkResult):
                html += f"""
                        <tr><td><strong>Provider:</strong></td><td>{result.provider}</td></tr>
                        <tr><td><strong>Model:</strong></td><td>{result.model}</td></tr>
                        <tr><td><strong>Latency:</strong></td><td>{result.metrics.latency_ms:.2f} ms</td></tr>
                        <tr><td><strong>Success Rate:</strong></td><td>{result.metrics.success_rate:.2%}</td></tr>
                        <tr><td><strong>Total Requests:</strong></td><td>{result.metrics.total_requests}</td></tr>
                        <tr><td><strong>Total Tokens:</strong></td><td>{result.metrics.total_tokens}</td></tr>
                """
            elif isinstance(result, CostBenchmarkResult):
                html += f"""
                        <tr><td><strong>Provider:</strong></td><td>{result.provider}</td></tr>
                        <tr><td><strong>Model:</strong></td><td>{result.model}</td></tr>
                        <tr><td><strong>Total Cost:</strong></td><td>${result.metrics.total_cost:.4f}</td></tr>
                        <tr><td><strong>Cost per Token:</strong></td><td>${result.metrics.cost_per_token:.6f}</td></tr>
                        <tr><td><strong>Tokens per Dollar:</strong></td><td>{result.metrics.tokens_per_dollar:.0f}</td></tr>
                """
            elif isinstance(result, CustomBenchmarkResult):
                html += f"""
                        <tr><td><strong>Provider:</strong></td><td>{result.provider}</td></tr>
                        <tr><td><strong>Model:</strong></td><td>{result.model}</td></tr>
                        <tr><td><strong>Average Score:</strong></td><td>{result.metrics.avg_score:.3f}</td></tr>
                        <tr><td><strong>Success Rate:</strong></td><td>{result.metrics.success_rate:.2%}</td></tr>
                        <tr><td><strong>Total Tests:</strong></td><td>{result.metrics.total_tests}</td></tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        html += """
        </section>
        """

        return html

    def _serialize_results(self) -> List[Dict[str, Any]]:
        """Serialize results for JSON export."""
        serialized = []

        for result in self.results:
            if isinstance(result, BenchmarkResult):
                serialized.append(
                    {
                        "type": "performance",
                        "provider": result.provider,
                        "model": result.model,
                        "timestamp": result.timestamp.isoformat(),
                        "metrics": {
                            "latency_ms": result.metrics.latency_ms,
                            "tokens_per_second": result.metrics.tokens_per_second,
                            "requests_per_second": result.metrics.requests_per_second,
                            "success_rate": result.metrics.success_rate,
                            "error_count": result.metrics.error_count,
                            "total_requests": result.metrics.total_requests,
                            "total_tokens": result.metrics.total_tokens,
                            "avg_response_length": result.metrics.avg_response_length,
                        },
                        "errors": result.errors,
                    }
                )
            elif isinstance(result, CostBenchmarkResult):
                serialized.append(
                    {
                        "type": "cost",
                        "provider": result.provider,
                        "model": result.model,
                        "timestamp": result.timestamp.isoformat(),
                        "metrics": {
                            "total_cost": result.metrics.total_cost,
                            "cost_per_token": result.metrics.cost_per_token,
                            "cost_per_request": result.metrics.cost_per_request,
                            "tokens_per_dollar": result.metrics.tokens_per_dollar,
                            "requests_per_dollar": result.metrics.requests_per_dollar,
                            "total_tokens": result.metrics.total_tokens,
                            "total_requests": result.metrics.total_requests,
                            "avg_tokens_per_request": result.metrics.avg_tokens_per_request,
                        },
                        "errors": result.errors,
                    }
                )
            elif isinstance(result, CustomBenchmarkResult):
                serialized.append(
                    {
                        "type": "custom",
                        "provider": result.provider,
                        "model": result.model,
                        "timestamp": result.timestamp.isoformat(),
                        "metrics": {
                            "total_score": result.metrics.total_score,
                            "avg_score": result.metrics.avg_score,
                            "max_score": result.metrics.max_score,
                            "min_score": result.metrics.min_score,
                            "score_variance": result.metrics.score_variance,
                            "total_tests": result.metrics.total_tests,
                            "passed_tests": result.metrics.passed_tests,
                            "failed_tests": result.metrics.failed_tests,
                            "success_rate": result.metrics.success_rate,
                            "avg_latency_ms": result.metrics.avg_latency_ms,
                        },
                        "errors": result.errors,
                    }
                )

        return serialized

    def _generate_analysis_data(self) -> Dict[str, Any]:
        """Generate analysis data for JSON export."""
        return {
            "performance_insights": self.analyzer.get_performance_insights(),
            "provider_comparison": {
                "provider_rankings": self.analyzer.compare_providers().provider_rankings,
                "performance_scores": self.analyzer.compare_providers().performance_scores,
                "cost_efficiency_scores": self.analyzer.compare_providers().cost_efficiency_scores,
                "overall_scores": self.analyzer.compare_providers().overall_scores,
                "best_provider": self.analyzer.compare_providers().best_provider,
                "worst_provider": self.analyzer.compare_providers().worst_provider,
                "recommendations": self.analyzer.compare_providers().recommendations,
            },
        }

    def _generate_summary_data(self) -> Dict[str, Any]:
        """Generate summary data for JSON export."""
        insights = self.analyzer.get_performance_insights()
        return {
            "total_benchmarks": len(self.results),
            "performance_benchmarks": insights.get("performance_benchmarks", 0),
            "cost_benchmarks": insights.get("cost_benchmarks", 0),
            "custom_benchmarks": insights.get("custom_benchmarks", 0),
            "generated_at": datetime.now().isoformat(),
        }

    def _generate_markdown_content(self) -> str:
        """Generate Markdown report content."""
        insights = self.analyzer.get_performance_insights()
        comparison = self.analyzer.compare_providers()

        md = f"""# {self.config.title}

{self.config.description}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Benchmarks:** {insights.get('total_benchmarks', 0)}
- **Performance Benchmarks:** {insights.get('performance_benchmarks', 0)}
- **Cost Benchmarks:** {insights.get('cost_benchmarks', 0)}
- **Custom Benchmarks:** {insights.get('custom_benchmarks', 0)}

## Provider Rankings

| Rank | Provider | Overall Score | Performance Score | Cost Efficiency Score |
|------|----------|---------------|-------------------|----------------------|
"""

        # Sort providers by rank
        sorted_providers = sorted(
            comparison.provider_rankings.items(), key=lambda x: x[1]
        )

        for provider, rank in sorted_providers:
            overall_score = comparison.overall_scores.get(provider, 0.0)
            perf_score = comparison.performance_scores.get(provider, 0.0)
            cost_score = comparison.cost_efficiency_scores.get(provider, 0.0)

            md += f"| {rank} | {provider} | {overall_score:.3f} | {perf_score:.3f} | {cost_score:.3f} |\n"

        md += "\n## Recommendations\n\n"

        for recommendation in comparison.recommendations:
            md += f"- {recommendation}\n"

        md += "\n## Detailed Results\n\n"

        # Add detailed results
        for i, result in enumerate(self.results):
            md += f"### Benchmark {i+1}: {type(result).__name__}\n\n"

            if isinstance(result, BenchmarkResult):
                md += f"""
- **Provider:** {result.provider}
- **Model:** {result.model}
- **Latency:** {result.metrics.latency_ms:.2f} ms
- **Success Rate:** {result.metrics.success_rate:.2%}
- **Total Requests:** {result.metrics.total_requests}
- **Total Tokens:** {result.metrics.total_tokens}
"""
            elif isinstance(result, CostBenchmarkResult):
                md += f"""
- **Provider:** {result.provider}
- **Model:** {result.model}
- **Total Cost:** ${result.metrics.total_cost:.4f}
- **Cost per Token:** ${result.metrics.cost_per_token:.6f}
- **Tokens per Dollar:** {result.metrics.tokens_per_dollar:.0f}
"""
            elif isinstance(result, CustomBenchmarkResult):
                md += f"""
- **Provider:** {result.provider}
- **Model:** {result.model}
- **Average Score:** {result.metrics.avg_score:.3f}
- **Success Rate:** {result.metrics.success_rate:.2%}
- **Total Tests:** {result.metrics.total_tests}
"""

            md += "\n"

        return md

    def generate_csv_report(self, output_path: str) -> str:
        """
        Generate a CSV report from benchmark results.

        Args:
            output_path: Path where to save the CSV file

        Returns:
            Path to the generated CSV file
        """
        import csv

        if not self.results:
            raise ValueError("No results to export")

        with open(output_path, "w", newline="") as csvfile:
            fieldnames = [
                "provider",
                "model",
                "test_type",
                "score",
                "latency_ms",
                "cost",
                "tokens_used",
                "success_rate",
                "timestamp",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in self.results:
                # Extract data from result object
                row = {
                    "provider": getattr(result, "provider", "unknown"),
                    "model": getattr(result, "model", "unknown"),
                    "test_type": getattr(result, "test_type", "unknown"),
                    "score": getattr(result.metrics, "avg_score", 0.0),
                    "latency_ms": getattr(result.metrics, "latency_ms", 0.0),
                    "cost": getattr(result.metrics, "total_cost", 0.0),
                    "tokens_used": getattr(result.metrics, "total_tokens", 0),
                    "success_rate": getattr(result.metrics, "success_rate", 0.0),
                    "timestamp": getattr(result, "timestamp", "unknown"),
                }
                writer.writerow(row)

        return output_path

    def generate_custom_report(
        self,
        output_file: str,
        template: Optional[str] = None,
        format_type: str = "html",
        include_charts: bool = False,
    ) -> str:
        """
        Generate a custom report using a template.

        Args:
            output_file: Path where to save the report
            template: Custom template string (optional)
            format_type: Format type (html, markdown, json)
            include_charts: Whether to include charts in the report

        Returns:
            Path to the generated report file
        """
        if not self.results:
            raise ValueError("No results to export")

        if template is None:
            # Use default template based on format type
            if format_type == "html":
                template = """
<!DOCTYPE html>
<html>
<head>
    <title>Benchmark Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; }
        .result { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Benchmark Report</h1>
        <p>Generated on: {timestamp}</p>
    </div>
    {content}
</body>
</html>
                """
            elif format_type == "markdown":
                template = (
                    "# Benchmark Report\n\nGenerated on: {timestamp}\n\n{content}"
                )
            else:  # json
                template = '{{"timestamp": "{timestamp}", "results": {content}}}'

        # Generate content based on results
        if format_type == "json":
            content = json.dumps(
                [
                    {
                        "provider": getattr(r, "provider", "unknown"),
                        "score": getattr(r.metrics, "avg_score", 0.0),
                        "latency": getattr(r.metrics, "latency_ms", 0.0),
                    }
                    for r in self.results
                ],
                indent=2,
            )
        else:
            content = "\n".join(
                [
                    f"**Provider:** {getattr(r, 'provider', 'unknown')} | "
                    f"**Score:** {getattr(r.metrics, 'avg_score', 0.0):.3f} | "
                    f"**Latency:** {getattr(r.metrics, 'latency_ms', 0.0):.1f}ms"
                    for r in self.results
                ]
            )

        # Fill template
        report_content = template.format(
            timestamp=datetime.now().isoformat(), content=content
        )

        # Write to file
        with open(output_file, "w") as f:
            f.write(report_content)

        return output_file
