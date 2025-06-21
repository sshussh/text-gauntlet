"""Advanced theme management system for Text Gauntlet."""

import json
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import customtkinter as ctk

from config.settings import settings
from utils.logger import logger


class ThemeManager:
    """Advanced theme management with dynamic switching and customization."""

    def __init__(self) -> None:
        """Initialize theme manager."""
        self.currentTheme = "system"
        self.customThemes: dict[str, dict[str, Any]] = {}
        self.themeChangeCallbacks: list[Callable[[str], None]] = []
        self._loadCustomThemes()

    def _loadCustomThemes(self) -> None:
        """Load custom themes from assets directory."""
        try:
            themesDir = settings.getAssetPath("themes")
            if not themesDir.exists():
                logger.warning("Themes directory not found")
                return

            for themeFile in themesDir.glob("*.json"):
                try:
                    with open(themeFile, encoding="utf-8") as f:
                        themeData = json.load(f)
                        themeName = themeFile.stem.lower()
                        self.customThemes[themeName] = themeData
                        logger.info(f"Loaded custom theme: {themeName}")
                except Exception as e:
                    logger.error(f"Failed to load theme {themeFile}: {e}")

        except Exception as e:
            logger.error(f"Failed to load custom themes: {e}")

    def getAvailableThemes(self) -> list[str]:
        """Get list of available themes."""
        builtinThemes = ["blue", "green", "dark-blue"]
        customThemes = list(self.customThemes.keys())
        return ["system"] + builtinThemes + customThemes

    def setTheme(self, themeName: str) -> bool:
        """Set the current theme."""
        try:
            themeName = themeName.lower()

            # Handle appearance mode
            if themeName == "system":
                ctk.set_appearance_mode("System")
                ctk.set_default_color_theme("blue")
            elif themeName in ["light", "dark"]:
                ctk.set_appearance_mode(themeName.title())
                ctk.set_default_color_theme("blue")
            elif themeName in ["blue", "green", "dark-blue"]:
                # Built-in themes
                ctk.set_default_color_theme(themeName)
            elif themeName in self.customThemes:
                # Custom theme
                themeData = self.customThemes[themeName]
                self._applyCustomTheme(themeData)
            else:
                logger.warning(f"Unknown theme: {themeName}")
                return False

            self.currentTheme = themeName
            self._notifyThemeChange(themeName)
            logger.info(f"Theme changed to: {themeName}")
            return True

        except Exception as e:
            logger.error(f"Failed to set theme {themeName}: {e}")
            return False

    def _applyCustomTheme(self, themeData: dict[str, Any]) -> None:
        """Apply a custom theme configuration."""
        try:
            # Set appearance mode before applying theme
            appearance_mode = self._detectAppearanceMode(themeData)
            ctk.set_appearance_mode(appearance_mode)

            # Create a temporary file for the theme data
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as temp_file:
                json.dump(themeData, temp_file, indent=2)
                temp_file_path = temp_file.name

            try:
                ctk.set_default_color_theme(temp_file_path)
            finally:
                # Clean up the temporary file immediately after use
                Path(temp_file_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Failed to apply custom theme: {e}")
            raise

    def _detectAppearanceMode(self, themeData: dict[str, Any]) -> str:
        """Detect the appropriate appearance mode for a theme."""
        try:
            # Check if theme explicitly specifies appearance mode
            if "appearance_mode" in themeData:
                return themeData["appearance_mode"]

            # Analyze theme colors to determine if it's light or dark
            # Check the main background color
            if "CTk" in themeData and "fg_color" in themeData["CTk"]:
                bg_colors = themeData["CTk"]["fg_color"]
                if isinstance(bg_colors, list) and len(bg_colors) >= 2:
                    # Use the dark color (index 1) to determine theme type
                    dark_bg = bg_colors[1]
                    if self._isColorDark(dark_bg):
                        return "dark"
                    else:
                        return "light"

            # Default to dark for custom themes like Oblivion
            return "dark"

        except Exception:
            return "dark"

    def _isColorDark(self, color: str) -> bool:
        """Determine if a color is dark."""
        try:
            # Remove # if present
            color = color.lstrip("#")

            # Convert to RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            # Calculate luminance (simplified)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

            # Dark if luminance is less than 0.5
            return luminance < 0.5

        except Exception:
            return True  # Default to dark if can't determine

    def getCurrentTheme(self) -> str:
        """Get the current theme name."""
        return self.currentTheme

    def addThemeChangeCallback(self, callback: Callable[[str], None]) -> None:
        """Add a callback for theme changes."""
        self.themeChangeCallbacks.append(callback)

    def removeThemeChangeCallback(self, callback: Callable[[str], None]) -> None:
        """Remove a theme change callback."""
        if callback in self.themeChangeCallbacks:
            self.themeChangeCallbacks.remove(callback)

    def _notifyThemeChange(self, themeName: str) -> None:
        """Notify all callbacks of theme change."""
        for callback in self.themeChangeCallbacks:
            try:
                callback(themeName)
            except Exception as e:
                logger.error(f"Theme change callback failed: {e}")

    def getThemeColors(self, themeName: str | None = None) -> dict[str, str]:
        """Get color palette for a theme."""
        if themeName is None:
            themeName = self.currentTheme

        # Default color palette
        defaultColors = {
            "primary": "#3b82f6",
            "secondary": "#6b7280",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "info": "#06b6d4",
            "light": "#f8fafc",
            "dark": "#1e293b",
            "background": "#ffffff",
            "surface": "#f1f5f9",
            "text": "#0f172a",
            "textSecondary": "#64748b",
        }

        # Custom theme colors
        if themeName in self.customThemes:
            themeData = self.customThemes[themeName]
            if "CTk" in themeData and "color" in themeData["CTk"]:
                colors = themeData["CTk"]["color"]
                # Map custom theme colors to our standard palette
                colorMap = {
                    "window_bg_color": "background",
                    "top_level_bg_color": "surface",
                    "button_color": "primary",
                    "button_hover_color": "primary",
                    "entry_bg_color": "surface",
                    "text_color": "text",
                    "text_color_disabled": "textSecondary",
                }

                for customKey, standardKey in colorMap.items():
                    if customKey in colors:
                        colorValue = colors[customKey]
                        if isinstance(colorValue, list) and len(colorValue) >= 2:
                            # Use light mode color
                            defaultColors[standardKey] = colorValue[0]
                        elif isinstance(colorValue, str):
                            defaultColors[standardKey] = colorValue

        return defaultColors

    def getColor(self, colorName: str) -> str:
        """
        Get a color value from the current theme.

        Args:
            colorName: Name of the color to get

        Returns:
            Color value as a string
        """
        try:
            # For custom themes like Oblivion, extract from theme data first
            if self.currentTheme in self.customThemes:
                return self._getCustomColor(
                    colorName, self.customThemes[self.currentTheme]
                )

            # Fall back to default theme colors
            colors = self.getThemeColors()

            # Map common UI color names to theme colors
            colorMap = {
                "primary": colors.get("primary", "#3b82f6"),
                "primary_variant": self._darkenColor(colors.get("primary", "#3b82f6")),
                "on_primary": "#ffffff",
                "secondary": colors.get("secondary", "#6b7280"),
                "accent": colors.get("primary", "#3b82f6"),
                "background": colors.get("background", "#ffffff"),
                "surface": colors.get("surface", "#f1f5f9"),
                "surface_variant": colors.get("surface", "#f1f5f9"),
                "surface_hover": self._lightenColor(colors.get("surface", "#f1f5f9")),
                "card_background": colors.get("surface", "#f1f5f9"),
                "text_primary": colors.get("text", "#0f172a"),
                "text_secondary": colors.get("textSecondary", "#64748b"),
                "success": colors.get("success", "#22c55e"),
                "warning": colors.get("warning", "#f59e0b"),
                "error": colors.get("danger", "#ef4444"),
                "error_hover": self._darkenColor(colors.get("danger", "#ef4444")),
                "warning_hover": self._darkenColor(colors.get("warning", "#f59e0b")),
            }

            return colorMap.get(colorName, colors.get("text", "#000000"))

        except Exception as e:
            logger.warning(f"Failed to get color {colorName}: {e}")
            return "#000000"  # Fallback color

    def _getCustomColor(self, colorName: str, themeData: dict[str, Any]) -> str:
        """Get color from custom theme data."""
        try:
            # First check if there's a CustomColors section
            if "CustomColors" in themeData:
                customColors = themeData["CustomColors"]

                # For dark appearance mode, automatically map generic names to dark variants FIRST
                if ctk.get_appearance_mode() == "Dark":
                    dark_mapping = {
                        "background": "background_dark",
                        "surface": "surface_dark",
                        "surface_variant": "surface_variant_dark",
                        "surface_hover": "surface_hover_dark",
                        "on_background": "on_background_dark",
                        "on_surface": "on_surface_dark",
                        "text_primary": "text_primary_dark",
                        "text_secondary": "text_secondary_dark",
                        "text_muted": "text_muted_dark",
                        "border": "border_dark",
                        "border_hover": "border_hover_dark",
                    }

                    dark_variant = dark_mapping.get(colorName)
                    if dark_variant and dark_variant in customColors:
                        logger.debug(
                            f"Dark mode mapping: {colorName} -> {dark_variant} = {customColors[dark_variant]}"
                        )
                        return customColors[dark_variant]

                # Then check for exact color name match
                if colorName in customColors:
                    return customColors[colorName]

            # Fallback to component-based extraction
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
                "surface_variant": self._extractColor(
                    themeData, "CTkEntry", "fg_color"
                ),
                "surface_hover": self._extractColor(
                    themeData, "CTkButton", "hover_color"
                ),
                "card_background": self._extractColor(
                    themeData, "CTkFrame", "fg_color"
                ),
                "text_primary": self._extractColor(themeData, "CTkLabel", "text_color"),
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
        except Exception:
            return "#FFFFFF"

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

    def _darkenColor(self, color: str, factor: float = 0.2) -> str:
        """Darken a hex color by a factor."""
        try:
            # Remove # if present
            color = color.lstrip("#")

            # Convert to RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            # Darken
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))

            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color

    def _lightenColor(self, color: str, factor: float = 0.1) -> str:
        """Lighten a hex color by a factor."""
        try:
            # Remove # if present
            color = color.lstrip("#")

            # Convert to RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            # Lighten
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))

            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color

    def createThemeSelector(self, parent: ctk.CTkFrame) -> ctk.CTkOptionMenu:
        """Create a theme selector widget."""
        themes = self.getAvailableThemes()
        themeSelector = ctk.CTkOptionMenu(
            parent, values=themes, command=self._onThemeSelected
        )
        themeSelector.set(self.currentTheme.title())
        return themeSelector

    def _onThemeSelected(self, themeName: str) -> None:
        """Handle theme selection from selector widget."""
        self.setTheme(themeName.lower())


# Global theme manager instance
themeManager = ThemeManager()
