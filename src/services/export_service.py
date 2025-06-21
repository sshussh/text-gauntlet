"""Export service for Text Gauntlet analysis results."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.exceptions import ExportError
from utils.logger import logger


class ExportService:
    """Service for exporting analysis results in various formats."""

    def __init__(self) -> None:
        """Initialize the export service."""
        self.supportedFormats = ["json", "csv", "txt", "html"]
        logger.info(
            "Export service initialized with formats: "
            + ", ".join(self.supportedFormats)
        )

    def exportResults(
        self,
        results: list[dict[str, Any]],
        filePath: Path,
        format: str = "json",
        includeMetadata: bool = True,
    ) -> None:
        """Export analysis results to a file.

        Args:
            results: List of analysis result dictionaries
            filePath: Path to save the exported file
            format: Export format ("json", "csv", "txt", "html")
            includeMetadata: Whether to include metadata in export

        Raises:
            ExportError: If export fails
        """
        if format.lower() not in self.supportedFormats:
            raise ExportError(
                f"Unsupported format: {format}. Supported: {self.supportedFormats}"
            )

        try:
            # Ensure directory exists
            filePath.parent.mkdir(parents=True, exist_ok=True)

            # Export based on format
            if format.lower() == "json":
                self._exportJson(results, filePath, includeMetadata)
            elif format.lower() == "csv":
                self._exportCsv(results, filePath, includeMetadata)
            elif format.lower() == "txt":
                self._exportText(results, filePath, includeMetadata)
            elif format.lower() == "html":
                self._exportHtml(results, filePath, includeMetadata)

            logger.info(
                f"Exported {len(results)} results to {filePath} in {format} format"
            )

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise ExportError(f"Failed to export results: {e}") from e

    def _exportJson(
        self, results: list[dict[str, Any]], filePath: Path, includeMetadata: bool
    ) -> None:
        """Export results to JSON format."""
        exportData = (
            {
                "exported_at": datetime.now().isoformat(),
                "total_results": len(results),
                "format_version": "1.0",
                "results": results,
            }
            if includeMetadata
            else results
        )

        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(exportData, f, indent=2, ensure_ascii=False, default=str)

    def _exportCsv(
        self, results: list[dict[str, Any]], filePath: Path, includeMetadata: bool
    ) -> None:
        """Export results to CSV format."""
        if not results:
            return

        with open(filePath, "w", newline="", encoding="utf-8") as f:
            # Flatten the data for CSV
            flatResults = []
            for result in results:
                flatResult = result.copy()

                # Handle scores array
                if "scores" in result and isinstance(result["scores"], list):
                    for score in result["scores"]:
                        if isinstance(score, dict):
                            label = score.get("label", "unknown")
                            flatResult[f"score_{label}"] = score.get("score", 0.0)
                    del flatResult["scores"]

                flatResults.append(flatResult)

            if flatResults:
                fieldnames = flatResults[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                # Add metadata as comments if requested
                if includeMetadata:
                    f.write(f"# Exported at: {datetime.now().isoformat()}\n")
                    f.write(f"# Total results: {len(results)}\n")
                    f.write("# Format version: 1.0\n")

                writer.writeheader()
                writer.writerows(flatResults)

    def _exportText(
        self, results: list[dict[str, Any]], filePath: Path, includeMetadata: bool
    ) -> None:
        """Export results to plain text format."""
        with open(filePath, "w", encoding="utf-8") as f:
            if includeMetadata:
                f.write("TEXT GAUNTLET - SENTIMENT ANALYSIS EXPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Results: {len(results)}\n")
                f.write("Format Version: 1.0\n")
                f.write("=" * 50 + "\n\n")

            for i, result in enumerate(results, 1):
                f.write(f"ANALYSIS #{i}\n")
                f.write("-" * 20 + "\n")

                # Basic info
                f.write(
                    f"Text: {result.get('input_text', 'N/A')[:100]}{'...' if len(result.get('input_text', '')) > 100 else ''}\n"
                )
                f.write(f"Sentiment: {result.get('primary_sentiment', 'N/A')}\n")
                f.write(f"Confidence: {result.get('confidence', 0):.2%}\n")
                f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
                f.write(f"Processing Time: {result.get('processing_time', 0):.3f}s\n")

                # Detailed scores
                if "scores" in result and isinstance(result["scores"], list):
                    f.write("\nDetailed Scores:\n")
                    for score in result["scores"]:
                        if isinstance(score, dict):
                            label = score.get("label", "unknown").title()
                            value = score.get("score", 0)
                            f.write(f"  • {label}: {value:.2%}\n")

                f.write("\n" + "=" * 50 + "\n\n")

    def _exportHtml(
        self, results: list[dict[str, Any]], filePath: Path, includeMetadata: bool
    ) -> None:
        """Export results to HTML format."""
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(self._generateHtmlContent(results, includeMetadata))

    def _generateHtmlContent(
        self, results: list[dict[str, Any]], includeMetadata: bool
    ) -> str:
        """Generate HTML content for export."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text Gauntlet - Sentiment Analysis Export</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .metadata {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .result-card {
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .result-header {
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .result-body {
            padding: 20px;
        }
        .sentiment {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        .sentiment.positive { background-color: #22c55e; }
        .sentiment.negative { background-color: #ef4444; }
        .sentiment.neutral { background-color: #6b7280; }
        .confidence {
            font-size: 1.2em;
            font-weight: bold;
            color: #4f46e5;
        }
        .text-preview {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #4f46e5;
            margin: 15px 0;
            font-style: italic;
        }
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .score-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .score-label {
            font-weight: bold;
            text-transform: capitalize;
            margin-bottom: 5px;
        }
        .score-value {
            font-size: 1.5em;
            color: #4f46e5;
            font-weight: bold;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .meta-item {
            text-align: center;
        }
        .meta-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #4f46e5;
        }
        .meta-label {
            color: #6b7280;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #6b7280;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Text Gauntlet</h1>
        <p>Sentiment Analysis Export Report</p>
    </div>
"""

        if includeMetadata:
            html += f"""
    <div class="metadata">
        <div class="meta-grid">
            <div class="meta-item">
                <div class="meta-value">{len(results)}</div>
                <div class="meta-label">Total Analyses</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">{datetime.now().strftime("%Y-%m-%d")}</div>
                <div class="meta-label">Export Date</div>
            </div>
            <div class="meta-item">
                <div class="meta-value">1.0</div>
                <div class="meta-label">Format Version</div>
            </div>
        </div>
    </div>
"""

        for i, result in enumerate(results, 1):
            sentiment = result.get("primary_sentiment", "neutral").lower()
            confidence = result.get("confidence", 0)
            text = result.get("input_text", "N/A")
            timestamp = result.get("timestamp", "N/A")
            processingTime = result.get("processing_time", 0)

            html += f"""
    <div class="result-card">
        <div class="result-header">
            <h3>Analysis #{i}</h3>
            <span class="sentiment {sentiment}">{sentiment}</span>
            <span class="confidence">{confidence:.1%} Confidence</span>
        </div>
        <div class="result-body">
            <div class="text-preview">
                "{text[:200]}{"..." if len(text) > 200 else ""}"
            </div>

            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Processing Time:</strong> {processingTime:.3f} seconds</p>
"""

            if "scores" in result and isinstance(result["scores"], list):
                html += """
            <h4>Detailed Sentiment Scores</h4>
            <div class="scores-grid">
"""
                for score in result["scores"]:
                    if isinstance(score, dict):
                        label = score.get("label", "unknown").title()
                        value = score.get("score", 0)
                        html += f"""
                <div class="score-item">
                    <div class="score-label">{label}</div>
                    <div class="score-value">{value:.1%}</div>
                </div>
"""
                html += """
            </div>
"""

            html += """
        </div>
    </div>
"""

        html += f"""
    <div class="footer">
        <p>Generated by Text Gauntlet v2.0 on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}</p>
    </div>
</body>
</html>
"""
        return html

    def exportSummaryReport(
        self, results: list[dict[str, Any]], filePath: Path, format: str = "html"
    ) -> None:
        """Export a summary report with analytics.

        Args:
            results: List of analysis result dictionaries
            filePath: Path to save the report
            format: Export format for the report

        Raises:
            ExportError: If export fails
        """
        try:
            # Generate analytics
            analytics = self._generateAnalytics(results)

            if format.lower() == "html":
                self._exportSummaryHtml(analytics, filePath)
            elif format.lower() == "json":
                self._exportSummaryJson(analytics, filePath)
            else:
                raise ExportError("Summary reports only support HTML and JSON formats")

            logger.info(f"Exported summary report to {filePath} in {format} format")

        except Exception as e:
            logger.error(f"Summary export failed: {e}")
            raise ExportError(f"Failed to export summary: {e}") from e

    def _generateAnalytics(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate analytics from analysis results."""
        if not results:
            return {"totalAnalyses": 0}

        # Basic statistics
        totalAnalyses = len(results)
        sentiments = [r.get("primary_sentiment", "unknown") for r in results]
        confidences = [
            r.get("confidence", 0) for r in results if r.get("confidence") is not None
        ]
        processingTimes = [
            r.get("processing_time", 0)
            for r in results
            if r.get("processing_time") is not None
        ]

        # Sentiment distribution
        sentimentCounts = {}
        for sentiment in sentiments:
            sentimentCounts[sentiment] = sentimentCounts.get(sentiment, 0) + 1

        # Calculate averages
        avgConfidence = sum(confidences) / len(confidences) if confidences else 0
        avgProcessingTime = (
            sum(processingTimes) / len(processingTimes) if processingTimes else 0
        )

        # Most common sentiment
        mostCommonSentiment = (
            max(sentimentCounts.items(), key=lambda x: x[1])[0]
            if sentimentCounts
            else "unknown"
        )

        return {
            "totalAnalyses": totalAnalyses,
            "sentimentDistribution": sentimentCounts,
            "averageConfidence": avgConfidence,
            "averageProcessingTime": avgProcessingTime,
            "mostCommonSentiment": mostCommonSentiment,
            "confidenceRange": {
                "min": min(confidences) if confidences else 0,
                "max": max(confidences) if confidences else 0,
            },
            "processingTimeRange": {
                "min": min(processingTimes) if processingTimes else 0,
                "max": max(processingTimes) if processingTimes else 0,
            },
        }

    def _exportSummaryHtml(self, analytics: dict[str, Any], filePath: Path) -> None:
        """Export summary analytics as HTML."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text Gauntlet - Analytics Summary</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #6b7280;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .sentiment-bar {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .sentiment-label {{
            width: 100px;
            font-weight: bold;
            text-transform: capitalize;
        }}
        .sentiment-progress {{
            flex: 1;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            margin: 0 15px;
            overflow: hidden;
        }}
        .sentiment-fill {{
            height: 100%;
            border-radius: 15px;
            transition: width 0.3s ease;
        }}
        .positive {{ background-color: #22c55e; }}
        .negative {{ background-color: #ef4444; }}
        .neutral {{ background-color: #6b7280; }}
        .sentiment-count {{
            width: 50px;
            text-align: right;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Analytics Summary</h1>
        <p>Text Gauntlet Sentiment Analysis Report</p>
        <p>Generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{analytics["totalAnalyses"]}</div>
            <div class="stat-label">Total Analyses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{analytics["averageConfidence"]:.1%}</div>
            <div class="stat-label">Average Confidence</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{analytics["averageProcessingTime"]:.2f}s</div>
            <div class="stat-label">Avg Processing Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{analytics["mostCommonSentiment"].title()}</div>
            <div class="stat-label">Most Common Sentiment</div>
        </div>
    </div>

    <div class="chart-container">
        <h2>Sentiment Distribution</h2>
"""

        # Add sentiment distribution chart
        sentimentDistribution = analytics.get("sentimentDistribution", {})
        totalCount = sum(sentimentDistribution.values())

        for sentiment, count in sentimentDistribution.items():
            percentage = (count / totalCount * 100) if totalCount > 0 else 0
            cssClass = (
                sentiment.lower()
                if sentiment.lower() in ["positive", "negative", "neutral"]
                else "neutral"
            )

            html += f"""
        <div class="sentiment-bar">
            <div class="sentiment-label">{sentiment.title()}</div>
            <div class="sentiment-progress">
                <div class="sentiment-fill {cssClass}" style="width: {percentage}%"></div>
            </div>
            <div class="sentiment-count">{count}</div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        with open(filePath, "w", encoding="utf-8") as f:
            f.write(html)

    def _exportSummaryJson(self, analytics: dict[str, Any], filePath: Path) -> None:
        """Export summary analytics as JSON."""
        exportData = {
            "generated_at": datetime.now().isoformat(),
            "format_version": "1.0",
            "analytics": analytics,
        }

        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(exportData, f, indent=2, ensure_ascii=False)
