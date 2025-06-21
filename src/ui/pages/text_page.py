"""Text analysis page for direct text input."""

import threading
from typing import Any

import customtkinter as ctk

from services.application_services import services
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


class TextPage(PageFrame):
    """Page for direct text input sentiment analysis."""

    def __init__(self, parent: ctk.CTk, **kwargs) -> None:
        """Initialize the text analysis page.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        # UI Components
        self.inputCard: Card | None = None
        self.textInput: InputField | None = None
        self.analyzeButton: ActionButton | None = None
        self.resultsCard: Card | None = None
        self.statusIndicator: StatusIndicator | None = None

        # Result labels
        self.primaryResultLabel: ctk.CTkLabel | None = None
        self.confidenceLabel: ctk.CTkLabel | None = None
        self.scoresLabel: ctk.CTkLabel | None = None
        self.timingLabel: ctk.CTkLabel | None = None

    def _setupPage(self) -> None:
        """Set up the text analysis page."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Page header
        self._createHeader()

        # Main content area
        self._createContent()

        logger.info("Text analysis page initialized")

    def _createHeader(self) -> None:
        """Create the page header."""
        headerFrame = ctk.CTkFrame(self, fg_color="transparent")
        headerFrame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        headerFrame.grid_columnconfigure(0, weight=1)

        # Page title
        titleLabel = ctk.CTkLabel(
            headerFrame,
            text="Text Sentiment Analysis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("text_primary"),
        )
        titleLabel.grid(row=0, column=0, sticky="w")

        # Page description
        descLabel = ctk.CTkLabel(
            headerFrame,
            text="Enter any text to analyze its sentiment and emotional content",
            font=ctk.CTkFont(size=14),
            text_color=themeManager.getColor("text_secondary"),
        )
        descLabel.grid(row=1, column=0, sticky="w", pady=(5, 0))

    def _createContent(self) -> None:
        """Create the main content area."""
        # Create a scrollable content area
        scrollableFrame = ScrollableFrame(self)
        scrollableFrame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        contentFrame = scrollableFrame.contentFrame
        contentFrame.grid_columnconfigure(0, weight=1)

        # Input section
        self._createInputSection(contentFrame)

        # Results section
        self._createResultsSection(contentFrame)

    def _createInputSection(self, parent: ctk.CTkFrame) -> None:
        """Create the text input section.

        Args:
            parent: Parent frame
        """
        self.inputCard = Card(parent, title="Text Input")
        self.inputCard.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Text input field
        self.textInput = InputField(
            self.inputCard.contentFrame,
            placeholder="Enter your text here...",
            height=120,
            multiline=True,
        )
        self.textInput.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        # Button frame
        buttonFrame = ctk.CTkFrame(self.inputCard.contentFrame, fg_color="transparent")
        buttonFrame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        buttonFrame.grid_columnconfigure(0, weight=1)

        # Analyze button
        self.analyzeButton = ActionButton(
            buttonFrame, text="Analyze Sentiment", command=self._onAnalyzeClick
        )
        self.analyzeButton.grid(row=0, column=0, sticky="e")

        # Status indicator
        self.statusIndicator = StatusIndicator(buttonFrame)
        self.statusIndicator.grid(row=0, column=1, padx=(10, 0))

    def _createResultsSection(self, parent: ctk.CTkFrame) -> None:
        """Create the results display section.

        Args:
            parent: Parent frame
        """
        self.resultsCard = Card(
            parent,
            title="Analysis Results",
        )
        self.resultsCard.grid(row=1, column=0, sticky="nsew")

        # Results content frame
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

    def _onAnalyzeClick(self) -> None:
        """Handle analyze button click."""
        text = self.textInput.getText().strip()

        if not text:
            self.statusIndicator.setStatus("error", "Please enter some text to analyze")
            return

        # Disable button during analysis
        self.analyzeButton.setEnabled(False)
        self.statusIndicator.setStatus("loading", "Analyzing text...")

        # Run analysis in background thread
        thread = threading.Thread(target=self._performAnalysis, args=(text,))
        thread.daemon = True
        thread.start()

    def _performAnalysis(self, text: str) -> None:
        """Perform sentiment analysis in background thread.

        Args:
            text: Text to analyze
        """
        try:
            # Perform analysis
            result = services.analyzeText(text, saveToHistory=True)

            # Update UI in main thread
            self.after(0, self._onAnalysisComplete, result)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.after(0, self._onAnalysisError, str(e))

    def _onAnalysisComplete(self, result: dict[str, Any]) -> None:
        """Handle successful analysis completion.

        Args:
            result: Analysis result dictionary
        """
        try:
            # Update primary result
            sentiment = result["primary_sentiment"]
            confidence = result["confidence"]

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
            scores = result.get("scores", [])
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
            processingTime = result.get("processing_time", 0)
            self.timingLabel.configure(text=f"{processingTime:.2f} seconds")

            # Update status
            self.statusIndicator.setStatus("success", "Analysis completed successfully")

        except Exception as e:
            logger.error(f"Failed to update UI with results: {e}")
            self.statusIndicator.setStatus("error", f"Failed to display results: {e}")

        finally:
            # Re-enable button
            self.analyzeButton.setEnabled(True)

    def _onAnalysisError(self, error: str) -> None:
        """Handle analysis error.

        Args:
            error: Error message
        """
        self.statusIndicator.setStatus("error", f"Analysis failed: {error}")
        self.analyzeButton.setEnabled(True)

    def onShow(self) -> None:
        """Called when the page is shown."""
        super().onShow()
        # Focus on text input when page is shown
        if self.textInput:
            self.textInput.focus()

    def clearInput(self) -> None:
        """Clear the text input."""
        if self.textInput:
            self.textInput.clear()

    def clearResults(self) -> None:
        """Clear the analysis results."""
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
