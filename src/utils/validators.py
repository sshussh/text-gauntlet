"""Input validation utilities for Text Gauntlet."""

import re
from urllib.parse import urlparse

from config.settings import settings
from utils.exceptions import ValidationError


class TextValidator:
    """Validator for text input operations."""

    @staticmethod
    def validateText(text: str, allowEmpty: bool = False) -> str:
        """
        Validate input text for sentiment analysis.

        Args:
            text: Input text to validate
            allowEmpty: Whether to allow empty text

        Returns:
            Cleaned and validated text

        Raises:
            ValidationError: If text is invalid
        """
        if not isinstance(text, str):
            raise ValidationError("Text must be a string", "text")

        # Clean whitespace
        cleanedText = text.strip()

        # Check if empty
        if not cleanedText and not allowEmpty:
            raise ValidationError("Text cannot be empty", "text")

        # Check length limits
        if len(cleanedText) > settings.model.maxTextLength:
            raise ValidationError(
                f"Text too long. Maximum {settings.model.maxTextLength} characters allowed",
                "text",
            )

        # Check for potentially harmful content (basic check)
        if TextValidator._containsHarmfulContent(cleanedText):
            raise ValidationError("Text contains potentially harmful content", "text")

        return cleanedText

    @staticmethod
    def _containsHarmfulContent(text: str) -> bool:
        """Check for basic harmful content patterns."""
        # This is a basic implementation - in production you'd want more sophisticated filtering
        harmfulPatterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"vbscript:",  # VBScript URLs
        ]

        for pattern in harmfulPatterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def validateArtistAndSong(artist: str, song: str) -> tuple[str, str]:
        """
        Validate artist and song names for lyrics search.

        Args:
            artist: Artist name
            song: Song name

        Returns:
            Tuple of cleaned artist and song names

        Raises:
            ValidationError: If names are invalid
        """
        # Validate artist
        if not isinstance(artist, str) or not artist.strip():
            raise ValidationError("Artist name cannot be empty", "artist")

        # Validate song
        if not isinstance(song, str) or not song.strip():
            raise ValidationError("Song name cannot be empty", "song")

        cleanedArtist = artist.strip()
        cleanedSong = song.strip()

        # Check length limits
        if len(cleanedArtist) > 100:
            raise ValidationError("Artist name too long (max 100 characters)", "artist")

        if len(cleanedSong) > 100:
            raise ValidationError("Song name too long (max 100 characters)", "song")

        # Check for valid characters (allow letters, numbers, spaces, and common punctuation)
        validPattern = re.compile(r"^[a-zA-Z0-9\s\-\'\.\,\&\(\)]+$")

        if not validPattern.match(cleanedArtist):
            raise ValidationError("Artist name contains invalid characters", "artist")

        if not validPattern.match(cleanedSong):
            raise ValidationError("Song name contains invalid characters", "song")

        return cleanedArtist, cleanedSong

    @staticmethod
    def validateMovieName(movieName: str) -> str:
        """
        Validate movie name for reviews search.

        Args:
            movieName: Movie name to validate

        Returns:
            Cleaned movie name

        Raises:
            ValidationError: If movie name is invalid
        """
        if not isinstance(movieName, str) or not movieName.strip():
            raise ValidationError("Movie name cannot be empty", "movieName")

        cleanedName = movieName.strip()

        # Check length limits
        if len(cleanedName) > 200:
            raise ValidationError(
                "Movie name too long (max 200 characters)", "movieName"
            )

        # Allow more flexible characters for movie names (including special characters)
        validPattern = re.compile(r"^[a-zA-Z0-9\s\-\'\"\.\,\&\(\)\:\;\!\?]+$")

        if not validPattern.match(cleanedName):
            raise ValidationError("Movie name contains invalid characters", "movieName")

        return cleanedName

    @staticmethod
    def validateUrl(url: str) -> str:
        """
        Validate URL for web scraping.

        Args:
            url: URL to validate

        Returns:
            Validated URL

        Raises:
            ValidationError: If URL is invalid
        """
        if not isinstance(url, str) or not url.strip():
            raise ValidationError("URL cannot be empty", "url")

        cleanedUrl = url.strip()

        # Parse URL
        try:
            parsed = urlparse(cleanedUrl)
        except Exception as e:
            raise ValidationError("Invalid URL format", "url") from e

        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            raise ValidationError("URL must use HTTP or HTTPS protocol", "url")

        # Check if hostname exists
        if not parsed.netloc:
            raise ValidationError("URL must have a valid hostname", "url")

        # Basic length check
        if len(cleanedUrl) > 2000:
            raise ValidationError("URL too long (max 2000 characters)", "url")

        return cleanedUrl


class ConfigValidator:
    """Validator for configuration settings."""

    @staticmethod
    def validateTheme(themeName: str) -> str:
        """
        Validate theme name.

        Args:
            themeName: Theme name to validate

        Returns:
            Validated theme name

        Raises:
            ValidationError: If theme name is invalid
        """
        validThemes = ["Oblivion", "blue", "green", "dark-blue"]

        if themeName not in validThemes:
            raise ValidationError(
                f"Invalid theme. Must be one of: {', '.join(validThemes)}", "theme"
            )

        return themeName

    @staticmethod
    def validateScaling(scaling: float) -> float:
        """
        Validate widget scaling value.

        Args:
            scaling: Scaling value to validate

        Returns:
            Validated scaling value

        Raises:
            ValidationError: If scaling is invalid
        """
        if not isinstance(scaling, int | float):
            raise ValidationError("Scaling must be a number", "scaling")

        if not 0.5 <= scaling <= 3.0:
            raise ValidationError("Scaling must be between 0.5 and 3.0", "scaling")

        return float(scaling)
