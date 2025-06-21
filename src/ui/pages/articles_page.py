"""Articles analysis page for Text Gauntlet."""

import threading

import customtkinter as ctk

from services.application_services import services
from services.article_service import ArticleService
from ui.components.base import (
    ActionButton,
    Card,
    InputField,
    ScrollableFrame,
    StatusIndicator,
)
from ui.components.theme_manager import themeManager
from utils.logger import logger


class ArticlesPage(ctk.CTkFrame):
    """Page for analyzing news articles and web content."""

    def __init__(
        self, parent: ctk.CTk, articleService: ArticleService, **kwargs
    ) -> None:
        """Initialize the articles page.

        Args:
            parent: Parent widget
            articleService: Article service instance
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)

        self.articleService = articleService
        self.currentUrl: str | None = None
        self.currentContent: str | None = None
        self._is_destroyed = False

        # Create main scrollable frame for the entire page
        self.mainScrollFrame: ScrollableFrame | None = None
        self.contentFrame: ctk.CTkFrame | None = None

        # UI Components (will be children of contentFrame)
        self.inputCard: Card | None = None
        self.urlInput: InputField | None = None
        self.fetchButton: ActionButton | None = None
        self.previewCard: Card | None = None
        self.analyzeButton: ActionButton | None = None
        self.analysisCard: Card | None = None
        self.statusIndicator: StatusIndicator | None = None

        self._setupPage()

    def _setupPage(self) -> None:
        """Set up the articles page layout."""
        # Configure main frame grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main scrollable frame using our custom component
        self.mainScrollFrame = ScrollableFrame(self, fg_color="transparent")
        self.mainScrollFrame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Use the scrollable frame's content as our content frame
        self.contentFrame = self.mainScrollFrame.contentFrame
        self.contentFrame.grid_columnconfigure(0, weight=1)

        # Page title
        titleLabel = ctk.CTkLabel(
            self.contentFrame,
            text="Article Analysis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("accent"),
        )
        titleLabel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Input section
        self._createInputSection()

        # Preview section
        self._createPreviewSection()

        # Analysis section
        self._createAnalysisSection()

        # Status indicator
        self.statusIndicator = StatusIndicator(self.contentFrame)
        self.statusIndicator.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        logger.info("Articles page setup completed with scrollable main frame")

    def _createInputSection(self) -> None:
        """Create the URL input section."""
        self.inputCard = Card(self.contentFrame, title="Enter Article URL")
        self.inputCard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Description
        descLabel = ctk.CTkLabel(
            self.inputCard.contentFrame,
            text="Enter the URL of a news article or web page to analyze:",
            font=ctk.CTkFont(size=12),
            text_color=themeManager.getColor("text_secondary"),
        )
        descLabel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # URL input
        self.urlInput = InputField(
            self.inputCard.contentFrame,
            placeholder="https://example.com/article...",
            height=40,
        )
        self.urlInput.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Fetch button
        self.fetchButton = ActionButton(
            self.inputCard.contentFrame,
            text="Fetch Article",
            command=self._fetchArticle,
            style="primary",
        )
        self.fetchButton.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Configure grid
        self.inputCard.contentFrame.grid_columnconfigure(0, weight=1)

    def _createPreviewSection(self) -> None:
        """Create the article preview section."""
        self.previewCard = Card(self.contentFrame, title="Article Preview")
        self.previewCard.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Configure grid
        self.previewCard.contentFrame.grid_columnconfigure(0, weight=1)

        # Initially hidden - analyze button will be created dynamically when content is displayed
        self.previewCard.grid_remove()

    def _createAnalysisSection(self) -> None:
        """Create the analysis results section."""
        self.analysisCard = Card(self.contentFrame, title="Analysis Results")
        self.analysisCard.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Initially hidden
        self.analysisCard.grid_remove()

    def _safe_after(self, callback):
        """Safely schedule a callback, checking if widget still exists."""
        try:
            if not self._is_destroyed and self.winfo_exists():
                self.after(0, callback)
        except Exception as e:
            logger.debug(f"Failed to schedule callback: {e}")

    def _fetchArticle(self) -> None:
        """Fetch article content from URL."""
        url = self.urlInput.getValue().strip()
        if not url:
            self.statusIndicator.showError("Please enter a URL")
            return

        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.urlInput.setValue(url)

        self.fetchButton.setLoading(True)
        self.statusIndicator.showInfo("Fetching article content...")

        def fetchTask() -> None:
            try:
                # Fetch article content
                content = self.articleService.fetchArticleContent(url)

                # Update UI on main thread
                self._safe_after(lambda: self._displayArticlePreview(url, content))

            except Exception as e:
                logger.error(f"Article fetch failed: {e}")
                error_msg = str(e)
                self._safe_after(
                    lambda: self.statusIndicator
                    and self.statusIndicator.showError(f"Fetch failed: {error_msg}")
                )
            finally:
                self._safe_after(
                    lambda: self.fetchButton and self.fetchButton.setLoading(False)
                )

        threading.Thread(target=fetchTask, daemon=True).start()

    def _displayArticlePreview(self, url: str, content: str) -> None:
        """Display article preview."""
        if self._is_destroyed:
            return

        self.currentUrl = url
        self.currentContent = content

        if not content or not content.strip():
            if self.statusIndicator:
                self.statusIndicator.showWarning("No readable content found in article")
            if self.previewCard:
                self.previewCard.grid_remove()
            return

        # Clear all previous content and recreate analyze button fresh
        for widget in self.previewCard.contentFrame.winfo_children():
            widget.destroy()

        # Content preview frame
        previewFrame = ctk.CTkFrame(
            self.previewCard.contentFrame, fg_color="transparent"
        )
        previewFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        previewFrame.grid_columnconfigure(0, weight=1)

        # URL display
        urlLabel = ctk.CTkLabel(
            previewFrame,
            text=f"URL: {url}",
            font=ctk.CTkFont(size=12),
            text_color=themeManager.getColor("text_secondary"),
            anchor="w",
        )
        urlLabel.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Content preview (first 500 characters)
        preview_text = content[:500] + ("..." if len(content) > 500 else "")
        contentPreview = ctk.CTkTextbox(
            previewFrame, height=150, wrap="word", font=ctk.CTkFont(size=11)
        )
        contentPreview.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        contentPreview.insert("0.0", preview_text)
        contentPreview.configure(state="disabled")

        # Content stats
        statsLabel = ctk.CTkLabel(
            previewFrame,
            text=f"Content length: {len(content)} characters • {len(content.split())} words",
            font=ctk.CTkFont(size=11),
            text_color=themeManager.getColor("text_secondary"),
            anchor="w",
        )
        statsLabel.grid(row=2, column=0, sticky="ew")

        # Recreate the analyze button
        self.analyzeButton = ActionButton(
            self.previewCard.contentFrame,
            text="Analyze Article",
            command=self._analyzeArticle,
            style="primary",
        )
        self.analyzeButton.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Show preview card
        if self.previewCard:
            self.previewCard.grid()
        if self.statusIndicator:
            self.statusIndicator.showSuccess("Article content fetched successfully!")

    def _analyzeArticle(self) -> None:
        """Analyze the fetched article content."""
        if not self.currentContent:
            self.statusIndicator.showError("No article content to analyze")
            return

        self.analyzeButton.setLoading(True)
        self.statusIndicator.showInfo("Analyzing article content...")

        def analyzeTask() -> None:
            try:
                # Create TextInput object for the article content
                from core.models import TextInput

                textInput = TextInput(
                    content=self.currentContent,
                    source="article",
                    metadata={
                        "url": self.currentUrl,
                        "content_length": len(self.currentContent),
                        "word_count": len(self.currentContent.split()),
                    },
                )

                # Use ApplicationServices to analyze and save the result
                analysis_result = services.analyzeText(textInput, saveToHistory=True)

                # Convert scores from list format to dict format for UI compatibility
                scores_dict = {}
                if "scores" in analysis_result and isinstance(
                    analysis_result["scores"], list
                ):
                    scores_dict = {
                        score["label"]: score["score"]
                        for score in analysis_result["scores"]
                    }
                else:
                    scores_dict = analysis_result.get("scores", {})

                # Convert to format expected by UI (for compatibility with existing display code)
                results = {
                    "primarySentiment": analysis_result["primary_sentiment"],
                    "confidence": analysis_result["confidence"],
                    "scores": scores_dict,
                    "contentLength": len(self.currentContent),
                    "wordCount": len(self.currentContent.split()),
                    "processingTime": analysis_result["processing_time"],
                    "url": self.currentUrl,
                    "analysis_result": analysis_result,
                }

                # Update UI on main thread
                self._safe_after(lambda: self._displayAnalysisResults(results))

            except Exception as e:
                logger.error(f"Article analysis failed: {e}")
                error_msg = str(e)
                self._safe_after(
                    lambda: self.statusIndicator
                    and self.statusIndicator.showError(f"Analysis failed: {error_msg}")
                )
            finally:
                self._safe_after(
                    lambda: self.analyzeButton and self.analyzeButton.setLoading(False)
                )

        threading.Thread(target=analyzeTask, daemon=True).start()

    def _displayAnalysisResults(self, results: dict) -> None:
        """Display analysis results."""
        if self._is_destroyed:
            return

        # Clear previous results
        if self.analysisCard:
            for widget in self.analysisCard.contentFrame.winfo_children():
                widget.destroy()

        # Results frame
        resultsFrame = ctk.CTkFrame(
            self.analysisCard.contentFrame, fg_color="transparent"
        )
        resultsFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        resultsFrame.grid_columnconfigure(1, weight=1)

        # Primary sentiment
        primaryLabel = ctk.CTkLabel(
            resultsFrame,
            text="Overall Sentiment:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        primaryLabel.grid(row=0, column=0, sticky="w", padx=(0, 10))

        sentimentColor = self._getSentimentColor(results.get("primarySentiment", ""))
        primaryValueLabel = ctk.CTkLabel(
            resultsFrame,
            text=results.get("primarySentiment", "Unknown").title(),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=sentimentColor,
        )
        primaryValueLabel.grid(row=0, column=1, sticky="w")

        # Confidence
        confidenceLabel = ctk.CTkLabel(
            resultsFrame, text="Confidence:", font=ctk.CTkFont(size=12)
        )
        confidenceLabel.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

        confidenceValue = results.get("confidence", 0)
        confidenceValueLabel = ctk.CTkLabel(
            resultsFrame,
            text=f"{confidenceValue:.1%}",
            font=ctk.CTkFont(size=12),
            text_color=self._getConfidenceColor(confidenceValue),
        )
        confidenceValueLabel.grid(row=1, column=1, sticky="w", pady=(5, 0))

        # Content length
        contentLengthLabel = ctk.CTkLabel(
            resultsFrame, text="Content Length:", font=ctk.CTkFont(size=12)
        )
        contentLengthLabel.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

        contentLength = results.get("contentLength", 0)
        contentLengthValueLabel = ctk.CTkLabel(
            resultsFrame, text=f"{contentLength} characters", font=ctk.CTkFont(size=12)
        )
        contentLengthValueLabel.grid(row=2, column=1, sticky="w", pady=(5, 0))

        # Processing time
        if "processingTime" in results:
            timingLabel = ctk.CTkLabel(
                resultsFrame, text="Processing Time:", font=ctk.CTkFont(size=12)
            )
            timingLabel.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

            timingValueLabel = ctk.CTkLabel(
                resultsFrame,
                text=f"{results['processingTime']:.2f}s",
                font=ctk.CTkFont(size=12),
            )
            timingValueLabel.grid(row=3, column=1, sticky="w", pady=(5, 0))

        # URL
        if "url" in results:
            urlLabel = ctk.CTkLabel(
                resultsFrame, text="Source URL:", font=ctk.CTkFont(size=12)
            )
            urlLabel.grid(row=4, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

            urlValueLabel = ctk.CTkLabel(
                resultsFrame,
                text=results["url"][:50] + ("..." if len(results["url"]) > 50 else ""),
                font=ctk.CTkFont(size=11),
                text_color=themeManager.getColor("text_secondary"),
            )
            urlValueLabel.grid(row=4, column=1, sticky="w", pady=(5, 0))

        # Detailed scores
        if "scores" in results:
            self._displayDetailedScores(resultsFrame, results["scores"], 5)

        # Show analysis card
        if self.analysisCard:
            self.analysisCard.grid()
        if self.statusIndicator:
            self.statusIndicator.showSuccess("Analysis completed successfully!")

    def _displayDetailedScores(
        self, parent: ctk.CTkFrame, scores: dict | list, startRow: int
    ) -> None:
        """Display detailed sentiment scores."""
        scoresLabel = ctk.CTkLabel(
            parent, text="Detailed Scores:", font=ctk.CTkFont(size=12, weight="bold")
        )
        scoresLabel.grid(row=startRow, column=0, sticky="w", pady=(10, 5), columnspan=2)

        row = startRow + 1

        # Handle both dict and list formats
        if isinstance(scores, dict):
            score_items = scores.items()
        elif isinstance(scores, list):
            # Convert list format to dict items
            score_items = [
                (score.get("label", "unknown"), score.get("score", 0))
                for score in scores
            ]
        else:
            # Fallback for unexpected format
            return

        for sentiment, score in score_items:
            sentimentLabel = ctk.CTkLabel(
                parent, text=f"  {sentiment.title()}:", font=ctk.CTkFont(size=11)
            )
            sentimentLabel.grid(row=row, column=0, sticky="w", padx=(20, 10))

            scoreLabel = ctk.CTkLabel(
                parent,
                text=f"{score:.3f}",
                font=ctk.CTkFont(size=11),
                text_color=self._getSentimentColor(sentiment) if score > 0.3 else None,
            )
            scoreLabel.grid(row=row, column=1, sticky="w")

            row += 1

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
            self.currentUrl = None
            self.currentContent = None

            if self.urlInput:
                try:
                    self.urlInput.clear()
                except Exception:
                    pass  # Widget may already be destroyed

            if self.previewCard:
                try:
                    self.previewCard.grid_remove()
                except Exception:
                    pass  # Widget may already be destroyed

            if self.analysisCard:
                try:
                    self.analysisCard.grid_remove()
                except Exception:
                    pass  # Widget may already be destroyed

            if self.statusIndicator:
                try:
                    self.statusIndicator.clear()
                except Exception:
                    pass  # Widget may already be destroyed

            logger.info("Articles page reset")

        except Exception as e:
            logger.warning(f"Error during articles page reset: {e}")
            # Continue with cleanup even if some operations fail
