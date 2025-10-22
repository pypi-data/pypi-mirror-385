# src/ingot/workspaces/canvas.py
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from ..workspace import WorkspaceManager  # Import the base WorkspaceManager
from ..scene.view import SceneView  # Import the new SceneView


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

    def __init__(
        self, view_config: dict, canvas_config: dict | None = None, update_slot=None
    ):
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
            update_slot: A slot function to connect to canvas status updates
        """
        # Store canvas-specific config
        self._canvas_config = canvas_config or {}

        # Store the update slot
        self._update_slot = update_slot

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
        in a QScrollArea, but now uses SceneView as the content widget.
        """
        # Calculate the tab number before creating the content
        tab_number = self.count() + 1

        # Create a SceneView instance as the content widget
        scene_view = SceneView()

        # Use the _view_factory_callable or _scene_factory (if it exists) to populate the scene
        # instead of creating the widget itself
        factory_callable = getattr(self, '_view_factory_callable', None) or getattr(self, '_scene_factory', None)
        
        if factory_callable and callable(factory_callable):
            # Pass the scene_view to the factory function so it can populate the scene
            factory_callable(scene_view)

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

        # Wrap the SceneView in the scroll area
        scroll_area.setWidget(scene_view)

        # Add the scroll area as a new tab
        tab_text = f"Tab {tab_number}"
        index = self.addTab(scroll_area, tab_text)
        self.setCurrentIndex(index)

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

        # Connect the scene.status_updated signal to the _update_slot
        if self._update_slot and hasattr(scene_view, "status_updated"):
            scene_view.status_updated.connect(self._update_slot)

        return scene_view

    # Optional Enhancement: Add methods for common canvas operations
    # Example: Zoom functionality (requires content widget support)
    def zoom_in(self):
        """Attempts to zoom in the content of the current tab."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the SceneView widget inside the scroll area
            scene_view = current_scroll_area.widget()
            if scene_view and hasattr(scene_view, "zoom_in"):
                scene_view.zoom_in()

    def zoom_out(self):
        """Attempts to zoom out the content of the current tab."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the SceneView widget inside the scroll area
            scene_view = current_scroll_area.widget()
            if scene_view and hasattr(scene_view, "zoom_out"):
                scene_view.zoom_out()

    def reset_zoom(self):
        """Attempts to reset the zoom level of the content of the current tab."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the SceneView widget inside the scroll area
            scene_view = current_scroll_area.widget()
            if scene_view and hasattr(scene_view, "reset_zoom"):
                scene_view.reset_zoom()

    def toggle_scope(self):
        """Toggle the scope visibility on the current scene view."""
        current_scroll_area = self.currentWidget()
        if current_scroll_area:
            # Get the SceneView widget inside the scroll area
            scene_view = current_scroll_area.widget()
            if scene_view and hasattr(scene_view, "toggle_scope"):
                scene_view.toggle_scope()
