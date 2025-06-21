# Text Gauntlet

## Table of Contents

- [About](#about)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [API Setup](#api-setup)
- [Development](#development)
- [Project Structure](#project-structure)
- [License](#license)

## About

A desktop sentiment analysis tool that makes understanding text emotions simple and fun.

Started as my personal project to explore AI-powered text analysis, Text Gauntlet has grown into a comprehensive app that analyzes sentiment in lyrics, movie reviews, news articles, and any text you throw at it. Built with Python and featuring a sleek dark theme.

Full documentation at [DOCUMENTATION.md](DOCUMENTATION.md).

## Features

### Core Analysis

- Real-time sentiment detection using Hugging Face transformers
- Batch processing for multiple texts
- Confidence scoring and detailed analytics

### Multiple Sources

- **Lyrics**: Search songs via Genius API and analyze emotional themes
- **Movies**: Aggregate review sentiment from TMDB data
- **News**: Extract and analyze articles from URLs
- **Text**: Paste anything - emails, posts, stories

### Data Management

- History tracking with search
- Export to JSON, CSV, or HTML
- Visual charts and statistics
- Local storage (your data stays private)

## Technology Stack

### Core Technologies

- **Python 3.13+**: Latest Python features and performance optimizations
- **CustomTkinter**: Modern, cross-platform GUI framework with native theming
- **PyTorch & Transformers**: State-of-the-art machine learning models for NLP
- **NLTK**: Comprehensive natural language processing toolkit

### Data Processing & Storage

- **Pandas**: High-performance data manipulation and analysis
- **BeautifulSoup4**: Robust web scraping and HTML parsing
- **JSON/CSV**: Standard data serialization formats for exports
- **SQLite**: Lightweight database for history tracking (built into Python)

### External APIs & Services

- **Genius API**: Comprehensive lyrics database with metadata
- **TMDB API**: Movie database with review aggregation
- **Web Scraping**: Direct content extraction for news articles

### Development & Quality

- **UV Package Manager**: Fast, modern Python dependency management
- **Ruff**: Lightning-fast Python linter and formatter
- **MyPy**: Static type checking for better code quality
- **Pytest**: Comprehensive testing framework

## Quick Start

**Requirements**: Python 3.13+, 1.5GB space, internet for API features

### Installation

```bash
# Clone and install
git clone https://github.com/yourusername/text-gauntlet.git
cd text-gauntlet
uv sync  # or: pip install -r requirements.txt

# Run
uv run src/main.py  # or: python src/main.py
```

## API Setup

Optional but recommended for full features:

**Genius API** (lyrics): Get token from [genius.com/api-clients](https://genius.com/api-clients)  
**TMDB API** (movies): Get key from [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

```bash
cp .env.example .env
# Edit .env and add your keys:
# GENIUS_ACCESS_TOKEN="your_token"
# TMDB_API_KEY="your_key"
```

## Development

```bash
uv sync --dev
uv run ruff check src/    # linting
uv run mypy src/          # type checking
uv run pytest tests/      # testing
```

**Architecture**: Clean modular design with separate UI, services, and core analysis components. Type hints throughout, comprehensive error handling, local data processing.

### Project Structure

```text
text-gauntlet/
├── src/
│   ├── main.py                   # Application entry point
│   ├── config/                   # App settings and configuration
│   │   ├── settings.py           # Environment handling and app config
│   │   └── __init__.py           # Package initialization
│   ├── core/                     # Core business logic
│   │   ├── models.py             # Data structures and models
│   │   ├── text_processor.py     # Text cleaning and preprocessing
│   │   └── sentiment_analyzer.py # ML model interface
│   ├── services/                 # External API integrations
│   │   ├── genius_service.py     # Genius API client
│   │   ├── tmdb_service.py       # TMDB API client
│   │   ├── news_service.py       # Web scraping for news
│   │   └── analytics_service.py  # Data analytics and reporting
│   ├── ui/                       # User interface components
│   │   ├── main_window.py        # Main application window
│   │   ├── components/           # Reusable UI components
│   │   └── pages/                # Individual page implementations
│   └── utils/                    # Helper functions and utilities
│       ├── logger.py             # Logging setup
│       ├── file_manager.py       # File operations
│       └── validators.py         # Input validation
├── assets/                       # Static resources
│   ├── themes/                   # UI theme files
│   └── images/                   # App icons and graphics
└── docs/                         # Documentation
```

## License

MIT License - see [LICENSE](LICENSE) for details.
