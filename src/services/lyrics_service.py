"""Lyrics analysis service using Genius API."""

import re
from typing import Any

import lyricsgenius
import requests

from config.settings import settings
from core.models import TextInput
from utils.exceptions import ApiError, ValidationError
from utils.logger import logger


class LyricsService:
    """Service for fetching and analyzing song lyrics."""

    def __init__(self, apiKey: str | None = None) -> None:
        """Initialize the lyrics service.

        Args:
            apiKey: Genius API key. If None, will try to get from settings.
        """
        self.apiKey = apiKey or settings.api.geniusApiKey
        self.baseUrl = "https://api.genius.com"
        self.headers = {
            "Authorization": f"Bearer {self.apiKey}" if self.apiKey else "",
            "User-Agent": "TextGauntlet/2.0.0",
        }

        # Initialize LyricsGenius client for lyrics extraction
        if self.apiKey:
            self.genius = lyricsgenius.Genius(
                self.apiKey,
                verbose=False,  # Reduce logging
                remove_section_headers=True,  # Clean up lyrics format
                skip_non_songs=True,  # Skip non-song results
                excluded_terms=[
                    "(Remix)",
                    "(Live)",
                    "(Acoustic)",
                    "(Demo)",
                ],  # Skip remixes by default
                timeout=15,  # Increase timeout for better reliability
            )
            # Configure additional cleaning options
            self.genius.response_format = "plain"  # Get plain text instead of formatted
        else:
            self.genius = None
            logger.warning(
                "Genius API key not configured - lyrics service will be limited"
            )

    def searchSong(self, query: str) -> list[dict[str, Any]]:
        """Search for songs on Genius.

        Args:
            query: Search query (artist + song title)

        Returns:
            List of song search results

        Raises:
            ApiError: If the API request fails
            ValidationError: If the query is invalid
        """
        if not query or len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters")

        if not self.apiKey:
            raise ApiError("Genius API key not configured")

        try:
            response = requests.get(
                f"{self.baseUrl}/search",
                headers=self.headers,
                params={"q": query.strip()},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            hits = data.get("response", {}).get("hits", [])

            results = []
            for hit in hits[:10]:  # Limit to top 10 results
                song = hit.get("result", {})
                results.append(
                    {
                        "id": song.get("id"),
                        "title": song.get("title", "Unknown"),
                        "artist": song.get("primary_artist", {}).get("name", "Unknown"),
                        "url": song.get("url"),
                        "thumbnail": song.get("song_art_image_thumbnail_url"),
                    }
                )

            logger.info(f"Found {len(results)} songs for query: {query}")
            return results

        except requests.RequestException as e:
            logger.error(f"Genius API request failed: {e}")
            raise ApiError(f"Failed to search songs: {e}") from e

    def getLyrics(self, songId: int) -> str:
        """Get lyrics for a specific song using LyricsGenius.

        Args:
            songId: Genius song ID

        Returns:
            Song lyrics as plain text

        Raises:
            ApiError: If the API request fails or lyrics not found
        """
        if not self.genius:
            raise ApiError("Genius API key not configured")

        try:
            # First get song details from the API
            response = requests.get(
                f"{self.baseUrl}/songs/{songId}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            song = data.get("response", {}).get("song", {})

            if not song:
                raise ApiError("Song not found")

            title = song.get("title", "")
            artist = song.get("primary_artist", {}).get("name", "")

            if not title or not artist:
                raise ApiError("Song title or artist not found")

            # Use LyricsGenius to get lyrics
            logger.info(f"Fetching lyrics for '{title}' by {artist} using LyricsGenius")

            # Search for the song using LyricsGenius
            genius_song = self.genius.search_song(title, artist)

            if not genius_song:
                raise ApiError(f"Lyrics not found for '{title}' by {artist}")

            lyrics = genius_song.lyrics

            if not lyrics:
                raise ApiError("Lyrics content is empty")

            # Clean up the lyrics (LyricsGenius sometimes includes extra info)
            lyrics = self._cleanLyrics(lyrics)

            logger.info(
                f"Retrieved lyrics for song ID: {songId} ({len(lyrics)} characters)"
            )
            return lyrics

        except requests.RequestException as e:
            logger.error(f"Failed to get song details for {songId}: {e}")
            raise ApiError(f"Failed to retrieve song details: {e}") from e
        except Exception as e:
            logger.error(f"Failed to get lyrics for song {songId}: {e}")
            raise ApiError(f"Failed to retrieve lyrics: {e}") from e

    def _cleanLyrics(self, lyrics: str) -> str:
        """Clean up lyrics text from LyricsGenius.

        Args:
            lyrics: Raw lyrics text

        Returns:
            Cleaned lyrics text
        """
        if not lyrics:
            return ""

        # Remove common artifacts from LyricsGenius
        # Remove contributor counts and metadata at the beginning
        lyrics = re.sub(
            r"^\d+\s*Contributors?.*?(?=\n|\r)", "", lyrics, flags=re.MULTILINE
        )
        lyrics = re.sub(r"^.*?Translations.*?(?=\n|\r)", "", lyrics, flags=re.MULTILINE)
        lyrics = re.sub(
            r"^.*?Türkçe.*?Deutsch.*?(?=\n|\r)", "", lyrics, flags=re.MULTILINE
        )

        # Remove song descriptions and "Read More" content
        lyrics = re.sub(r"^.*?Read More.*?(?=\n|\r)", "", lyrics, flags=re.MULTILINE)
        lyrics = re.sub(r"^Written.*?(?=\n\n|\r\r)", "", lyrics, flags=re.DOTALL)
        lyrics = re.sub(
            r"^.*?entered the studio.*?(?=\n\n|\r\r)", "", lyrics, flags=re.DOTALL
        )

        # Remove song title and description that appears before actual lyrics
        lyrics = re.sub(
            r'^.*?Lyrics.*?".*?" is not only.*?(?=\n\n|\r\r)',
            "",
            lyrics,
            flags=re.DOTALL,
        )
        lyrics = re.sub(
            r'^.*?Lyrics.*?".*?" is .*?(?=\n\n|\r\r)', "", lyrics, flags=re.DOTALL
        )

        # Remove embed/sharing info that sometimes appears at the end
        lyrics = re.sub(r"\d+Embed$", "", lyrics)
        lyrics = re.sub(r"You might also like.*$", "", lyrics, flags=re.DOTALL)

        # Remove any remaining metadata patterns
        lyrics = re.sub(r"^.*?Contributors.*?$", "", lyrics, flags=re.MULTILINE)
        lyrics = re.sub(r"^.*?Translation.*?$", "", lyrics, flags=re.MULTILINE)

        # Remove lines that are clearly metadata (contain URLs, special formatting, etc.)
        lines = lyrics.split("\n")
        cleaned_lines = []
        in_actual_lyrics = False

        for line in lines:
            line = line.strip()

            # Skip empty lines at the beginning
            if not line and not in_actual_lyrics:
                continue

            # Skip lines that look like metadata or descriptions
            if (
                line
                and not re.match(r"^\d+\s*(Contributors?|Translations?)", line)
                and not re.match(r"^(Türkçe|Português|Deutsch|English)", line)
                and "genius.com" not in line.lower()
                and "embed" not in line.lower()
                and not line.endswith("Lyrics")
                and "Read More" not in line
                and not re.match(r"^Written.*", line)
                and not re.match(r"^.*entered the studio.*", line)
                and len(line) > 1
            ):  # Skip very short lines that might be artifacts
                # Check if this looks like actual song lyrics
                # Lyrics typically start with "I" or have common lyrical patterns
                if not in_actual_lyrics and (
                    line.startswith("I'm ")
                    or line.startswith("I ")
                    or line.startswith("You ")
                    or line.startswith("We ")
                    or line.startswith("She ")
                    or line.startswith("He ")
                    or line.startswith("They ")
                    or any(
                        word in line.lower()
                        for word in [
                            "feel",
                            "love",
                            "heart",
                            "time",
                            "know",
                            "want",
                            "need",
                        ]
                    )
                ):
                    in_actual_lyrics = True

                if in_actual_lyrics:
                    cleaned_lines.append(line)

        lyrics = "\n".join(cleaned_lines)

        # Remove extra whitespace and normalize
        lyrics = re.sub(r"\n\s*\n\s*\n", "\n\n", lyrics)  # Normalize paragraph breaks
        lyrics = lyrics.strip()

        return lyrics

    def analyzeLyrics(self, artist: str, songTitle: str) -> dict[str, Any]:
        """Search for a song and analyze its lyrics using LyricsGenius.

        Args:
            artist: Artist name
            songTitle: Song title

        Returns:
            Dictionary containing song info and analysis results

        Raises:
            ApiError: If song not found or lyrics unavailable
            ValidationError: If inputs are invalid
        """
        if not artist or not songTitle:
            raise ValidationError("Both artist and song title are required")

        if not self.genius:
            raise ApiError("Genius API key not configured")

        try:
            # Use LyricsGenius to search and get lyrics directly
            logger.info(f"Searching for '{songTitle}' by {artist}")

            genius_song = self.genius.search_song(songTitle, artist)

            if not genius_song:
                raise ApiError(f"No song found for '{songTitle}' by {artist}")

            lyrics = genius_song.lyrics

            if not lyrics:
                raise ApiError(f"Lyrics not available for '{songTitle}' by {artist}")

            # Clean up the lyrics
            lyrics = self._cleanLyrics(lyrics)

            # Create song info dict to match the original API format
            song_info = {
                "id": getattr(genius_song, "id", None),
                "title": genius_song.title,
                "artist": genius_song.artist,
                "url": getattr(genius_song, "url", ""),
                "thumbnail": getattr(genius_song, "song_art_image_url", ""),
            }

            # Create TextInput for analysis
            textInput = TextInput(
                content=lyrics,
                source="lyrics",
                metadata={
                    "song_id": song_info["id"],
                    "title": song_info["title"],
                    "artist": song_info["artist"],
                    "url": song_info["url"],
                    "thumbnail": song_info["thumbnail"],
                },
            )

            logger.info(f"Successfully analyzed lyrics for '{songTitle}' by {artist}")

            return {
                "song_info": song_info,
                "lyrics": lyrics,
                "text_input": textInput,
                "word_count": textInput.wordCount,
                "character_count": textInput.length,
            }

        except Exception as e:
            logger.error(f"Failed to analyze lyrics for {artist} - {songTitle}: {e}")
            raise ApiError(f"Failed to analyze song lyrics: {e}") from e

    def getSongRecommendations(
        self, artistName: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get popular songs by an artist.

        Args:
            artistName: Name of the artist
            limit: Maximum number of songs to return

        Returns:
            List of popular songs by the artist
        """
        if not self.apiKey:
            logger.warning("API key not available for recommendations")
            return []

        try:
            # Search for the artist first
            response = requests.get(
                f"{self.baseUrl}/search",
                headers=self.headers,
                params={"q": artistName},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            hits = data.get("response", {}).get("hits", [])

            # Filter for songs by this artist
            songs = []
            for hit in hits:
                song = hit.get("result", {})
                artist = song.get("primary_artist", {}).get("name", "")

                if artistName.lower() in artist.lower():
                    songs.append(
                        {
                            "id": song.get("id"),
                            "title": song.get("title", "Unknown"),
                            "artist": artist,
                            "url": song.get("url"),
                            "thumbnail": song.get("song_art_image_thumbnail_url"),
                        }
                    )

                    if len(songs) >= limit:
                        break

            return songs

        except Exception as e:
            logger.error(f"Failed to get recommendations for {artistName}: {e}")
            return []
