"""Modern sentiment analysis core using transformer models."""

import time

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)

from core.models import (
    SentimentResult,
    SentimentScore,
    TextInput,
)
from core.text_processor import ProcessedText, TextProcessor
from utils.exceptions import AnalysisError
from utils.logger import logger


class SentimentAnalyzer:
    """Advanced sentiment analyzer using modern transformer models."""

    def __init__(
        self, modelName: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    ) -> None:
        """
        Initialize sentiment analyzer with specified model.

        Args:
            modelName: HuggingFace model name for sentiment analysis
        """
        self.modelName = modelName
        self.pipeline: pipeline | None = None
        self.tokenizer: AutoTokenizer | None = None
        self.model: AutoModelForSequenceClassification | None = None
        self.textProcessor = TextProcessor()
        self.isLoaded = False

        logger.info(f"Sentiment analyzer initialized with model: {modelName}")

    def loadModel(self) -> None:
        """Load the sentiment analysis model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.modelName}")

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.modelName)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.modelName
            )

            # Create pipeline for easier inference
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                top_k=None,  # Get all labels
                device=0 if torch.cuda.is_available() else -1,
            )

            self.isLoaded = True
            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise AnalysisError(f"Model loading failed: {e}", "model_loading") from e

    def analyzeText(self, textInput: TextInput) -> SentimentResult:
        """
        Analyze sentiment of input text.

        Args:
            textInput: Text input to analyze

        Returns:
            SentimentResult with detailed analysis

        Raises:
            AnalysisError: If analysis fails
        """
        startTime = time.time()

        try:
            # Ensure model is loaded
            if not self.isLoaded:
                self.loadModel()

            # Process text
            processedText = self.textProcessor.processText(textInput)

            # Analyze sentiment
            scores = self._analyzeSentiment(processedText)

            # Determine primary sentiment and confidence
            primarySentiment, confidence = self._determinePrimarySentiment(scores)

            processingTime = time.time() - startTime

            result = SentimentResult(
                text=textInput.content,
                scores=scores,
                primarySentiment=primarySentiment,
                confidence=confidence,
                processingTime=processingTime,
                timestamp=time.time(),
            )

            logger.debug(
                f"Analysis complete: {primarySentiment} ({confidence:.3f}) in {processingTime:.3f}s"
            )
            return result

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise AnalysisError(f"Sentiment analysis failed: {e}", "analysis") from e

    def batchAnalyze(self, textInputs: list[TextInput]) -> list[SentimentResult]:
        """
        Analyze multiple texts efficiently.

        Args:
            textInputs: List of text inputs to analyze

        Returns:
            List of sentiment results
        """
        results = []

        logger.info(f"Starting batch analysis of {len(textInputs)} texts")

        for i, textInput in enumerate(textInputs):
            try:
                result = self.analyzeText(textInput)
                results.append(result)

                if (i + 1) % 10 == 0:
                    logger.debug(f"Processed {i + 1}/{len(textInputs)} texts")

            except Exception as e:
                logger.warning(f"Failed to analyze text {i + 1}: {e}")
                # Create a minimal result for failed analysis
                results.append(self._createFailedResult(textInput, str(e)))

        logger.info(f"Batch analysis complete: {len(results)} results")
        return results

    def _analyzeSentiment(self, processedText: ProcessedText) -> list[SentimentScore]:
        """
        Perform sentiment analysis on processed text.

        Args:
            processedText: Preprocessed text data

        Returns:
            List of sentiment scores
        """
        # Use processed text for analysis
        text = processedText.processedText

        # Handle empty text
        if not text.strip():
            return [SentimentScore(label="neutral", score=1.0)]

        # Truncate text if too long (model limit)
        maxLength = 512
        if len(text) > maxLength:
            text = text[:maxLength]
            logger.debug("Text truncated to fit model limit")

        # Get predictions from pipeline
        predictions = self.pipeline(text)[0]  # Get first (and only) result

        # Convert to SentimentScore objects
        scores = []
        for pred in predictions:
            # Map model labels to our format
            label = self._mapLabel(pred["label"])
            score = float(pred["score"])
            scores.append(SentimentScore(label=label, score=score))

        return scores

    def _mapLabel(self, modelLabel: str) -> str:
        """
        Map model-specific labels to standardized labels.

        Args:
            modelLabel: Label from the model

        Returns:
            Standardized label
        """
        labelMapping = {
            "LABEL_0": "negative",
            "LABEL_1": "neutral",
            "LABEL_2": "positive",
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral",
            "POSITIVE": "positive",
        }

        return labelMapping.get(modelLabel.upper(), modelLabel.lower())

    def _determinePrimarySentiment(
        self, scores: list[SentimentScore]
    ) -> tuple[str, float]:
        """
        Determine primary sentiment and confidence score.

        Args:
            scores: List of sentiment scores

        Returns:
            Tuple of (primary_sentiment, confidence)
        """
        if not scores:
            return "neutral", 0.0

        # Find highest scoring sentiment
        topScore = max(scores, key=lambda x: x.score)

        # Calculate confidence based on score distribution
        confidence = self._calculateConfidence(scores, topScore)

        return topScore.label, confidence

    def _calculateConfidence(
        self, scores: list[SentimentScore], topScore: SentimentScore
    ) -> float:
        """
        Calculate confidence score based on prediction distribution.

        Args:
            scores: All sentiment scores
            topScore: Highest scoring sentiment

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if len(scores) <= 1:
            return topScore.score

        # Sort scores in descending order
        sortedScores = sorted(scores, key=lambda x: x.score, reverse=True)

        # Calculate confidence as difference between top two scores
        topScore = sortedScores[0].score
        secondScore = sortedScores[1].score if len(sortedScores) > 1 else 0.0

        # Higher difference = higher confidence
        confidence = topScore - secondScore

        # Ensure confidence is reasonable (not too low)
        return max(confidence, topScore * 0.7)

    def _createFailedResult(self, textInput: TextInput, error: str) -> SentimentResult:
        """
        Create a result object for failed analysis.

        Args:
            textInput: Original text input
            error: Error message

        Returns:
            SentimentResult with neutral sentiment and low confidence
        """
        return SentimentResult(
            text=textInput.content,
            scores=[SentimentScore(label="neutral", score=0.5)],
            primarySentiment="neutral",
            confidence=0.0,
            processingTime=0.0,
            timestamp=time.time(),
        )

    def getModelInfo(self) -> dict[str, str]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "modelName": self.modelName,
            "isLoaded": str(self.isLoaded),
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "torchVersion": torch.__version__,
        }

    def clearModel(self) -> None:
        """Clear model from memory to free resources."""
        if self.isLoaded:
            self.pipeline = None
            self.tokenizer = None
            self.model = None
            self.isLoaded = False

            # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info("Model cleared from memory")
