"""
Quality report generation for benchmark results.

This module provides comprehensive reporting tools for quality benchmark
results including HTML reports, charts, and custom report templates.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import base64

try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from .quality_benchmark import QualityResults
from .analysis import QualityAnalyzer


class QualityReporter:
    """
    Quality reporter for generating comprehensive reports.

    This class provides tools for generating HTML reports, charts,
    and custom reports from quality benchmark results.
    """

    def __init__(self, results: QualityResults):
        """
        Initialize quality reporter.

        Args:
            results: Quality benchmark results to report on
        """
        self.results = results
        self.analyzer = QualityAnalyzer(results)

    def generate_report(self, output_file: str) -> str:
        """
        Generate comprehensive HTML quality report.

        Args:
            output_file: Path to output HTML file

        Returns:
            Path to generated report file
        """
        html_content = self._generate_html_content()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_file

    def generate_charts(self, output_file: str) -> str:
        """
        Generate quality charts.

        Args:
            output_file: Path to output chart file

        Returns:
            Path to generated chart file
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for chart generation")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Quality Benchmark Results", fontsize=16, fontweight="bold")

        # Provider comparison chart
        self._create_provider_comparison_chart(axes[0, 0])

        # Task type comparison chart
        self._create_task_comparison_chart(axes[0, 1])

        # Quality distribution chart
        self._create_quality_distribution_chart(axes[1, 0])

        # Trend analysis chart
        self._create_trend_analysis_chart(axes[1, 1])

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.close()

        return output_file

    def generate_interactive_charts(self, output_file: str) -> str:
        """
        Generate interactive charts using Plotly.

        Args:
            output_file: Path to output HTML file with interactive charts

        Returns:
            Path to generated chart file
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("plotly is required for interactive chart generation")

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Provider Comparison",
                "Task Type Comparison",
                "Quality Distribution",
                "Trend Analysis",
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "scatter"}],
            ],
        )

        # Add provider comparison
        self._add_provider_comparison_plotly(fig, 1, 1)

        # Add task comparison
        self._add_task_comparison_plotly(fig, 1, 2)

        # Add quality distribution
        self._add_quality_distribution_plotly(fig, 2, 1)

        # Add trend analysis
        self._add_trend_analysis_plotly(fig, 2, 2)

        # Update layout
        fig.update_layout(
            title="Quality Benchmark Results - Interactive Dashboard",
            showlegend=True,
            height=800,
        )

        # Save as HTML
        fig.write_html(output_file)

        return output_file

    def generate_custom_report(
        self,
        template: str,
        output_file: str,
        include_charts: bool = True,
        include_raw_data: bool = True,
        include_statistical_analysis: bool = True,
    ) -> str:
        """
        Generate custom report using template.

        Args:
            template: Path to HTML template file
            output_file: Path to output file
            include_charts: Whether to include charts
            include_raw_data: Whether to include raw data
            include_statistical_analysis: Whether to include statistical analysis

        Returns:
            Path to generated report file
        """
        # Load template
        with open(template, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Prepare data for template
        template_data = self._prepare_template_data(
            include_charts, include_raw_data, include_statistical_analysis
        )

        # Replace template placeholders
        report_content = self._replace_template_placeholders(
            template_content, template_data
        )

        # Save report
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        return output_file

    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Benchmark Report</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Quality Benchmark Report</h1>
            <p class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        <section class="summary">
            <h2>Executive Summary</h2>
            {self._generate_summary_section()}
        </section>
        
        <section class="provider-comparison">
            <h2>Provider Comparison</h2>
            {self._generate_provider_comparison_section()}
        </section>
        
        <section class="task-analysis">
            <h2>Task Type Analysis</h2>
            {self._generate_task_analysis_section()}
        </section>
        
        <section class="statistical-analysis">
            <h2>Statistical Analysis</h2>
            {self._generate_statistical_analysis_section()}
        </section>
        
        <section class="recommendations">
            <h2>Recommendations</h2>
            {self._generate_recommendations_section()}
        </section>
    </div>
</body>
</html>
"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for the report."""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        header {
            text-align: center;
            border-bottom: 2px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #007acc;
            margin: 0;
        }
        
        .timestamp {
            color: #666;
            font-style: italic;
        }
        
        section {
            margin-bottom: 40px;
        }
        
        h2 {
            color: #333;
            border-left: 4px solid #007acc;
            padding-left: 15px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
        }
        
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: #007acc;
            color: white;
        }
        
        tr:hover {
            background-color: #f5f5f5;
        }
        
        .recommendation {
            background: #e8f4fd;
            padding: 15px;
            border-left: 4px solid #007acc;
            margin: 10px 0;
        }
        """

    def _generate_summary_section(self) -> str:
        """Generate executive summary section."""
        return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self.results.overall_accuracy:.1%}</div>
                <div class="metric-label">Overall Accuracy</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.results.avg_quality_score:.2f}</div>
                <div class="metric-label">Average Quality Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.results.consistency_score:.2f}</div>
                <div class="metric-label">Consistency Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.results.evaluation_time:.1f}s</div>
                <div class="metric-label">Evaluation Time</div>
            </div>
        </div>
        """

    def _generate_provider_comparison_section(self) -> str:
        """Generate provider comparison section."""
        if not self.results.provider_metrics:
            return "<p>No provider metrics available.</p>"

        table_rows = ""
        for provider, metrics in self.results.provider_metrics.items():
            table_rows += f"""
            <tr>
                <td>{provider}</td>
                <td>{metrics.accuracy:.1%}</td>
                <td>{metrics.quality_score:.2f}</td>
                <td>{metrics.factual_accuracy:.1%}</td>
                <td>{metrics.creative_quality:.2f}</td>
                <td>{metrics.total_tests}</td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th>Accuracy</th>
                    <th>Quality Score</th>
                    <th>Factual Accuracy</th>
                    <th>Creative Quality</th>
                    <th>Total Tests</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """

    def _generate_task_analysis_section(self) -> str:
        """Generate task analysis section."""
        if not self.results.task_metrics:
            return "<p>No task metrics available.</p>"

        table_rows = ""
        for task, metrics in self.results.task_metrics.items():
            table_rows += f"""
            <tr>
                <td>{task}</td>
                <td>{metrics.accuracy:.1%}</td>
                <td>{metrics.quality_score:.2f}</td>
                <td>{metrics.creative_quality:.2f}</td>
                <td>{metrics.explanatory_quality:.2f}</td>
                <td>{metrics.analytical_quality:.2f}</td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Task Type</th>
                    <th>Accuracy</th>
                    <th>Quality Score</th>
                    <th>Creative Quality</th>
                    <th>Explanatory Quality</th>
                    <th>Analytical Quality</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """

    def _generate_statistical_analysis_section(self) -> str:
        """Generate statistical analysis section."""
        stats = self.analyzer.get_statistical_analysis()

        if not stats:
            return "<p>No statistical analysis available.</p>"

        content = ""
        for metric, analysis in stats.items():
            content += f"""
            <h3>{metric.title()} Analysis</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{analysis.mean:.3f}</div>
                    <div class="metric-label">Mean</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{analysis.median:.3f}</div>
                    <div class="metric-label">Median</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{analysis.std:.3f}</div>
                    <div class="metric-label">Standard Deviation</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{analysis.p95:.3f}</div>
                    <div class="metric-label">95th Percentile</div>
                </div>
            </div>
            """

        return content

    def _generate_recommendations_section(self) -> str:
        """Generate recommendations section."""
        recommendations = []

        # Analyze results and generate recommendations
        if self.results.overall_accuracy < 0.8:
            recommendations.append(
                "Consider improving prompt engineering or using different models for better accuracy."
            )

        if self.results.consistency_score < 0.7:
            recommendations.append(
                "Implement consistency checks and consider using more deterministic parameters."
            )

        if len(self.results.provider_metrics) > 1:
            best_provider = max(
                self.results.provider_metrics.items(), key=lambda x: x[1].quality_score
            )
            recommendations.append(
                f"Consider using {best_provider[0]} as the primary provider for best quality."
            )

        if not recommendations:
            recommendations.append(
                "Quality metrics look good. Continue monitoring for consistency."
            )

        content = ""
        for i, rec in enumerate(recommendations, 1):
            content += f"""
            <div class="recommendation">
                <strong>Recommendation {i}:</strong> {rec}
            </div>
            """

        return content

    def _create_provider_comparison_chart(self, ax):
        """Create provider comparison chart."""
        if not self.results.provider_metrics:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            return

        providers = list(self.results.provider_metrics.keys())
        quality_scores = [
            m.quality_score for m in self.results.provider_metrics.values()
        ]

        bars = ax.bar(providers, quality_scores, color="skyblue", edgecolor="navy")
        ax.set_title("Provider Quality Comparison")
        ax.set_ylabel("Quality Score")
        ax.set_ylim(0, 1)

        # Add value labels on bars
        for bar, score in zip(bars, quality_scores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{score:.2f}",
                ha="center",
                va="bottom",
            )

    def _create_task_comparison_chart(self, ax):
        """Create task comparison chart."""
        if not self.results.task_metrics:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            return

        tasks = list(self.results.task_metrics.keys())
        accuracy_scores = [m.accuracy for m in self.results.task_metrics.values()]

        bars = ax.bar(tasks, accuracy_scores, color="lightgreen", edgecolor="darkgreen")
        ax.set_title("Task Type Accuracy Comparison")
        ax.set_ylabel("Accuracy")
        ax.set_ylim(0, 1)

        # Add value labels on bars
        for bar, score in zip(bars, accuracy_scores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{score:.1%}",
                ha="center",
                va="bottom",
            )

    def _create_quality_distribution_chart(self, ax):
        """Create quality distribution chart."""
        all_scores = []
        for metrics in self.results.provider_metrics.values():
            all_scores.append(metrics.quality_score)

        if not all_scores:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            return

        ax.hist(all_scores, bins=10, color="lightcoral", edgecolor="darkred", alpha=0.7)
        ax.set_title("Quality Score Distribution")
        ax.set_xlabel("Quality Score")
        ax.set_ylabel("Frequency")

    def _create_trend_analysis_chart(self, ax):
        """Create trend analysis chart."""
        # This would show trends over time
        # For now, show a placeholder
        ax.text(
            0.5,
            0.5,
            "Trend analysis\n(requires time series data)",
            ha="center",
            va="center",
            fontsize=12,
        )
        ax.set_title("Quality Trend Analysis")

    def _add_provider_comparison_plotly(self, fig, row, col):
        """Add provider comparison to Plotly figure."""
        if not self.results.provider_metrics:
            return

        providers = list(self.results.provider_metrics.keys())
        quality_scores = [
            m.quality_score for m in self.results.provider_metrics.values()
        ]

        fig.add_trace(
            go.Bar(x=providers, y=quality_scores, name="Quality Score"),
            row=row,
            col=col,
        )

    def _add_task_comparison_plotly(self, fig, row, col):
        """Add task comparison to Plotly figure."""
        if not self.results.task_metrics:
            return

        tasks = list(self.results.task_metrics.keys())
        accuracy_scores = [m.accuracy for m in self.results.task_metrics.values()]

        fig.add_trace(
            go.Bar(x=tasks, y=accuracy_scores, name="Accuracy"), row=row, col=col
        )

    def _add_quality_distribution_plotly(self, fig, row, col):
        """Add quality distribution to Plotly figure."""
        all_scores = []
        for metrics in self.results.provider_metrics.values():
            all_scores.append(metrics.quality_score)

        if all_scores:
            fig.add_trace(
                go.Histogram(x=all_scores, name="Quality Distribution"),
                row=row,
                col=col,
            )

    def _add_trend_analysis_plotly(self, fig, row, col):
        """Add trend analysis to Plotly figure."""
        # Placeholder for trend analysis
        fig.add_trace(
            go.Scatter(
                x=[1, 2, 3], y=[0.8, 0.85, 0.9], mode="lines+markers", name="Trend"
            ),
            row=row,
            col=col,
        )

    def _prepare_template_data(
        self,
        include_charts: bool,
        include_raw_data: bool,
        include_statistical_analysis: bool,
    ) -> Dict[str, Any]:
        """Prepare data for template replacement."""
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_accuracy": self.results.overall_accuracy,
            "avg_quality_score": self.results.avg_quality_score,
            "consistency_score": self.results.consistency_score,
            "evaluation_time": self.results.evaluation_time,
        }

        if include_raw_data:
            data["provider_metrics"] = self.results.provider_metrics
            data["task_metrics"] = self.results.task_metrics

        if include_statistical_analysis:
            data["statistical_analysis"] = self.analyzer.get_statistical_analysis()

        return data

    def _replace_template_placeholders(
        self, template: str, data: Dict[str, Any]
    ) -> str:
        """Replace template placeholders with actual data."""
        # Simple placeholder replacement
        # In practice, you might want to use a proper templating engine like Jinja2
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)
            template = template.replace(placeholder, str(value))

        return template
