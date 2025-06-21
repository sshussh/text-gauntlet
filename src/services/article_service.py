"""News and article analysis service using web scraping."""

from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from core.models import TextInput
from core.sentiment_analyzer import SentimentAnalyzer
from utils.exceptions import ApiError, ValidationError
from utils.logger import logger


class ArticleService:
    """Service for fetching and analyzing news articles and web content."""

    def __init__(self) -> None:
        """Initialize the article service."""
        # Initialize sentiment analyzer
        self.analyzer = SentimentAnalyzer()

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TextGauntlet/2.0.0"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Common selectors for article content
        self.contentSelectors = [
            'article[role="main"]',
            'div[role="main"]',
            "main",
            "article",
            ".article-content",
            ".post-content",
            ".entry-content",
            ".content",
            ".story-body",
            ".article-body",
            ".post-body",
            '[data-testid="article-body"]',
            ".article-text",
        ]

        # Selectors to remove (noise)
        self.noiseSelectors = [
            "nav",
            "header",
            "footer",
            "aside",
            ".advertisement",
            ".ad",
            ".ads",
            ".social-share",
            ".share-buttons",
            ".comments",
            ".comment-section",
            ".related-articles",
            ".recommended",
            ".newsletter-signup",
            ".subscription",
            "script",
            "style",
            "noscript",
        ]

    def validateUrl(self, url: str) -> str:
        """Validate and normalize a URL.

        Args:
            url: URL to validate

        Returns:
            Normalized URL

        Raises:
            ValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL is required and must be a string")

        url = url.strip()

        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Parse URL to validate structure
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValidationError("Invalid URL format")
            return url
        except Exception as e:
            raise ValidationError(f"Invalid URL: {e}") from e

    def fetchArticle(self, url: str) -> dict[str, Any]:
        """Fetch and parse an article from a URL.

        Args:
            url: Article URL

        Returns:
            Dictionary containing article data

        Raises:
            APIError: If fetching or parsing fails
            ValidationError: If URL is invalid
        """
        url = self.validateUrl(url)

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Check content type
            contentType = response.headers.get("content-type", "").lower()
            if "text/html" not in contentType:
                raise ApiError(f"URL does not contain HTML content: {contentType}")

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for selector in self.noiseSelectors:
                for element in soup.select(selector):
                    element.decompose()

            # Extract article content
            article = self._extractArticleContent(soup)

            if not article["content"]:
                raise ApiError("Could not extract readable content from the page")

            article["url"] = url
            article["content_length"] = len(article["content"])
            article["word_count"] = len(article["content"].split())

            logger.info(f"Successfully extracted article from {url}")
            return article

        except requests.RequestException as e:
            logger.error(f"Failed to fetch article from {url}: {e}")
            raise ApiError(f"Failed to fetch article: {e}") from e
        except Exception as e:
            logger.error(f"Error processing article from {url}: {e}")
            raise ApiError(f"Failed to process article: {e}") from e

    def _extractArticleContent(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract article content, title, and metadata from BeautifulSoup object.

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            Dictionary with extracted article data
        """
        article = {
            "title": "",
            "content": "",
            "author": "",
            "published_date": "",
            "description": "",
            "image_url": "",
            "site_name": "",
        }

        # Extract title
        title_selectors = [
            "h1.article-title",
            "h1.entry-title",
            "h1.post-title",
            ".article-headline h1",
            'h1[data-testid="headline"]',
            "h1",
            "title",
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                article["title"] = title_elem.get_text(strip=True)
                break

        # Extract main content
        content_text = ""
        for selector in self.contentSelectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Get text from paragraphs within the content
                paragraphs = content_elem.find_all(["p", "div"], recursive=True)
                paragraph_texts = []

                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out short/empty paragraphs
                        paragraph_texts.append(text)

                if paragraph_texts:
                    content_text = "\n\n".join(paragraph_texts)
                    break

        # Fallback: extract all paragraphs
        if not content_text:
            paragraphs = soup.find_all("p")
            paragraph_texts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    paragraph_texts.append(text)

            if len(paragraph_texts) >= 3:  # Ensure we have substantial content
                content_text = "\n\n".join(paragraph_texts)

        article["content"] = content_text

        # Extract metadata
        # Author
        author_selectors = [
            ".author-name",
            ".byline-author",
            '[rel="author"]',
            ".article-author",
            ".post-author",
        ]
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                article["author"] = author_elem.get_text(strip=True)
                break

        # Meta tags
        meta_tags = soup.find_all("meta")
        for meta in meta_tags:
            property_attr = meta.get("property", "").lower()
            name_attr = meta.get("name", "").lower()
            content = meta.get("content", "")

            if property_attr == "og:description" or name_attr == "description":
                if not article["description"]:
                    article["description"] = content

            elif property_attr == "og:image":
                if not article["image_url"]:
                    article["image_url"] = content

            elif property_attr == "og:site_name":
                if not article["site_name"]:
                    article["site_name"] = content

            elif name_attr in ["author", "article:author"]:
                if not article["author"]:
                    article["author"] = content

            elif (
                property_attr == "article:published_time"
                or name_attr == "article:published_time"
            ):
                if not article["published_date"]:
                    article["published_date"] = content

        return article

    def analyzeArticle(self, url: str) -> dict[str, Any]:
        """Fetch an article from URL and prepare it for sentiment analysis.

        Args:
            url: Article URL

        Returns:
            Dictionary containing article info and TextInput for analysis

        Raises:
            APIError: If article cannot be fetched or processed
            ValidationError: If URL is invalid
        """
        article = self.fetchArticle(url)

        if not article["content"]:
            raise ApiError("No readable content found in the article")

        # Create TextInput for analysis
        textInput = TextInput(
            content=article["content"],
            source="article",
            metadata={
                "url": url,
                "title": article["title"],
                "author": article["author"],
                "published_date": article["published_date"],
                "description": article["description"],
                "site_name": article["site_name"],
                "image_url": article["image_url"],
            },
        )

        return {
            "article_info": article,
            "text_input": textInput,
            "word_count": textInput.wordCount,
            "character_count": textInput.length,
            "estimated_reading_time": max(1, textInput.wordCount // 200),  # ~200 WPM
        }

    def analyzeMultipleArticles(
        self, urls: list[str], maxArticles: int = 5
    ) -> dict[str, Any]:
        """Analyze multiple articles and combine their content.

        Args:
            urls: List of article URLs
            maxArticles: Maximum number of articles to process

        Returns:
            Dictionary containing combined analysis data

        Raises:
            ValidationError: If input is invalid
            APIError: If no articles could be processed
        """
        if not urls or not isinstance(urls, list):
            raise ValidationError("URLs must be provided as a list")

        if len(urls) > maxArticles:
            urls = urls[:maxArticles]
            logger.warning(f"Limited to {maxArticles} articles")

        articles = []
        failed_urls = []

        for url in urls:
            try:
                article_data = self.analyzeArticle(url)
                articles.append(article_data)
                logger.info(f"Successfully processed article: {url}")
            except Exception as e:
                logger.error(f"Failed to process article {url}: {e}")
                failed_urls.append({"url": url, "error": str(e)})

        if not articles:
            raise ApiError("No articles could be processed successfully")

        # Combine all article content
        combined_content = "\n\n---ARTICLE BREAK---\n\n".join(
            [
                f"Title: {article['article_info']['title']}\n\n{article['text_input'].content}"
                for article in articles
            ]
        )

        # Create combined TextInput
        combined_metadata = {
            "source_count": len(articles),
            "failed_count": len(failed_urls),
            "articles": [
                {
                    "url": article["article_info"]["url"],
                    "title": article["article_info"]["title"],
                    "author": article["article_info"]["author"],
                    "site_name": article["article_info"]["site_name"],
                }
                for article in articles
            ],
            "failed_urls": failed_urls,
        }

        textInput = TextInput(
            content=combined_content,
            source="multiple_articles",
            metadata=combined_metadata,
        )

        return {
            "articles": articles,
            "text_input": textInput,
            "total_word_count": textInput.wordCount,
            "total_character_count": textInput.length,
            "processed_count": len(articles),
            "failed_count": len(failed_urls),
            "estimated_reading_time": max(1, textInput.wordCount // 200),
        }

    def getNewsHeadlines(
        self, query: str = "", category: str = ""
    ) -> list[dict[str, Any]]:
        """Get news headlines (mock implementation for demo).

        Args:
            query: Search query
            category: News category

        Returns:
            List of news headlines with URLs

        Note:
            This is a mock implementation. In production, you would integrate
            with a news API like NewsAPI, Google News API, or RSS feeds.
        """
        # Mock headlines for demonstration
        mock_headlines = [
            {
                "title": "Technology Advances in AI and Machine Learning",
                "url": "https://example.com/tech-ai-advances",
                "source": "Tech News",
                "published_at": "2025-06-20T10:00:00Z",
                "description": "Latest developments in artificial intelligence technology...",
            },
            {
                "title": "Global Climate Change Summit Reaches Agreement",
                "url": "https://example.com/climate-summit",
                "source": "Environmental News",
                "published_at": "2025-06-20T08:30:00Z",
                "description": "World leaders agree on new climate action framework...",
            },
            {
                "title": "Stock Market Shows Strong Growth This Quarter",
                "url": "https://example.com/market-growth",
                "source": "Financial Times",
                "published_at": "2025-06-20T07:15:00Z",
                "description": "Major indices post significant gains amid economic recovery...",
            },
        ]

        logger.info(
            "Returned mock news headlines (implement real news API for production)"
        )
        return mock_headlines

    def analyzeArticleContent(
        self, content: str, url: str | None = None
    ) -> dict[str, Any]:
        """Analyze pre-fetched article content.

        Args:
            content: Article content text
            url: Optional source URL

        Returns:
            Dictionary containing analysis results

        Raises:
            ApiError: If content cannot be analyzed
            ValidationError: If content is invalid
        """
        if not content or not content.strip():
            raise ValidationError("Article content cannot be empty")

        try:
            # Create TextInput for analysis
            textInput = TextInput(
                content=content,
                source="article",
                metadata={
                    "url": url,
                    "content_length": len(content),
                    "word_count": len(content.split()),
                },
            )

            # Perform sentiment analysis
            result = self.analyzer.analyzeText(textInput)

            # Convert to format expected by UI
            return {
                "primarySentiment": result.primarySentiment,
                "confidence": result.confidence,
                "scores": {score.label: score.score for score in result.scores},
                "contentLength": len(content),
                "wordCount": len(content.split()),
                "processingTime": result.processingTime,
                "url": url,
                "timestamp": result.timestamp,
                "modelVersion": result.modelVersion,
            }

        except Exception as e:
            logger.error(f"Failed to analyze article content: {e}")
            raise ApiError(f"Failed to analyze article content: {e}") from e

    def fetchArticleContent(self, url: str) -> str:
        """Fetch article content as a simple string.

        Args:
            url: Article URL

        Returns:
            Article content as string

        Raises:
            ApiError: If fetching or parsing fails
            ValidationError: If URL is invalid
        """
        article = self.fetchArticle(url)
        return article.get("content", "")
