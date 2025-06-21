"""Theme configuration and management for Text Gauntlet."""

import json
from typing import Any

from config.settings import settings
from utils.exceptions import ResourceError
from utils.logger import logger


class ThemeManager:
    """Manager for application themes."""

    def __init__(self) -> None:
        """Initialize theme manager."""
        self._loadedThemes: dict[str, dict[str, Any]] = {}
        self._currentTheme: str = settings.ui.defaultTheme

    def loadTheme(self, themeName: str) -> dict[str, Any]:
        """
        Load theme configuration.

        Args:
            themeName: Name of the theme to load

        Returns:
            Theme configuration dictionary

        Raises:
            ResourceError: If theme cannot be loaded
        """
        if themeName in self._loadedThemes:
            return self._loadedThemes[themeName]

        try:
            if themeName == "Oblivion":
                themePath = settings.themesPath / "oblivion.json"
                if themePath.exists():
                    with open(themePath) as f:
                        themeData = json.load(f)
                    self._loadedThemes[themeName] = themeData
                    logger.info(f"Loaded custom theme: {themeName}")
                    return themeData
                else:
                    raise ResourceError(f"Theme file not found: {themePath}")
            else:
                # Built-in themes don't need loading
                self._loadedThemes[themeName] = {"name": themeName, "builtin": True}
                logger.info(f"Using built-in theme: {themeName}")
                return self._loadedThemes[themeName]

        except Exception as e:
            logger.error(f"Failed to load theme {themeName}: {e}")
            raise ResourceError(f"Could not load theme {themeName}: {e}") from e

    def getCurrentTheme(self) -> str:
        """Get current theme name."""
        return self._currentTheme

    def setCurrentTheme(self, themeName: str) -> None:
        """
        Set current theme.

        Args:
            themeName: Name of the theme to set as current
        """
        try:
            # Validate theme exists
            self.loadTheme(themeName)

            # Update current theme
            self._currentTheme = themeName

            # Save preference
            settings.saveThemePreference(themeName)

            logger.info(f"Theme changed to: {themeName}")

        except Exception as e:
            logger.error(f"Failed to set theme {themeName}: {e}")
            raise

    def getAvailableThemes(self) -> list[str]:
        """Get list of available themes."""
        themes = ["blue", "green", "dark-blue"]

        # Check if Oblivion theme file exists
        oblivionPath = settings.themesPath / "oblivion.json"
        if oblivionPath.exists():
            themes.insert(0, "Oblivion")

        return themes

    def getColor(self, colorName: str) -> str:
        """
        Get a color value from the current theme.

        Args:
            colorName: Name of the color to get

        Returns:
            Color value as a string
        """
        try:
            # Load current theme data
            themeData = self.loadTheme(self._currentTheme)

            # Default color mappings for built-in themes
            if themeData.get("builtin", False):
                return self._getBuiltinColor(colorName)

            # For custom themes like Oblivion, extract from theme data
            return self._getCustomColor(colorName, themeData)

        except Exception as e:
            logger.warning(f"Failed to get color {colorName}: {e}")
            return "#FFFFFF"  # Fallback color

    def _getBuiltinColor(self, colorName: str) -> str:
        """Get color from built-in theme."""
        # Default color palette for built-in themes
        colorMap = {
            "primary": "#3B82F6",
            "primary_variant": "#2563EB",
            "on_primary": "#FFFFFF",
            "secondary": "#6B7280",
            "accent": "#F59E0B",
            "background": "#FFFFFF",
            "surface": "#F9FAFB",
            "surface_variant": "#E5E7EB",
            "surface_hover": "#F3F4F6",
            "card_background": "#FFFFFF",
            "text_primary": "#111827",
            "text_secondary": "#6B7280",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
            "error_hover": "#DC2626",
            "warning_hover": "#D97706",
        }

        return colorMap.get(colorName, "#FFFFFF")

    def _getCustomColor(self, colorName: str, themeData: dict[str, Any]) -> str:
        """Get color from custom theme data."""
        # Map common color names to theme structure
        colorMap = {
            "primary": self._extractColor(themeData, "CTkButton", "fg_color"),
            "primary_variant": self._extractColor(
                themeData, "CTkButton", "hover_color"
            ),
            "on_primary": self._extractColor(themeData, "CTkButton", "text_color"),
            "secondary": self._extractColor(themeData, "CTkFrame", "fg_color"),
            "accent": self._extractColor(themeData, "CTkSwitch", "progress_color"),
            "background": self._extractColor(themeData, "CTk", "fg_color"),
            "surface": self._extractColor(themeData, "CTkFrame", "top_fg_color"),
            "surface_variant": self._extractColor(themeData, "CTkEntry", "fg_color"),
            "surface_hover": self._extractColor(themeData, "CTkButton", "hover_color"),
            "card_background": self._extractColor(themeData, "CTkFrame", "fg_color"),
            "text_primary": self._extractColor(
                themeData, "CTkLabel", "text_color", default="#FFFFFF"
            ),
            "text_secondary": self._extractColor(
                themeData, "CTkSwitch", "text_color_disabled"
            ),
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
            "error_hover": "#DC2626",
            "warning_hover": "#D97706",
        }

        return colorMap.get(colorName, "#FFFFFF")

    def _extractColor(
        self,
        themeData: dict[str, Any],
        component: str,
        property: str,
        default: str = "#FFFFFF",
    ) -> str:
        """Extract color from theme data structure."""
        try:
            componentData = themeData.get(component, {})
            if not componentData:
                return default

            colorValue = componentData.get(property, default)

            # Handle array format [light_color, dark_color] - use dark color (index 1)
            if isinstance(colorValue, list) and len(colorValue) >= 2:
                return colorValue[1]
            elif isinstance(colorValue, str):
                return colorValue
            else:
                return default

        except Exception:
            return default

    def createCustomTheme(self, themeName: str, themeData: dict[str, Any]) -> None:
        """
        Create a new custom theme.

        Args:
            themeName: Name for the new theme
            themeData: Theme configuration data

        Raises:
            ResourceError: If theme cannot be created
        """
        try:
            themePath = settings.themesPath / f"{themeName}.json"

            # Ensure themes directory exists
            settings.themesPath.mkdir(parents=True, exist_ok=True)

            # Write theme file
            with open(themePath, "w") as f:
                json.dump(themeData, f, indent=2)

            # Add to loaded themes
            self._loadedThemes[themeName] = themeData

            logger.info(f"Created custom theme: {themeName}")

        except Exception as e:
            logger.error(f"Failed to create theme {themeName}: {e}")
            raise ResourceError(f"Could not create theme {themeName}: {e}") from e


# Global theme manager instance
themeManager = ThemeManager()
