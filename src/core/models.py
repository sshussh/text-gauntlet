"""Data models for Text Gauntlet application."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class SentimentLabel(Enum):
    """Enumeration for sentiment labels."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EmotionLabel(Enum):
    """Enumeration for emotion labels based on Go Emotions dataset."""

    ADMIRATION = "admiration"
    AMUSEMENT = "amusement"
    ANGER = "anger"
    ANNOYANCE = "annoyance"
    APPROVAL = "approval"
    CARING = "caring"
    CONFUSION = "confusion"
    CURIOSITY = "curiosity"
    DESIRE = "desire"
    DISAPPOINTMENT = "disappointment"
    DISAPPROVAL = "disapproval"
    DISGUST = "disgust"
    EMBARRASSMENT = "embarrassment"
    EXCITEMENT = "excitement"
    FEAR = "fear"
    GRATITUDE = "gratitude"
    GRIEF = "grief"
    JOY = "joy"
    LOVE = "love"
    NERVOUSNESS = "nervousness"
    OPTIMISM = "optimism"
    PRIDE = "pride"
    REALIZATION = "realization"
    RELIEF = "relief"
    REMORSE = "remorse"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"


@dataclass
class SentimentScore:
    """Individual sentiment score with label and confidence."""

    label: str
    score: float

    def __post_init__(self) -> None:
        """Validate score range."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")


@dataclass
class SentimentResult:
    """Complete sentiment analysis result."""

    text: str
    scores: list[SentimentScore]
    primarySentiment: str
    confidence: float
    processingTime: float
    timestamp: float
    modelVersion: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not hasattr(self, "timestamp") or self.timestamp == 0:
            self.timestamp = time.time()

    @property
    def topEmotions(self) -> list[SentimentScore]:
        """Get top 3 emotions by score."""
        return sorted(self.scores, key=lambda x: x.score, reverse=True)[:3]

    def toDict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "scores": [{"label": s.label, "score": s.score} for s in self.scores],
            "primarySentiment": self.primarySentiment,
            "confidence": self.confidence,
            "processingTime": self.processingTime,
            "timestamp": self.timestamp,
            "modelVersion": self.modelVersion,
        }


@dataclass
class TextInput:
    """Input text with metadata."""

    content: str
    source: str = "direct"  # "direct", "lyrics", "reviews", "url"
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}

    @property
    def length(self) -> int:
        """Get text length."""
        return len(self.content)

    @property
    def wordCount(self) -> int:
        """Get word count."""
        return len(self.content.split())


@dataclass
class LyricsData:
    """Song lyrics data structure."""

    artist: str
    title: str
    lyrics: str
    album: str | None = None
    year: int | None = None
    url: str | None = None

    def toTextInput(self) -> TextInput:
        """Convert to TextInput for analysis."""
        metadata = {
            "artist": self.artist,
            "title": self.title,
            "album": self.album,
            "year": self.year,
            "url": self.url,
        }
        return TextInput(content=self.lyrics, source="lyrics", metadata=metadata)


@dataclass
class MovieReview:
    """Individual movie review data."""

    content: str
    rating: float | None = None
    author: str | None = None
    date: str | None = None
    helpful: int | None = None


@dataclass
class MovieData:
    """Movie reviews data structure."""

    title: str
    year: int | None
    imdbId: str | None
    reviews: list[MovieReview]
    averageRating: float | None = None

    def toTextInput(self) -> TextInput:
        """Convert reviews to TextInput for analysis."""
        combinedReviews = "\n".join([review.content for review in self.reviews])
        metadata = {
            "title": self.title,
            "year": self.year,
            "imdbId": self.imdbId,
            "reviewCount": len(self.reviews),
            "averageRating": self.averageRating,
        }
        return TextInput(content=combinedReviews, source="reviews", metadata=metadata)


@dataclass
class AnalysisSession:
    """Analysis session data for tracking history."""

    sessionId: str
    results: list[SentimentResult]
    startTime: float
    endTime: float | None = None

    def __post_init__(self) -> None:
        """Initialize timestamps."""
        if not hasattr(self, "startTime") or self.startTime == 0:
            self.startTime = time.time()

    def addResult(self, result: SentimentResult) -> None:
        """Add analysis result to session."""
        self.results.append(result)

    def finish(self) -> None:
        """Mark session as finished."""
        self.endTime = time.time()

    @property
    def duration(self) -> float | None:
        """Get session duration if finished."""
        if self.endTime:
            return self.endTime - self.startTime
        return None

    @property
    def totalAnalyses(self) -> int:
        """Get total number of analyses in session."""
        return len(self.results)
