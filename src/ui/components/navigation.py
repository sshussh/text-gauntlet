"""Navigation sidebar component for Text Gauntlet."""

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from ui.components.theme_manager import themeManager
from utils.logger import logger


class NavigationSidebar(ctk.CTkFrame):
    """Navigation sidebar with different analysis pages."""

    def __init__(
        self, parent: ctk.CTk, onPageChanged: Callable[[str], None], **kwargs
    ) -> None:
        """Initialize the navigation sidebar.

        Args:
            parent: Parent widget
            onPageChanged: Callback when page is changed
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)

        self.onPageChanged = onPageChanged
        self.currentPage = None  # Start with no page selected
        self.navigationButtons: dict[str, ctk.CTkButton] = {}

        self._setupSidebar()

    def _setupSidebar(self) -> None:
        """Set up the navigation sidebar."""
        # Configure grid
        self.grid_rowconfigure(7, weight=1)  # Spacer
        self.grid_columnconfigure(0, weight=1)

        # App title with improved styling
        titleLabel = ctk.CTkLabel(
            self,
            text="Text Gauntlet",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=themeManager.getColor("accent"),
        )
        titleLabel.grid(row=0, column=0, padx=20, pady=(35, 5), sticky="ew")

        # Subtitle with better spacing
        subtitleLabel = ctk.CTkLabel(
            self,
            text="Sentiment Analysis",
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=themeManager.getColor("text_secondary"),
        )
        subtitleLabel.grid(row=1, column=0, padx=20, pady=(0, 35), sticky="ew")

        # Navigation buttons with icons
        self.pages = [
            ("text", "Text Analysis", "Direct text input analysis"),
            ("lyrics", "Song Lyrics", "Analyze song lyrics sentiment"),
            ("movies", "Movie Reviews", "Analyze movie reviews"),
            ("articles", "News Articles", "Analyze web articles"),
            ("history", "History", "View analysis history"),
            ("settings", "Settings", "Application settings"),
        ]

        for i, (pageId, title, description) in enumerate(self.pages):
            button = self._createNavigationButton(pageId, title, description)
            button.grid(row=i + 2, column=0, padx=18, pady=6, sticky="ew")
            self.navigationButtons[pageId] = button

        # Select the first page by default
        self._selectPage("text")

    def _createNavigationButton(
        self, pageId: str, title: str, description: str
    ) -> ctk.CTkButton:
        """Create a navigation button.

        Args:
            pageId: Page identifier
            title: Button title
            description: Button description (tooltip)

        Returns:
            Created navigation button
        """
        button = ctk.CTkButton(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="normal"),
            height=48,
            corner_radius=12,
            anchor="w",
            command=lambda: self._selectPage(pageId),
            fg_color="transparent",
            text_color=themeManager.getColor("text_primary"),
            hover_color=themeManager.getColor("surface_hover"),
            border_width=0,
        )

        # Add tooltip (simple implementation)
        self._addTooltip(button, description)

        return button

    def _addTooltip(self, widget: Any, text: str) -> None:
        """Add a simple tooltip to a widget.

        Args:
            widget: Widget to add tooltip to
            text: Tooltip text

        Note:
            This is a basic tooltip implementation. For production,
            consider using a more sophisticated tooltip library.
        """

        def onEnter(event) -> None:
            # Simple status update instead of complex tooltip
            pass

        def onLeave(event) -> None:
            pass

        widget.bind("<Enter>", onEnter)
        widget.bind("<Leave>", onLeave)

    def _selectPage(self, pageId: str) -> None:
        """Select a navigation page.

        Args:
            pageId: Page identifier to select
        """
        if pageId == self.currentPage:
            return

        # Update button styles
        for btnPageId, button in self.navigationButtons.items():
            if btnPageId == pageId:
                # Selected state with enhanced styling - using theme colors
                button.configure(
                    fg_color=themeManager.getColor("primary"),
                    text_color=themeManager.getColor("on_primary"),
                    hover_color=themeManager.getColor("primary_variant"),
                    font=ctk.CTkFont(size=14, weight="bold"),
                    border_width=0,
                )
            else:
                # Unselected state with better contrast
                button.configure(
                    fg_color="transparent",
                    text_color=themeManager.getColor("text_primary"),
                    hover_color=themeManager.getColor("surface_hover"),
                    font=ctk.CTkFont(size=14, weight="normal"),
                    border_width=0,
                )

        self.currentPage = pageId
        self.onPageChanged(pageId)

    def getCurrentPage(self) -> str:
        """Get the currently selected page.

        Returns:
            Current page identifier
        """
        return self.currentPage

    def setPage(self, pageId: str) -> None:
        """Programmatically set the current page.

        Args:
            pageId: Page identifier to set
        """
        if pageId in self.navigationButtons:
            self._selectPage(pageId)
        else:
            logger.warning(f"Unknown page ID: {pageId}")

    def setCurrentPage(self, pageId: str) -> None:
        """Set the current page without triggering the callback.

        Args:
            pageId: Page identifier to set as current
        """
        if pageId in self.navigationButtons:
            # Use the existing _selectPage method but don't trigger callback
            oldCallback = self.onPageChanged
            self.onPageChanged = lambda x: None  # Temporarily disable callback
            self._selectPage(pageId)
            self.onPageChanged = oldCallback  # Restore callback
        else:
            logger.warning(f"Unknown page ID: {pageId}")


class PageFrame(ctk.CTkFrame):
    """Base class for page frames."""

    def __init__(self, parent: ctk.CTk, **kwargs) -> None:
        """Initialize the page frame.

        Args:
            parent: Parent widget
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(parent, **kwargs)
        self.isInitialized = False

    def initialize(self) -> None:
        """Initialize the page (called when first shown)."""
        if not self.isInitialized:
            self._setupPage()
            self.isInitialized = True

    def _setupPage(self) -> None:
        """Set up the page content (override in subclasses)."""
        pass

    def onShow(self) -> None:
        """Called when the page is shown."""
        self.initialize()

    def onHide(self) -> None:
        """Called when the page is hidden."""
        pass

    def refresh(self) -> None:
        """Refresh the page content."""
        pass
