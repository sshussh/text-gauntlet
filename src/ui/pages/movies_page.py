"""Movies analysis page for Text Gauntlet."""

import threading

import customtkinter as ctk

from services.application_services import services
from services.movie_service import MovieService
from ui.components.base import (
    ActionButton,
    Card,
    InputField,
    ScrollableFrame,
    StatusIndicator,
)
from ui.components.theme_manager import themeManager
from utils.logger import logger


class MoviesPage(ctk.CTkFrame):
    """Page for analyzing movie reviews."""

    def __init__(self, parent: ctk.CTk, movieService: MovieService, **kwargs) -> None:
        """Initialize the movies page.

        Args:
            parent: Parent widget
            movieService: Movie service instance
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)

        self.movieService = movieService
        self.currentMovie: dict | None = None
        self.searchResults: list[dict] = []
        self._is_destroyed = False

        # Create main scrollable frame for the entire page
        self.mainScrollFrame: ScrollableFrame | None = None
        self.contentFrame: ctk.CTkFrame | None = None

        # UI Components (will be children of contentFrame)
        self.searchCard: Card | None = None
        self.searchInput: InputField | None = None
        self.searchButton: ActionButton | None = None
        self.resultsFrameComponent: ScrollableFrame | None = None
        self.resultsFrame: ctk.CTkFrame | None = None
        self.moviePreviewCard: Card | None = None
        self.analyzeButton: ActionButton | None = None
        self.analysisCard: Card | None = None
        self.statusIndicator: StatusIndicator | None = None

        self._setupPage()

    def _setupPage(self) -> None:
        """Set up the movies page layout."""
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
            text="Movie Reviews Analysis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("accent"),
        )
        titleLabel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Search section
        self._createSearchSection()

        # Results section
        self._createResultsSection()

        # Movie preview section
        self._createMoviePreviewSection()

        # Analysis section
        self._createAnalysisSection()

        # Status indicator
        self.statusIndicator = StatusIndicator(self.contentFrame)
        self.statusIndicator.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        logger.info("Movies page setup completed with scrollable main frame")

    def _createSearchSection(self) -> None:
        """Create the movie search section."""
        self.searchCard = Card(self.contentFrame, title="Search Movies")
        self.searchCard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Search input
        self.searchInput = InputField(
            self.searchCard.contentFrame,
            placeholder="Enter movie title to search...",
            height=40,
        )
        self.searchInput.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Search button
        self.searchButton = ActionButton(
            self.searchCard.contentFrame,
            text="Search Movies",
            command=self._searchMovies,
            style="primary",
        )
        self.searchButton.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Configure grid
        self.searchCard.contentFrame.grid_columnconfigure(0, weight=1)

    def _createResultsSection(self) -> None:
        """Create the search results section."""
        # Results frame
        self.resultsFrameComponent = ScrollableFrame(
            self.contentFrame, height=200, fg_color=themeManager.getColor("surface")
        )
        self.resultsFrameComponent.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.resultsFrame = self.resultsFrameComponent.contentFrame
        self.resultsFrame.grid_columnconfigure(0, weight=1)

        # Initially hidden
        self.resultsFrameComponent.grid_remove()

    def _createMoviePreviewSection(self) -> None:
        """Create the movie preview section."""
        self.moviePreviewCard = Card(self.contentFrame, title="Selected Movie")
        self.moviePreviewCard.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Analyze button
        self.analyzeButton = ActionButton(
            self.moviePreviewCard.contentFrame,
            text="Analyze Reviews",
            command=self._analyzeMovie,
            style="primary",
        )
        self.analyzeButton.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Configure grid
        self.moviePreviewCard.contentFrame.grid_columnconfigure(0, weight=1)

        # Initially hidden
        self.moviePreviewCard.grid_remove()

    def _safe_after(self, callback):
        """Safely schedule a callback, checking if widget still exists."""
        try:
            if not self._is_destroyed and self.winfo_exists():
                self.after(0, callback)
        except Exception as e:
            logger.debug(f"Failed to schedule callback: {e}")

    def _createAnalysisSection(self) -> None:
        """Create the analysis results section."""
        # Create analysis card directly since main frame is now scrollable
        self.analysisCard = Card(self.contentFrame, title="Analysis Results")
        self.analysisCard.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Configure grid for content expansion
        self.analysisCard.contentFrame.grid_columnconfigure(0, weight=1)

        # Initially hidden
        self.analysisCard.grid_remove()

    def _searchMovies(self) -> None:
        """Search for movies."""
        query = self.searchInput.getValue().strip()
        if not query:
            self.statusIndicator.showError("Please enter a movie title to search")
            return

        # Reset current state when starting new search
        self.currentMovie = None
        if self.moviePreviewCard:
            self.moviePreviewCard.grid_remove()
        if self.analysisCard:
            self.analysisCard.grid_remove()

        self.searchButton.setLoading(True)
        self.statusIndicator.showInfo("Searching movies...")

        def searchTask() -> None:
            try:
                # Search movies
                results = self.movieService.searchMovies(query)

                # Update UI on main thread
                self._safe_after(lambda: self._displaySearchResults(results))

            except Exception as e:
                logger.error(f"Movie search failed: {e}")
                error_msg = str(e)
                self._safe_after(
                    lambda: self.statusIndicator
                    and self.statusIndicator.showError(f"Search failed: {error_msg}")
                )
            finally:
                self._safe_after(
                    lambda: self.searchButton and self.searchButton.setLoading(False)
                )

        threading.Thread(target=searchTask, daemon=True).start()

    def _displaySearchResults(self, results: list[dict]) -> None:
        """Display search results."""
        if self._is_destroyed:
            return

        self.searchResults = results

        if not results:
            if self.statusIndicator:
                self.statusIndicator.showWarning("No movies found")
            if self.resultsFrameComponent:
                self.resultsFrameComponent.grid_remove()
            return

        # Clear previous results
        for widget in self.resultsFrame.winfo_children():
            widget.destroy()

        # Show results frame
        self.resultsFrameComponent.grid()

        # Create result items
        for i, movie in enumerate(results):
            self._createMovieResultItem(movie, i)

        if self.statusIndicator:
            self.statusIndicator.showSuccess(f"Found {len(results)} movies")

    def _createMovieResultItem(self, movie: dict, index: int) -> None:
        """Create a search result item."""
        # Movie card
        movieCard = ctk.CTkFrame(
            self.resultsFrame,
            fg_color=themeManager.getColor("card_background"),
            corner_radius=8,
        )
        movieCard.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        movieCard.grid_columnconfigure(0, weight=1)

        # Movie info frame
        infoFrame = ctk.CTkFrame(movieCard, fg_color="transparent")
        infoFrame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        infoFrame.grid_columnconfigure(0, weight=1)

        # Title
        titleLabel = ctk.CTkLabel(
            infoFrame,
            text=movie.get("title", "Unknown Title"),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        titleLabel.grid(row=0, column=0, sticky="ew")

        # Release date and rating
        details = []
        if movie.get("release_date"):
            details.append(f"Released: {movie['release_date']}")
        if movie.get("vote_average"):
            details.append(f"Rating: {movie['vote_average']}/10")

        if details:
            detailsLabel = ctk.CTkLabel(
                infoFrame,
                text=" • ".join(details),
                font=ctk.CTkFont(size=12),
                text_color=themeManager.getColor("text_secondary"),
                anchor="w",
            )
            detailsLabel.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        # Overview
        if movie.get("overview"):
            overviewLabel = ctk.CTkLabel(
                infoFrame,
                text=movie["overview"][:150]
                + ("..." if len(movie["overview"]) > 150 else ""),
                font=ctk.CTkFont(size=11),
                text_color=themeManager.getColor("text_secondary"),
                anchor="w",
                wraplength=400,
            )
            overviewLabel.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        # Select button
        selectButton = ctk.CTkButton(
            movieCard,
            text="Select Movie",
            command=lambda: self._selectMovie(movie),
            width=120,
            height=30,
        )
        selectButton.grid(row=0, column=1, padx=15, pady=15, sticky="e")

    def _selectMovie(self, movie: dict) -> None:
        """Select a movie for analysis."""
        if self._is_destroyed:
            return

        self.currentMovie = movie

        # Update movie preview
        self._updateMoviePreview(movie)

        # Show preview card
        if self.moviePreviewCard:
            self.moviePreviewCard.grid()

        # Hide results
        if self.resultsFrameComponent:
            self.resultsFrameComponent.grid_remove()

        if self.statusIndicator:
            self.statusIndicator.showSuccess(
                f"Selected: {movie.get('title', 'Unknown')}"
            )

    def _updateMoviePreview(self, movie: dict) -> None:
        """Update the movie preview display."""
        if not self.moviePreviewCard:
            return

        # Clear previous content
        for widget in self.moviePreviewCard.contentFrame.winfo_children():
            if widget != getattr(self.analyzeButton, "_widget", None):
                widget.destroy()

        # Movie info frame
        infoFrame = ctk.CTkFrame(
            self.moviePreviewCard.contentFrame, fg_color="transparent"
        )
        infoFrame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        infoFrame.grid_columnconfigure(0, weight=1)

        # Title
        titleLabel = ctk.CTkLabel(
            infoFrame,
            text=movie.get("title", "Unknown Title"),
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        titleLabel.grid(row=0, column=0, sticky="ew")

        # Details
        details = []
        if movie.get("release_date"):
            details.append(f"📅 {movie['release_date']}")
        if movie.get("vote_average"):
            details.append(f"Rating: {movie['vote_average']}/10")

        if details:
            detailsLabel = ctk.CTkLabel(
                infoFrame,
                text=" • ".join(details),
                font=ctk.CTkFont(size=12),
                text_color=themeManager.getColor("text_secondary"),
                anchor="w",
            )
            detailsLabel.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        # Overview
        if movie.get("overview"):
            overviewLabel = ctk.CTkLabel(
                infoFrame,
                text=movie["overview"],
                font=ctk.CTkFont(size=11),
                text_color=themeManager.getColor("text_secondary"),
                anchor="w",
                wraplength=500,
                justify="left",
            )
            overviewLabel.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        # Make sure the analyze button is visible and properly positioned
        self.analyzeButton.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")
        logger.info(
            f"Analyze button positioned for movie: {movie.get('title', 'Unknown')}"
        )

    def _analyzeMovie(self) -> None:
        """Analyze the selected movie reviews."""
        if not self.currentMovie:
            self.statusIndicator.showError("No movie selected")
            return

        self.analyzeButton.setLoading(True)
        self.statusIndicator.showInfo("Analyzing movie reviews...")

        def analyzeTask() -> None:
            try:
                # Get movie review data from the movie service
                results = self.movieService.analyzeMovieReviews(
                    self.currentMovie["title"], maxReviews=15
                )

                # Extract the TextInput object which contains the movie review text and metadata
                textInput = results.get("text_input")
                if textInput:
                    # Use ApplicationServices to analyze and save the result
                    analysisResult = services.analyzeText(textInput, saveToHistory=True)
                    # Add the analysis result to the movie results for display
                    results["analysis_result"] = analysisResult

                # Update UI on main thread
                self._safe_after(lambda: self._displayAnalysisResults(results))

            except Exception as e:
                logger.error(f"Movie analysis failed: {e}")
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

        logger.info(f"Displaying analysis results with keys: {list(results.keys())}")
        logger.info(f"Primary sentiment: {results.get('primarySentiment', 'MISSING')}")
        logger.info(f"Confidence: {results.get('confidence', 'MISSING')}")
        logger.info(f"Review count: {results.get('reviewCount', 'MISSING')}")

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

        # Review count
        reviewCountLabel = ctk.CTkLabel(
            resultsFrame, text="Reviews Analyzed:", font=ctk.CTkFont(size=12)
        )
        reviewCountLabel.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

        reviewCountValue = results.get("reviewCount", 0)
        reviewCountValueLabel = ctk.CTkLabel(
            resultsFrame, text=str(reviewCountValue), font=ctk.CTkFont(size=12)
        )
        reviewCountValueLabel.grid(row=2, column=1, sticky="w", pady=(5, 0))

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

        # Detailed scores
        if "scores" in results:
            self._displayDetailedScores(resultsFrame, results["scores"], 4)

        # Show analysis card
        if self.analysisCard:
            self.analysisCard.grid()
        if self.statusIndicator:
            self.statusIndicator.showSuccess("Analysis completed successfully!")

    def _displayDetailedScores(
        self, parent: ctk.CTkFrame, scores: dict, startRow: int
    ) -> None:
        """Display detailed sentiment scores."""
        scoresLabel = ctk.CTkLabel(
            parent, text="Detailed Scores:", font=ctk.CTkFont(size=12, weight="bold")
        )
        scoresLabel.grid(row=startRow, column=0, sticky="w", pady=(10, 5), columnspan=2)

        row = startRow + 1
        for sentiment, score in scores.items():
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
        if sentiment in ["positive", "joy", "love", "admiration"]:
            return themeManager.getColor("success")
        elif sentiment in ["negative", "anger", "sadness", "fear", "disgust"]:
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
            self.currentMovie = None
            self.searchResults = []

            if self.searchInput:
                try:
                    self.searchInput.clear()
                except Exception:
                    pass  # Widget may already be destroyed

            if self.resultsFrameComponent:
                try:
                    self.resultsFrameComponent.grid_remove()
                except Exception:
                    pass  # Widget may already be destroyed

            if self.resultsFrame:
                try:
                    for widget in self.resultsFrame.winfo_children():
                        try:
                            widget.destroy()
                        except Exception:
                            pass  # Widget may already be destroyed
                except Exception:
                    pass  # Frame may already be destroyed

            if self.moviePreviewCard:
                try:
                    self.moviePreviewCard.grid_remove()
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

            logger.info("Movies page reset")

        except Exception as e:
            logger.warning(f"Error during movies page reset: {e}")
            # Continue with cleanup even if some operations fail
