"""
SceneView widget for the new canvas architecture.

This replaces the old CanvasWidget with a more flexible scene-based approach
that supports drawable items.
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import pyqtSignal, QPoint, QRect, Qt
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QMouseEvent
from typing import List
from .drawable import Drawable


class SceneView(QWidget):
    """
    The SceneView widget is the "engine" that handles all rendering and interaction
    for the new scene-based canvas architecture.
    """

    # Signal emitted when status information changes (zoom, position, etc.)
    status_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        # Initialize state
        self._scene_items: List[Drawable] = []
        self._zoom_level = 1.0
        self._scope_visible = True
        self._mouse_pos = QPoint(0, 0)

        # Set up the widget
        self.setMinimumSize(400, 300)  # Minimum size for usability
        self.setMouseTracking(True)  # Enable mouse tracking for scope

        # Create the "emptiness" background gradient
        self._create_background_gradient()

    def _create_background_gradient(self):
        """Create the radial gradient for the "emptiness" background."""
        # This creates a radial gradient that represents the "emptiness" of the scene
        # The gradient will be drawn as the base layer
        pass  # Gradient is created dynamically in paintEvent for flexibility

    def add_item(self, item: Drawable):
        """
        Add an item to the scene and re-sort by z_index.

        Args:
            item: The Drawable item to add to the scene
        """
        self._scene_items.append(item)
        # Sort items by z_index to ensure correct drawing order
        self._scene_items.sort(key=lambda x: x.z_index)
        self.update()  # Trigger a repaint

    def set_zoom_level(self, level: float):
        """
        Set the zoom level for the scene.

        Args:
            level: The new zoom level (will be clamped to reasonable bounds)
        """
        # Clamp zoom level to reasonable bounds (e.g., 0.1 to 10.0)
        MIN_ZOOM = 0.1
        MAX_ZOOM = 10.0
        self._zoom_level = max(MIN_ZOOM, min(MAX_ZOOM, level))

        # Emit status update and trigger repaint
        self._emit_status()
        self.update()

    def toggle_scope(self):
        """Toggle the visibility of the cursor scope (crosshair)."""
        self._scope_visible = not self._scope_visible
        self.update()  # Trigger repaint to show/hide scope

    def paintEvent(self, event):
        """
        Handle the paint event by drawing the scene in layers:
        - Layer 0: The "emptiness" radial gradient background
        - Layer 1: Scene items scaled by zoom level
        - Layer 2: Crosshair scope if visible
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Layer 0: Draw the "emptiness" radial gradient background
        self._draw_background(painter)

        # Layer 1: Draw scene items with zoom scaling
        painter.save()  # Save the painter state
        painter.scale(self._zoom_level, self._zoom_level)
        for item in self._scene_items:
            if item.visible:
                item.paint(painter)
        painter.restore()  # Restore the painter state

        # Layer 2: Draw the 1px crosshair scope if visible
        if self._scope_visible:
            self._draw_scope(painter)

    def _draw_background(self, painter: QPainter):
        """Draw the radial gradient background representing emptiness."""
        # Create a radial gradient centered in the widget
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        radius = max(self.width(), self.height()) / 2.0

        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, QColor(30, 30, 30))  # Darker center
        gradient.setColorAt(1, QColor(15, 15, 15))  # Darker edge

        painter.fillRect(0, 0, self.width(), self.height(), gradient)

    def _draw_scope(self, painter: QPainter):
        """Draw the crosshair scope at the current mouse position."""
        # Draw a simple crosshair at the mouse position
        x, y = self._mouse_pos.x(), self._mouse_pos.y()

        painter.setPen(QColor(255, 255, 255, 200))  # Semi-transparent white

        # Draw horizontal line
        painter.drawLine(0, y, self.width(), y)
        # Draw vertical line
        painter.drawLine(x, 0, x, self.height())

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handle mouse movement to track position and update scope.

        Args:
            event: The mouse event containing position information
        """
        # Store the current mouse position
        self._mouse_pos = event.position().toPoint()

        # Emit status update and trigger repaint for scope
        self._emit_status()
        self.update()

    def _emit_status(self):
        """Private helper to gather status data and emit the signal."""
        # Gather all relevant status information
        # Format needs to match what StatusBar.update_from_canvas expects
        status_data = {
            "pos": self._mouse_pos,  # QPoint for mouse position
            "relative": QPoint(
                self._mouse_pos.x(), self._mouse_pos.y()
            ),  # For center offset
            "color": QColor(
                255, 255, 255, 255
            ),  # Default white color (can be updated based on scene content)
            "zoom": self._zoom_level,  # Current zoom level
            # Additional metadata from items could be added here
        }

        # Emit the signal with the status data
        self.status_updated.emit(status_data)

    # Public API methods for zoom control
    def get_zoom_level(self) -> float:
        """Get the current zoom level."""
        return self._zoom_level

    def zoom_in(self):
        """Increase zoom level by 25%."""
        self.set_zoom_level(self._zoom_level * 1.25)

    def zoom_out(self):
        """Decrease zoom level by 20% (1/1.25)."""
        self.set_zoom_level(self._zoom_level / 1.25)

    def reset_zoom(self):
        """Reset zoom level to 1.0."""
        self.set_zoom_level(1.0)
