"""Main application service manager for Text Gauntlet Phase 4."""

from datetime import datetime
from pathlib import Path

from config.settings import settings
from core.models import TextInput
from core.sentiment_analyzer import SentimentAnalyzer
from utils.logger import logger

from .analytics_service import AnalyticsService
from .api_manager import APIManager, BackgroundTaskManager
from .article_service import ArticleService
from .data_service import DataService
from .export_service import ExportService
from .lyrics_service import LyricsService
from .movie_service import MovieService


class ApplicationServices:
    """Central manager for all application services."""

    def __init__(self) -> None:
        """Initialize all application services."""
        self._initialized = False

        # Core services
        self.sentimentAnalyzer: SentimentAnalyzer | None = None
        self.dataService: DataService | None = None
        self.apiManager: APIManager | None = None
        self.exportService: ExportService | None = None
        self.analyticsService: AnalyticsService | None = None
        self.backgroundTasks: BackgroundTaskManager | None = None

        # Content analysis services
        self.lyricsService: LyricsService | None = None
        self.movieService: MovieService | None = None
        self.articleService: ArticleService | None = None

        logger.info("Application services manager created")

    def initialize(self) -> None:
        """Initialize all services."""
        if self._initialized:
            logger.warning("Services already initialized")
            return

        try:
            logger.info("Initializing application services...")

            # Initialize core sentiment analyzer
            self.sentimentAnalyzer = SentimentAnalyzer()

            # Initialize data service
            dataPath = settings.getDataPath()
            settingsPath = settings.getSettingsPath()
            databasePath = settings.getDatabasePath()
            self.dataService = DataService(dataPath, settingsPath, databasePath)

            # Initialize API manager with caching and rate limiting
            self.apiManager = APIManager(
                maxRequests=100,
                timeWindow=60,
                cacheSize=settings.cache.maxSize,
                cacheTtl=settings.cache.ttlSeconds,
            )

            # Initialize export service
            self.exportService = ExportService()

            # Initialize analytics service
            self.analyticsService = AnalyticsService(self.dataService)

            # Initialize background task manager
            self.backgroundTasks = BackgroundTaskManager(self.apiManager)
            if settings.cache.enabled:
                self.backgroundTasks.startMaintenance(settings.cache.cleanupInterval)

            # Initialize content analysis services
            self.lyricsService = LyricsService(apiKey=settings.api.geniusApiKey)
            self.movieService = MovieService(apiKey=settings.api.tmdbApiKey)
            self.articleService = ArticleService()

            self._initialized = True
            logger.info("All application services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        if not self._initialized:
            return

        logger.info("Shutting down application services...")

        # Stop background tasks
        if self.backgroundTasks:
            self.backgroundTasks.stopMaintenance()

        # Clear caches
        if self.apiManager:
            self.apiManager.clearCache()

        self._initialized = False
        logger.info("Application services shutdown complete")

    def analyzeText(self, text: str | TextInput, saveToHistory: bool = True) -> dict:
        """Analyze text with full Phase 4 integration.

        Args:
            text: Text to analyze (string) or TextInput object
            saveToHistory: Whether to save the result to history

        Returns:
            Analysis result dictionary
        """
        if not self._initialized:
            raise RuntimeError("Services not initialized")

        # Use API manager for rate limiting and caching
        def performAnalysis(inputData: str | TextInput) -> dict:
            # Create input object if needed
            if isinstance(inputData, TextInput):
                textInput = inputData
            else:
                textInput = TextInput(content=inputData, source="direct")

            # Perform analysis
            result = self.sentimentAnalyzer.analyzeText(textInput)

            # Save to history if requested
            if saveToHistory and self.dataService:
                self.dataService.saveAnalysisResult(textInput, result)

            # Convert to dictionary for caching
            return {
                "primary_sentiment": result.primarySentiment,
                "confidence": result.confidence,
                "scores": [{"label": s.label, "score": s.score} for s in result.scores],
                "processing_time": result.processingTime,
                "timestamp": datetime.fromtimestamp(result.timestamp).isoformat(),
                "model_version": result.modelVersion,
            }

        # Get cache key based on input type
        cache_key = text.content if isinstance(text, TextInput) else text

        # Process through API manager - pass the original text object to performAnalysis
        return self.apiManager.processRequest(
            cache_key, lambda _: performAnalysis(text)
        )

    def getAnalysisHistory(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """Get analysis history.

        Args:
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of analysis records
        """
        if not self.dataService:
            return []

        return self.dataService.getAnalysisHistory(limit, offset)

    def searchHistory(self, query: str, sentiment: str | None = None) -> list[dict]:
        """Search analysis history.

        Args:
            query: Text to search for
            sentiment: Optional sentiment filter

        Returns:
            List of matching records
        """
        if not self.dataService:
            return []

        return self.dataService.searchAnalysisHistory(query, sentiment)

    def exportData(
        self,
        filePath: Path,
        format: str = "json",
        includeMetadata: bool = True,
        limit: int = 1000,
    ) -> None:
        """Export analysis data.

        Args:
            filePath: Path to save exported data
            format: Export format
            includeMetadata: Whether to include metadata
            limit: Maximum number of records to export
        """
        if not self.exportService or not self.dataService:
            raise RuntimeError("Export or data service not available")

        # Get data to export
        data = self.dataService.getAnalysisHistory(limit)

        # Export using export service
        self.exportService.exportResults(data, filePath, format, includeMetadata)

    def generateSummaryReport(self, filePath: Path, format: str = "html") -> None:
        """Generate a summary analytics report.

        Args:
            filePath: Path to save the report
            format: Report format (html or json)
        """
        if not self.exportService or not self.dataService:
            raise RuntimeError("Export or data service not available")

        # Get data for report
        data = self.dataService.getAnalysisHistory(limit=5000)

        # Generate report
        self.exportService.exportSummaryReport(data, filePath, format)

    def getUsageAnalytics(self, days: int = 30) -> dict:
        """Get usage analytics.

        Args:
            days: Number of days to analyze

        Returns:
            Analytics dictionary
        """
        if not self.analyticsService:
            return {}

        return self.analyticsService.generateUsageReport(days)

    def getQuickStats(self) -> dict:
        """Get quick dashboard statistics.

        Returns:
            Quick statistics dictionary
        """
        if not self.analyticsService:
            return {}

        return self.analyticsService.getQuickStats()

    def getAPIStats(self) -> dict:
        """Get API usage statistics.

        Returns:
            API statistics dictionary
        """
        if not self.apiManager:
            return {}

        return self.apiManager.getStats()

    def clearOldData(self, daysToKeep: int = 365) -> int:
        """Clear old analysis data.

        Args:
            daysToKeep: Number of days to retain

        Returns:
            Number of records deleted
        """
        if not self.dataService:
            return 0

        return self.dataService.clearOldData(daysToKeep)

    def backupData(self, backupPath: Path) -> None:
        """Create a backup of all data.

        Args:
            backupPath: Path to save backup
        """
        if not self.exportService or not self.dataService:
            raise RuntimeError("Backup services not available")

        # Export all data as JSON backup
        allData = self.dataService.getAnalysisHistory(limit=100000)
        self.exportService.exportResults(
            allData,
            backupPath / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "json",
            includeMetadata=True,
        )

    def getServiceStatus(self) -> dict:
        """Get status of all services.

        Returns:
            Service status dictionary
        """
        return {
            "initialized": self._initialized,
            "sentiment_analyzer": self.sentimentAnalyzer is not None,
            "data_service": self.dataService is not None,
            "api_manager": self.apiManager is not None,
            "export_service": self.exportService is not None,
            "analytics_service": self.analyticsService is not None,
            "background_tasks": self.backgroundTasks is not None
            and self.backgroundTasks.isRunning,
            "database_size": (
                self.dataService.getDatabaseSize() if self.dataService else 0
            ),
            "record_count": (
                self.dataService.getRecordCount() if self.dataService else 0
            ),
        }


# Global services instance
services = ApplicationServices()
