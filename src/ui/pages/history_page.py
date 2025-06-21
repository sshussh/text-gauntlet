"""History page for Text Gauntlet."""

import threading
from datetime import datetime

import customtkinter as ctk

from services.data_service import DataService
from ui.components.base import ActionButton, Card, ScrollableFrame, StatusIndicator
from ui.components.theme_manager import themeManager
from utils.logger import logger


class HistoryPage(ctk.CTkFrame):
    """Page for viewing analysis history."""

    def __init__(self, parent: ctk.CTk, dataService: DataService, **kwargs) -> None:
        """Initialize the history page.

        Args:
            parent: Parent widget
            dataService: Data service instance
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)

        self.dataService = dataService
        self.historyData: list[dict] = []
        self._is_destroyed = False

        # UI Components
        self.controlsCard: Card | None = None
        self.refreshButton: ActionButton | None = None
        self.clearButton: ActionButton | None = None
        self.historyFrame: ctk.CTkFrame | None = None
        self.statusIndicator: StatusIndicator | None = None

        self._setupPage()

    def _setupPage(self) -> None:
        """Set up the history page layout."""
        # Configure grid
        self.grid_rowconfigure(2, weight=1)  # History list area
        self.grid_columnconfigure(0, weight=1)

        # Page title
        titleLabel = ctk.CTkLabel(
            self,
            text="Analysis History",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("accent"),
        )
        titleLabel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Controls section
        self._createControlsSection()

        # History list section
        self._createHistorySection()

        # Status indicator
        self.statusIndicator = StatusIndicator(self)
        self.statusIndicator.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Defer history loading to after the widget is fully initialized
        self.after(100, self._refreshHistory)

        logger.info("History page setup completed")

    def _createControlsSection(self) -> None:
        """Create the controls section."""
        self.controlsCard = Card(self, title="History Controls")
        self.controlsCard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Controls frame
        controlsFrame = ctk.CTkFrame(
            self.controlsCard.contentFrame, fg_color="transparent"
        )
        controlsFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        controlsFrame.grid_columnconfigure(0, weight=1)
        controlsFrame.grid_columnconfigure(1, weight=1)

        # Refresh button
        self.refreshButton = ActionButton(
            controlsFrame,
            text="Refresh History",
            command=self._refreshHistory,
            style="primary",
        )
        self.refreshButton.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")

        # Clear button
        self.clearButton = ActionButton(
            controlsFrame,
            text="Clear History",
            command=self._clearHistory,
            style="danger",
        )
        self.clearButton.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="ew")

    def _createHistorySection(self) -> None:
        """Create the history list section."""
        # History frame
        scrollableFrameComponent = ScrollableFrame(
            self, height=400, fg_color=themeManager.getColor("surface")
        )
        scrollableFrameComponent.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.historyFrame = scrollableFrameComponent.contentFrame
        self.historyFrame.grid_columnconfigure(0, weight=1)

    def _safe_after(self, callback):
        """Safely schedule a callback, checking if widget still exists."""
        try:
            if not self._is_destroyed and self.winfo_exists():
                self.after(0, callback)
        except Exception as e:
            logger.debug(f"Failed to schedule callback: {e}")

    def _refreshHistory(self) -> None:
        """Refresh the history data."""
        self.refreshButton.setLoading(True) if self.refreshButton else None
        if self.statusIndicator:
            self.statusIndicator.showInfo("Loading history...")

        def loadHistoryTask() -> None:
            try:
                # Load history from data service
                history = self.dataService.getAnalysisHistory()

                # Update UI on main thread
                self._safe_after(lambda: self._displayHistory(history))

            except Exception as e:
                logger.error(f"Failed to load history: {e}")
                error_msg = str(e)
                self._safe_after(
                    lambda: self.statusIndicator
                    and self.statusIndicator.showError(
                        f"Failed to load history: {error_msg}"
                    )
                )
            finally:
                self._safe_after(
                    lambda: (
                        self.refreshButton.setLoading(False)
                        if self.refreshButton
                        else None
                    )
                )

        threading.Thread(target=loadHistoryTask, daemon=True).start()

    def _displayHistory(self, history: list[dict]) -> None:
        """Display history data."""
        if self._is_destroyed:
            return

        self.historyData = history

        # Clear previous history
        for widget in self.historyFrame.winfo_children():
            widget.destroy()

        if not history:
            # Empty state
            emptyLabel = ctk.CTkLabel(
                self.historyFrame,
                text="No analysis history found\n\nAnalyze some text to see your history here!",
                font=ctk.CTkFont(size=14),
                text_color=themeManager.getColor("text_secondary"),
                justify="center",
            )
            emptyLabel.grid(row=0, column=0, padx=20, pady=50, sticky="ew")

            if self.statusIndicator:
                self.statusIndicator.showInfo("No history entries found")
            return

        # Create history items
        for i, entry in enumerate(history):
            self._createHistoryItem(entry, i)

        if self.statusIndicator:
            self.statusIndicator.showSuccess(f"Loaded {len(history)} history entries")

    def _createHistoryItem(self, entry: dict, index: int) -> None:
        """Create a history item."""
        # History card
        historyCard = ctk.CTkFrame(
            self.historyFrame,
            fg_color=themeManager.getColor("card_background"),
            corner_radius=8,
        )
        historyCard.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        historyCard.grid_columnconfigure(0, weight=1)

        # Header frame
        headerFrame = ctk.CTkFrame(historyCard, fg_color="transparent")
        headerFrame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        headerFrame.grid_columnconfigure(0, weight=1)

        # Analysis type and timestamp
        typeText = self._getAnalysisTypeDisplay(entry.get("input_source", "Unknown"))
        timestamp = entry.get("timestamp", "")
        if timestamp:
            try:
                # Parse timestamp and format nicely
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                timeStr = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                timeStr = timestamp
        else:
            timeStr = "Unknown time"

        headerLabel = ctk.CTkLabel(
            headerFrame,
            text=f"{typeText} • {timeStr}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        headerLabel.grid(row=0, column=0, sticky="ew")

        # Content preview
        contentFrame = ctk.CTkFrame(historyCard, fg_color="transparent")
        contentFrame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        contentFrame.grid_columnconfigure(0, weight=1)

        # Input text preview - customize based on analysis type
        inputText = entry.get("input_text", "")
        metadata = entry.get("input_metadata", {})
        analysisType = entry.get("input_source", "")

        if inputText or metadata:
            previewText = self._getDisplayText(analysisType, inputText, metadata)
            inputLabel = ctk.CTkLabel(
                contentFrame,
                text=previewText,
                font=ctk.CTkFont(size=11),
                text_color=themeManager.getColor("text_secondary"),
                anchor="w",
                wraplength=500,
            )
            inputLabel.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Results frame
        resultsFrame = ctk.CTkFrame(historyCard, fg_color="transparent")
        resultsFrame.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")
        resultsFrame.grid_columnconfigure(1, weight=1)

        # Primary sentiment
        primarySentiment = entry.get("primary_sentiment", "Unknown")
        sentimentLabel = ctk.CTkLabel(
            resultsFrame, text="Sentiment:", font=ctk.CTkFont(size=11)
        )
        sentimentLabel.grid(row=0, column=0, sticky="w", padx=(0, 10))

        sentimentColor = self._getSentimentColor(primarySentiment)
        sentimentValueLabel = ctk.CTkLabel(
            resultsFrame,
            text=primarySentiment.title(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=sentimentColor,
        )
        sentimentValueLabel.grid(row=0, column=1, sticky="w")

        # Confidence
        confidence = entry.get("confidence", 0)
        confidenceLabel = ctk.CTkLabel(
            resultsFrame, text="Confidence:", font=ctk.CTkFont(size=11)
        )
        confidenceLabel.grid(row=0, column=2, sticky="w", padx=(20, 10))

        confidenceValueLabel = ctk.CTkLabel(
            resultsFrame,
            text=f"{confidence:.1%}",
            font=ctk.CTkFont(size=11),
            text_color=self._getConfidenceColor(confidence),
        )
        confidenceValueLabel.grid(row=0, column=3, sticky="w")

        # Processing time
        processingTime = entry.get("processing_time", 0)
        if processingTime > 0:
            timeLabel = ctk.CTkLabel(
                resultsFrame, text="Time:", font=ctk.CTkFont(size=11)
            )
            timeLabel.grid(row=0, column=4, sticky="w", padx=(20, 10))

            timeValueLabel = ctk.CTkLabel(
                resultsFrame, text=f"{processingTime:.2f}s", font=ctk.CTkFont(size=11)
            )
            timeValueLabel.grid(row=0, column=5, sticky="w")

    def _getDisplayText(self, analysisType: str, inputText: str, metadata: dict) -> str:
        """Get display text based on analysis type and metadata."""
        if analysisType == "direct":
            # For direct text, show the text content (truncated)
            return inputText[:100] + ("..." if len(inputText) > 100 else "")

        elif analysisType == "lyrics":
            # For lyrics, show artist and song name
            artist = metadata.get("artist", "Unknown Artist")
            title = metadata.get("title", "Unknown Song")
            return f"{artist} - {title}"

        elif analysisType in ["movie_reviews", "reviews"]:
            # For movies, show movie title
            title = metadata.get("title", "Unknown Movie")
            release_date = metadata.get("release_date", "")
            if release_date:
                try:
                    year = release_date.split("-")[0]
                    return f"{title} ({year})"
                except (IndexError, ValueError):
                    return f"{title}"
            return f"{title}"

        elif analysisType == "article":
            # For articles, show URL
            url = metadata.get("url", "Unknown URL")
            title = metadata.get("title", "")
            if title:
                return f"{title}\n{url}"
            return f"{url}"

        elif analysisType == "multiple_articles":
            # For multiple articles, show count and URLs
            return "Multiple Articles Analysis"

        else:
            # Fallback to text preview
            return inputText[:100] + ("..." if len(inputText) > 100 else "")

    def _getAnalysisTypeDisplay(self, analysisType: str) -> str:
        """Get display text for analysis type."""
        typeMap = {
            "direct": "Text Analyses",
            "lyrics": "Song Lyrics",
            "movie_reviews": "Movie Reviews",
            "reviews": "Movie Reviews",
            "article": "News Article",
            "multiple_articles": "Multiple Articles",
            "url": "URL Content",
        }
        return typeMap.get(analysisType, f"Unknown: {analysisType.title()}")

    def _clearHistory(self) -> None:
        """Clear analysis history with confirmation."""
        # Create confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Clear History")
        dialog.geometry("400x200")
        dialog.transient(self.winfo_toplevel())

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")

        # Wait for dialog to be visible before grabbing
        dialog.after(100, lambda: dialog.grab_set())

        # Dialog content
        contentFrame = ctk.CTkFrame(dialog, fg_color="transparent")
        contentFrame.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning icon and text
        warningLabel = ctk.CTkLabel(
            contentFrame,
            text="Warning: Clear Analysis History",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=themeManager.getColor("warning"),
        )
        warningLabel.pack(pady=(0, 10))

        messageLabel = ctk.CTkLabel(
            contentFrame,
            text="Are you sure you want to clear all analysis history?\n\nThis action cannot be undone.",
            font=ctk.CTkFont(size=12),
            justify="center",
        )
        messageLabel.pack(pady=(0, 20))

        # Buttons frame
        buttonsFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        buttonsFrame.pack(fill="x")
        buttonsFrame.grid_columnconfigure(0, weight=1)
        buttonsFrame.grid_columnconfigure(1, weight=1)

        # Cancel button
        cancelButton = ctk.CTkButton(
            buttonsFrame,
            text="Cancel",
            command=dialog.destroy,
            fg_color=themeManager.getColor("surface"),
            hover_color=themeManager.getColor("surface_hover"),
        )
        cancelButton.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Confirm button
        confirmButton = ctk.CTkButton(
            buttonsFrame,
            text="Clear History",
            command=lambda: self._confirmClearHistory(dialog),
            fg_color=themeManager.getColor("error"),
            hover_color=themeManager.getColor("error_hover"),
        )
        confirmButton.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _confirmClearHistory(self, dialog: ctk.CTkToplevel) -> None:
        """Confirm and execute history clearing."""
        dialog.destroy()

        if self.statusIndicator:
            self.statusIndicator.showInfo("Clearing history...")

        def clearTask() -> None:
            try:
                # Clear history using data service
                self.dataService.clearAnalysisHistory()

                # Refresh display on main thread
                self._safe_after(lambda: self._refreshHistory())
                self._safe_after(
                    lambda: self.statusIndicator
                    and self.statusIndicator.showSuccess("History cleared successfully")
                )

            except Exception as e:
                logger.error(f"Failed to clear history: {e}")
                error_msg = str(e)
                self._safe_after(
                    lambda: self.statusIndicator
                    and self.statusIndicator.showError(
                        f"Failed to clear history: {error_msg}"
                    )
                )

        threading.Thread(target=clearTask, daemon=True).start()

    def _getSentimentColor(self, sentiment: str) -> str:
        """Get color for sentiment."""
        sentiment = sentiment.lower()
        if sentiment in ["positive", "joy", "love", "optimism", "admiration"]:
            return themeManager.getColor("success")
        elif sentiment in [
            "negative",
            "anger",
            "sadness",
            "fear",
            "disgust",
            "pessimism",
        ]:
            return themeManager.getColor("error")
        elif sentiment in ["neutral"]:
            return themeManager.getColor("warning")
        else:
            return themeManager.getColor("text_primary")

    def _getConfidenceColor(self, confidence: float) -> str:
        """Get color for confidence level."""
        if confidence >= 0.8:
            return themeManager.getColor("success")
        elif confidence >= 0.6:
            return themeManager.getColor("warning")
        else:
            return themeManager.getColor("error")

    def reset(self) -> None:
        """Reset the page to initial state."""
        try:
            self._is_destroyed = True  # Mark as destroyed to prevent callbacks

            # Clear history display
            if self.historyFrame:
                try:
                    for widget in self.historyFrame.winfo_children():
                        try:
                            widget.destroy()
                        except Exception:
                            pass  # Widget may already be destroyed
                except Exception:
                    pass  # Frame may already be destroyed

            if self.statusIndicator:
                try:
                    self.statusIndicator.clear()
                except Exception:
                    pass  # Widget may already be destroyed

            logger.info("History page reset")

        except Exception as e:
            logger.warning(f"Error during history page reset: {e}")
            # Continue with cleanup even if some operations fail

    def refresh(self) -> None:
        """Refresh the history page."""
        self._refreshHistory()
