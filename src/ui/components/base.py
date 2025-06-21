"""Base UI components for Text Gauntlet application."""

from abc import ABC, abstractmethod
from collections.abc import Callable

import customtkinter as ctk

from ui.components.theme_manager import themeManager


class BaseComponent(ABC):
    """Abstract base class for all UI components."""

    def __init__(self, parent: ctk.CTk | ctk.CTkFrame, **kwargs) -> None:
        """Initialize base component."""
        self.parent = parent
        self.kwargs = kwargs
        self._widget: ctk.CTkBaseClass | None = None
        self._isVisible = True

    @abstractmethod
    def create(self) -> ctk.CTkBaseClass:
        """Create and return the component widget."""
        pass

    def show(self) -> None:
        """Show the component."""
        if self._widget:
            self._widget.grid()
            self._isVisible = True

    def hide(self) -> None:
        """Hide the component."""
        if self._widget:
            self._widget.grid_remove()
            self._isVisible = False

    def destroy(self) -> None:
        """Destroy the component."""
        if self._widget:
            self._widget.destroy()
            self._widget = None

    def grid(self, **kwargs) -> None:
        """Grid the component widget."""
        if not self._widget:
            self.create()
        if self._widget:
            self._widget.grid(**kwargs)

    def grid_remove(self) -> None:
        """Remove component from grid."""
        if self._widget:
            self._widget.grid_remove()

    def grid_forget(self) -> None:
        """Forget component from grid."""
        if self._widget:
            self._widget.grid_forget()

    def pack(self, **kwargs) -> None:
        """Pack the component widget."""
        if not self._widget:
            self.create()
        if self._widget:
            self._widget.pack(**kwargs)

    def pack_forget(self) -> None:
        """Forget component from pack."""
        if self._widget:
            self._widget.pack_forget()

    def place(self, **kwargs) -> None:
        """Place the component widget."""
        if not self._widget:
            self.create()
        if self._widget:
            self._widget.place(**kwargs)

    def place_forget(self) -> None:
        """Forget component from place."""
        if self._widget:
            self._widget.place_forget()

    @property
    def widget(self) -> ctk.CTkBaseClass | None:
        """Get the underlying widget."""
        return self._widget

    @property
    def isVisible(self) -> bool:
        """Check if component is visible."""
        return self._isVisible


class Card(BaseComponent):
    """Modern card component with elevation and styling."""

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame,
        title: str = "",
        corner_radius: int = 12,
        border_width: int = 1,
        **kwargs,
    ) -> None:
        """Initialize card component."""
        super().__init__(parent, **kwargs)
        self.title = title
        self.corner_radius = corner_radius
        self.border_width = border_width
        self.content_frame: ctk.CTkFrame | None = None

    def create(self) -> ctk.CTkFrame:
        """Create card widget."""
        self._widget = ctk.CTkFrame(
            self.parent,
            corner_radius=self.corner_radius,
            border_width=self.border_width,
            **self.kwargs,
        )

        # Configure grid
        self._widget.grid_columnconfigure(0, weight=1)

        # Add title if provided
        if self.title:
            titleLabel = ctk.CTkLabel(
                self._widget, text=self.title, font=ctk.CTkFont(size=16, weight="bold")
            )
            titleLabel.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))

            # Create content frame below title
            self.content_frame = ctk.CTkFrame(self._widget, fg_color="transparent")
            self.content_frame.grid(
                row=1, column=0, sticky="nsew", padx=15, pady=(0, 15)
            )
            self.content_frame.grid_columnconfigure(0, weight=1)
            self._widget.grid_rowconfigure(1, weight=1)
        else:
            # Use entire card as content frame
            self.content_frame = self._widget
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_rowconfigure(0, weight=1)

        return self._widget

    @property
    def contentFrame(self) -> ctk.CTkFrame:
        """Get the content frame (camelCase property for compatibility)."""
        if not self.content_frame:
            self.create()
        return self.content_frame

    def getContentFrame(self) -> ctk.CTkFrame:
        """Get the frame for adding content."""
        if not self.content_frame:
            raise ValueError("Card must be created before accessing content frame")
        return self.content_frame


class StatusIndicator(BaseComponent):
    """Status indicator with icon and message."""

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame,
        status: str = "ready",
        message: str = "Ready",
        **kwargs,
    ) -> None:
        """Initialize status indicator."""
        super().__init__(parent, **kwargs)
        self.status = status
        self.message = message
        self.label: ctk.CTkLabel | None = None

        # Status icons and colors
        self.statusConfig = {
            "ready": {"icon": "●", "color": "#4ade80"},
            "loading": {"icon": "○", "color": "#3b82f6"},
            "success": {"icon": "✓", "color": "#22c55e"},
            "warning": {"icon": "!", "color": "#f59e0b"},
            "error": {"icon": "✗", "color": "#ef4444"},
            "info": {"icon": "i", "color": "#06b6d4"},
        }

    def create(self) -> ctk.CTkLabel:
        """Create status indicator widget."""
        config = self.statusConfig.get(self.status, self.statusConfig["ready"])

        self.label = ctk.CTkLabel(
            self.parent,
            text=f"{config['icon']} {self.message}",
            text_color=config["color"],
            font=ctk.CTkFont(size=12),
            **self.kwargs,
        )

        self._widget = self.label
        return self.label

    def showInfo(self, message: str) -> None:
        """Show info status with message."""
        self.updateStatus("info", message)

    def showSuccess(self, message: str) -> None:
        """Show success status with message."""
        self.updateStatus("success", message)

    def showWarning(self, message: str) -> None:
        """Show warning status with message."""
        self.updateStatus("warning", message)

    def showError(self, message: str) -> None:
        """Show error status with message."""
        self.updateStatus("error", message)

    def showLoading(self, message: str) -> None:
        """Show loading status with message."""
        self.updateStatus("loading", message)

    def showReady(self, message: str = "Ready") -> None:
        """Show ready status with message."""
        self.updateStatus("ready", message)

    def setStatus(self, status: str, message: str = "") -> None:
        """Set status and message."""
        self.status = status
        if message:
            self.message = message

        if not self.label:
            self.create()

        if self.label:
            config = self.statusConfig.get(status, self.statusConfig["ready"])
            self.label.configure(
                text=f"{config['icon']} {self.message}", text_color=config["color"]
            )

    def updateStatus(self, status: str, message: str = "") -> None:
        """Update status and message (alias for setStatus)."""
        self.setStatus(status, message)

    def clear(self) -> None:
        """Clear the status indicator."""
        self.setStatus("ready", "Ready")


class ProgressCard(Card):
    """Card with built-in progress indicator."""

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame,
        title: str = "Progress",
        showPercentage: bool = True,
        **kwargs,
    ) -> None:
        """Initialize progress card."""
        super().__init__(parent, title=title, **kwargs)
        self.showPercentage = showPercentage
        self.progressBar: ctk.CTkProgressBar | None = None
        self.percentageLabel: ctk.CTkLabel | None = None
        self._progress = 0.0

    def create(self) -> ctk.CTkFrame:
        """Create progress card widget."""
        super().create()

        content = self.getContentFrame()

        # Progress bar
        self.progressBar = ctk.CTkProgressBar(content)
        self.progressBar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progressBar.set(0)

        # Percentage label
        if self.showPercentage:
            self.percentageLabel = ctk.CTkLabel(
                content, text="0%", font=ctk.CTkFont(size=12)
            )
            self.percentageLabel.grid(row=1, column=0, sticky="ew")

        content.grid_columnconfigure(0, weight=1)

        return self._widget

    def setProgress(self, progress: float) -> None:
        """Set progress value (0.0 to 1.0)."""
        self._progress = max(0.0, min(1.0, progress))

        if self.progressBar:
            self.progressBar.set(self._progress)

        if self.percentageLabel:
            self.percentageLabel.configure(text=f"{int(self._progress * 100)}%")


class ActionButton(BaseComponent):
    """Enhanced button with loading states and styling."""

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame,
        text: str,
        command: Callable[[], None] | None = None,
        style: str = "primary",
        width: int = 160,
        height: int = 40,
        **kwargs,
    ) -> None:
        """Initialize action button."""
        super().__init__(parent, **kwargs)
        self.text = text
        self.command = command
        self.style = style
        self.width = width
        self.height = height
        self.button: ctk.CTkButton | None = None
        self._originalText = text
        self._isLoading = False

        # Button styles - enhanced for better visual hierarchy
        self.styles = {
            "primary": {
                "fg_color": themeManager.getColor("primary"),
                "hover_color": themeManager.getColor("primary_variant"),
                "corner_radius": 12,
                "font": ctk.CTkFont(size=14, weight="bold"),
                "border_width": 0,
                "text_color": themeManager.getColor("on_primary"),
            },
            "secondary": {
                "fg_color": themeManager.getColor("surface"),
                "hover_color": themeManager.getColor("surface_hover"),
                "corner_radius": 12,
                "font": ctk.CTkFont(size=14, weight="normal"),
                "border_width": 2,
                "border_color": themeManager.getColor("border"),
                "text_color": themeManager.getColor("text_primary"),
            },
            "success": {
                "fg_color": themeManager.getColor("success"),
                "hover_color": themeManager.getColor("success_variant"),
                "corner_radius": 12,
                "font": ctk.CTkFont(size=14, weight="bold"),
                "border_width": 0,
                "text_color": themeManager.getColor("on_primary"),
            },
            "danger": {
                "fg_color": themeManager.getColor("error"),
                "hover_color": themeManager.getColor("error_variant"),
                "corner_radius": 12,
                "font": ctk.CTkFont(size=14, weight="bold"),
                "border_width": 0,
                "text_color": themeManager.getColor("on_primary"),
            },
            "warning": {
                "fg_color": themeManager.getColor("warning"),
                "hover_color": themeManager.getColor("warning_variant"),
                "corner_radius": 12,
                "font": ctk.CTkFont(size=14, weight="bold"),
                "border_width": 0,
                "text_color": themeManager.getColor("on_primary"),
            },
        }

    def create(self) -> ctk.CTkButton:
        """Create button widget."""
        style_config = self.styles.get(self.style, self.styles["primary"])

        self.button = ctk.CTkButton(
            self.parent,
            text=self.text,
            command=self._handleClick,
            width=self.width,
            height=self.height,
            **style_config,
            **self.kwargs,
        )

        self._widget = self.button
        return self.button

    def _handleClick(self) -> None:
        """Handle button click."""
        if not self._isLoading and self.command:
            self.command()

    def setLoading(self, loading: bool, loadingText: str = "Loading...") -> None:
        """Set button loading state."""
        self._isLoading = loading

        if self.button:
            if loading:
                self.button.configure(text=loadingText, state="disabled")
            else:
                self.button.configure(text=self._originalText, state="normal")

    def setEnabled(self, enabled: bool) -> None:
        """Enable or disable the button."""
        if not self.button:
            self.create()

        if self.button:
            state = "normal" if enabled else "disabled"
            self.button.configure(state=state)

    def setText(self, text: str) -> None:
        """Update button text."""
        self._originalText = text
        if self.button and not self._isLoading:
            self.button.configure(text=text)


class InputField(BaseComponent):
    """Enhanced input field with validation and styling."""

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame,
        placeholder: str = "",
        validator: Callable[[str], tuple[bool, str]] | None = None,
        multiline: bool = False,
        height: int = 32,
        **kwargs,
    ) -> None:
        """Initialize input field."""
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.validator = validator
        self.multiline = multiline
        self.height = height
        self.entry: ctk.CTkEntry | ctk.CTkTextbox | None = None
        self.errorLabel: ctk.CTkLabel | None = None
        self._isValid = True

    def create(self) -> ctk.CTkFrame:
        """Create input field widget."""
        # Container frame
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.grid_columnconfigure(0, weight=1)

        # Input widget
        if self.multiline:
            self.entry = ctk.CTkTextbox(container, height=self.height, **self.kwargs)
        else:
            self.entry = ctk.CTkEntry(
                container,
                placeholder_text=self.placeholder,
                height=self.height,
                **self.kwargs,
            )

        self.entry.grid(row=0, column=0, sticky="ew")

        # Error label (hidden by default)
        self.errorLabel = ctk.CTkLabel(
            container,
            text="",
            text_color="#ef4444",
            font=ctk.CTkFont(size=10),
            height=0,
        )
        self.errorLabel.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.errorLabel.grid_remove()

        self._widget = container
        return container

    def getValue(self) -> str:
        """Get input value."""
        if not self.entry:
            return ""

        if self.multiline:
            return self.entry.get("1.0", "end-1c")
        else:
            return self.entry.get()

    def setValue(self, value: str) -> None:
        """Set input value."""
        if not self.entry:
            return

        if self.multiline:
            self.entry.delete("1.0", "end")
            self.entry.insert("1.0", value)
        else:
            self.entry.delete(0, "end")
            self.entry.insert(0, value)

    def validate(self) -> bool:
        """Validate input value."""
        if not self.validator:
            return True

        value = self.getValue()
        isValid, errorMessage = self.validator(value)

        self._isValid = isValid

        if self.errorLabel:
            if isValid:
                self.errorLabel.grid_remove()
            else:
                self.errorLabel.configure(text=errorMessage)
                self.errorLabel.grid()

        return isValid

    @property
    def isValid(self) -> bool:
        """Check if input is valid."""
        return self._isValid

    def focus(self) -> None:
        """Set focus to the input field."""
        if self.entry:
            self.entry.focus()

    def getText(self) -> str:
        """Get input text (alias for getValue for compatibility)."""
        return self.getValue()

    def clear(self) -> None:
        """Clear the input field."""
        self.setValue("")

    def selectAll(self) -> None:
        """Select all text in the input field."""
        if not self.entry:
            return

        if self.multiline:
            self.entry.tag_add("sel", "1.0", "end")
        else:
            self.entry.select_range(0, "end")


class ScrollableFrame(BaseComponent):
    """Scrollable frame component for long content."""

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame,
        **kwargs,
    ) -> None:
        """Initialize scrollable frame."""
        super().__init__(parent, **kwargs)
        self.scrollableFrame: ctk.CTkScrollableFrame | None = None

    def create(self) -> ctk.CTkScrollableFrame:
        """Create scrollable frame widget."""
        self.scrollableFrame = ctk.CTkScrollableFrame(self.parent, **self.kwargs)
        self._widget = self.scrollableFrame

        # Enable mouse wheel scrolling
        self._bind_mousewheel(self.scrollableFrame)

        return self.scrollableFrame

    def _bind_mousewheel(self, widget) -> None:
        """Bind mouse wheel events for scrolling."""

        def _on_mousewheel(event):
            # Check if the widget is still valid and has a scroll method
            try:
                if hasattr(widget, "_parent_canvas"):
                    canvas = widget._parent_canvas
                    if canvas and canvas.winfo_exists():
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass  # Ignore errors if widget is destroyed

        # Bind to the frame and all its children
        def bind_to_mousewheel(w):
            w.bind("<MouseWheel>", _on_mousewheel)  # Windows
            w.bind(
                "<Button-4>",
                lambda e: _on_mousewheel(type("Event", (), {"delta": 120})()),
            )  # Linux
            w.bind(
                "<Button-5>",
                lambda e: _on_mousewheel(type("Event", (), {"delta": -120})()),
            )  # Linux

        bind_to_mousewheel(widget)

        # Also bind to children when they are added
        def bind_children():
            try:
                for child in widget.winfo_children():
                    bind_to_mousewheel(child)
                    if hasattr(child, "winfo_children"):
                        for grandchild in child.winfo_children():
                            bind_to_mousewheel(grandchild)
            except Exception:
                pass

        # Bind initially and also after a short delay to catch dynamically added widgets
        widget.after(100, bind_children)

    @property
    def contentFrame(self) -> ctk.CTkScrollableFrame:
        """Get the content frame for adding widgets."""
        if not self.scrollableFrame:
            self.create()
        return self.scrollableFrame
