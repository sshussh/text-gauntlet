"""Helper utilities for Text Gauntlet application."""

import hashlib
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any


class TimeHelper:
    """Helper class for time-related operations."""

    @staticmethod
    def getCurrentTimestamp() -> float:
        """Get current timestamp."""
        return time.time()

    @staticmethod
    def formatTimestamp(timestamp: float, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format timestamp to readable string."""
        return time.strftime(format, time.localtime(timestamp))

    @staticmethod
    def getCurrentTimeString() -> str:
        """Get current time as formatted string."""
        return time.strftime("%H:%M:%S", time.localtime())

    @staticmethod
    def measureExecutionTime(func):
        """Decorator to measure function execution time."""

        def wrapper(*args, **kwargs):
            startTime = time.time()
            result = func(*args, **kwargs)
            endTime = time.time()
            executionTime = endTime - startTime

            # Add execution time to result if it's a dictionary
            if isinstance(result, dict):
                result["executionTime"] = executionTime

            return result

        return wrapper


class StringHelper:
    """Helper class for string operations."""

    @staticmethod
    def truncateText(text: str, maxLength: int, suffix: str = "...") -> str:
        """Truncate text to specified length with optional suffix."""
        if len(text) <= maxLength:
            return text

        truncatedLength = maxLength - len(suffix)
        return text[:truncatedLength] + suffix

    @staticmethod
    def cleanText(text: str) -> str:
        """Clean text by removing extra whitespace and normalizing."""
        # Remove extra whitespace
        cleaned = " ".join(text.split())

        # Normalize unicode characters
        cleaned = cleaned.encode("ascii", "ignore").decode("ascii")

        return cleaned.strip()

    @staticmethod
    def generateHash(text: str) -> str:
        """Generate SHA-256 hash of text."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def generateSessionId() -> str:
        """Generate unique session ID."""
        return str(uuid.uuid4())

    @staticmethod
    def sanitizeFilename(filename: str) -> str:
        """Sanitize filename by removing invalid characters."""
        invalidChars = '<>:"/\\|?*'
        sanitized = "".join(c for c in filename if c not in invalidChars)
        return sanitized.strip()


class FileHelper:
    """Helper class for file operations."""

    @staticmethod
    def ensureDirectoryExists(path: Path) -> None:
        """Ensure directory exists, create if it doesn't."""
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def getFileSize(path: Path) -> int:
        """Get file size in bytes."""
        return path.stat().st_size if path.exists() else 0

    @staticmethod
    def isFileNewer(file1: Path, file2: Path) -> bool:
        """Check if file1 is newer than file2."""
        if not file1.exists() or not file2.exists():
            return False

        return file1.stat().st_mtime > file2.stat().st_mtime

    @staticmethod
    def backupFile(originalPath: Path, backupSuffix: str = ".backup") -> Path:
        """Create backup of file."""
        backupPath = originalPath.with_suffix(originalPath.suffix + backupSuffix)

        if originalPath.exists():
            import shutil

            shutil.copy2(originalPath, backupPath)

        return backupPath


class DataHelper:
    """Helper class for data operations."""

    @staticmethod
    def flattenDict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """Flatten nested dictionary."""

        def _flatten(obj: Any, parent_key: str = "") -> dict[str, Any]:
            items = []

            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    items.extend(_flatten(value, new_key).items())
            else:
                return {parent_key: obj}

            return dict(items)

        return _flatten(data)

    @staticmethod
    def chunkList(data: list[Any], chunkSize: int) -> list[list[Any]]:
        """Split list into chunks of specified size."""
        return [data[i : i + chunkSize] for i in range(0, len(data), chunkSize)]

    @staticmethod
    def filterEmptyValues(data: dict[str, Any]) -> dict[str, Any]:
        """Filter out empty values from dictionary."""
        return {k: v for k, v in data.items() if v is not None and v != ""}

    @staticmethod
    def mergeResults(results: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge multiple analysis results."""
        if not results:
            return {}

        merged = {
            "totalAnalyses": len(results),
            "averageConfidence": sum(r.get("confidence", 0) for r in results)
            / len(results),
            "totalProcessingTime": sum(r.get("processingTime", 0) for r in results),
            "results": results,
        }

        return merged


class UIHelper:
    """Helper class for UI operations."""

    @staticmethod
    def centerWindow(window, width: int, height: int) -> None:
        """Center window on screen."""
        # Get screen dimensions
        screenWidth = window.winfo_screenwidth()
        screenHeight = window.winfo_screenheight()

        # Calculate position
        x = int((screenWidth / 2) - (width / 2))
        y = int((screenHeight / 2) - (height / 2))

        # Set window geometry
        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def formatScore(score: float, precision: int = 2) -> str:
        """Format score as percentage string."""
        return f"{score * 100:.{precision}f}%"

    @staticmethod
    def formatEmotionScores(scores: list[dict[str, Any]], topN: int = 5) -> list[str]:
        """Format emotion scores for display."""
        # Sort by score
        sortedScores = sorted(scores, key=lambda x: x.get("score", 0), reverse=True)

        # Format top N scores
        formatted = []
        for i, score in enumerate(sortedScores[:topN]):
            label = score.get("label", "Unknown").title()
            value = UIHelper.formatScore(score.get("score", 0))
            formatted.append(f"{i + 1}. {label}: {value}")

        return formatted

    @staticmethod
    def createProgressCallback(
        totalSteps: int, updateCallback: Callable[[float, str], None] | None = None
    ):
        """Create progress tracking callback."""
        currentStep = 0

        def progressCallback(message: str = ""):
            nonlocal currentStep
            currentStep += 1
            progress = (currentStep / totalSteps) * 100

            if updateCallback:
                updateCallback(progress, message)

            return progress

        return progressCallback

    @staticmethod
    def getSentimentColor(sentiment: str) -> str:
        """Get color for sentiment display."""
        colors = {
            "positive": "#22c55e",  # Green
            "negative": "#ef4444",  # Red
            "neutral": "#6b7280",  # Gray
        }
        return colors.get(sentiment.lower(), "#ffffff")

    @staticmethod
    def getConfidenceColor(confidence: float) -> str:
        """Get color for confidence display based on confidence level."""
        if confidence >= 0.8:
            return "#22c55e"  # Green for high confidence
        elif confidence >= 0.6:
            return "#f59e0b"  # Amber for medium confidence
        else:
            return "#ef4444"  # Red for low confidence
