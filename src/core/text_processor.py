"""Advanced text processing pipeline for Text Gauntlet."""

import re
import unicodedata
from dataclasses import dataclass

from core.models import TextInput
from utils.exceptions import ValidationError
from utils.logger import logger


@dataclass
class ProcessedText:
    """Container for processed text with metadata."""

    originalText: str
    processedText: str
    detectedLanguage: str | None = None
    extractedEmojis: list[str] = None
    extractedUrls: list[str] = None
    extractedMentions: list[str] = None
    extractedHashtags: list[str] = None
    wordCount: int = 0
    characterCount: int = 0

    def __post_init__(self) -> None:
        """Initialize lists if None."""
        if self.extractedEmojis is None:
            self.extractedEmojis = []
        if self.extractedUrls is None:
            self.extractedUrls = []
        if self.extractedMentions is None:
            self.extractedMentions = []
        if self.extractedHashtags is None:
            self.extractedHashtags = []


class TextProcessor:
    """Advanced text processor for sentiment analysis preparation."""

    def __init__(self) -> None:
        """Initialize text processor."""
        self.emojiPattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002500-\U00002bef"  # chinese char
            "\U00002702-\U000027b0"
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2b55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+",
            flags=re.UNICODE,
        )

        self.urlPattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )

        self.mentionPattern = re.compile(r"@[A-Za-z0-9_]+")
        self.hashtagPattern = re.compile(r"#[A-Za-z0-9_]+")

        # Emoji to text mapping for sentiment context
        self.emojiToText = {
            "😀": "happy",
            "😃": "happy",
            "😄": "happy",
            "😁": "happy",
            "😆": "happy",
            "😅": "happy",
            "😂": "happy",
            "😍": "love",
            "😘": "love",
            "😗": "love",
            "😙": "love",
            "😚": "love",
            "😋": "happy",
            "😎": "cool",
            "😏": "smirk",
            "😐": "neutral",
            "😑": "neutral",
            "😶": "neutral",
            "😒": "annoyed",
            "😔": "sad",
            "😢": "sad",
            "😭": "sad",
            "😮": "surprised",
            "😲": "surprised",
            "😴": "tired",
            "😪": "tired",
            "😫": "tired",
            "😌": "sleepy",
            "😇": "peaceful",
            "😜": "playful",
            "😝": "playful",
            "🤪": "crazy",
            "😛": "playful",
            "🤤": "greedy",
            "🤭": "giggling",
            "🤫": "quiet",
            "🤥": "lying",
            "😶‍🌫️": "speechless",
            "😬": "grimace",
            "😟": "frowning",
            "😧": "anguished",
            "😦": "astonished",
            "🥺": "pleading",
            "😿": "crying",
            "😾": "crying",
            "😠": "angry",
            "😡": "angry",
            "🤬": "angry",
            "😤": "angry",
            "🤯": "mind_blown",
            "😳": "flushed",
            "🥵": "hot",
            "🥶": "cold",
            "😱": "scared",
            "😨": "fearful",
            "😰": "anxious",
            "😞": "downcast",
            "🤷": "shrugging",
            "🙅": "no_good",
            "🙆": "ok_gesture",
            "🙋": "raising_hand",
            "🤦": "facepalm",
            "💕": "love",
            "💖": "love",
            "💗": "love",
            "💓": "love",
            "💞": "love",
            "💘": "love",
            "💝": "love",
            "💟": "love",
            "❤": "love",
            "🧡": "love",
            "💛": "love",
            "💚": "love",
            "💙": "love",
            "💜": "love",
            "🖤": "love",
            "🤍": "love",
            "🤎": "love",
            "💔": "broken_heart",
            "❣": "love",
            "💯": "perfect",
            "💢": "angry",
            "💥": "explosive",
            "💫": "dizzy",
            "💦": "sweat",
            "💨": "dash",
            "🔥": "fire",
            "✨": "sparkles",
            "⭐": "star",
            "🌟": "star",
            "💀": "skull",
            "👻": "ghost",
            "👍": "thumbs_up",
            "👎": "thumbs_down",
            "👌": "ok",
            "✌": "peace",
            "🤞": "crossed_fingers",
            "🤟": "love_you",
            "🤘": "rock_on",
            "🤙": "call_me",
            "👈": "pointing",
            "👉": "pointing",
            "👆": "pointing",
            "👇": "pointing",
            "☝": "pointing",
            "✋": "hand",
            "🤚": "hand",
            "🖐": "hand",
            "🖖": "vulcan",
            "👋": "wave",
            "🤏": "pinch",
            "💪": "muscle",
            "🦾": "muscle",
            "🦿": "leg",
            "🦵": "leg",
            "🦶": "foot",
            "👂": "ear",
            "🦻": "ear",
            "👃": "nose",
            "🧠": "brain",
            "🦷": "tooth",
            "🦴": "bone",
            "👀": "eyes",
            "👁": "eye",
            "👅": "tongue",
        }

        logger.info("Text processor initialized with emoji and pattern recognition")

    def processText(self, textInput: TextInput) -> ProcessedText:
        """
        Process text input for sentiment analysis.

        Args:
            textInput: Input text with metadata

        Returns:
            ProcessedText with analysis-ready content

        Raises:
            ValidationError: If processing fails
        """
        try:
            originalText = textInput.content

            # Extract components before processing
            extractedEmojis = self._extractEmojis(originalText)
            extractedUrls = self._extractUrls(originalText)
            extractedMentions = self._extractMentions(originalText)
            extractedHashtags = self._extractHashtags(originalText)

            # Process text step by step
            processedText = self._normalizeUnicode(originalText)
            processedText = self._convertEmojisToText(processedText)
            processedText = self._removeUrls(processedText)
            processedText = self._processMentionsAndHashtags(processedText)
            processedText = self._cleanWhitespace(processedText)
            processedText = self._normalizeText(processedText)

            # Detect language (basic implementation)
            detectedLanguage = self._detectLanguage(processedText)

            # Calculate metrics
            wordCount = len(processedText.split())
            characterCount = len(processedText)

            result = ProcessedText(
                originalText=originalText,
                processedText=processedText,
                detectedLanguage=detectedLanguage,
                extractedEmojis=extractedEmojis,
                extractedUrls=extractedUrls,
                extractedMentions=extractedMentions,
                extractedHashtags=extractedHashtags,
                wordCount=wordCount,
                characterCount=characterCount,
            )

            logger.debug(
                f"Processed text: {wordCount} words, {characterCount} chars, lang: {detectedLanguage}"
            )
            return result

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            raise ValidationError(f"Text processing failed: {e}", "text") from e

    def _normalizeUnicode(self, text: str) -> str:
        """Normalize unicode characters."""
        return unicodedata.normalize("NFKD", text)

    def _extractEmojis(self, text: str) -> list[str]:
        """Extract emojis from text."""
        return self.emojiPattern.findall(text)

    def _extractUrls(self, text: str) -> list[str]:
        """Extract URLs from text."""
        return self.urlPattern.findall(text)

    def _extractMentions(self, text: str) -> list[str]:
        """Extract mentions (@username) from text."""
        return self.mentionPattern.findall(text)

    def _extractHashtags(self, text: str) -> list[str]:
        """Extract hashtags (#tag) from text."""
        return self.hashtagPattern.findall(text)

    def _convertEmojisToText(self, text: str) -> str:
        """Convert emojis to descriptive text for better sentiment analysis."""

        def emojiReplacer(match):
            emoji = match.group(0)
            return f" {self.emojiToText.get(emoji, 'emoji')} "

        return self.emojiPattern.sub(emojiReplacer, text)

    def _removeUrls(self, text: str) -> str:
        """Remove URLs from text."""
        return self.urlPattern.sub(" ", text)

    def _processMentionsAndHashtags(self, text: str) -> str:
        """Process mentions and hashtags."""
        # Convert hashtags to words (remove #)
        text = self.hashtagPattern.sub(lambda m: m.group(0)[1:], text)

        # Remove mentions
        text = self.mentionPattern.sub(" ", text)

        return text

    def _cleanWhitespace(self, text: str) -> str:
        """Clean and normalize whitespace."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalizeText(self, text: str) -> str:
        """Apply final text normalization."""
        # Convert to lowercase for consistency
        text = text.lower()

        # Remove excessive punctuation
        text = re.sub(r"[.]{2,}", ".", text)
        text = re.sub(r"[!]{2,}", "!", text)
        text = re.sub(r"[?]{2,}", "?", text)

        # Normalize contractions for better analysis
        contractions = {
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am",
        }

        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)

        return text

    def _detectLanguage(self, text: str) -> str:
        """Basic language detection (English-focused for now)."""
        # Simple heuristic - count English common words
        englishWords = {
            "the",
            "and",
            "is",
            "in",
            "to",
            "of",
            "a",
            "that",
            "it",
            "with",
            "for",
            "as",
            "was",
            "on",
            "are",
            "you",
            "this",
            "be",
            "at",
            "have",
            "not",
            "or",
            "from",
            "by",
            "they",
            "we",
            "can",
            "an",
            "your",
            "all",
            "but",
            "will",
            "one",
            "would",
            "there",
            "their",
        }

        words = text.lower().split()
        if not words:
            return "unknown"

        englishCount = sum(1 for word in words if word in englishWords)
        englishRatio = englishCount / len(words)

        if englishRatio > 0.3:
            return "en"
        else:
            return "unknown"

    def batchProcess(self, textInputs: list[TextInput]) -> list[ProcessedText]:
        """
        Process multiple texts efficiently.

        Args:
            textInputs: List of text inputs to process

        Returns:
            List of processed texts
        """
        results = []

        for textInput in textInputs:
            try:
                processed = self.processText(textInput)
                results.append(processed)
            except Exception as e:
                logger.warning(f"Failed to process text: {e}")
                # Create a minimal processed text for failed inputs
                results.append(
                    ProcessedText(
                        originalText=textInput.content,
                        processedText=textInput.content,
                        detectedLanguage="unknown",
                    )
                )

        logger.info(f"Batch processed {len(results)} texts")
        return results
