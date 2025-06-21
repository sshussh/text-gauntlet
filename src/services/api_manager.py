"""API management service with rate limiting and caching for Text Gauntlet."""

import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from utils.exceptions import APILimitError
from utils.logger import logger


class RateLimiter:
    """Rate limiting service to prevent API abuse."""

    def __init__(self, maxRequests: int = 100, timeWindow: int = 60) -> None:
        """Initialize the rate limiter.

        Args:
            maxRequests: Maximum number of requests allowed in time window
            timeWindow: Time window in seconds
        """
        self.maxRequests = maxRequests
        self.timeWindow = timeWindow
        self.requestHistory: list[float] = []

        logger.info(
            f"Rate limiter initialized: {maxRequests} requests per {timeWindow}s"
        )

    def checkLimit(self) -> bool:
        """Check if the current request is within rate limits.

        Returns:
            True if request is allowed, False otherwise
        """
        currentTime = time.time()

        # Remove requests outside the time window
        cutoffTime = currentTime - self.timeWindow
        self.requestHistory = [
            timestamp for timestamp in self.requestHistory if timestamp > cutoffTime
        ]

        # Check if we're within limits
        if len(self.requestHistory) >= self.maxRequests:
            logger.warning("Rate limit exceeded")
            return False

        # Record this request
        self.requestHistory.append(currentTime)
        logger.debug(
            f"Request allowed, {len(self.requestHistory)}/{self.maxRequests} used"
        )
        return True

    def timeUntilReset(self) -> float:
        """Get the time until the rate limit resets.

        Returns:
            Time in seconds until rate limit resets
        """
        if not self.requestHistory:
            return 0.0

        oldestRequest = min(self.requestHistory)
        resetTime = oldestRequest + self.timeWindow
        currentTime = time.time()

        return max(0.0, resetTime - currentTime)

    def getRemainingRequests(self) -> int:
        """Get the number of remaining requests in the current window.

        Returns:
            Number of remaining requests
        """
        self.checkLimit()  # Clean up old requests
        return max(0, self.maxRequests - len(self.requestHistory))


class AnalysisCache:
    """Caching service for analysis results."""

    def __init__(self, maxSize: int = 1000, ttlSeconds: int = 3600) -> None:
        """Initialize the analysis cache.

        Args:
            maxSize: Maximum number of cached items
            ttlSeconds: Time-to-live for cached items in seconds
        """
        self.maxSize = maxSize
        self.ttlSeconds = ttlSeconds
        self.cache: dict[str, dict[str, Any]] = {}

        logger.info(f"Analysis cache initialized: {maxSize} items, {ttlSeconds}s TTL")

    def _generateKey(self, text: str) -> str:
        """Generate a cache key for the given text.

        Args:
            text: Input text to generate key for

        Returns:
            Cache key string
        """
        import hashlib

        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get(self, text: str) -> dict[str, Any] | None:
        """Get cached analysis result for the given text.

        Args:
            text: Input text to look up

        Returns:
            Cached result dictionary or None if not found/expired
        """
        key = self._generateKey(text)

        if key not in self.cache:
            logger.debug(f"Cache miss for key: {key}")
            return None

        entry = self.cache[key]

        # Check if entry has expired
        if time.time() - entry["timestamp"] > self.ttlSeconds:
            logger.debug(f"Cache entry expired for key: {key}")
            del self.cache[key]
            return None

        logger.debug(f"Cache hit for key: {key}")
        return entry["result"]

    def put(self, text: str, result: dict[str, Any]) -> None:
        """Store analysis result in cache.

        Args:
            text: Input text
            result: Analysis result to cache
        """
        key = self._generateKey(text)

        # If cache is full, remove oldest entry
        if len(self.cache) >= self.maxSize:
            oldestKey = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldestKey]
            logger.debug(f"Removed oldest cache entry: {oldestKey}")

        # Store new entry
        self.cache[key] = {"result": result, "timestamp": time.time()}

        logger.debug(f"Cached result for key: {key}")

    def clear(self) -> None:
        """Clear all cached entries."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cache entries")

    def cleanup(self) -> int:
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        currentTime = time.time()
        expiredKeys = [
            key
            for key, entry in self.cache.items()
            if currentTime - entry["timestamp"] > self.ttlSeconds
        ]

        for key in expiredKeys:
            del self.cache[key]

        if expiredKeys:
            logger.info(f"Cleaned up {len(expiredKeys)} expired cache entries")

        return len(expiredKeys)

    def getStats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics
        """
        return {
            "size": len(self.cache),
            "maxSize": self.maxSize,
            "ttlSeconds": self.ttlSeconds,
            "hitRate": getattr(self, "_hitRate", 0.0),
            "totalRequests": getattr(self, "_totalRequests", 0),
            "hits": getattr(self, "_hits", 0),
            "misses": getattr(self, "_misses", 0),
        }


class APIManager:
    """Main API management service combining rate limiting and caching."""

    def __init__(
        self,
        maxRequests: int = 100,
        timeWindow: int = 60,
        cacheSize: int = 1000,
        cacheTtl: int = 3600,
    ) -> None:
        """Initialize the API manager.

        Args:
            maxRequests: Maximum requests per time window
            timeWindow: Time window for rate limiting in seconds
            cacheSize: Maximum cache size
            cacheTtl: Cache TTL in seconds
        """
        self.rateLimiter = RateLimiter(maxRequests, timeWindow)
        self.cache = AnalysisCache(cacheSize, cacheTtl)

        # Statistics tracking
        self._stats = {
            "totalRequests": 0,
            "rateLimitedRequests": 0,
            "cacheHits": 0,
            "cacheMisses": 0,
            "startTime": datetime.now(),
        }

        logger.info("API manager initialized with rate limiting and caching")

    def processRequest(
        self, text: str, analysisFunction: Callable[[str], dict[str, Any]]
    ) -> dict[str, Any]:
        """Process a sentiment analysis request with rate limiting and caching.

        Args:
            text: Text to analyze
            analysisFunction: Function to perform the analysis

        Returns:
            Analysis result dictionary

        Raises:
            APILimitError: If rate limit is exceeded
            CacheError: If caching fails
        """
        self._stats["totalRequests"] += 1

        # Check rate limit
        if not self.rateLimiter.checkLimit():
            self._stats["rateLimitedRequests"] += 1
            waitTime = self.rateLimiter.timeUntilReset()
            raise APILimitError(
                f"Rate limit exceeded. Try again in {waitTime:.1f} seconds.",
                retryAfter=waitTime,
            )

        # Check cache first
        cachedResult = self.cache.get(text)
        if cachedResult is not None:
            self._stats["cacheHits"] += 1
            logger.info("Returning cached analysis result")
            return cachedResult

        # Cache miss - perform analysis
        self._stats["cacheMisses"] += 1
        logger.info("Performing new analysis (cache miss)")

        try:
            result = analysisFunction(text)

            # Cache the result
            self.cache.put(text, result)

            return result

        except Exception as e:
            logger.error(f"Analysis function failed: {e}")
            raise

    def getStats(self) -> dict[str, Any]:
        """Get comprehensive API usage statistics.

        Returns:
            Dictionary containing usage statistics
        """
        uptime = datetime.now() - self._stats["startTime"]
        cacheStats = self.cache.getStats()

        # Calculate cache hit rate
        totalCacheRequests = self._stats["cacheHits"] + self._stats["cacheMisses"]
        cacheHitRate = (
            self._stats["cacheHits"] / totalCacheRequests
            if totalCacheRequests > 0
            else 0.0
        )

        return {
            "uptime": str(uptime),
            "totalRequests": self._stats["totalRequests"],
            "rateLimitedRequests": self._stats["rateLimitedRequests"],
            "cacheHits": self._stats["cacheHits"],
            "cacheMisses": self._stats["cacheMisses"],
            "cacheHitRate": f"{cacheHitRate:.2%}",
            "remainingRequests": self.rateLimiter.getRemainingRequests(),
            "timeUntilReset": self.rateLimiter.timeUntilReset(),
            "cache": cacheStats,
        }

    def clearCache(self) -> None:
        """Clear the analysis cache."""
        self.cache.clear()
        logger.info("API cache cleared")

    def cleanupCache(self) -> int:
        """Clean up expired cache entries.

        Returns:
            Number of entries removed
        """
        return self.cache.cleanup()

    def resetStats(self) -> None:
        """Reset API usage statistics."""
        self._stats = {
            "totalRequests": 0,
            "rateLimitedRequests": 0,
            "cacheHits": 0,
            "cacheMisses": 0,
            "startTime": datetime.now(),
        }
        logger.info("API statistics reset")


class BackgroundTaskManager:
    """Manager for background maintenance tasks."""

    def __init__(self, apiManager: APIManager) -> None:
        """Initialize the background task manager.

        Args:
            apiManager: API manager instance to maintain
        """
        self.apiManager = apiManager
        self.isRunning = False
        self._lastCleanup = datetime.now()

        logger.info("Background task manager initialized")

    def startMaintenance(self, intervalMinutes: int = 15) -> None:
        """Start periodic maintenance tasks.

        Args:
            intervalMinutes: Interval between maintenance runs
        """
        import threading

        def maintenanceLoop() -> None:
            while self.isRunning:
                try:
                    # Clean up expired cache entries
                    cleaned = self.apiManager.cleanupCache()
                    if cleaned > 0:
                        logger.info(f"Maintenance: cleaned {cleaned} cache entries")

                    self._lastCleanup = datetime.now()

                    # Sleep until next maintenance
                    time.sleep(intervalMinutes * 60)

                except Exception as e:
                    logger.error(f"Maintenance task failed: {e}")
                    time.sleep(60)  # Wait a minute before retrying

        if not self.isRunning:
            self.isRunning = True
            thread = threading.Thread(target=maintenanceLoop, daemon=True)
            thread.start()
            logger.info(f"Started maintenance tasks (interval: {intervalMinutes}m)")

    def stopMaintenance(self) -> None:
        """Stop maintenance tasks."""
        self.isRunning = False
        logger.info("Stopped maintenance tasks")

    def getMaintenanceStatus(self) -> dict[str, Any]:
        """Get maintenance status information.

        Returns:
            Dictionary containing maintenance status
        """
        return {
            "isRunning": self.isRunning,
            "lastCleanup": self._lastCleanup.isoformat(),
            "timeSinceLastCleanup": str(datetime.now() - self._lastCleanup),
        }
