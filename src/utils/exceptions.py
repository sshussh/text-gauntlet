"""Custom exceptions for Text Gauntlet application."""


class TextGauntletError(Exception):
    """Base exception for Text Gauntlet application."""

    def __init__(self, message: str, errorCode: str = None) -> None:
        """Initialize exception with message and optional error code."""
        super().__init__(message)
        self.message = message
        self.errorCode = errorCode or "UNKNOWN_ERROR"


class ModelError(TextGauntletError):
    """Exception raised when model operations fail."""

    def __init__(self, message: str, modelName: str = None) -> None:
        """Initialize model error with model name."""
        super().__init__(message, "MODEL_ERROR")
        self.modelName = modelName


class ApiError(TextGauntletError):
    """Exception raised when API operations fail."""

    def __init__(
        self, message: str, apiName: str = None, statusCode: int = None
    ) -> None:
        """Initialize API error with service name and status code."""
        super().__init__(message, "API_ERROR")
        self.apiName = apiName
        self.statusCode = statusCode


class ValidationError(TextGauntletError):
    """Exception raised when input validation fails."""

    def __init__(self, message: str, fieldName: str = None) -> None:
        """Initialize validation error with field name."""
        super().__init__(message, "VALIDATION_ERROR")
        self.fieldName = fieldName


class ConfigurationError(TextGauntletError):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str, configKey: str = None) -> None:
        """Initialize configuration error with config key."""
        super().__init__(message, "CONFIG_ERROR")
        self.configKey = configKey


class ResourceError(TextGauntletError):
    """Exception raised when resource operations fail."""

    def __init__(self, message: str, resourcePath: str = None) -> None:
        """Initialize resource error with resource path."""
        super().__init__(message, "RESOURCE_ERROR")
        self.resourcePath = resourcePath


class NetworkError(TextGauntletError):
    """Exception raised when network operations fail."""

    def __init__(self, message: str, url: str = None) -> None:
        """Initialize network error with URL."""
        super().__init__(message, "NETWORK_ERROR")
        self.url = url


class RateLimitError(ApiError):
    """Exception raised when API rate limits are exceeded."""

    def __init__(
        self, message: str, apiName: str = None, retryAfter: int = None
    ) -> None:
        """Initialize rate limit error with retry information."""
        super().__init__(message, apiName, 429)
        self.errorCode = "RATE_LIMIT_ERROR"
        self.retryAfter = retryAfter


class AuthenticationError(ApiError):
    """Exception raised when API authentication fails."""

    def __init__(self, message: str, apiName: str = None) -> None:
        """Initialize authentication error."""
        super().__init__(message, apiName, 401)
        self.errorCode = "AUTH_ERROR"


class AnalysisError(TextGauntletError):
    """Exception raised when text analysis operations fail."""

    def __init__(self, message: str, analysisType: str = None) -> None:
        """Initialize analysis error with analysis type."""
        super().__init__(message, "ANALYSIS_ERROR")
        self.analysisType = analysisType


class DataPersistenceError(TextGauntletError):
    """Exception raised when data persistence operations fail."""

    def __init__(self, message: str, operation: str = None) -> None:
        """Initialize data persistence error with operation type."""
        super().__init__(message, "DATA_PERSISTENCE_ERROR")
        self.operation = operation


class APILimitError(TextGauntletError):
    """Exception raised when API limits are exceeded."""

    def __init__(self, message: str, retryAfter: float = None) -> None:
        """Initialize API limit error with retry information."""
        super().__init__(message, "API_LIMIT_ERROR")
        self.retryAfter = retryAfter


class ExportError(TextGauntletError):
    """Exception raised when export operations fail."""

    def __init__(self, message: str, format: str = None) -> None:
        """Initialize export error with format information."""
        super().__init__(message, "EXPORT_ERROR")
        self.format = format


class CacheError(TextGauntletError):
    """Exception raised when cache operations fail."""

    def __init__(self, message: str, operation: str = None) -> None:
        """Initialize cache error with operation type."""
        super().__init__(message, "CACHE_ERROR")
        self.operation = operation
