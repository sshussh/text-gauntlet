"""Movie reviews analysis service using TMDB API."""

import time
from typing import Any

import requests

from config.settings import settings
from core.models import TextInput
from core.sentiment_analyzer import SentimentAnalyzer
from utils.exceptions import ApiError, ValidationError
from utils.logger import logger


class MovieService:
    """Service for fetching and analyzing movie reviews."""

    def __init__(self, apiKey: str | None = None) -> None:
        """Initialize the movie service.

        Args:
            apiKey: TMDB API key. If None, will try to get from settings.
        """
        self.apiKey = apiKey or settings.api.tmdbApiKey
        self.baseUrl = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {self.apiKey}" if self.apiKey else "",
            "User-Agent": "TextGauntlet/2.0.0",
        }

        # Initialize sentiment analyzer
        self.analyzer = SentimentAnalyzer()

        if not self.apiKey:
            logger.warning(
                "TMDB API key not configured - movie service will be limited"
            )

    def searchMovies(self, query: str) -> list[dict[str, Any]]:
        """Search for movies on TMDB.

        Args:
            query: Movie title to search for

        Returns:
            List of movie search results

        Raises:
            ApiError: If the API request fails
            ValidationError: If the query is invalid
        """
        if not query or len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters")

        if not self.apiKey:
            raise ApiError("TMDB API key not configured")

        try:
            response = requests.get(
                f"{self.baseUrl}/search/movie",
                params={
                    "api_key": self.apiKey,
                    "query": query.strip(),
                    "language": "en-US",
                    "page": 1,
                },
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            movies = data.get("results", [])

            results = []
            for movie in movies[:10]:  # Limit to top 10 results
                results.append(
                    {
                        "id": movie.get("id"),
                        "title": movie.get("title", "Unknown"),
                        "release_date": movie.get("release_date", ""),
                        "overview": movie.get("overview", ""),
                        "rating": movie.get("vote_average", 0),
                        "vote_count": movie.get("vote_count", 0),
                        "poster_path": movie.get("poster_path"),
                        "backdrop_path": movie.get("backdrop_path"),
                    }
                )

            logger.info(f"Found {len(results)} movies for query: {query}")
            return results

        except requests.RequestException as e:
            logger.error(f"TMDB API request failed: {e}")
            raise ApiError(f"Failed to search movies: {e}") from e

    def getMovieReviews(self, movieId: int, limit: int = 20) -> list[dict[str, Any]]:
        """Get reviews for a specific movie.

        Args:
            movieId: TMDB movie ID
            limit: Maximum number of reviews to fetch

        Returns:
            List of movie reviews

        Raises:
            ApiError: If the API request fails
        """
        if not self.apiKey:
            raise ApiError("TMDB API key not configured")

        try:
            reviews = []
            page = 1
            maxPages = 5  # Limit to 5 pages to avoid excessive requests

            while len(reviews) < limit and page <= maxPages:
                response = requests.get(
                    f"{self.baseUrl}/movie/{movieId}/reviews",
                    params={
                        "api_key": self.apiKey,
                        "language": "en-US",
                        "page": page,
                    },
                    timeout=10,
                )
                response.raise_for_status()

                data = response.json()
                pageReviews = data.get("results", [])

                if not pageReviews:
                    break

                for review in pageReviews:
                    if len(reviews) >= limit:
                        break

                    reviews.append(
                        {
                            "id": review.get("id"),
                            "author": review.get("author", "Anonymous"),
                            "content": review.get("content", ""),
                            "rating": review.get("author_details", {}).get("rating"),
                            "created_at": review.get("created_at"),
                            "updated_at": review.get("updated_at"),
                            "url": review.get("url"),
                        }
                    )

                page += 1

            logger.info(f"Retrieved {len(reviews)} reviews for movie ID: {movieId}")
            return reviews

        except requests.RequestException as e:
            logger.error(f"Failed to get reviews for movie {movieId}: {e}")
            raise ApiError(f"Failed to retrieve movie reviews: {e}") from e

    def getMovieDetails(self, movieId: int) -> dict[str, Any]:
        """Get detailed information about a movie.

        Args:
            movieId: TMDB movie ID

        Returns:
            Detailed movie information

        Raises:
            ApiError: If the API request fails
        """
        if not self.apiKey:
            raise ApiError("TMDB API key not configured")

        try:
            response = requests.get(
                f"{self.baseUrl}/movie/{movieId}",
                params={
                    "api_key": self.apiKey,
                    "language": "en-US",
                },
                timeout=10,
            )
            response.raise_for_status()

            movie = response.json()

            return {
                "id": movie.get("id"),
                "title": movie.get("title", "Unknown"),
                "tagline": movie.get("tagline", ""),
                "overview": movie.get("overview", ""),
                "release_date": movie.get("release_date", ""),
                "runtime": movie.get("runtime", 0),
                "budget": movie.get("budget", 0),
                "revenue": movie.get("revenue", 0),
                "rating": movie.get("vote_average", 0),
                "vote_count": movie.get("vote_count", 0),
                "popularity": movie.get("popularity", 0),
                "genres": [g["name"] for g in movie.get("genres", [])],
                "production_companies": [
                    c["name"] for c in movie.get("production_companies", [])
                ],
                "poster_path": movie.get("poster_path"),
                "backdrop_path": movie.get("backdrop_path"),
                "homepage": movie.get("homepage"),
                "imdb_id": movie.get("imdb_id"),
            }

        except requests.RequestException as e:
            logger.error(f"Failed to get movie details for {movieId}: {e}")
            raise ApiError(f"Failed to retrieve movie details: {e}") from e

    def analyzeMovieReviews(
        self, movieTitle: str, maxReviews: int = 20
    ) -> dict[str, Any]:
        """Search for a movie and analyze its reviews.

        Args:
            movieTitle: Title of the movie to analyze
            maxReviews: Maximum number of reviews to analyze

        Returns:
            Dictionary containing movie info and review analysis data

        Raises:
            ApiError: If movie not found or no reviews available
            ValidationError: If inputs are invalid
        """
        if not movieTitle:
            raise ValidationError("Movie title is required")

        start_time = time.time()

        # Search for the movie
        searchResults = self.searchMovies(movieTitle)

        if not searchResults:
            raise ApiError(f"No movies found for: {movieTitle}")

        # Use the first (most relevant) result
        movie = searchResults[0]
        movieId = movie["id"]

        try:
            # Get movie details and reviews
            movieDetails = self.getMovieDetails(movieId)
            reviews = self.getMovieReviews(movieId, maxReviews)

            if not reviews:
                raise ApiError("No reviews available for this movie")

            # Combine all review texts
            allReviewsText = "\n\n".join(
                [
                    f"Review by {review['author']}: {review['content']}"
                    for review in reviews
                    if review["content"]
                ]
            )

            if not allReviewsText.strip():
                raise ApiError("No readable review content found")

            # Create TextInput for analysis
            textInput = TextInput(
                content=allReviewsText,
                source="movie_reviews",
                metadata={
                    "movie_id": movieId,
                    "title": movieDetails["title"],
                    "release_date": movieDetails["release_date"],
                    "rating": movieDetails["rating"],
                    "genres": movieDetails["genres"],
                    "review_count": len(reviews),
                    "poster_path": movieDetails["poster_path"],
                },
            )

            # Perform sentiment analysis
            logger.info(f"Analyzing sentiment for {len(reviews)} reviews...")
            try:
                analysis_results = self.analyzer.analyzeText(textInput)
            except Exception as sentiment_error:
                logger.warning(f"Sentiment analysis failed: {sentiment_error}")
                # Provide fallback results
                from core.models import SentimentResult, SentimentScore

                fallback_scores = [
                    SentimentScore("positive", 0.33),
                    SentimentScore("neutral", 0.34),
                    SentimentScore("negative", 0.33),
                ]

                analysis_results = SentimentResult(
                    text=(
                        allReviewsText[:100] + "..."
                        if len(allReviewsText) > 100
                        else allReviewsText
                    ),
                    scores=fallback_scores,
                    primarySentiment="neutral",
                    confidence=0.5,
                    processingTime=0.0,
                    timestamp=time.time(),
                )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Prepare response with sentiment analysis results
            return {
                "movie_info": movieDetails,
                "reviews": reviews,
                "text_input": textInput,
                "reviewCount": len(reviews),  # Changed from review_count
                "review_count": len(reviews),  # Keep for backwards compatibility
                "total_words": textInput.wordCount,
                "total_characters": textInput.length,
                "processingTime": processing_time,  # Changed from processing_time
                "processing_time": processing_time,  # Keep for backwards compatibility
                # Sentiment analysis results
                "primary_sentiment": analysis_results.primarySentiment,
                "primarySentiment": analysis_results.primarySentiment,  # Legacy compatibility
                "confidence": analysis_results.confidence,
                "scores": {
                    score.label: score.score for score in analysis_results.scores
                },
                "emotions": {
                    score.label: score.score for score in analysis_results.topEmotions
                },
                "analysis_results": analysis_results,
            }

        except Exception as e:
            logger.error(f"Failed to analyze reviews for {movieTitle}: {e}")
            raise ApiError(f"Failed to analyze movie reviews: {e}") from e

    def analyzeMovie(self, movieId: int, movieTitle: str) -> dict[str, Any]:
        """Analyze movie reviews by movie ID and title.

        Args:
            movieId: TMDB movie ID
            movieTitle: Movie title

        Returns:
            Dictionary containing movie analysis results

        Raises:
            ApiError: If analysis fails
            ValidationError: If inputs are invalid
        """
        # For now, use the existing analyzeMovieReviews method with the title
        # In the future, we could use the movieId to get more specific data
        return self.analyzeMovieReviews(movieTitle)

    def getTrendingMovies(self, timeWindow: str = "week") -> list[dict[str, Any]]:
        """Get trending movies.

        Args:
            timeWindow: 'day' or 'week'

        Returns:
            List of trending movies
        """
        if not self.apiKey:
            logger.warning("API key not available for trending movies")
            return []

        try:
            response = requests.get(
                f"{self.baseUrl}/trending/movie/{timeWindow}",
                params={"api_key": self.apiKey},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            movies = data.get("results", [])

            results = []
            for movie in movies[:10]:
                results.append(
                    {
                        "id": movie.get("id"),
                        "title": movie.get("title", "Unknown"),
                        "release_date": movie.get("release_date", ""),
                        "overview": movie.get("overview", ""),
                        "rating": movie.get("vote_average", 0),
                        "popularity": movie.get("popularity", 0),
                        "poster_path": movie.get("poster_path"),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Failed to get trending movies: {e}")
            return []

    def getPopularMovies(self, page: int = 1) -> list[dict[str, Any]]:
        """Get popular movies.

        Args:
            page: Page number (1-based)

        Returns:
            List of popular movies
        """
        if not self.apiKey:
            logger.warning("API key not available for popular movies")
            return []

        try:
            response = requests.get(
                f"{self.baseUrl}/movie/popular",
                params={
                    "api_key": self.apiKey,
                    "language": "en-US",
                    "page": page,
                },
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            movies = data.get("results", [])

            results = []
            for movie in movies:
                results.append(
                    {
                        "id": movie.get("id"),
                        "title": movie.get("title", "Unknown"),
                        "release_date": movie.get("release_date", ""),
                        "overview": movie.get("overview", ""),
                        "rating": movie.get("vote_average", 0),
                        "popularity": movie.get("popularity", 0),
                        "poster_path": movie.get("poster_path"),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Failed to get popular movies: {e}")
            return []
