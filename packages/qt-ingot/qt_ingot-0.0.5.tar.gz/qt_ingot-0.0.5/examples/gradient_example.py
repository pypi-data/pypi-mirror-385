"""
Simple Gradient Example - Demonstrating gradient drawing in Qt

This example creates a simple gradient widget that works within the canvas framework.
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QRadialGradient, QLinearGradient, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

from ingot.app import IngotApp
from ingot.views.base import BaseView


class GradientWidget(QWidget):
    """
    A simple gradient widget that demonstrates Qt's gradient drawing capabilities.
    """

    # Define the same signal as the canvas widget
    status_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 600)
        self._zoom_level = 1.0
        self._canvas_center = QPoint(300, 300)
        self._mouse_pos = QPoint(0, 0)
        self._current_color = QColor(128, 128, 128, 255)

        # Enable mouse tracking for color picking
        self.setMouseTracking(True)

    def paintEvent(self, event):
        """Draw the gradient."""
        painter = QPainter(self)
        painter.setRenderHint(painter.RenderHint.Antialiasing)

        # Create a linear gradient from top-left to bottom-right
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(255, 0, 0))  # Red
        gradient.setColorAt(0.33, QColor(0, 255, 0))  # Green
        gradient.setColorAt(0.66, QColor(0, 0, 255))  # Blue
        gradient.setColorAt(1, QColor(255, 255, 0))  # Yellow

        # Fill with gradient
        painter.fillRect(self.rect(), gradient)

        # Draw some circles with radial gradients
        self.draw_radial_gradients(painter)

    def draw_radial_gradients(self, painter):
        """Draw some circles with radial gradients."""
        # Circle 1: Red to transparent
        center_x, center_y = 150, 150
        radial_grad1 = QRadialGradient(center_x, center_y, 0, center_x, center_y, 50)
        radial_grad1.setColorAt(0, QColor(255, 0, 0, 255))  # Opaque red center
        radial_grad1.setColorAt(1, QColor(255, 0, 0, 0))  # Transparent edge

        painter.setBrush(radial_grad1)
        painter.drawEllipse(center_x - 50, center_y - 50, 100, 100)

        # Circle 2: Blue to white
        center_x, center_y = 400, 150
        radial_grad2 = QRadialGradient(center_x, center_y, 0, center_x, center_y, 50)
        radial_grad2.setColorAt(0, QColor(0, 0, 255, 255))  # Opaque blue center
        radial_grad2.setColorAt(1, QColor(255, 255, 255, 255))  # White edge

        painter.setBrush(radial_grad2)
        painter.drawEllipse(center_x - 50, center_y - 50, 100, 100)

        # Circle 3: Multi-color radial
        center_x, center_y = 150, 400
        radial_grad3 = QRadialGradient(center_x, center_y, 0, center_x, center_y, 60)
        radial_grad3.setColorAt(0, QColor(255, 255, 0, 255))  # Yellow center
        radial_grad3.setColorAt(0.5, QColor(0, 255, 255, 255))  # Cyan middle
        radial_grad3.setColorAt(1, QColor(255, 0, 255, 255))  # Magenta edge

        painter.setBrush(radial_grad3)
        painter.drawEllipse(center_x - 60, center_y - 60, 120, 120)

        # Circle 4: Rainbow radial
        center_x, center_y = 400, 400
        radial_grad4 = QRadialGradient(center_x, center_y, 0, center_x, center_y, 70)
        radial_grad4.setColorAt(0, QColor(255, 0, 0, 255))  # Red center
        radial_grad4.setColorAt(0.16, QColor(255, 165, 0, 255))  # Orange
        radial_grad4.setColorAt(0.33, QColor(255, 255, 0, 255))  # Yellow
        radial_grad4.setColorAt(0.5, QColor(0, 255, 0, 255))  # Green
        radial_grad4.setColorAt(0.66, QColor(0, 0, 255, 255))  # Blue
        radial_grad4.setColorAt(0.83, QColor(75, 0, 130, 255))  # Indigo
        radial_grad4.setColorAt(1, QColor(238, 130, 238, 255))  # Violet

        painter.setBrush(radial_grad4)
        painter.drawEllipse(center_x - 70, center_y - 70, 140, 140)

    def mouseMoveEvent(self, event):
        """Handle mouse movement for color sampling."""
        self._mouse_pos = event.pos()

        # Sample the color at the mouse position
        self._current_color = self.get_color_at_position(self._mouse_pos)

        # Emit the status update signal to update the status bar
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        rel_x = self._mouse_pos.x() - center_x
        rel_y = self._mouse_pos.y() - center_y

        status_data = {
            "pos": self._mouse_pos,
            "relative": QPoint(rel_x, rel_y),
            "color": self._current_color,
            "zoom": self._zoom_level,
        }
        self.status_updated.emit(status_data)

        super().mouseMoveEvent(event)

    def get_color_at_position(self, pos):
        """
        Sample the color at a given position.
        For this gradient example, we'll calculate an approximate color.
        """
        # Calculate normalized position in the widget (0 to 1)
        norm_x = pos.x() / self.width()
        norm_y = pos.y() / self.height()

        # For the linear gradient (red -> green -> blue -> yellow)
        # This is a simplified calculation
        r = min(255, int(255 * norm_x * 2))
        g = min(255, int(255 * norm_y * 2))
        b = min(255, int(255 * (1 - norm_x) * 2))

        return QColor(r, g, b, 255)

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
        """Get the current color."""
        return self._current_color

    def get_zoom_level(self):
        """Get the current zoom level."""
        return self._zoom_level

    def set_zoom_level(self, zoom_level):
        """Set the zoom level."""
        self._zoom_level = max(0.1, min(3.0, zoom_level))

        # Emit signal to update status bar
        status_data = {
            "pos": self._mouse_pos,
            "relative": self.get_center_offset(),
            "color": self._current_color,
            "zoom": self._zoom_level,
        }
        self.status_updated.emit(status_data)


class GradientView(BaseView):
    """
    A view that contains the gradient widget.
    """

    def __init__(self):
        super().__init__()
        self.gradient_widget = GradientWidget()
        self.layout().addWidget(self.gradient_widget)


def create_gradient_view(tab_number=1):
    """Factory function to create a gradient view."""
    return GradientView()


def main():
    app = QApplication(sys.argv)

    # Configuration for the gradient example
    APP_CONFIG = {
        "title": "Qt Ingot - Gradient Example",
        "version": "1.6.0",
        "author": "My Name",
    }

    VIEW_CONFIG = {
        "view_factory": create_gradient_view,
    }

    # Create the main application window with canvas workspace
    main_window = IngotApp(
        view_config=VIEW_CONFIG,
        config=APP_CONFIG,
        workspace_type="canvas",  # Use canvas workspace for zoom/scroll support
    )

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
