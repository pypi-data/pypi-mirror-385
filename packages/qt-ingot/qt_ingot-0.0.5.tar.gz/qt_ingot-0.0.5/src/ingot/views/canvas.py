"""
src/ingot/views/canvas.py
Simplified canvas views with comprehensive logging and core functionality
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter, QRadialGradient, QPen, QColor, QCursor
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from .base import BaseView
import logging

# Set up logging
import sys
import logging
from rich.console import Console

# Set up rich console
console = Console()
logger = logging.getLogger(__name__)


class CanvasWidget(QWidget):
    """
    Base canvas widget with zoom, coordinate tracking, and color picking.
    Serves as a container for any type of content with proper coordinate system.
    """

    status_updated = pyqtSignal(dict)  # Our new signal

    def __init__(self, width=4096, height=4096):
        super().__init__()
        self.setFixedSize(width, height)
        self._zoom_level = 1.0
        self._canvas_center = QPoint(2048, 2048)  # Center of the large canvas
        self._mouse_pos = QPoint(0, 0)
        self._current_color = QColor(128, 128, 128, 255)  # Default gray
        self._scope_visible = True  # Default to visible as per v0.0.5 requirements
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        # Enable mouse tracking for real-time coordinate updates
        self.setMouseTracking(True)
        logger.info(
            "CanvasWidget initialized with size 4096x4096, center at (2048,2048)"
        )

        # Track last position to limit logging frequency
        self._last_log_pos = QPoint(-100, -100)  # Initialize to different position
        self._log_threshold = 50  # Only log if mouse moves more than this distance

        # Set object name for styling as per v0.0.5 requirements
        self.setObjectName("ingotCanvasWidget")

    def paint_content(self, painter):
        """Override this method in subclasses to paint specific content."""
        pass

    def mouseMoveEvent(self, event):
        """Handle mouse movement for coordinate tracking and color sampling."""
        self._mouse_pos = event.pos()

        # Update current color at mouse position
        self._current_color = self._get_color_at_position(self._mouse_pos)

        # Conditionally log with rich colored output - only if mouse moved significantly
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        rel_x = self._mouse_pos.x() - center_x
        rel_y = self._mouse_pos.y() - center_y

        # Calculate distance from last logged position
        dist_sq = (self._mouse_pos.x() - self._last_log_pos.x()) ** 2 + (
            self._mouse_pos.y() - self._last_log_pos.y()
        ) ** 2

        if dist_sq >= self._log_threshold**2:  # Only log if moved more than threshold
            # Create rich text with color visualization
            color_r, color_g, color_b, color_a = (
                self._current_color.red(),
                self._current_color.green(),
                self._current_color.blue(),
                self._current_color.alpha(),
            )

            # Create a colored block character to represent the color
            color_block = f"[{color_r},{color_g},{color_b}]"
            # Print to console with rich color representation
            console.print(
                f"[bold]Position:[/] ({self._mouse_pos.x()}, {self._mouse_pos.y()}), "
                f"[bold]Relative to center:[/] ({rel_x}, {rel_y}), "
                f"[bold]Color:[/] ({color_r}, {color_g}, {color_b}, {color_a}) "
                f"[on rgb({color_r},{color_g},{color_b})]{color_block}[/]"
            )

            self._last_log_pos = QPoint(self._mouse_pos)

        # Update the display
        self.update()

        # Emit the signal with all necessary data
        status_data = {
            "pos": self._mouse_pos,
            "relative": QPoint(rel_x, rel_y),
            "color": self._current_color,
            "zoom": self._zoom_level,
        }
        self.status_updated.emit(status_data)  # Fire the signal

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for color sampling."""
        self._mouse_pos = event.pos()
        self._current_color = self._get_color_at_position(self._mouse_pos)

        # Print rich color information to terminal
        color_r, color_g, color_b, color_a = (
            self._current_color.red(),
            self._current_color.green(),
            self._current_color.blue(),
            self._current_color.alpha(),
        )
        color_block = f"[{color_r},{color_g},{color_b}]"
        console.print(
            f"[bold red]Mouse Press:[/] ({self._mouse_pos.x()}, {self._mouse_pos.y()}), "
            f"[bold]Color:[/] ({color_r}, {color_g}, {color_b}, {color_a}) "
            f"[on rgb({color_r},{color_g},{color_b})]{color_block}[/]"
        )
        super().mousePressEvent(event)

    def _get_color_at_position(self, pos):
        """Override this method in subclasses to provide proper color sampling."""
        return QColor(128, 128, 128, 255)  # Default gray background

    def set_zoom_level(self, zoom_level):
        """Set the zoom level for the canvas."""
        self._zoom_level = max(
            0.1, min(3.0, zoom_level)
        )  # Limit zoom between 0.1x and 3x
        # Print zoom information to terminal with rich formatting
        zoom_percent = self._zoom_level * 100
        console.print(
            f"[bold yellow]Zoom:[/] {self._zoom_level:.2f}x ({zoom_percent:.0f}%)"
        )
        self.update()

        # Emit the signal with all necessary data
        status_data = {
            "pos": self._mouse_pos,
            "relative": self.get_center_offset(),  # Use existing methods
            "color": self._current_color,
            "zoom": self._zoom_level,
        }
        self.status_updated.emit(status_data)  # Fire the signal

    def get_zoom_level(self):
        """Get the current zoom level."""
        return self._zoom_level

    def get_mouse_position(self):
        """Get the current mouse position."""
        return self._mouse_pos

    def get_center_offset(self):
        """Get the offset from the center."""
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        dx = self._mouse_pos.x() - center_x
        dy = self._mouse_pos.y() - center_y
        return QPoint(dx, dy)

    def get_current_color(self):
        """Get the current color at the cursor position."""
        return self._current_color

    def toggle_scope(self):
        """Toggle the visibility of the cursor scope."""
        self._scope_visible = not self._scope_visible
        self.update()  # Force a repaint

    def is_scope_visible(self):
        """Check if the scope is currently visible."""
        return self._scope_visible

    def paintEvent(self, event):
        """Paint the canvas content with zoom and optional scope."""
        painter = QPainter(self)

        # Apply zoom transformation as per v0.0.5 requirements
        painter.scale(self._zoom_level, self._zoom_level)

        # Paint the main content
        self.paint_content(painter)

        # Draw the scope crosshairs if visible as per v0.0.5 requirements
        if self._scope_visible:
            # Create a pen with a width that is INVERSE to the zoom
            # This makes it always appear 1px wide on screen
            scope_pen = QPen(
                QColor(150, 150, 150), 1 / self._zoom_level
            )  # As per v0.0.5 requirements
            scope_pen.setStyle(Qt.PenStyle.DotLine)  # As per v0.0.5 requirements
            painter.setPen(scope_pen)

            # Draw lines based on the stored mouse position
            mouse_x = self._mouse_pos.x()
            mouse_y = self._mouse_pos.y()
            painter.drawLine(
                mouse_x, 0, mouse_x, self.height()
            )  # As per v0.0.5 requirements
            painter.drawLine(
                0, mouse_y, self.width(), mouse_y
            )  # As per v0.0.5 requirements


class GradientCanvasWidget(CanvasWidget):
    """
    Canvas widget that displays a large gradient circle for testing color picking.
    The gradient is centered at (0,0) which is at (2048,2048) in canvas coordinates.
    """

    def __init__(self):
        super().__init__()
        logger.info("GradientCanvasWidget initialized")

    def paint_content(self, painter):
        """Draw the gradient circle."""
        # Apply the same transformation as the base class, so we draw at the canvas center
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()

        # To maintain the circular shape regardless of zoom, we need to account for the zoom level
        # The gradient should appear as a perfect circle of a fixed visual size at the center
        actual_radius = 512  # Physical size in canvas coordinates

        # Create radial gradient centered at (center_x, center_y)
        gradient = QRadialGradient(
            center_x,
            center_y,
            0,  # Center with 0 radius
            center_x,
            center_y,
            actual_radius,  # Focal point and radius
        )
        gradient.setColorAt(0, QColor(255, 0, 0))  # Red center
        gradient.setColorAt(0.5, QColor(0, 255, 0))  # Green middle
        gradient.setColorAt(1, QColor(0, 0, 255))  # Blue edge

        # Draw the gradient circle (1024x1024) - this will be affected by the zoom transformation
        painter.fillRect(
            center_x - actual_radius,
            center_y - actual_radius,
            actual_radius * 2,
            actual_radius * 2,
            gradient,
        )

    def _get_color_at_position(self, pos):
        """Get color based on gradient position."""
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        dx = pos.x() - center_x
        dy = pos.y() - center_y
        distance = (dx * dx + dy * dy) ** 0.5

        # If within the gradient circle (radius 512)
        if distance <= 512:
            ratio = min(distance / 512.0, 1.0)
            # Create the same gradient calculation as in paint_content
            # Red at center, green at middle, blue at edge
            if ratio <= 0.5:
                # From red (1,0,0) to green (0,1,0) in first half
                t = ratio * 2  # t from 0 to 1
                red = int(255 * (1 - t))
                green = int(255 * t)
                blue = 0
            else:
                # From green (0,1,0) to blue (0,0,1) in second half
                t = (ratio - 0.5) * 2  # t from 0 to 1
                red = 0
                green = int(255 * (1 - t))
                blue = int(255 * t)
            return QColor(red, green, blue, 255)
        else:
            # Outside the gradient circle - return background color
            return QColor(128, 128, 128, 255)


class SmallWidgetCanvasWidget(CanvasWidget):
    """
    Canvas widget that demonstrates a small widget placed on a large canvas.
    """

    def __init__(self):
        super().__init__()
        logger.info("SmallWidgetCanvasWidget initialized")

        # Create a small widget to place on the canvas
        self.small_widget = QLabel("Small Widget\n(256x256)")
        self.small_widget.setFixedSize(256, 256)
        self.small_widget.setObjectName("ingotSmallCanvasWidget")
        self.small_widget.setParent(self)  # Make it a child of the canvas
        # Position it at (1024, 1024) on the canvas
        self.small_widget.move(1024, 1024)

    def paint_content(self, painter):
        """Draw additional content if needed - currently empty."""
        pass

    def _get_color_at_position(self, pos):
        """Get color based on whether the position is over the small widget."""
        widget_x, widget_y = 1024, 1024
        widget_width, widget_height = 256, 256

        # Check if the position is within the small widget
        if (
            widget_x <= pos.x() <= widget_x + widget_width
            and widget_y <= pos.y() <= widget_y + widget_height
        ):
            # Return the widget's color
            return QColor(255, 100, 100, 150)  # Red with some transparency
        else:
            # Return the background color
            return QColor(128, 128, 128, 255)


class GradientCanvasView(BaseView):
    """
    A canvas view that displays a gradient circle for testing all features.
    """

    def __init__(self):
        super().__init__()
        self.canvas_widget = GradientCanvasWidget()
        self.layout().addWidget(self.canvas_widget)


class SmallWidgetCanvasView(BaseView):
    """
    A canvas view that demonstrates a small widget on a large canvas.
    """

    def __init__(self):
        super().__init__()
        self.canvas_widget = SmallWidgetCanvasWidget()
        self.layout().addWidget(self.canvas_widget)
