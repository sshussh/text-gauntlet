"""Application settings and configuration management."""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


@dataclass
class ModelConfig:
    """Configuration for sentiment analysis models."""

    primaryModel: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    maxTextLength: int = 512
    confidenceThreshold: float = 0.5


@dataclass
class ApiConfig:
    """Configuration for external API services."""

    # API Keys (should be set via environment variables)
    geniusApiKey: str | None = None
    tmdbApiKey: str | None = None

    # Request settings
    requestTimeout: int = 30
    maxRetries: int = 3
    rateLimitPerMinute: int = 60
    cacheExpiry: int = 3600  # 1 hour in seconds


@dataclass
class UiConfig:
    """Configuration for user interface."""

    defaultTheme: str = "Oblivion"
    widgetScaling: float = 1.0
    windowWidth: int = 1000
    windowHeight: int = 450


@dataclass
class LoggingConfig:
    """Configuration for logging system."""

    level: str = "INFO"
    enableFileLogging: bool = True
    logRotation: bool = True
    maxLogSize: int = 10 * 1024 * 1024  # 10MB
    backupCount: int = 5


@dataclass
class DataConfig:
    """Configuration for data persistence."""

    dataDirectory: str = "data"
    maxHistoryRecords: int = 10000


@dataclass
class CacheConfig:
    """Configuration for caching system."""

    enabled: bool = True
    maxSize: int = 1000
    ttlSeconds: int = 3600
    cleanupInterval: int = 15  # minutes


class Settings:
    """Main settings class for Text Gauntlet application."""

    def __init__(self) -> None:
        """Initialize settings with default values and load from environment."""
        self._loadEnvironment()

        # Get application paths
        self.appRoot = Path(__file__).parent.parent.parent
        self.assetsPath = self.appRoot / "assets"
        self.themesPath = self.assetsPath / "themes"

        # Set up data directory structure
        self.dataPath = self.appRoot / "data"
        self.logsPath = self.dataPath / "logs"
        self.settingsPath = self.dataPath / "settings"
        self.databasePath = self.dataPath / "database"

        # Create directories if they don't exist
        self.dataPath.mkdir(exist_ok=True)
        self.logsPath.mkdir(exist_ok=True)
        self.settingsPath.mkdir(exist_ok=True)
        self.databasePath.mkdir(exist_ok=True)

        # Initialize configuration sections
        self.model = ModelConfig()
        self.api = ApiConfig(
            geniusApiKey=os.getenv("GENIUS_ACCESS_TOKEN"),
            tmdbApiKey=os.getenv("TMDB_API_KEY"),
        )
        self.ui = UiConfig()
        self.logging = LoggingConfig()
        self.data = DataConfig()
        self.cache = CacheConfig()

        # Load theme preference
        self._loadThemePreference()

        # Load saved settings from preferences file
        self.load()

    def _loadEnvironment(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv(override=True)

    def _loadThemePreference(self) -> None:
        """Load theme preference from preferences.json file."""
        try:
            # Try to load from preferences.json first
            prefsPath = self.settingsPath / "preferences.json"
            if prefsPath.exists():
                import json

                with open(prefsPath) as f:
                    preferences = json.load(f)
                    if "ui" in preferences and "defaultTheme" in preferences["ui"]:
                        theme = preferences["ui"]["defaultTheme"]
                        if theme in ["Oblivion", "blue", "green", "dark-blue"]:
                            self.ui.defaultTheme = theme
                            return

            # Fallback: check for legacy launch.txt file and migrate
            launchFile = self.appRoot / "launch.txt"
            if launchFile.exists():
                theme = launchFile.read_text().strip()
                if theme in ["Oblivion", "blue", "green", "dark-blue"]:
                    self.ui.defaultTheme = theme
                    # Migrate to preferences.json and remove launch.txt
                    self._migrateThemePreference()
                else:
                    self.ui.defaultTheme = "Oblivion"
            else:
                self.ui.defaultTheme = "Oblivion"

        except Exception as e:
            logging.warning(f"Could not load theme preference - {e}")
            self.ui.defaultTheme = "Oblivion"

    def _migrateThemePreference(self) -> None:
        """Migrate theme preference from launch.txt to preferences.json."""
        try:
            # Save current settings (which includes the theme)
            self.save()

            # Remove old launch.txt file
            launchFile = self.appRoot / "launch.txt"
            if launchFile.exists():
                launchFile.unlink()
                logging.info(
                    "Migrated theme preference from launch.txt to preferences.json"
                )
        except Exception as e:
            logging.warning(f"Could not migrate theme preference - {e}")

    def saveThemePreference(self, theme: str) -> None:
        """Save theme preference to preferences.json file."""
        try:
            self.ui.defaultTheme = theme
            # Use the existing save method which saves to preferences.json
            self.save()
        except Exception as e:
            logging.error(f"Could not save theme preference - {e}")

    def getThemePath(self, themeName: str = None) -> Path:
        """Get path to theme file."""
        theme = themeName or self.ui.defaultTheme

        if theme == "Oblivion":
            return self.themesPath / "oblivion.json"
        else:
            # For built-in themes, return the theme name
            return Path(theme)

    def getAssetPath(self, assetName: str) -> Path:
        """Get path to asset file."""
        return self.assetsPath / assetName

    def getDataPath(self) -> Path:
        """Get the data storage directory path."""
        dataPath = self.appRoot / self.data.dataDirectory
        dataPath.mkdir(exist_ok=True)
        return dataPath

    def getSettingsPath(self) -> Path:
        """Get the settings storage directory path."""
        settingsPath = self.dataPath / "settings"
        settingsPath.mkdir(exist_ok=True)
        return settingsPath

    def getDatabasePath(self) -> Path:
        """Get the database storage directory path."""
        databasePath = self.dataPath / "database"
        databasePath.mkdir(exist_ok=True)
        return databasePath

    def toDict(self) -> dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "model": self.model.__dict__,
            "api": self.api.__dict__,
            "ui": self.ui.__dict__,
            "logging": self.logging.__dict__,
            "data": self.data.__dict__,
            "cache": self.cache.__dict__,
        }

    def updateFromDict(self, config: dict[str, Any]) -> None:
        """Update settings from dictionary."""
        if "model" in config:
            for key, value in config["model"].items():
                if hasattr(self.model, key):
                    setattr(self.model, key, value)

        if "api" in config:
            for key, value in config["api"].items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)

        if "ui" in config:
            for key, value in config["ui"].items():
                if hasattr(self.ui, key):
                    setattr(self.ui, key, value)

        if "logging" in config:
            for key, value in config["logging"].items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)

        if "data" in config:
            for key, value in config["data"].items():
                if hasattr(self.data, key):
                    setattr(self.data, key, value)

        if "cache" in config:
            for key, value in config["cache"].items():
                if hasattr(self.cache, key):
                    setattr(self.cache, key, value)

    def save(self) -> None:
        """Save current settings to preferences file."""
        try:
            from services.data_service import DataService

            # Get data service instance with new structured paths
            data_service = DataService(
                dataDir=self.getDataPath(),
                settingsDir=self.getSettingsPath(),
                databaseDir=self.getDatabasePath(),
            )

            # Save settings as preferences
            preferences = self.toDict()
            data_service.saveUserPreferences(preferences)

            logging.info("Settings saved successfully")

        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            raise

    def load(self) -> None:
        """Load settings from preferences file."""
        try:
            # Load preferences file if it exists
            prefs_path = self.settingsPath / "preferences.json"
            if prefs_path.exists():
                import json

                with open(prefs_path) as f:
                    preferences = json.load(f)
                self.updateFromDict(preferences)
                logging.info("Settings loaded from preferences file")

        except Exception as e:
            logging.warning(f"Failed to load settings from file: {e}")
            # Continue with default settings

    def resetToDefaults(self) -> None:
        """Reset all settings to their default values."""
        try:
            # Reset all config sections to their default values
            self.model = ModelConfig()
            self.api = ApiConfig(
                geniusApiKey=os.getenv("GENIUS_ACCESS_TOKEN"),
                tmdbApiKey=os.getenv("TMDB_API_KEY"),
            )
            self.ui = UiConfig()
            self.logging = LoggingConfig()
            self.data = DataConfig()
            self.cache = CacheConfig()

            # Save the reset settings
            self.save()

            logging.info("Settings reset to defaults")

        except Exception as e:
            logging.error(f"Failed to reset settings to defaults: {e}")
            raise


# Global settings instance
settings = Settings()
