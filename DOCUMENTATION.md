# Text Gauntlet - Complete Documentation

## Table of Contents

- [Overview](#overview)
- [Installation & Setup](#installation--setup)
- [API Configuration](#api-configuration)
- [User Guide](#user-guide)
- [Features Deep Dive](#features-deep-dive)
- [Architecture & Design](#architecture--design)
- [Development Guide](#development-guide)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Security & Privacy](#security--privacy)
- [Performance](#performance)
- [Contributing](#contributing)
- [Release Notes](#release-notes)

## Overview

Text Gauntlet is a desktop sentiment analysis application that makes understanding emotions in text simple and accessible. Built as a personal project to explore AI-powered text analysis, it has evolved into a comprehensive tool for analyzing sentiment across multiple data sources.

### Key Features

- **Real-time sentiment analysis** using state-of-the-art transformer models
- **Multi-source content analysis**: lyrics, movies, news articles, and custom text
- **Comprehensive data management** with history tracking and export capabilities
- **Modern desktop interface** with dark theme and intuitive navigation
- **Privacy-focused** with local processing and secure credential management

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **Python Version**: 3.13 or higher
- **Memory**: 4GB RAM minimum (8GB recommended for batch processing)
- **Storage**: 1.5GB available space
- **Network**: Internet connection for API features (basic text analysis works offline)

## Installation & Setup

### Method 1: Using UV (Recommended)

UV is a fast, modern Python package manager that handles dependencies efficiently.

```bash
# Clone the repository
git clone https://github.com/yourusername/text-gauntlet.git
cd text-gauntlet

# Install dependencies
uv sync

# Run the application
uv run src/main.py
```

### Method 2: Traditional Pip Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/text-gauntlet.git
cd text-gauntlet

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Verification

After installation, verify the setup by running:

```bash
# Check Python version
python --version  # Should be 3.13+

# Test basic functionality
python -c "import torch, transformers, customtkinter; print('All dependencies installed successfully')"
```

## API Configuration

Text Gauntlet supports optional external APIs that enhance functionality. The application works without these APIs but provides a richer experience when configured.

### Genius API (Lyrics Analysis)

The Genius API provides access to a comprehensive database of song lyrics and metadata.

**Setup Steps:**

1. Visit [Genius API Clients](https://genius.com/api-clients)
2. Create a new application with any name
3. Copy the "Client Access Token" from your app dashboard

**Features Enabled:**

- Song lyric search and retrieval
- Artist and album metadata
- Lyric annotation and popularity data
- Verse-by-verse analysis capabilities

**Rate Limits:** 1000 requests per day (free tier)

### TMDB API (Movie Analysis)

The Movie Database API provides movie information and review data.

**Setup Steps:**

1. Register at [The Movie Database](https://www.themoviedb.org/settings/api)
2. Request an API key (approval is typically instant)
3. Copy your API key from the settings page

**Features Enabled:**

- Movie search and metadata
- User review aggregation
- Box office and popularity data
- Genre and cast information

**Rate Limits:** 1000 requests per day (free tier)

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
# Genius API Configuration
GENIUS_ACCESS_TOKEN="your_genius_client_access_token_here"

# TMDB API Configuration
TMDB_API_KEY="your_tmdb_api_key_here"

# Optional: Logging Configuration
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Optional: Application Settings
THEME="oblivion"  # Default theme name
```

### API Testing

Test your API configuration:

```bash
# Test Genius API
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('GENIUS_ACCESS_TOKEN')
print('Genius API:', 'Configured' if token else 'Not configured')
"

# Test TMDB API
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('TMDB_API_KEY')
print('TMDB API:', 'Configured' if key else 'Not configured')
"
```

## User Guide

### Getting Started

1. **Launch the Application**

   ```bash
   uv run src/main.py  # or: python src/main.py
   ```

2. **Interface Overview**
   - **Sidebar Navigation**: Switch between different analysis modes
   - **Main Content Area**: Input text and view results
   - **Results Panel**: Displays sentiment scores and analytics
   - **History Panel**: Access previous analyses

3. **Basic Text Analysis**
   - Navigate to "Text Analysis" page
   - Paste or type text in the input area
   - Click "Analyze" to process the text
   - View sentiment scores and confidence levels

### Text Analysis

**Input Methods:**

- Direct text input (paste or type)
- File upload (supports .txt, .md, .csv files)
- Batch processing (multiple texts at once)

**Output Information:**

- **Sentiment Classification**: Positive, Negative, or Neutral
- **Confidence Score**: How certain the model is (0-100%)
- **Emotional Breakdown**: Joy, anger, fear, surprise, etc.
- **Key Phrases**: Important words that influenced the sentiment

**Advanced Options:**

- Adjust confidence threshold
- Select different model variants
- Enable/disable preprocessing steps

### Lyrics Analysis

**Search and Analysis:**

1. Navigate to "Lyrics Analysis" page
2. Enter song title and artist name
3. Select from search results
4. View comprehensive lyric sentiment analysis

**Features:**

- **Verse-by-verse analysis**: See how sentiment changes throughout the song
- **Artist profiling**: Analyze multiple songs from the same artist
- **Genre trends**: Compare sentiment across different musical genres
- **Lyric highlighting**: Visual indicators of positive/negative phrases

**Search Tips:**

- Use fuzzy matching: "Bohemian Rhaps" will find "Bohemian Rhapsody"
- Include artist name for better accuracy
- Use quotation marks for exact matches

### Movie Analysis

**Movie Search and Reviews:**

1. Navigate to "Movie Analysis" page
2. Search by movie title, genre, or year
3. Select a movie from results
4. View aggregated review sentiment

**Analysis Features:**

- **Review Sentiment**: Aggregate analysis of user and critic reviews
- **Trend Analysis**: How sentiment correlates with ratings and box office
- **Genre Comparison**: Compare sentiment across different movie genres
- **Time-based Analysis**: See how sentiment changes over time

**Search Filters:**

- Release year range
- Genre categories
- Popularity thresholds
- Rating minimums

### News Analysis

**Article Analysis:**

1. Navigate to "News Analysis" page
2. Paste article URL or text content
3. View sentiment analysis results
4. Track sentiment trends by source

**Supported Sources:**

- Most major news websites
- Blog posts and articles
- Social media posts (when accessible)
- RSS feed content

**Features:**

- **Source tracking**: Monitor sentiment patterns by news outlet
- **Topic clustering**: Group related articles by sentiment
- **Trend monitoring**: Track how sentiment changes over time
- **Bias detection**: Identify potential editorial bias in coverage

### Data Management

**History Tracking:**

- All analyses are automatically saved
- Search through past analyses
- Filter by date, source, or sentiment
- Export individual or batch results

**Export Options:**

1. **JSON Format** (for developers):

   ```json
   {
     "text": "Sample text",
     "sentiment": "positive",
     "confidence": 0.85,
     "timestamp": "2025-06-21T09:30:00Z"
   }
   ```

2. **CSV Format** (for spreadsheets):

   ```csv
   text,sentiment,confidence,timestamp
   "Sample text",positive,0.85,2025-06-21T09:30:00Z
   ```

3. **HTML Format** (for presentations):
   - Formatted reports with charts
   - Visual sentiment indicators
   - Summary statistics

**Privacy Controls:**

- Delete individual analyses
- Clear all history
- Export before deletion
- Local data storage only

## Features Deep Dive

### Sentiment Analysis Engine

**Model Architecture:**

- Base model: RoBERTa (Robustly Optimized BERT Pretraining Approach)
- Fine-tuned on: Twitter sentiment data, movie reviews, and general text
- Model size: ~500MB compressed
- Inference speed: ~50ms per text on modern hardware

**Preprocessing Pipeline:**

1. **Text Cleaning**: Remove URLs, mentions, special characters
2. **Normalization**: Convert to lowercase, standardize whitespace
3. **Tokenization**: Split text into meaningful units
4. **Encoding**: Convert to model-compatible format

**Confidence Scoring:**

- Based on model's probability distribution
- Adjusted for text length and complexity
- Calibrated against validation datasets
- Threshold recommendations: >0.7 for high confidence

### Multi-language Support

**Currently Supported:**

- English (primary, fully supported)
- Spanish (experimental)
- French (experimental)

**Planned Languages:**

- German, Italian, Portuguese
- Chinese (Simplified), Japanese
- Arabic, Russian

### Batch Processing

**Capabilities:**

- Process up to 1000 texts simultaneously
- Progress tracking with cancellation support
- Memory-efficient streaming processing
- Automatic result aggregation

**File Formats Supported:**

- Plain text (.txt)
- CSV files with text column
- JSON arrays of text objects
- Markdown files (.md)

**Usage Example:**

```python
# Via command line
python src/main.py --batch input_file.csv --output results.json

# Via UI
# 1. Navigate to Text Analysis
# 2. Click "Batch Upload"
# 3. Select file
# 4. Configure options
# 5. Start processing
```

## Architecture & Design

### System Architecture

Text Gauntlet follows a modular architecture with clear separation of concerns:

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layer      │    │  Service Layer  │    │   Core Layer    │
│                 │    │                 │    │                 │
│ • Main Window   │────│ • Genius API    │────│ • Text Processor│
│ • Page Router   │    │ • TMDB API      │    │ • Sentiment AI  │
│ • Components    │    │ • News Scraper  │    │ • Data Models   │
│ • Theme Manager │    │ • Analytics     │    │ • Validators    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │
                       ┌─────────────────┐
                       │  Utils Layer    │
                       │                 │
                       │ • Logger        │
                       │ • File Manager  │
                       │ • Config        │
                       └─────────────────┘
```

### Design Patterns

**Model-View-Controller (MVC):**

- **Models**: Data structures in `core/models.py`
- **Views**: UI components in `ui/` directory
- **Controllers**: Service layer orchestrates business logic

**Dependency Injection:**

- Services are injected into UI components
- Enables testing with mock services
- Reduces coupling between components

**Observer Pattern:**

- Theme changes notify all UI components
- Analysis progress updates UI in real-time
- Error handling propagates through event system

**Factory Pattern:**

- Service creation based on configuration
- Model selection based on requirements
- Export format selection

### Data Flow

1. **User Input** → UI Component
2. **Input Validation** → Core Validators
3. **Service Call** → External APIs or Local Processing
4. **Data Processing** → Core Models and Analysis
5. **Result Storage** → Local Database
6. **UI Update** → Display Results
7. **Export Option** → File Generation

### Error Handling Strategy

**Graceful Degradation:**

- API failures don't crash the application
- Offline mode for core text analysis
- User-friendly error messages
- Automatic retry with exponential backoff

**Logging Levels:**

- **DEBUG**: Detailed execution flow
- **INFO**: Normal operations and state changes
- **WARNING**: Recoverable issues
- **ERROR**: Non-fatal errors with fallback
- **CRITICAL**: Fatal errors requiring restart

### Security Architecture

**Credential Management:**

- Environment variables for API keys
- No hardcoded secrets in source code
- Encrypted storage option for sensitive data
- Secure defaults for all configurations

**Data Protection:**

- Local processing by default
- Optional cloud features clearly marked
- User consent for any external data transmission
- Automatic cleanup of temporary files

**Input Validation:**

- All user inputs sanitized
- File type restrictions
- Size limits on uploads
- URL validation for news articles

## Development Guide

### Setting Up Development Environment

**Prerequisites:**

- Python 3.13+
- Git
- UV package manager (recommended)

**Development Setup:**

```bash
# Clone and setup
git clone https://github.com/yourusername/text-gauntlet.git
cd text-gauntlet

# Install development dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Verify setup
uv run python -m pytest tests/ -v
```

### Code Style and Standards

**Python Style Guide:**

- Follow PEP 8 with line length of 88 characters
- Use type hints for all function signatures
- Docstrings for all public functions and classes
- Descriptive variable and function names

**Linting and Formatting:**

```bash
# Format code
uv run ruff format src/

# Check for issues
uv run ruff check src/

# Type checking
uv run mypy src/

# Run all checks
uv run python scripts/check_quality.py
```

**Git Workflow:**

- Main branch is protected
- Feature branches for all changes
- Descriptive commit messages
- Pull requests required for merges

### Testing Strategy

**Test Structure:**

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for service interactions
├── ui/            # UI component tests
└── fixtures/      # Test data and mock objects
```

**Running Tests:**

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src

# Specific test file
uv run pytest tests/unit/test_sentiment_analyzer.py

# Integration tests only
uv run pytest tests/integration/
```

**Test Categories:**

- **Unit Tests**: Individual function/class testing
- **Integration Tests**: Service interaction testing
- **UI Tests**: User interface component testing
- **API Tests**: External service integration testing

### Adding New Features

**Feature Development Process:**

1. **Planning Phase:**
   - Create GitHub issue with feature specification
   - Design API and data models
   - Plan UI/UX changes
   - Estimate effort and timeline

2. **Implementation Phase:**
   - Create feature branch
   - Implement core functionality
   - Add comprehensive tests
   - Update documentation

3. **Integration Phase:**
   - Integrate with existing codebase
   - Update UI components
   - Add configuration options
   - Test edge cases

4. **Review Phase:**
   - Code review by maintainers
   - Performance testing
   - Security review
   - Documentation review

**Example: Adding New Data Source**

1. **Create Service Class:**

   ```python
   # src/services/new_source_service.py
   class NewSourceService:
       def __init__(self, api_key: str):
           self.api_key = api_key
       
       def search(self, query: str) -> List[SearchResult]:
           # Implementation
           pass
   ```

2. **Add Configuration:**

   ```python
   # src/config/settings.py
   NEW_SOURCE_API_KEY = os.getenv("NEW_SOURCE_API_KEY")
   ```

3. **Create UI Page:**

   ```python
   # src/ui/pages/new_source_page.py
   class NewSourcePage(BasePage):
       def __init__(self, parent, service):
           super().__init__(parent)
           self.service = service
   ```

4. **Add Tests:**

   ```python
   # tests/unit/test_new_source_service.py
   def test_search_functionality():
       # Test implementation
       pass
   ```

### Performance Optimization

**Profiling Tools:**

```bash
# Profile application startup
uv run python -m cProfile -o startup.prof src/main.py

# Memory profiling
uv run python -m memory_profiler src/main.py

# Line-by-line profiling
uv run kernprof -l -v src/core/sentiment_analyzer.py
```

**Optimization Guidelines:**

- Cache frequently accessed data
- Use lazy loading for large models
- Optimize database queries
- Minimize UI updates during processing
- Use background threads for long operations

### Debugging

**Debug Mode:**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uv run src/main.py

# Debug specific module
export LOG_LEVEL=DEBUG
export DEBUG_MODULES="sentiment_analyzer,genius_service"
uv run src/main.py
```

**Common Debug Scenarios:**

- API connection issues
- Model loading problems
- UI threading issues
- File I/O errors
- Memory usage problems

## API Reference

### Core Classes

#### SentimentAnalyzer

```python
class SentimentAnalyzer:
    """Main sentiment analysis engine."""
    
    def __init__(self, model_name: str = "default"):
        """Initialize analyzer with specified model."""
        
    def analyze(self, text: str) -> AnalysisResult:
        """Analyze sentiment of given text."""
        
    def analyze_batch(self, texts: List[str]) -> List[AnalysisResult]:
        """Analyze multiple texts efficiently."""
        
    def get_confidence_threshold(self) -> float:
        """Get current confidence threshold."""
        
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set confidence threshold (0.0-1.0)."""
```

#### AnalysisResult

```python
@dataclass
class AnalysisResult:
    """Result of sentiment analysis."""
    
    text: str
    sentiment: str  # "positive", "negative", "neutral"
    confidence: float  # 0.0-1.0
    emotions: Dict[str, float]  # emotion -> confidence
    timestamp: datetime
    metadata: Dict[str, Any]
```

#### GeniusService

```python
class GeniusService:
    """Interface to Genius API for lyrics."""
    
    def __init__(self, access_token: str):
        """Initialize with API access token."""
        
    def search_songs(self, query: str, limit: int = 10) -> List[Song]:
        """Search for songs by title/artist."""
        
    def get_lyrics(self, song_id: int) -> Optional[str]:
        """Get lyrics for specific song."""
        
    def get_artist_songs(self, artist_id: int) -> List[Song]:
        """Get all songs for an artist."""
```

#### TMDBService

```python
class TMDBService:
    """Interface to TMDB API for movies."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        
    def search_movies(self, query: str) -> List[Movie]:
        """Search for movies by title."""
        
    def get_movie_reviews(self, movie_id: int) -> List[Review]:
        """Get reviews for specific movie."""
        
    def get_popular_movies(self, page: int = 1) -> List[Movie]:
        """Get currently popular movies."""
```

### Configuration

#### Settings Class

```python
class Settings:
    """Application configuration management."""
    
    # Core settings
    MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_TEXT_LENGTH: int = 512
    
    # API settings
    GENIUS_ACCESS_TOKEN: Optional[str] = None
    TMDB_API_KEY: Optional[str] = None
    
    # UI settings
    THEME: str = "oblivion"
    WINDOW_SIZE: Tuple[int, int] = (1200, 800)
    
    # Data settings
    DATA_DIR: Path = Path("data")
    EXPORT_DIR: Path = Path("exports")
    LOG_LEVEL: str = "INFO"
```

### Event System

#### Event Types

```python
class EventType(Enum):
    """Application event types."""
    
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"
    THEME_CHANGED = "theme_changed"
    API_ERROR = "api_error"
    DATA_EXPORTED = "data_exported"
```

#### Event Handler

```python
class EventHandler:
    """Handle application events."""
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to event type."""
        
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from event type."""
        
    def emit(self, event_type: EventType, data: Any = None) -> None:
        """Emit event to all subscribers."""
```

## Troubleshooting

### Common Issues

#### Installation Problems

**Issue: Python version compatibility**

```bash
# Check Python version
python --version

# Should be 3.13 or higher
# If not, install from python.org or use pyenv
```

**Issue: Dependencies not installing**

```bash
# Clear package cache
uv cache clean

# Reinstall from scratch
rm -rf .venv uv.lock
uv sync
```

**Issue: UV not found**

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

#### Runtime Issues

**Issue: Model download fails**

```
Error: Failed to download model
```

**Solution:**

```bash
# Check internet connection
ping huggingface.co

# Manual model download
python -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
model_name = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
print('Model downloaded successfully')
"
```

**Issue: API authentication fails**

```
Error: 401 Unauthorized
```

**Solution:**

1. Verify API keys in `.env` file
2. Check key permissions on provider website
3. Test with curl:

   ```bash
   # Test Genius API
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.genius.com/account
   
   # Test TMDB API
   curl "https://api.themoviedb.org/3/configuration?api_key=YOUR_KEY"
   ```

**Issue: UI doesn't start**

```
Error: No module named 'customtkinter'
```

**Solution:**

```bash
# Check virtual environment
which python

# Reinstall UI dependencies
uv sync --group ui

# Or manually
pip install customtkinter
```

#### Performance Issues

**Issue: Slow analysis speed**

**Diagnosis:**

```bash
# Check CPU usage
top -p $(pgrep -f "python.*main.py")

# Check memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

**Solutions:**

- Close other resource-intensive applications
- Increase confidence threshold to reduce processing
- Use batch processing for multiple texts
- Consider GPU acceleration if available

**Issue: High memory usage**

**Solutions:**

- Reduce batch size for large datasets
- Clear history periodically
- Restart application if memory usage grows
- Check for memory leaks in custom code

#### Data Issues

**Issue: Export fails**

```
Error: Permission denied writing to file
```

**Solutions:**

- Check file permissions
- Ensure export directory exists
- Close file if open in another application
- Use different export location

**Issue: History not loading**

```
Error: Database locked
```

**Solutions:**

- Close other instances of the application
- Check database file permissions
- Backup and recreate database if corrupted:

  ```bash
  cp data/history.db data/history.db.backup
  rm data/history.db
  # Restart application to recreate
  ```

### Getting Help

**GitHub Issues:**

- Search existing issues first
- Provide detailed error messages
- Include system information
- Attach log files if possible

**Log Files:**

```bash
# Find log files
find . -name "*.log" -type f

# View recent logs
tail -f logs/application.log

# Search for errors
grep -i error logs/application.log
```

**System Information:**

```bash
# Generate system report
python scripts/system_info.py > system_report.txt
```

## Security & Privacy

### Data Privacy

**Local Processing:**

- All sentiment analysis happens on your machine
- No text data sent to external servers (except for API features)
- User data never shared with third parties
- Complete control over your analysis history

**API Data Handling:**

- Only search queries sent to external APIs
- No personal text analysis data transmitted
- API keys stored securely in environment variables
- Network requests use HTTPS encryption

**Data Retention:**

- History stored locally in SQLite database
- User controls all data deletion
- Export options available before deletion
- No automatic cloud backups

### Security Measures

**Credential Security:**

- API keys stored in environment variables
- No credentials in source code or logs
- Secure defaults for all configurations
- Optional credential encryption

**Input Validation:**

- All user inputs sanitized and validated
- File upload restrictions and scanning
- URL validation for news articles
- Protection against code injection

**Network Security:**

- HTTPS for all external API calls
- Certificate validation enabled
- Request timeout limits
- Rate limiting to prevent abuse

### Privacy Controls

**Data Management:**

- View all stored data
- Export data in multiple formats
- Delete individual analyses
- Clear all history
- Disable history tracking

**Network Controls:**

- Offline mode for core features
- API usage indicators
- Network request logging
- Proxy support for corporate environments

### Compliance

**GDPR Compliance:**

- User consent for data processing
- Right to data portability (export)
- Right to erasure (delete)
- Data minimization principles
- Privacy by design architecture

**Security Best Practices:**

- Regular dependency updates
- Vulnerability scanning
- Security-focused code review
- Minimal privilege principles
- Secure error handling

## Performance

### In-Depth System Requirements

**Minimum Requirements:**

- CPU: Dual-core 2.0 GHz
- RAM: 4GB
- Storage: 500MB free space
- Python: 3.13+

**Recommended Requirements:**

- CPU: Quad-core 3.0 GHz or better
- RAM: 8GB or more
- Storage: 2GB free space (for models and data)
- SSD storage for better performance

### Performance Metrics

**Startup Performance:**

- Cold start: ~3-5 seconds
- Warm start: ~1-2 seconds
- Model loading: ~2-3 seconds
- UI initialization: ~1 second

**Analysis Performance:**

- Single text (100 words): ~50-100ms
- Batch processing (100 texts): ~5-10 seconds
- Large document (1000+ words): ~200-500ms
- API requests: ~1-3 seconds (network dependent)

**Memory Usage:**

- Base application: ~200MB
- With loaded models: ~800MB-1.2GB
- Peak during batch processing: ~1.5-2GB
- Long-running sessions: Stable memory usage

### Optimization Tips

**For Better Performance:**

1. Use SSD storage for faster model loading
2. Close unnecessary applications
3. Increase virtual memory if needed
4. Use batch processing for multiple analyses
5. Adjust confidence threshold for speed

**For Lower Memory Usage:**

1. Clear history periodically
2. Use smaller batch sizes
3. Close unused analysis pages
4. Restart application for long sessions
5. Monitor system resources

**For Network Performance:**

1. Use stable internet connection
2. Configure proxy if needed
3. Monitor API rate limits
4. Cache API responses when possible
5. Use offline mode when appropriate

### Monitoring

**Built-in Monitoring:**

- Performance metrics in debug mode
- Memory usage tracking
- API response time logging
- Error rate monitoring

**External Monitoring:**

```bash
# Monitor CPU usage
top -p $(pgrep -f "python.*main.py")

# Monitor memory usage
ps aux | grep "python.*main.py"

# Monitor network usage
netstat -p | grep python
```

## Contributing

### How to Contribute

**Types of Contributions:**

- Bug reports and fixes
- Feature requests and implementations
- Documentation improvements
- Performance optimizations
- UI/UX enhancements
- Test coverage improvements

### Development Workflow

**Getting Started:**

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch
4. Make your changes
5. Add tests for new functionality
6. Update documentation
7. Submit a pull request

**Branch Naming:**

- `feature/description` for new features
- `bugfix/description` for bug fixes
- `docs/description` for documentation
- `refactor/description` for refactoring

**Commit Messages:**

```text
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation
- style: formatting
- refactor: code restructuring
- test: adding tests
- chore: maintenance
```

### Code Review Process

**Pull Request Requirements:**

- Clear description of changes
- Link to related issues
- All tests passing
- Code coverage maintained
- Documentation updated
- Reviewer approval

**Review Criteria:**

- Code quality and style
- Test coverage
- Performance impact
- Security considerations
- Documentation completeness
- Backward compatibility

### Testing Requirements

**Required Tests:**

- Unit tests for new functions
- Integration tests for API changes
- UI tests for interface changes
- Performance tests for optimizations

**Test Coverage:**

- Maintain >80% overall coverage
- 100% coverage for critical paths
- Test both success and error cases
- Include edge case testing

### Documentation Standards

**Required Documentation:**

- Docstrings for all public functions
- README updates for new features
- API documentation for interfaces
- User guide updates
- Installation instructions

## Release Notes

### Version 2.0.0 (Current)

**Major Features:**

- Complete UI overhaul with modern dark theme
- Multi-source analysis (lyrics, movies, news)
- Comprehensive data export capabilities
- Real-time sentiment analysis
- Local data processing and privacy

**Technical Improvements:**

- Python 3.13 compatibility
- Modern dependency management with UV
- Comprehensive type hints
- Modular architecture
- Extensive test coverage

**Security Enhancements:**

- Secure credential management
- Input validation and sanitization
- Local processing by default
- HTTPS for all external requests

### Version 1.0.0 (Legacy)

**Initial Features:**

- Basic text sentiment analysis
- Simple GUI interface
- CSV export functionality
- Basic error handling

### Upcoming Features (Roadmap)

**Version 2.1.0 (Planned):**

- Multi-language support
- Advanced emotion detection
- Custom model training
- API rate limiting improvements
- Performance optimizations

**Version 2.2.0 (Future):**

- Cloud storage integration (optional)
- Collaborative analysis features
- Advanced visualization
- Mobile companion app
- Browser extension

**Long-term Goals:**

- Real-time streaming analysis
- Machine learning model marketplace
- Enterprise features
- Advanced analytics dashboard
- Integration with popular tools

---

## Appendix

### Supported File Formats

**Input Formats:**

- `.txt`: Plain text files
- `.csv`: Comma-separated values
- `.json`: JSON arrays or objects
- `.md`: Markdown files
- `.xml`: XML documents (basic support)

**Export Formats:**

- `.json`: Structured data format
- `.csv`: Spreadsheet compatible
- `.html`: Formatted reports
- `.pdf`: Professional reports (future)

### API Rate Limits

**Genius API:**

- 1000 requests per day (free)
- 10 requests per minute
- Automatic retry with backoff

**TMDB API:**

- 1000 requests per day (free)
- 40 requests per 10 seconds
- Automatic throttling

### Model Information

**Primary Model:**

- Name: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Size: ~500MB
- Languages: English (primary)
- Accuracy: ~85% on test datasets
- Speed: ~50ms per analysis

**Alternative Models:**

- `distilbert-base-uncased-finetuned-sst-2-english`
- `nlptown/bert-base-multilingual-uncased-sentiment`
- Custom models (user-provided)

### Keyboard Shortcuts

**Global Shortcuts:**

- `Ctrl+N`: New analysis
- `Ctrl+O`: Open file
- `Ctrl+S`: Save results
- `Ctrl+E`: Export data
- `Ctrl+H`: Show history
- `Ctrl+Q`: Quit application

**Analysis Shortcuts:**

- `Ctrl+Enter`: Analyze text
- `Ctrl+R`: Clear input
- `Ctrl+C`: Copy results
- `F5`: Refresh data
- `Esc`: Cancel operation

### Environment Variables

**Core Settings:**

```env
# Application
LOG_LEVEL=INFO
THEME=oblivion
DEBUG=false

# APIs
GENIUS_ACCESS_TOKEN=your_token
TMDB_API_KEY=your_key

# Data
DATA_DIR=./data
EXPORT_DIR=./exports
HISTORY_SIZE=10000

# Performance
BATCH_SIZE=100
CACHE_SIZE=1000
TIMEOUT=30
```

### Troubleshooting Commands

**Diagnostic Commands:**

```bash
# System information
python scripts/system_info.py

# Configuration check
python scripts/check_config.py

# API connectivity test
python scripts/test_apis.py

# Performance benchmark
python scripts/benchmark.py

# Database integrity check
python scripts/check_database.py
```

This comprehensive documentation covers all aspects of Text Gauntlet, from basic usage to advanced development. It serves as the complete reference for users, developers, and contributors.
