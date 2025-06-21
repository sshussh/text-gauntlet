"""Data persistence service for Text Gauntlet."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.models import SentimentResult, TextInput
from utils.exceptions import DataPersistenceError
from utils.logger import logger


class DataService:
    """Service for data persistence and retrieval."""

    def __init__(
        self, dataDir: Path, settingsDir: Path = None, databaseDir: Path = None
    ) -> None:
        """Initialize the data service.

        Args:
            dataDir: Directory to store data files (legacy parameter)
            settingsDir: Directory to store settings files
            databaseDir: Directory to store database files
        """
        self.dataDir = dataDir
        self.dataDir.mkdir(parents=True, exist_ok=True)

        # Use new structured directories if provided, otherwise use legacy structure
        if settingsDir is not None and databaseDir is not None:
            self.settingsDir = settingsDir
            self.databaseDir = databaseDir
            self.settingsDir.mkdir(parents=True, exist_ok=True)
            self.databaseDir.mkdir(parents=True, exist_ok=True)

            # Database file in the database directory
            self.dbPath = self.databaseDir / "text_gauntlet.db"
            # JSON file for user preferences in settings directory
            self.prefsPath = self.settingsDir / "preferences.json"
        else:
            # Legacy structure - files directly in data directory
            self.settingsDir = self.dataDir
            self.databaseDir = self.dataDir
            # Database file for analysis history
            self.dbPath = self.dataDir / "text_gauntlet.db"
            # JSON file for user preferences
            self.prefsPath = self.dataDir / "preferences.json"

        # Initialize database
        self._initializeDatabase()

        logger.info(f"Data service initialized with directory: {self.dataDir}")
        if settingsDir is not None:
            logger.info(f"Settings directory: {self.settingsDir}")
            logger.info(f"Database directory: {self.databaseDir}")

    def _initializeDatabase(self) -> None:
        """Initialize the SQLite database."""
        try:
            with sqlite3.connect(self.dbPath) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        input_text TEXT NOT NULL,
                        input_source TEXT NOT NULL,
                        input_metadata TEXT DEFAULT '{}',
                        primary_sentiment TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        scores TEXT NOT NULL,
                        processing_time REAL NOT NULL,
                        model_version TEXT NOT NULL
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        analyses_count INTEGER DEFAULT 0,
                        total_processing_time REAL DEFAULT 0.0,
                        avg_confidence REAL DEFAULT 0.0,
                        most_common_sentiment TEXT DEFAULT '',
                        unique_sessions INTEGER DEFAULT 1
                    )
                """
                )

                conn.commit()
                logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DataPersistenceError(f"Database initialization failed: {e}") from e

        # Add metadata column if it doesn't exist (migration for existing databases)
        try:
            with sqlite3.connect(self.dbPath) as conn:
                conn.execute(
                    "ALTER TABLE analysis_history ADD COLUMN input_metadata TEXT DEFAULT '{}'"
                )
                conn.commit()
                logger.info("Added input_metadata column to existing database")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                logger.warning(f"Could not add metadata column: {e}")

    def saveAnalysisResult(self, textInput: TextInput, result: SentimentResult) -> int:
        """Save an analysis result to the database.

        Args:
            textInput: The input that was analyzed
            result: The analysis result

        Returns:
            The ID of the saved record
        """
        try:
            # Serialize scores to JSON
            scoresJson = json.dumps(
                [
                    {"label": score.label, "score": score.score}
                    for score in result.scores
                ]
            )

            # Serialize metadata to JSON
            metadataJson = json.dumps(textInput.metadata or {})

            with sqlite3.connect(self.dbPath) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO analysis_history
                    (timestamp, input_text, input_source, input_metadata, primary_sentiment,
                     confidence, scores, processing_time, model_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.fromtimestamp(result.timestamp).isoformat(),
                        textInput.content,
                        textInput.source,
                        metadataJson,
                        result.primarySentiment,
                        result.confidence,
                        scoresJson,
                        result.processingTime,
                        result.modelVersion,
                    ),
                )

                recordId = cursor.lastrowid
                conn.commit()

                # Update usage statistics
                self._updateUsageStats(result)

                logger.info(f"Analysis result saved with ID: {recordId}")
                return recordId

        except sqlite3.Error as e:
            logger.error(f"Failed to save analysis result: {e}")
            raise DataPersistenceError(f"Failed to save analysis: {e}") from e

    def getAnalysisHistory(
        self, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get analysis history from the database.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of analysis records
        """
        try:
            with sqlite3.connect(self.dbPath) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM analysis_history
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    # Parse scores JSON
                    record["scores"] = json.loads(record["scores"])
                    # Parse metadata JSON
                    try:
                        record["input_metadata"] = json.loads(
                            record.get("input_metadata", "{}")
                        )
                    except (json.JSONDecodeError, TypeError):
                        record["input_metadata"] = {}
                    records.append(record)

                logger.info(f"Retrieved {len(records)} analysis records")
                return records

        except sqlite3.Error as e:
            logger.error(f"Failed to get analysis history: {e}")
            raise DataPersistenceError(f"Failed to retrieve history: {e}") from e

    def searchAnalysisHistory(
        self, query: str, sentiment: str | None = None
    ) -> list[dict[str, Any]]:
        """Search analysis history by text content or sentiment.

        Args:
            query: Text to search for in input_text
            sentiment: Optional sentiment filter

        Returns:
            List of matching analysis records
        """
        try:
            with sqlite3.connect(self.dbPath) as conn:
                conn.row_factory = sqlite3.Row

                sql = """
                    SELECT * FROM analysis_history
                    WHERE input_text LIKE ?
                """
                params = [f"%{query}%"]

                if sentiment:
                    sql += " AND primary_sentiment = ?"
                    params.append(sentiment)

                sql += " ORDER BY timestamp DESC LIMIT 50"

                cursor = conn.execute(sql, params)

                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    record["scores"] = json.loads(record["scores"])
                    records.append(record)

                logger.info(f"Search returned {len(records)} matching records")
                return records

        except sqlite3.Error as e:
            logger.error(f"Failed to search analysis history: {e}")
            raise DataPersistenceError(f"Search failed: {e}") from e

    def _updateUsageStats(self, result: SentimentResult) -> None:
        """Update daily usage statistics.

        Args:
            result: The analysis result to include in stats
        """
        try:
            today = datetime.now().date().isoformat()

            with sqlite3.connect(self.dbPath) as conn:
                # Check if record exists for today
                cursor = conn.execute(
                    "SELECT * FROM usage_stats WHERE date = ?", (today,)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing record
                    newCount = existing[2] + 1
                    newTotalTime = existing[3] + result.processingTime
                    newAvgConfidence = (
                        (existing[4] * existing[2]) + result.confidence
                    ) / newCount

                    conn.execute(
                        """
                        UPDATE usage_stats
                        SET analyses_count = ?,
                            total_processing_time = ?,
                            avg_confidence = ?,
                            most_common_sentiment = ?
                        WHERE date = ?
                    """,
                        (
                            newCount,
                            newTotalTime,
                            newAvgConfidence,
                            result.primarySentiment,
                            today,
                        ),
                    )
                else:
                    # Create new record
                    conn.execute(
                        """
                        INSERT INTO usage_stats
                        (date, analyses_count, total_processing_time,
                         avg_confidence, most_common_sentiment)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            today,
                            1,
                            result.processingTime,
                            result.confidence,
                            result.primarySentiment,
                        ),
                    )

                conn.commit()

        except sqlite3.Error as e:
            logger.warning(f"Failed to update usage stats: {e}")

    def getUsageStats(self, days: int = 30) -> list[dict[str, Any]]:
        """Get usage statistics for the specified number of days.

        Args:
            days: Number of days to retrieve stats for

        Returns:
            List of usage statistics records
        """
        try:
            with sqlite3.connect(self.dbPath) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM usage_stats
                    ORDER BY date DESC
                    LIMIT ?
                """,
                    (days,),
                )

                records = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Retrieved usage stats for {len(records)} days")
                return records

        except sqlite3.Error as e:
            logger.error(f"Failed to get usage stats: {e}")
            raise DataPersistenceError(f"Failed to retrieve stats: {e}") from e

    def saveUserPreferences(self, preferences: dict[str, Any]) -> None:
        """Save user preferences to JSON file.

        Args:
            preferences: Dictionary of user preferences
        """
        try:
            with open(self.prefsPath, "w") as f:
                json.dump(preferences, f, indent=2)

            logger.info("User preferences saved successfully")

        except (OSError, json.JSONEncodeError) as e:
            logger.error(f"Failed to save user preferences: {e}")
            raise DataPersistenceError(f"Failed to save preferences: {e}") from e

    def loadUserPreferences(self) -> dict[str, Any]:
        """Load user preferences from JSON file.

        Returns:
            Dictionary of user preferences
        """
        try:
            if self.prefsPath.exists():
                with open(self.prefsPath) as f:
                    preferences = json.load(f)
                logger.info("User preferences loaded successfully")
                return preferences
            else:
                logger.info("No preferences file found, using defaults")
                return {}

        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load user preferences: {e}")
            return {}

    def exportAnalysisHistory(self, filePath: Path, format: str = "json") -> None:
        """Export analysis history to a file.

        Args:
            filePath: Path to save the exported data
            format: Export format ("json" or "csv")
        """
        try:
            history = self.getAnalysisHistory(limit=10000)  # Get all records

            if format.lower() == "json":
                with open(filePath, "w") as f:
                    json.dump(history, f, indent=2, default=str)
            elif format.lower() == "csv":
                import csv

                with open(filePath, "w", newline="") as f:
                    if history:
                        writer = csv.DictWriter(f, fieldnames=history[0].keys())
                        writer.writeheader()
                        for record in history:
                            # Flatten scores for CSV
                            record_copy = record.copy()
                            record_copy["scores"] = json.dumps(record["scores"])
                            writer.writerow(record_copy)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            logger.info(f"Analysis history exported to {filePath} in {format} format")

        except Exception as e:
            logger.error(f"Failed to export analysis history: {e}")
            raise DataPersistenceError(f"Export failed: {e}") from e

    def clearAnalysisHistory(self) -> int:
        """Clear all analysis history.

        Returns:
            Number of records deleted
        """
        try:
            with sqlite3.connect(self.dbPath) as conn:
                cursor = conn.execute("DELETE FROM analysis_history")
                deletedCount = cursor.rowcount
                conn.commit()

                logger.info(f"Cleared all {deletedCount} analysis history records")
                return deletedCount

        except sqlite3.Error as e:
            logger.error(f"Failed to clear analysis history: {e}")
            raise DataPersistenceError(f"Failed to clear analysis history: {e}") from e

    def clearOldData(self, daysToKeep: int = 365) -> int:
        """Clear old analysis data to manage storage.

        Args:
            daysToKeep: Number of days of data to retain

        Returns:
            Number of records deleted
        """
        try:
            cutoffDate = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=daysToKeep)

            with sqlite3.connect(self.dbPath) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM analysis_history
                    WHERE timestamp < ?
                """,
                    (cutoffDate.isoformat(),),
                )

                deletedCount = cursor.rowcount
                conn.commit()

                logger.info(f"Cleared {deletedCount} old analysis records")
                return deletedCount

        except sqlite3.Error as e:
            logger.error(f"Failed to clear old data: {e}")
            raise DataPersistenceError(f"Failed to clear data: {e}") from e

    def getDatabaseSize(self) -> int:
        """Get the size of the database file in bytes.

        Returns:
            Database file size in bytes
        """
        try:
            return self.dbPath.stat().st_size if self.dbPath.exists() else 0
        except OSError:
            return 0

    def getRecordCount(self) -> int:
        """Get the total number of analysis records.

        Returns:
            Total number of records in the database
        """
        try:
            with sqlite3.connect(self.dbPath) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM analysis_history")
                count = cursor.fetchone()[0]
                return count

        except sqlite3.Error as e:
            logger.error(f"Failed to get record count: {e}")
            return 0
