# src/ingot/workspaces/canvas.py
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from ..workspace import WorkspaceManager  # Import the base WorkspaceManager


class CanvasWorkspace(WorkspaceManager):
    """
    A specialized workspace where each tab's content is
    automatically wrapped in a QScrollArea for panning and zooming.

    This workspace inherits the layout building capabilities from
    WorkspaceManager and wraps the resulting content widget in a
    scroll area before adding it to the tab.

    Configuration Options:
    - All options supported by WorkspaceManager (view_config) are valid here.
    - Additional options can be added in the future (e.g., default scroll behavior).
    """

    def __init__(self, view_config: dict, canvas_config: dict | None = None):
        """
        Initializes the CanvasWorkspace.

        Args:
            view_config (dict): The configuration dictionary passed to the base
                                WorkspaceManager, containing layout_template,
                                widget_factories, or view_factory.
            canvas_config (dict, optional): Configuration specific to the CanvasWorkspace.
                                            Defaults to None. Example keys could be:
                                            - 'default_scroll_behavior': 'AsNeeded' | 'AlwaysOff' | 'AlwaysOn'
                                            - 'default_resize_policy': 'AdjustToContents' | 'Fixed'
        """
        # Store canvas-specific config
        self._canvas_config = canvas_config or {}

        # Apply default canvas-specific settings first to ensure _default_scroll_policy is set
        # before parent's __init__ calls new_tab()
        self._apply_canvas_defaults()

        # Initialize the parent WorkspaceManager with the view_config
        # This handles the layout building logic internally
        super().__init__(view_config)

    def _apply_canvas_defaults(self):
        """
        Applies default settings specific to the canvas behavior,
        potentially based on _canvas_config.
        """
        # Set default scroll behavior policy
        default_scroll_policy = self._canvas_config.get(
            "default_scroll_behavior", "AsNeeded"
        )
        policies_map = {
            "AsNeeded": Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            "AlwaysOff": Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            "AlwaysOn": Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
        }
        self._default_scroll_policy = policies_map.get(
            default_scroll_policy, Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

    def new_tab(self):
        """
        Overrides the base method to wrap the generated content
        in a QScrollArea.
        """
        # Calculate the tab number before creating the content
        tab_number = self.count() + 1

        # Create the content widget with the correct tab number
        original_content_widget = self._create_content_widget(tab_number)

        # Create the scroll area
        scroll_area = QScrollArea()
        scroll_area.setObjectName(
            "ingotCanvasScrollArea"
        )  # Consistent naming for theming
        scroll_area.setWidgetResizable(
            True
        )  # Allows content to resize within the scroll area

        # Apply default scroll bar policies
        scroll_area.setHorizontalScrollBarPolicy(self._default_scroll_policy)
        scroll_area.setVerticalScrollBarPolicy(self._default_scroll_policy)

        # Wrap the original content in the scroll area
        scroll_area.setWidget(original_content_widget)

        # Add the scroll area as a new tab
        tab_text = f"Tab {tab_number}"
        index = self.addTab(scroll_area, tab_text)
        self.setCurrentIndex(index)

        # If the content widget has a method to set tab number, use it as backup
        if hasattr(original_content_widget, "set_tab_number"):
            original_content_widget.set_tab_number(tab_number)

        # Center the scroll area content if possible
        scroll_area.horizontalScrollBar().setValue(
            scroll_area.horizontalScrollBar().maximum() // 2
        )
        scroll_area.verticalScrollBar().setValue(
            scroll_area.verticalScrollBar().maximum() // 2
        )

        # Set the cursor for the viewport to be a crosshair
        from PyQt6.QtGui import QCursor
        from PyQt6.QtCore import Qt
        scroll_area.viewport().setCursor(QCursor(Qt.CursorShape.CrossCursor))

        return original_content_widget

    def _create_content_widget(self, tab_number=1):
        """Helper method to create content widget following the same logic as parent."""
        if self._layout_template and self._widget_factories:
            # Build from a layout template
            return self._build_layout_from_template(
                self._layout_template, self._widget_factories
            )
        elif self._view_factory_callable and callable(self._view_factory_callable):
            # For backward compatibility
            # Check if the factory function accepts a tab_number parameter
            import inspect

            sig = inspect.signature(self._view_factory_callable)
            if len(sig.parameters) > 0:
                # If the factory accepts parameters, call it with the tab number
                return self._view_factory_callable(tab_number)
            else:
                # If the factory doesn't accept parameters, call it without
                return self._view_factory_callable()
        else:
            raise ValueError(
                "view_config must provide either 'view_factory' (callable) or 'layout_template' and 'widget_factories'."
            )

    # Optional Enhancement: Add methods for common canvas operations
    # Example: Zoom functionality (requires content widget support)
    def zoom_in(self, factor: float = 1.2):
        """Attempts to zoom in the content of the current tab."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the actual content widget inside the scroll area
            content_widget = current_scroll_area.widget()
            if content_widget and hasattr(content_widget, "set_zoom_level"):
                current_zoom = content_widget.get_zoom_level()
                new_zoom = current_zoom * factor
                content_widget.set_zoom_level(new_zoom)

    def zoom_out(self, factor: float = 1.2):
        """Attempts to zoom out the content of the current tab."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the actual content widget inside the scroll area
            content_widget = current_scroll_area.widget()
            if content_widget and hasattr(content_widget, "set_zoom_level"):
                current_zoom = content_widget.get_zoom_level()
                new_zoom = current_zoom / factor
                # Ensure zoom doesn't go below a minimum (e.g., 0.1)
                if new_zoom >= 0.1:
                    content_widget.set_zoom_level(new_zoom)
                else:
                    print("Zoom out limited to prevent excessive scaling down.")

    def reset_zoom(self):
        """Attempts to reset the zoom level of the content of the current tab."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the actual content widget inside the scroll area
            content_widget = current_scroll_area.widget()
            if content_widget and hasattr(content_widget, "set_zoom_level"):
                content_widget.set_zoom_level(1.0)
