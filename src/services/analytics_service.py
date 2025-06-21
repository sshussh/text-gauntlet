"""Analytics service for Text Gauntlet usage insights."""

from datetime import datetime
from typing import Any

from utils.logger import logger

from .data_service import DataService


class AnalyticsService:
    """Service for generating usage analytics and insights."""

    def __init__(self, dataService: DataService) -> None:
        """Initialize the analytics service.

        Args:
            dataService: Data service instance for data access
        """
        self.dataService = dataService
        logger.info("Analytics service initialized")

    def generateUsageReport(self, days: int = 30) -> dict[str, Any]:
        """Generate a comprehensive usage report.

        Args:
            days: Number of days to include in the report

        Returns:
            Dictionary containing usage analytics
        """
        try:
            # Get raw data
            usageStats = self.dataService.getUsageStats(days)
            analysisHistory = self.dataService.getAnalysisHistory(limit=1000)

            # Calculate metrics
            metrics = self._calculateMetrics(usageStats, analysisHistory, days)

            # Generate insights
            insights = self._generateInsights(metrics, usageStats, analysisHistory)

            report = {
                "generated_at": datetime.now().isoformat(),
                "period_days": days,
                "metrics": metrics,
                "insights": insights,
                "raw_data": {
                    "usage_stats": usageStats,
                    "sample_analyses": analysisHistory[:10],  # Include sample
                },
            }

            logger.info(f"Generated usage report for {days} days")
            return report

        except Exception as e:
            logger.error(f"Failed to generate usage report: {e}")
            raise

    def _calculateMetrics(
        self,
        usageStats: list[dict[str, Any]],
        analysisHistory: list[dict[str, Any]],
        days: int,
    ) -> dict[str, Any]:
        """Calculate key metrics from usage data."""
        if not usageStats and not analysisHistory:
            return self._getEmptyMetrics()

        # Basic counts
        totalAnalyses = sum(stat.get("analyses_count", 0) for stat in usageStats)
        totalDays = len(usageStats)
        avgAnalysesPerDay = totalAnalyses / totalDays if totalDays > 0 else 0

        # Confidence metrics
        confidences = [
            record.get("confidence", 0)
            for record in analysisHistory
            if record.get("confidence") is not None
        ]
        avgConfidence = sum(confidences) / len(confidences) if confidences else 0
        maxConfidence = max(confidences) if confidences else 0
        minConfidence = min(confidences) if confidences else 0

        # Processing time metrics
        processingTimes = [
            record.get("processing_time", 0)
            for record in analysisHistory
            if record.get("processing_time") is not None
        ]
        avgProcessingTime = (
            sum(processingTimes) / len(processingTimes) if processingTimes else 0
        )
        maxProcessingTime = max(processingTimes) if processingTimes else 0
        minProcessingTime = min(processingTimes) if processingTimes else 0

        # Sentiment distribution
        sentiments = [
            record.get("primary_sentiment", "unknown") for record in analysisHistory
        ]
        sentimentDistribution = {}
        for sentiment in sentiments:
            sentimentDistribution[sentiment] = (
                sentimentDistribution.get(sentiment, 0) + 1
            )

        # Most active day
        mostActiveDay = (
            max(usageStats, key=lambda x: x.get("analyses_count", 0))
            if usageStats
            else None
        )

        # Activity trend (last 7 days vs previous 7 days)
        activityTrend = self._calculateActivityTrend(usageStats)

        return {
            "total_analyses": totalAnalyses,
            "active_days": totalDays,
            "avg_analyses_per_day": avgAnalysesPerDay,
            "confidence_metrics": {
                "average": avgConfidence,
                "maximum": maxConfidence,
                "minimum": minConfidence,
                "distribution": self._getConfidenceDistribution(confidences),
            },
            "processing_time_metrics": {
                "average": avgProcessingTime,
                "maximum": maxProcessingTime,
                "minimum": minProcessingTime,
            },
            "sentiment_distribution": sentimentDistribution,
            "most_active_day": mostActiveDay,
            "activity_trend": activityTrend,
            "unique_text_count": len(
                {r.get("input_text", "") for r in analysisHistory}
            ),
        }

    def _getConfidenceDistribution(self, confidences: list[float]) -> dict[str, int]:
        """Get distribution of confidence scores by ranges."""
        if not confidences:
            return {}

        distribution = {
            "very_low": 0,  # 0-20%
            "low": 0,  # 20-40%
            "medium": 0,  # 40-60%
            "high": 0,  # 60-80%
            "very_high": 0,  # 80-100%
        }

        for confidence in confidences:
            if confidence < 0.2:
                distribution["very_low"] += 1
            elif confidence < 0.4:
                distribution["low"] += 1
            elif confidence < 0.6:
                distribution["medium"] += 1
            elif confidence < 0.8:
                distribution["high"] += 1
            else:
                distribution["very_high"] += 1

        return distribution

    def _calculateActivityTrend(
        self, usageStats: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate activity trend comparing recent vs previous periods."""
        if len(usageStats) < 14:
            return {"trend": "insufficient_data", "change": 0.0}

        # Sort by date
        sortedStats = sorted(usageStats, key=lambda x: x.get("date", ""))

        # Get last 7 days and previous 7 days
        recent7Days = sortedStats[-7:]
        previous7Days = sortedStats[-14:-7]

        recentTotal = sum(stat.get("analyses_count", 0) for stat in recent7Days)
        previousTotal = sum(stat.get("analyses_count", 0) for stat in previous7Days)

        if previousTotal == 0:
            if recentTotal > 0:
                return {"trend": "increasing", "change": float("inf")}
            else:
                return {"trend": "stable", "change": 0.0}

        changePercent = ((recentTotal - previousTotal) / previousTotal) * 100

        if changePercent > 10:
            trend = "increasing"
        elif changePercent < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        return {"trend": trend, "change": changePercent}

    def _generateInsights(
        self,
        metrics: dict[str, Any],
        usageStats: list[dict[str, Any]],
        analysisHistory: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate actionable insights from the metrics."""
        insights = []

        # Usage patterns
        if metrics["total_analyses"] > 0:
            avgPerDay = metrics["avg_analyses_per_day"]
            if avgPerDay > 10:
                insights.append(
                    {
                        "type": "usage_pattern",
                        "level": "info",
                        "title": "High Usage Detected",
                        "description": f"You're performing {avgPerDay:.1f} analyses per day on average. Consider using batch processing for efficiency.",
                        "recommendation": "Explore batch analysis features to process multiple texts at once.",
                    }
                )
            elif avgPerDay < 1:
                insights.append(
                    {
                        "type": "usage_pattern",
                        "level": "info",
                        "title": "Low Usage Detected",
                        "description": f"You're averaging {avgPerDay:.1f} analyses per day. The tool is ready when you need it!",
                        "recommendation": "Consider integrating sentiment analysis into your regular workflow.",
                    }
                )

        # Confidence insights
        confidenceMetrics = metrics["confidence_metrics"]
        avgConfidence = confidenceMetrics["average"]

        if avgConfidence > 0.8:
            insights.append(
                {
                    "type": "confidence",
                    "level": "success",
                    "title": "High Confidence Results",
                    "description": f"Your analyses show {avgConfidence:.1%} average confidence. The model is very confident in its predictions.",
                    "recommendation": "Great! Your text inputs are well-suited for sentiment analysis.",
                }
            )
        elif avgConfidence < 0.6:
            insights.append(
                {
                    "type": "confidence",
                    "level": "warning",
                    "title": "Lower Confidence Detected",
                    "description": f"Average confidence is {avgConfidence:.1%}. This might indicate ambiguous or complex text.",
                    "recommendation": "Consider analyzing shorter, clearer text segments for better confidence scores.",
                }
            )

        # Sentiment distribution insights
        sentimentDist = metrics["sentiment_distribution"]
        totalSentiments = sum(sentimentDist.values())

        if totalSentiments > 0:
            mostCommon = max(sentimentDist.items(), key=lambda x: x[1])
            percentage = (mostCommon[1] / totalSentiments) * 100

            if percentage > 70:
                insights.append(
                    {
                        "type": "sentiment_distribution",
                        "level": "info",
                        "title": f"Predominantly {mostCommon[0].title()} Content",
                        "description": f"{percentage:.1f}% of your analyses are {mostCommon[0]}. This suggests consistent content mood.",
                        "recommendation": "Consider analyzing diverse content types to get a broader perspective.",
                    }
                )

        # Performance insights
        processingMetrics = metrics["processing_time_metrics"]
        avgProcessingTime = processingMetrics["average"]

        if avgProcessingTime > 2.0:
            insights.append(
                {
                    "type": "performance",
                    "level": "warning",
                    "title": "Slower Processing Times",
                    "description": f"Average processing time is {avgProcessingTime:.2f} seconds.",
                    "recommendation": "Consider analyzing shorter texts or check your system performance.",
                }
            )
        elif avgProcessingTime < 0.5:
            insights.append(
                {
                    "type": "performance",
                    "level": "success",
                    "title": "Fast Processing",
                    "description": f"Excellent! Average processing time is only {avgProcessingTime:.2f} seconds.",
                    "recommendation": "Your system is optimized for quick sentiment analysis.",
                }
            )

        # Activity trend insights
        activityTrend = metrics["activity_trend"]
        if activityTrend["trend"] == "increasing":
            insights.append(
                {
                    "type": "activity_trend",
                    "level": "info",
                    "title": "Increasing Usage",
                    "description": f"Your usage has increased by {activityTrend['change']:.1f}% in the last week.",
                    "recommendation": "Great to see you're finding the tool useful! Consider exploring advanced features.",
                }
            )
        elif activityTrend["trend"] == "decreasing":
            insights.append(
                {
                    "type": "activity_trend",
                    "level": "info",
                    "title": "Decreasing Usage",
                    "description": f"Your usage has decreased by {abs(activityTrend['change']):.1f}% in the last week.",
                    "recommendation": "We're here when you need sentiment analysis. Check out new features or use cases.",
                }
            )

        return insights

    def _getEmptyMetrics(self) -> dict[str, Any]:
        """Get empty metrics structure for when no data is available."""
        return {
            "total_analyses": 0,
            "active_days": 0,
            "avg_analyses_per_day": 0,
            "confidence_metrics": {
                "average": 0,
                "maximum": 0,
                "minimum": 0,
                "distribution": {},
            },
            "processing_time_metrics": {"average": 0, "maximum": 0, "minimum": 0},
            "sentiment_distribution": {},
            "most_active_day": None,
            "activity_trend": {"trend": "no_data", "change": 0.0},
            "unique_text_count": 0,
        }

    def getQuickStats(self) -> dict[str, Any]:
        """Get quick statistics for dashboard display.

        Returns:
            Dictionary with key statistics
        """
        try:
            # Get recent data
            recentStats = self.dataService.getUsageStats(7)  # Last 7 days
            recentAnalyses = self.dataService.getAnalysisHistory(50)  # Last 50 analyses

            # Calculate quick metrics
            totalAnalyses = sum(stat.get("analyses_count", 0) for stat in recentStats)
            avgConfidence = 0
            mostCommonSentiment = "unknown"

            if recentAnalyses:
                confidences = [
                    r.get("confidence", 0)
                    for r in recentAnalyses
                    if r.get("confidence")
                ]
                avgConfidence = (
                    sum(confidences) / len(confidences) if confidences else 0
                )

                sentiments = [
                    r.get("primary_sentiment", "unknown") for r in recentAnalyses
                ]
                sentimentCounts = {}
                for sentiment in sentiments:
                    sentimentCounts[sentiment] = sentimentCounts.get(sentiment, 0) + 1

                if sentimentCounts:
                    mostCommonSentiment = max(
                        sentimentCounts.items(), key=lambda x: x[1]
                    )[0]

            return {
                "total_analyses_7d": totalAnalyses,
                "avg_confidence": avgConfidence,
                "most_common_sentiment": mostCommonSentiment,
                "total_records": self.dataService.getRecordCount(),
                "database_size": self.dataService.getDatabaseSize(),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get quick stats: {e}")
            return {
                "total_analyses_7d": 0,
                "avg_confidence": 0,
                "most_common_sentiment": "unknown",
                "total_records": 0,
                "database_size": 0,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
            }

    def getTrendData(self, days: int = 30) -> dict[str, Any]:
        """Get trend data for visualization.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with trend data
        """
        try:
            usageStats = self.dataService.getUsageStats(days)

            # Prepare data for charts
            dates = [stat.get("date", "") for stat in usageStats]
            analysisCounts = [stat.get("analyses_count", 0) for stat in usageStats]
            avgConfidences = [stat.get("avg_confidence", 0) for stat in usageStats]

            return {
                "dates": dates,
                "analysis_counts": analysisCounts,
                "avg_confidences": avgConfidences,
                "total_period_analyses": sum(analysisCounts),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get trend data: {e}")
            return {
                "dates": [],
                "analysis_counts": [],
                "avg_confidences": [],
                "total_period_analyses": 0,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
            }
