"""Settings page for Text Gauntlet."""

import customtkinter as ctk

from config.settings import Settings
from ui.components.base import ActionButton, Card, ScrollableFrame, StatusIndicator
from ui.components.theme_manager import themeManager
from utils.logger import logger


class SettingsPage(ctk.CTkFrame):
    """Page for application settings."""

    def __init__(self, parent: ctk.CTk, settings: Settings, **kwargs) -> None:
        """Initialize the settings page.

        Args:
            parent: Parent widget
            settings: Settings instance
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)

        self.settings = settings

        # UI Components
        self.themeCard: Card | None = None
        self.apiCard: Card | None = None
        self.analysisCard: Card | None = None
        self.dataCard: Card | None = None
        self.statusIndicator: StatusIndicator | None = None

        # Settings widgets
        self.themeVar: ctk.StringVar | None = None
        self.scalingVar: ctk.StringVar | None = None
        self.maxHistoryVar: ctk.StringVar | None = None
        self.confidenceThresholdVar: ctk.StringVar | None = None
        self.rateLimitVar: ctk.StringVar | None = None
        self.cacheTTLVar: ctk.StringVar | None = None

        self._setupPage()

    def _setupPage(self) -> None:
        """Set up the settings page layout."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Page header
        headerFrame = ctk.CTkFrame(self, fg_color="transparent")
        headerFrame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        headerFrame.grid_columnconfigure(0, weight=1)

        # Page title
        titleLabel = ctk.CTkLabel(
            headerFrame,
            text="⚙ Application Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("accent"),
        )
        titleLabel.grid(row=0, column=0, sticky="w")

        # Create scrollable content area
        scrollableFrameComponent = ScrollableFrame(self)
        scrollableFrameComponent.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=(0, 20)
        )
        self.scrollableFrame = scrollableFrameComponent.contentFrame
        self.scrollableFrame.grid_columnconfigure(0, weight=1)

        # Theme settings
        self._createThemeSettings()

        # API settings
        self._createAPISettings()

        # Analysis settings
        self._createAnalysisSettings()

        # Data settings
        self._createDataSettings()

        # Action buttons
        self._createActionButtons()

        # Status indicator
        self.statusIndicator = StatusIndicator(self)
        self.statusIndicator.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        logger.info("Settings page setup completed")

    def _createThemeSettings(self) -> None:
        """Create theme and appearance settings."""
        self.themeCard = Card(self.scrollableFrame, title="Theme & Appearance")
        self.themeCard.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")

        # Settings frame
        settingsFrame = ctk.CTkFrame(
            self.themeCard.contentFrame, fg_color="transparent"
        )
        settingsFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        settingsFrame.grid_columnconfigure(1, weight=1)

        # Theme selection
        themeLabel = ctk.CTkLabel(
            settingsFrame, text="Color Theme:", font=ctk.CTkFont(size=12)
        )
        themeLabel.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

        self.themeVar = ctk.StringVar(value=self.settings.ui.defaultTheme)
        themeCombo = ctk.CTkComboBox(
            settingsFrame,
            values=["System", "Light", "Dark", "Oblivion"],
            variable=self.themeVar,
            state="readonly",
        )
        themeCombo.grid(row=0, column=1, sticky="ew", pady=(0, 10))

        # UI scaling
        scalingLabel = ctk.CTkLabel(
            settingsFrame, text="UI Scaling:", font=ctk.CTkFont(size=12)
        )
        scalingLabel.grid(row=1, column=0, sticky="w", padx=(0, 10))

        self.scalingVar = ctk.StringVar(value=str(self.settings.ui.widgetScaling))
        scalingCombo = ctk.CTkComboBox(
            settingsFrame,
            values=["0.8", "0.9", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
            variable=self.scalingVar,
            state="readonly",
        )
        scalingCombo.grid(row=1, column=1, sticky="ew")

    def _createAPISettings(self) -> None:
        """Create API configuration settings."""
        self.apiCard = Card(self.scrollableFrame, title="API Configuration")
        self.apiCard.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="ew")

        # Settings frame
        settingsFrame = ctk.CTkFrame(self.apiCard.contentFrame, fg_color="transparent")
        settingsFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        settingsFrame.grid_columnconfigure(1, weight=1)

        # Rate limiting
        rateLimitLabel = ctk.CTkLabel(
            settingsFrame, text="Rate Limit (req/min):", font=ctk.CTkFont(size=12)
        )
        rateLimitLabel.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

        self.rateLimitVar = ctk.StringVar(
            value=str(self.settings.api.rateLimitPerMinute)
        )
        rateLimitEntry = ctk.CTkEntry(
            settingsFrame, textvariable=self.rateLimitVar, placeholder_text="100"
        )
        rateLimitEntry.grid(row=0, column=1, sticky="ew", pady=(0, 10))

        # Cache TTL
        cacheTTLLabel = ctk.CTkLabel(
            settingsFrame, text="Cache TTL (seconds):", font=ctk.CTkFont(size=12)
        )
        cacheTTLLabel.grid(row=1, column=0, sticky="w", padx=(0, 10))

        self.cacheTTLVar = ctk.StringVar(value=str(self.settings.api.cacheExpiry))
        cacheTTLEntry = ctk.CTkEntry(
            settingsFrame, textvariable=self.cacheTTLVar, placeholder_text="3600"
        )
        cacheTTLEntry.grid(row=1, column=1, sticky="ew")

        # API status info
        statusFrame = ctk.CTkFrame(
            self.apiCard.contentFrame,
            fg_color=themeManager.getColor("surface"),
            corner_radius=8,
        )
        statusFrame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        statusLabel = ctk.CTkLabel(
            statusFrame,
            text=" API Keys Status",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        statusLabel.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        # Check API key status
        apiStatus = self._getAPIKeyStatus()
        for i, (service, status) in enumerate(apiStatus.items()):
            statusIcon = "OK" if status else "ERROR"
            serviceLabel = ctk.CTkLabel(
                statusFrame,
                text=f"{statusIcon} {service}: {'Configured' if status else 'Not configured'}",
                font=ctk.CTkFont(size=11),
                text_color=(
                    themeManager.getColor("success")
                    if status
                    else themeManager.getColor("error")
                ),
            )
            serviceLabel.grid(row=i + 1, column=0, padx=15, pady=2, sticky="w")

        # Note about API keys
        noteLabel = ctk.CTkLabel(
            statusFrame,
            text="Note: API keys are configured via environment variables or .env file",
            font=ctk.CTkFont(size=10),
            text_color=themeManager.getColor("text_secondary"),
        )
        noteLabel.grid(
            row=len(apiStatus) + 1, column=0, padx=15, pady=(5, 10), sticky="w"
        )

    def _createAnalysisSettings(self) -> None:
        """Create analysis configuration settings."""
        self.analysisCard = Card(self.scrollableFrame, title="Analysis Settings")
        self.analysisCard.grid(row=2, column=0, padx=0, pady=(0, 10), sticky="ew")

        # Settings frame
        settingsFrame = ctk.CTkFrame(
            self.analysisCard.contentFrame, fg_color="transparent"
        )
        settingsFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        settingsFrame.grid_columnconfigure(1, weight=1)

        # Confidence threshold
        confidenceLabel = ctk.CTkLabel(
            settingsFrame, text="Confidence Threshold:", font=ctk.CTkFont(size=12)
        )
        confidenceLabel.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.confidenceThresholdVar = ctk.StringVar(
            value=str(self.settings.model.confidenceThreshold)
        )
        confidenceEntry = ctk.CTkEntry(
            settingsFrame,
            textvariable=self.confidenceThresholdVar,
            placeholder_text="0.5",
        )
        confidenceEntry.grid(row=0, column=1, sticky="ew")

        # Model info
        modelFrame = ctk.CTkFrame(
            self.analysisCard.contentFrame,
            fg_color=themeManager.getColor("surface"),
            corner_radius=8,
        )
        modelFrame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        modelLabel = ctk.CTkLabel(
            modelFrame,
            text=" Sentiment Analysis Model",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        modelLabel.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        modelNameLabel = ctk.CTkLabel(
            modelFrame,
            text=f"Model: {self.settings.model.primaryModel}",
            font=ctk.CTkFont(size=11),
        )
        modelNameLabel.grid(row=1, column=0, padx=15, pady=2, sticky="w")

        modelTypeLabel = ctk.CTkLabel(
            modelFrame,
            text="Type: RoBERTa-based emotion detection",
            font=ctk.CTkFont(size=11),
            text_color=themeManager.getColor("text_secondary"),
        )
        modelTypeLabel.grid(row=2, column=0, padx=15, pady=(2, 10), sticky="w")

    def _createDataSettings(self) -> None:
        """Create data management settings."""
        self.dataCard = Card(self.scrollableFrame, title="Data Management")
        self.dataCard.grid(row=3, column=0, padx=0, pady=(0, 10), sticky="ew")

        # Settings frame
        settingsFrame = ctk.CTkFrame(self.dataCard.contentFrame, fg_color="transparent")
        settingsFrame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        settingsFrame.grid_columnconfigure(1, weight=1)

        # Max history entries
        historyLabel = ctk.CTkLabel(
            settingsFrame, text="Max History Entries:", font=ctk.CTkFont(size=12)
        )
        historyLabel.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.maxHistoryVar = ctk.StringVar(
            value=str(self.settings.data.maxHistoryRecords)
        )
        historyEntry = ctk.CTkEntry(
            settingsFrame, textvariable=self.maxHistoryVar, placeholder_text="1000"
        )
        historyEntry.grid(row=0, column=1, sticky="ew")

        # Data info
        infoFrame = ctk.CTkFrame(
            self.dataCard.contentFrame,
            fg_color=themeManager.getColor("surface"),
            corner_radius=8,
        )
        infoFrame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        infoLabel = ctk.CTkLabel(
            infoFrame,
            text=" Data Storage Information",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        infoLabel.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        dbPathLabel = ctk.CTkLabel(
            infoFrame,
            text=f"Data Directory: {self.settings.data.dataDirectory}",
            font=ctk.CTkFont(size=11),
            text_color=themeManager.getColor("text_secondary"),
        )
        dbPathLabel.grid(row=1, column=0, padx=15, pady=(2, 10), sticky="w")

    def _createActionButtons(self) -> None:
        """Create action buttons."""
        buttonsFrame = ctk.CTkFrame(self.scrollableFrame, fg_color="transparent")
        buttonsFrame.grid(row=4, column=0, padx=0, pady=20, sticky="ew")
        buttonsFrame.grid_columnconfigure(0, weight=1)
        buttonsFrame.grid_columnconfigure(1, weight=1)
        buttonsFrame.grid_columnconfigure(2, weight=1)

        # Save button
        saveButton = ActionButton(
            buttonsFrame,
            text=" Save Settings",
            command=self._saveSettings,
            style="primary",
        )
        saveButton.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Reset button
        resetButton = ActionButton(
            buttonsFrame,
            text="Reset to Defaults",
            command=self._resetSettings,
            style="secondary",
        )
        resetButton.grid(row=0, column=1, padx=10, sticky="ew")

        # About button
        aboutButton = ActionButton(
            buttonsFrame, text="About", command=self._showAbout, style="secondary"
        )
        aboutButton.grid(row=0, column=2, padx=(10, 0), sticky="ew")

    def _getAPIKeyStatus(self) -> dict[str, bool]:
        """Get API key configuration status."""
        return {
            "Genius (Lyrics)": bool(self.settings.api.geniusApiKey),
            "TMDB (Movies)": bool(self.settings.api.tmdbApiKey),
        }

    def _saveSettings(self) -> None:
        """Save settings to file."""
        try:
            # Update settings from UI
            self.settings.ui.defaultTheme = self.themeVar.get()
            self.settings.ui.widgetScaling = float(self.scalingVar.get())
            self.settings.api.rateLimitPerMinute = int(self.rateLimitVar.get())
            self.settings.api.cacheExpiry = int(self.cacheTTLVar.get())
            self.settings.model.confidenceThreshold = float(
                self.confidenceThresholdVar.get()
            )
            self.settings.data.maxHistoryRecords = int(self.maxHistoryVar.get())

            # Save to file
            self.settings.save()

            # Apply theme change
            themeManager.setTheme(self.settings.ui.defaultTheme)

            # Apply scaling
            ctk.set_widget_scaling(self.settings.ui.widgetScaling)

            self.statusIndicator.showSuccess("Settings saved successfully!")
            logger.info("Settings saved successfully")

        except ValueError as e:
            self.statusIndicator.showError(f"Invalid setting value: {e}")
            logger.error(f"Invalid setting value: {e}")
        except Exception as e:
            self.statusIndicator.showError(f"Failed to save settings: {e}")
            logger.error(f"Failed to save settings: {e}")

    def _resetSettings(self) -> None:
        """Reset settings to defaults."""
        # Create confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reset Settings")
        dialog.geometry("400x200")
        dialog.transient(self.winfo_toplevel())

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")

        # Set grab after window is properly positioned and displayed
        dialog.after(1, dialog.grab_set)

        # Dialog content
        contentFrame = ctk.CTkFrame(dialog, fg_color="transparent")
        contentFrame.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning icon and text
        warningLabel = ctk.CTkLabel(
            contentFrame,
            text="Reset Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=themeManager.getColor("warning"),
        )
        warningLabel.pack(pady=(0, 10))

        messageLabel = ctk.CTkLabel(
            contentFrame,
            text="Are you sure you want to reset all settings to their default values?",
            font=ctk.CTkFont(size=12),
            justify="center",
        )
        messageLabel.pack(pady=(0, 20))

        # Buttons frame
        buttonsFrame = ctk.CTkFrame(contentFrame, fg_color="transparent")
        buttonsFrame.pack(fill="x")
        buttonsFrame.grid_columnconfigure(0, weight=1)
        buttonsFrame.grid_columnconfigure(1, weight=1)

        # Cancel button
        cancelButton = ctk.CTkButton(
            buttonsFrame,
            text="Cancel",
            command=dialog.destroy,
            fg_color=themeManager.getColor("surface"),
            hover_color=themeManager.getColor("surface_hover"),
        )
        cancelButton.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Confirm button
        confirmButton = ctk.CTkButton(
            buttonsFrame,
            text="Reset",
            command=lambda: self._confirmResetSettings(dialog),
            fg_color=themeManager.getColor("warning"),
            hover_color=themeManager.getColor("warning_hover"),
        )
        confirmButton.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _confirmResetSettings(self, dialog: ctk.CTkToplevel) -> None:
        """Confirm and execute settings reset."""
        dialog.destroy()

        try:
            # Reset settings to defaults
            self.settings.resetToDefaults()

            # Update UI with default values
            self.themeVar.set(self.settings.ui.defaultTheme)
            self.scalingVar.set(str(self.settings.ui.widgetScaling))
            self.rateLimitVar.set(str(self.settings.api.rateLimitPerMinute))
            self.cacheTTLVar.set(str(self.settings.api.cacheExpiry))
            self.confidenceThresholdVar.set(
                str(self.settings.model.confidenceThreshold)
            )
            self.maxHistoryVar.set(str(self.settings.data.maxHistoryRecords))

            self.statusIndicator.showSuccess("Settings reset to defaults!")
            logger.info("Settings reset to defaults")

        except Exception as e:
            self.statusIndicator.showError(f"Failed to reset settings: {e}")
            logger.error(f"Failed to reset settings: {e}")

    def _showAbout(self) -> None:
        """Show about dialog."""
        # Create about dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("About Text Gauntlet")
        dialog.geometry("500x400")
        dialog.transient(self.winfo_toplevel())

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")

        # Set grab after window is properly positioned and displayed
        dialog.after(1, dialog.grab_set)

        # Dialog content - using custom ScrollableFrame
        scrollableFrameComponent = ScrollableFrame(dialog)
        scrollableFrameComponent.create()
        scrollableFrameComponent.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure dialog grid
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        contentFrame = scrollableFrameComponent.contentFrame

        # App icon and title
        titleLabel = ctk.CTkLabel(
            contentFrame,
            text=" Text Gauntlet v2.0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("accent"),
        )
        titleLabel.pack(pady=(0, 10))

        # Description
        descLabel = ctk.CTkLabel(
            contentFrame,
            text="Advanced Multi-Source Sentiment Analysis Tool",
            font=ctk.CTkFont(size=14),
            text_color=themeManager.getColor("text_secondary"),
        )
        descLabel.pack(pady=(0, 20))

        # Features
        featuresText = """
 Features:
• Direct text sentiment analysis
• Song lyrics analysis via Genius API
• Movie reviews analysis via TMDB API
• News articles and web content analysis
• Comprehensive analysis history
• Advanced caching and rate limiting
• Modern responsive UI with custom themes

 AI Technology:
• RoBERTa-based emotion detection model
• Multi-class sentiment classification
• Confidence scoring and detailed analysis
• Optimized for social media and informal text

 Data Management:
• SQLite database for history storage
• Configurable data retention policies
• Export and backup capabilities
• Privacy-focused local storage

⚙ Technical Stack:
• Python 3.13+ with modern typing
• CustomTkinter for modern UI
• HuggingFace Transformers for AI
• SQLite for data persistence
• Multiple API integrations
        """

        aboutText = ctk.CTkTextbox(
            contentFrame, height=200, wrap="word", font=ctk.CTkFont(size=11)
        )
        aboutText.pack(fill="both", expand=True, pady=(0, 20))
        aboutText.insert("0.0", featuresText.strip())
        aboutText.configure(state="disabled")

        # Close button
        closeButton = ctk.CTkButton(
            contentFrame, text="Close", command=dialog.destroy, width=100
        )
        closeButton.pack()

    def reset(self) -> None:
        """Reset the page to initial state."""
        try:
            if self.statusIndicator:
                try:
                    self.statusIndicator.clear()
                except Exception:
                    pass  # Widget may already be destroyed

            logger.info("Settings page reset")

        except Exception as e:
            logger.warning(f"Error during settings page reset: {e}")
            # Continue with cleanup even if some operations fail
