"""Main window for Text Gauntlet application."""

import customtkinter as ctk

from config.settings import settings
from services.application_services import services
from ui.components.navigation import NavigationSidebar
from ui.components.theme_manager import themeManager
from ui.pages import (
    ArticlesPage,
    HistoryPage,
    LyricsPage,
    MoviesPage,
    SettingsPage,
    TextPage,
)
from utils.exceptions import ConfigurationError
from utils.helpers import UIHelper
from utils.logger import logger


class TextGauntletApp:
    """Main application class for Text Gauntlet."""

    def __init__(self) -> None:
        """Initialize the Text Gauntlet application."""
        self.window: ctk.CTk | None = None

        # Navigation and pages
        self.navigationSidebar: NavigationSidebar | None = None
        self.currentPage: str = "text"
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.contentFrame: ctk.CTkFrame | None = None

        self._setupUI()

    def _setupUI(self) -> None:
        """Set up the main UI components."""
        try:
            # Configure CustomTkinter appearance
            self._configureAppearance()

            # Create main window
            self._createMainWindow()

            # Create navigation and content areas
            self._createLayout()

            # Initialize pages
            self._initializePages()

            # Show initial page
            self._showPage("text")

            logger.info("UI setup completed successfully")

        except Exception as e:
            logger.error(f"Failed to setup UI: {e}")
            raise ConfigurationError(f"UI setup failed: {e}") from e

    def _configureAppearance(self) -> None:
        """Configure CustomTkinter appearance settings."""
        try:
            # Use theme manager for appearance configuration
            themeManager.setTheme(settings.ui.defaultTheme)
            logger.info("Appearance configured with theme manager")

        except Exception as e:
            logger.error(f"Failed to configure appearance: {e}")
            # Fall back to default settings
            ctk.set_appearance_mode("System")
            ctk.set_widget_scaling(1.0)
            ctk.set_default_color_theme("blue")

    def _createMainWindow(self) -> None:
        """Create and configure the main window."""
        self.window = ctk.CTk()
        self.window.title("Text Gauntlet v2.0")

        # Set window icon
        try:
            # Try PNG icon first (better compatibility on Linux)
            iconPath = settings.getAssetPath("images/icon.png")
            if iconPath.exists():
                # For CustomTkinter, we can use iconphoto with PNG
                import tkinter as tk

                icon_image = tk.PhotoImage(file=str(iconPath))
                self.window.iconphoto(True, icon_image)
            else:
                # Fallback to ICO file
                iconPath = settings.getAssetPath("images/icon.ico")
                if iconPath.exists():
                    self.window.iconbitmap(str(iconPath))
        except Exception as e:
            logger.warning(f"Could not load window icon: {e}")

        # Configure window
        UIHelper.centerWindow(
            self.window, settings.ui.windowWidth, settings.ui.windowHeight
        )

        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        # Set up responsive grid - sidebar and main content
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)  # Main content area

    def _createLayout(self) -> None:
        """Create the main layout with navigation sidebar and content area."""
        if not self.window:
            raise ConfigurationError("Window not initialized")

        # Navigation sidebar with enhanced styling
        self.navigationSidebar = NavigationSidebar(
            self.window,
            onPageChanged=self._onPageChanged,
            width=260,
            corner_radius=0,
            fg_color=themeManager.getColor("surface"),
        )
        self.navigationSidebar.grid(row=0, column=0, sticky="nsew")

        # Main content frame with subtle border
        self.contentFrame = ctk.CTkFrame(
            self.window,
            corner_radius=0,
            fg_color=themeManager.getColor("background"),
            border_width=1,
            border_color=themeManager.getColor("surface_variant"),
        )
        self.contentFrame.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        self.contentFrame.grid_rowconfigure(0, weight=1)
        self.contentFrame.grid_columnconfigure(0, weight=1)

    def _initializePages(self) -> None:
        """Initialize all application pages."""
        if not self.contentFrame:
            raise ConfigurationError("Content frame not initialized")

        try:
            # Text analysis page
            self.pages["text"] = TextPage(self.contentFrame, fg_color="transparent")

            # Lyrics analysis page
            self.pages["lyrics"] = LyricsPage(
                self.contentFrame, services.lyricsService, fg_color="transparent"
            )

            # Movies analysis page
            self.pages["movies"] = MoviesPage(
                self.contentFrame, services.movieService, fg_color="transparent"
            )

            # Articles analysis page
            self.pages["articles"] = ArticlesPage(
                self.contentFrame, services.articleService, fg_color="transparent"
            )

            # History page
            self.pages["history"] = HistoryPage(
                self.contentFrame, services.dataService, fg_color="transparent"
            )

            # Settings page
            self.pages["settings"] = SettingsPage(
                self.contentFrame, settings, fg_color="transparent"
            )

            # Grid all pages (initially hidden)
            for page in self.pages.values():
                page.grid(row=0, column=0, sticky="nsew")
                page.grid_remove()

            logger.info("All pages initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize pages: {e}")
            raise ConfigurationError(f"Page initialization failed: {e}") from e

    def _onPageChanged(self, pageName: str) -> None:
        """Handle page change from navigation."""
        self._showPage(pageName)

    def _showPage(self, pageName: str) -> None:
        """Show the specified page and hide others."""
        if pageName not in self.pages:
            return

        # Hide current page
        if self.currentPage in self.pages:
            self.pages[self.currentPage].grid_remove()
            # Call onHide for the current page
            if hasattr(self.pages[self.currentPage], "onHide"):
                self.pages[self.currentPage].onHide()

        # Show new page
        self.pages[pageName].grid()
        # Call onShow to initialize the page
        if hasattr(self.pages[pageName], "onShow"):
            self.pages[pageName].onShow()
        self.currentPage = pageName

        # Update navigation sidebar
        if self.navigationSidebar:
            self.navigationSidebar.setCurrentPage(pageName)

        # Special handling for certain pages
        if pageName == "history":
            # Refresh history when switching to history page
            if hasattr(self.pages[pageName], "refresh"):
                self.pages[pageName].refresh()

        logger.info(f"Switched to {pageName} page")

    def run(self) -> None:
        """Run the application."""
        if not self.window:
            raise ConfigurationError("Window not initialized")

        try:
            logger.info("Starting Text Gauntlet application")
            self.window.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources before closing."""
        try:
            # Reset all pages with individual error handling
            for page_name, page in self.pages.items():
                if hasattr(page, "reset"):
                    try:
                        page.reset()
                    except Exception as e:
                        logger.warning(f"Error resetting {page_name} page: {e}")
                        # Continue with other pages

            # Close services
            if hasattr(services, "cleanup"):
                try:
                    services.cleanup()
                except Exception as e:
                    logger.warning(f"Error during services cleanup: {e}")

            logger.info("Application cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            # Don't re-raise to avoid blocking application shutdown

    def getCurrentPage(self) -> str:
        """Get the current active page name."""
        return self.currentPage

    def getPage(self, pageName: str) -> ctk.CTkFrame | None:
        """Get a specific page instance."""
        return self.pages.get(pageName)


def main() -> None:
    """Main entry point for the application."""
    try:
        app = TextGauntletApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()
