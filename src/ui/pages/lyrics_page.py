"""Song lyrics analysis page."""

import threading
from typing import Any

import customtkinter as ctk

from services.application_services import services
from services.lyrics_service import LyricsService
from ui.components.base import (
    ActionButton,
    Card,
    InputField,
    ScrollableFrame,
    StatusIndicator,
)
from ui.components.navigation import PageFrame
from ui.components.theme_manager import themeManager
from utils.helpers import UIHelper
from utils.logger import logger


class LyricsPage(PageFrame):
    """Page for song lyrics sentiment analysis."""

    def __init__(self, parent: ctk.CTk, lyricsService: LyricsService, **kwargs) -> None:
        """Initialize the lyrics analysis page.

        Args:
            parent: Parent widget
            lyricsService: Lyrics service instance
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        # Services
        self.lyricsService = lyricsService

        # UI Components
        self.searchCard: Card | None = None
        self.artistInput: InputField | None = None
        self.songInput: InputField | None = None
        self.searchButton: ActionButton | None = None
        self.songInfoCard: Card | None = None
        self.resultsCard: Card | None = None
        self.statusIndicator: StatusIndicator | None = None

        # Song info labels
        self.songTitleLabel: ctk.CTkLabel | None = None
        self.artistLabel: ctk.CTkLabel | None = None
        self.wordCountLabel: ctk.CTkLabel | None = None
        self.lyricsPreview: ctk.CTkTextbox | None = None

        # Result labels
        self.primaryResultLabel: ctk.CTkLabel | None = None
        self.confidenceLabel: ctk.CTkLabel | None = None
        self.scoresLabel: ctk.CTkLabel | None = None
        self.timingLabel: ctk.CTkLabel | None = None

    def _setupPage(self) -> None:
        """Set up the lyrics analysis page."""
        # Configure grid
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Page header
        self._createHeader()

        # Search section
        self._createSearchSection()

        # Results section
        self._createResultsSection()

        logger.info("Lyrics analysis page initialized")

    def _createHeader(self) -> None:
        """Create the page header."""
        headerFrame = ctk.CTkFrame(self, fg_color="transparent")
        headerFrame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        headerFrame.grid_columnconfigure(0, weight=1)

        # Page title
        titleLabel = ctk.CTkLabel(
            headerFrame,
            text="Song Lyrics Analysis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("text_primary"),
        )
        titleLabel.grid(row=0, column=0, sticky="w")

        # Page description
        descLabel = ctk.CTkLabel(
            headerFrame,
            text="Search for songs and analyze the sentiment of their lyrics",
            font=ctk.CTkFont(size=14),
            text_color=themeManager.getColor("text_secondary"),
        )
        descLabel.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # API status warning
        if not self.lyricsService or not self.lyricsService.apiKey:
            warningLabel = ctk.CTkLabel(
                headerFrame,
                text="Warning: Genius API key not configured - limited functionality",
                font=ctk.CTkFont(size=12),
                text_color=themeManager.getColor("error"),
            )
            warningLabel.grid(row=2, column=0, sticky="w", pady=(5, 0))

    def _createSearchSection(self) -> None:
        """Create the song search section."""
        self.searchCard = Card(
            self,
            title="Song Search",
        )
        self.searchCard.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Input grid
        inputFrame = ctk.CTkFrame(self.searchCard.contentFrame, fg_color="transparent")
        inputFrame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        inputFrame.grid_columnconfigure(0, weight=1)
        inputFrame.grid_columnconfigure(1, weight=1)

        # Artist input
        ctk.CTkLabel(inputFrame, text="Artist:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        self.artistInput = InputField(inputFrame, placeholder="Enter artist name...")
        self.artistInput.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

        # Song input
        ctk.CTkLabel(
            inputFrame, text="Song Title:", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))

        self.songInput = InputField(inputFrame, placeholder="Enter song title...")
        self.songInput.grid(row=1, column=1, sticky="ew", pady=(0, 10))

        # Button frame
        buttonFrame = ctk.CTkFrame(self.searchCard.contentFrame, fg_color="transparent")
        buttonFrame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        buttonFrame.grid_columnconfigure(0, weight=1)

        # Search button
        self.searchButton = ActionButton(
            buttonFrame, text="Search & Analyze", command=self._onSearchClick
        )
        self.searchButton.grid(row=0, column=0, sticky="e")

        # Status indicator
        self.statusIndicator = StatusIndicator(buttonFrame)
        self.statusIndicator.grid(row=0, column=1, padx=(10, 0))

    def _createResultsSection(self) -> None:
        """Create the results display section."""
        # Create a scrollable results area
        scrollableFrame = ScrollableFrame(self)
        scrollableFrame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        resultsFrame = scrollableFrame.contentFrame
        resultsFrame.grid_columnconfigure(0, weight=1)

        # Song info card
        self.songInfoCard = Card(
            resultsFrame,
            title="Song Information",
        )
        self.songInfoCard.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self._createSongInfoSection()

        # Analysis results card
        self.resultsCard = Card(
            resultsFrame,
            title="Lyrics Analysis",
        )
        self.resultsCard.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self._createAnalysisResultsSection()

    def _createSongInfoSection(self) -> None:
        """Create the song information display."""
        infoFrame = ctk.CTkFrame(self.songInfoCard.contentFrame, fg_color="transparent")
        infoFrame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        infoFrame.grid_columnconfigure(1, weight=1)

        # Song title
        ctk.CTkLabel(infoFrame, text="Song:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        self.songTitleLabel = ctk.CTkLabel(
            infoFrame,
            text="No song selected",
            text_color=themeManager.getColor("text_secondary"),
        )
        self.songTitleLabel.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))

        # Artist
        ctk.CTkLabel(infoFrame, text="Artist:", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )

        self.artistLabel = ctk.CTkLabel(
            infoFrame,
            text="No artist selected",
            text_color=themeManager.getColor("text_secondary"),
        )
        self.artistLabel.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 5))

        # Word count
        ctk.CTkLabel(
            infoFrame, text="Word Count:", font=ctk.CTkFont(weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=(0, 10))

        self.wordCountLabel = ctk.CTkLabel(
            infoFrame, text="N/A", text_color=themeManager.getColor("text_secondary")
        )
        self.wordCountLabel.grid(
            row=2, column=1, sticky="w", padx=(10, 0), pady=(0, 10)
        )

        # Lyrics preview
        ctk.CTkLabel(
            infoFrame, text="Lyrics Preview:", font=ctk.CTkFont(weight="bold")
        ).grid(row=3, column=0, sticky="nw", pady=(0, 5))

        self.lyricsPreview = ctk.CTkTextbox(
            infoFrame, height=80, wrap="word", state="disabled"
        )
        self.lyricsPreview.grid(row=3, column=1, sticky="ew", padx=(10, 0))

    def _createAnalysisResultsSection(self) -> None:
        """Create the analysis results display."""
        resultsFrame = ctk.CTkFrame(
            self.resultsCard.contentFrame, fg_color="transparent"
        )
        resultsFrame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        resultsFrame.grid_columnconfigure(1, weight=1)

        # Primary result
        ctk.CTkLabel(
            resultsFrame, text="Primary Sentiment:", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.primaryResultLabel = ctk.CTkLabel(
            resultsFrame,
            text="No analysis yet",
            text_color=themeManager.getColor("text_secondary"),
        )
        self.primaryResultLabel.grid(
            row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 10)
        )

        # Confidence score
        ctk.CTkLabel(
            resultsFrame, text="Confidence:", font=ctk.CTkFont(weight="bold")
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        self.confidenceLabel = ctk.CTkLabel(
            resultsFrame, text="N/A", text_color=themeManager.getColor("text_secondary")
        )
        self.confidenceLabel.grid(
            row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 10)
        )

        # Detailed scores
        ctk.CTkLabel(
            resultsFrame, text="Detailed Scores:", font=ctk.CTkFont(weight="bold")
        ).grid(row=2, column=0, sticky="nw", pady=(0, 10))

        self.scoresLabel = ctk.CTkLabel(
            resultsFrame,
            text="No scores available",
            text_color=themeManager.getColor("text_secondary"),
            justify="left",
        )
        self.scoresLabel.grid(row=2, column=1, sticky="nw", padx=(10, 0), pady=(0, 10))

        # Processing time
        ctk.CTkLabel(
            resultsFrame, text="Processing Time:", font=ctk.CTkFont(weight="bold")
        ).grid(row=3, column=0, sticky="w")

        self.timingLabel = ctk.CTkLabel(
            resultsFrame, text="N/A", text_color=themeManager.getColor("text_secondary")
        )
        self.timingLabel.grid(row=3, column=1, sticky="w", padx=(10, 0))

    def _onSearchClick(self) -> None:
        """Handle search button click."""
        artist = self.artistInput.getText().strip()
        song = self.songInput.getText().strip()

        if not artist and not song:
            self.statusIndicator.setStatus(
                "error", "Please enter artist and/or song title"
            )
            return

        if not self.lyricsService or not self.lyricsService.apiKey:
            self.statusIndicator.setStatus("error", "Genius API key not configured")
            return

        # Disable button during search
        self.searchButton.setEnabled(False)
        self.statusIndicator.setStatus("loading", "Searching for song...")

        # Run search in background thread
        thread = threading.Thread(target=self._performSearch, args=(artist, song))
        thread.daemon = True
        thread.start()

    def _performSearch(self, artist: str, song: str) -> None:
        """Perform song search and analysis in background thread.

        Args:
            artist: Artist name
            song: Song title
        """
        try:
            # Search and analyze lyrics
            result = self.lyricsService.analyzeLyrics(artist, song)

            # Perform sentiment analysis with the complete TextInput object
            textInput = result["text_input"]
            analysisResult = services.analyzeText(textInput, saveToHistory=True)

            # Combine results
            combined_result = {**result, "analysis": analysisResult}

            # Update UI in main thread
            self.after(0, self._onSearchComplete, combined_result)

        except Exception as e:
            logger.error(f"Lyrics search failed: {e}")
            self.after(0, self._onSearchError, str(e))

    def _onSearchComplete(self, result: dict[str, Any]) -> None:
        """Handle successful search completion.

        Args:
            result: Combined search and analysis result
        """
        try:
            # Update song info
            song_info = result["song_info"]
            self.songTitleLabel.configure(
                text=song_info["title"],
                text_color=themeManager.getColor("text_primary"),
            )

            self.artistLabel.configure(
                text=song_info["artist"],
                text_color=themeManager.getColor("text_primary"),
            )

            self.wordCountLabel.configure(
                text=str(result["word_count"]),
                text_color=themeManager.getColor("text_primary"),
            )

            # Update lyrics preview
            lyrics = result["lyrics"]
            preview = lyrics[:200] + "..." if len(lyrics) > 200 else lyrics

            self.lyricsPreview.configure(state="normal")
            self.lyricsPreview.delete("1.0", "end")
            self.lyricsPreview.insert("1.0", preview)
            self.lyricsPreview.configure(state="disabled")

            # Update analysis results
            analysis = result["analysis"]
            sentiment = analysis["primary_sentiment"]
            confidence = analysis["confidence"]

            # Get sentiment color
            sentimentColor = UIHelper.getSentimentColor(sentiment)

            self.primaryResultLabel.configure(
                text=sentiment.title(), text_color=sentimentColor
            )

            # Update confidence
            self.confidenceLabel.configure(
                text=f"{confidence:.1%}",
                text_color=UIHelper.getConfidenceColor(confidence),
            )

            # Update detailed scores
            scores = analysis.get("scores", [])
            if scores:
                scoresText = "\n".join(
                    [
                        f"{score['label'].title()}: {score['score']:.1%}"
                        for score in scores[:5]  # Show top 5 scores
                    ]
                )
            else:
                scoresText = "No detailed scores available"

            self.scoresLabel.configure(text=scoresText)

            # Update processing time
            processingTime = analysis.get("processing_time", 0)
            self.timingLabel.configure(text=f"{processingTime:.2f} seconds")

            # Update status
            self.statusIndicator.setStatus("success", "Lyrics analyzed successfully")

        except Exception as e:
            logger.error(f"Failed to update UI with results: {e}")
            self.statusIndicator.setStatus("error", f"Failed to display results: {e}")

        finally:
            # Re-enable button
            self.searchButton.setEnabled(True)

    def _onSearchError(self, error: str) -> None:
        """Handle search error.

        Args:
            error: Error message
        """
        self.statusIndicator.setStatus("error", f"Search failed: {error}")
        self.searchButton.setEnabled(True)

    def onShow(self) -> None:
        """Called when the page is shown."""
        super().onShow()
        # Focus on artist input when page is shown
        if self.artistInput:
            self.artistInput.focus()

    def clearInputs(self) -> None:
        """Clear the search inputs."""
        if self.artistInput:
            self.artistInput.clear()
        if self.songInput:
            self.songInput.clear()

    def clearResults(self) -> None:
        """Clear the search and analysis results."""
        # Clear song info
        if self.songTitleLabel:
            self.songTitleLabel.configure(
                text="No song selected",
                text_color=themeManager.getColor("text_secondary"),
            )

        if self.artistLabel:
            self.artistLabel.configure(
                text="No artist selected",
                text_color=themeManager.getColor("text_secondary"),
            )

        if self.wordCountLabel:
            self.wordCountLabel.configure(
                text="N/A", text_color=themeManager.getColor("text_secondary")
            )

        if self.lyricsPreview:
            self.lyricsPreview.configure(state="normal")
            self.lyricsPreview.delete("1.0", "end")
            self.lyricsPreview.configure(state="disabled")

        # Clear analysis results
        if self.primaryResultLabel:
            self.primaryResultLabel.configure(
                text="No analysis yet",
                text_color=themeManager.getColor("text_secondary"),
            )

        if self.confidenceLabel:
            self.confidenceLabel.configure(
                text="N/A", text_color=themeManager.getColor("text_secondary")
            )

        if self.scoresLabel:
            self.scoresLabel.configure(
                text="No scores available",
                text_color=themeManager.getColor("text_secondary"),
            )

        if self.timingLabel:
            self.timingLabel.configure(
                text="N/A", text_color=themeManager.getColor("text_secondary")
            )

        if self.statusIndicator:
            self.statusIndicator.clear()
