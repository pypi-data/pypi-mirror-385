"""
Image Zoom Example - Demonstrating zoom functionality with an image

This example creates an image viewer with zoom functionality similar to the canvas.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QWheelEvent
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect

from ingot.app import IngotApp
from ingot.views.base import BaseView


class ImageZoomWidget(QWidget):
    """
    An image viewer widget with zoom functionality.
    """

    # Define the same signal as the canvas widget
    status_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self._zoom_level = 1.0
        self._canvas_center = QPoint(400, 300)  # Center of the widget
        self._mouse_pos = QPoint(0, 0)
        self._current_color = QColor(128, 128, 128, 255)

        # Load the template image
        img_path = Path(__file__).parent.parent / "resources" / "img" / "template.png"
        self.image = QPixmap(str(img_path))

        # If image fails to load, create a dummy image
        if self.image.isNull():
            self.image = QPixmap(400, 400)
            self.image.fill(QColor(200, 200, 200))
            # Draw a simple pattern
            painter = QPainter(self.image)
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            for i in range(0, 400, 40):
                painter.drawLine(i, 0, i, 400)
                painter.drawLine(0, i, 400, i)
            painter.end()

        # Enable mouse tracking and mouse events
        self.setMouseTracking(True)

        # Track mouse press for panning
        self._panning = False
        self._last_mouse_pos = QPoint()

    def paintEvent(self, event):
        """Draw the image with zoom."""
        painter = QPainter(self)
        painter.setRenderHint(painter.RenderHint.Antialiasing)

        # Calculate the image position to center it initially
        img_width = self.image.width() * self._zoom_level
        img_height = self.image.height() * self._zoom_level

        # Center the image in the widget initially
        img_x = (self.width() - img_width) // 2
        img_y = (self.height() - img_height) // 2

        # Draw the image
        scaled_image = self.image.scaled(
            int(self.image.width() * self._zoom_level),
            int(self.image.height() * self._zoom_level),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(int(img_x), int(img_y), scaled_image)

        # Draw center indicator
        center_pen = QPen(QColor(255, 0, 0, 150), 2 / self._zoom_level)
        painter.setPen(center_pen)
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        painter.drawLine(center_x, 0, center_x, self.height())
        painter.drawLine(0, center_y, self.width(), center_y)

        # Draw mouse position indicator
        scope_pen = QPen(
            QColor(0, 255, 0, 200), 1 / self._zoom_level, Qt.PenStyle.DotLine
        )
        painter.setPen(scope_pen)
        mouse_x, mouse_y = self._mouse_pos.x(), self._mouse_pos.y()
        painter.drawLine(mouse_x, 0, mouse_x, self.height())
        painter.drawLine(0, mouse_y, self.width(), mouse_y)

    def mouseMoveEvent(self, event):
        """Handle mouse movement for position tracking and panning."""
        self._mouse_pos = event.pos()

        # Sample the color at the mouse position if possible
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

        # Handle panning if mouse is pressed
        if self._panning:
            delta = event.pos() - self._last_mouse_pos
            # Panning would typically adjust the view offset
            # For this example, we'll just update the view
            self._last_mouse_pos = event.pos()

        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Start panning on mouse press."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_mouse_pos = event.pos()
        else:
            # Sample color on left click too
            self._mouse_pos = event.pos()
            self._current_color = self.get_color_at_position(self._mouse_pos)

            # Emit status update
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

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Stop panning on mouse release."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with mouse wheel."""
        # Get zoom factor
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9

        # Calculate new zoom level
        new_zoom = self._zoom_level * zoom_factor
        # Limit zoom between 0.1x and 3x
        new_zoom = max(0.1, min(3.0, new_zoom))

        # Update zoom level
        self._zoom_level = new_zoom

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

        # Update the display
        self.update()

        super().wheelEvent(event)

    def get_color_at_position(self, pos):
        """
        Sample the color at a given position.
        For this image viewer, we'll calculate an approximate color.
        """
        # Calculate relative position to the centered image
        img_width = int(self.image.width() * self._zoom_level)
        img_height = int(self.image.height() * self._zoom_level)
        img_x = (self.width() - img_width) // 2
        img_y = (self.height() - img_height) // 2

        # Check if position is within image bounds
        if (
            img_x <= pos.x() <= img_x + img_width
            and img_y <= pos.y() <= img_y + img_height
        ):
            # Calculate the corresponding position in the original image
            orig_x = int((pos.x() - img_x) / self._zoom_level)
            orig_y = int((pos.y() - img_y) / self._zoom_level)

            # Ensure we don't go out of bounds
            orig_x = max(0, min(self.image.width() - 1, orig_x))
            orig_y = max(0, min(self.image.height() - 1, orig_y))

            # Get color from image if possible (this is a simplified approach)
            # In a real implementation, we'd sample the actual pixel
            return QColor(
                100 + (orig_x % 155),
                100 + (orig_y % 155),
                50 + ((orig_x + orig_y) % 105),
            )

        # Return default gray if outside image
        return QColor(128, 128, 128, 255)

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

        # Update display
        self.update()


class ImageZoomView(BaseView):
    """
    A view that contains the image zoom widget.
    """

    def __init__(self):
        super().__init__()
        self.image_zoom_widget = ImageZoomWidget()
        self.layout().addWidget(self.image_zoom_widget)


def create_image_zoom_view(tab_number=1):
    """Factory function to create an image zoom view."""
    return ImageZoomView()


def main():
    app = QApplication(sys.argv)

    # Configuration for the image zoom example
    APP_CONFIG = {
        "title": "Qt Ingot - Image Zoom Example",
        "version": "1.7.0",
        "author": "My Name",
    }

    VIEW_CONFIG = {
        "view_factory": create_image_zoom_view,
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
