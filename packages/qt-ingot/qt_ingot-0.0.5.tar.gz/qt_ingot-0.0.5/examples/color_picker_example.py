"""
Color Picker Example - Testing the signal-slot mechanism

This example creates a simple color picker widget to demonstrate
the signal-slot communication with the status bar.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QFrame,
    QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QPalette

from ingot.app import IngotApp


class ColorPickerWidget(QWidget):
    """
    A simple color picker widget that demonstrates signal-slot communication.
    """

    # Define the same signal as the canvas widget
    status_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self._zoom_level = 1.0
        self._canvas_center = QPoint(200, 200)
        self._mouse_pos = QPoint(200, 200)
        self._current_color = QColor(255, 0, 0)  # Start with red

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Set up the UI with RGB sliders and color preview."""
        layout = QVBoxLayout(self)

        # Color preview area
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(300, 150)
        self.color_preview.setAutoFillBackground(True)
        self.update_color_preview()

        # Sliders for RGB values
        rgb_layout = QGridLayout()

        # Red
        self.red_label = QLabel("R: 255")
        self.red_slider = QSlider(Qt.Orientation.Horizontal)
        self.red_slider.setRange(0, 255)
        self.red_slider.setValue(255)
        self.red_slider.setObjectName("red_slider")

        # Green
        self.green_label = QLabel("G: 0")
        self.green_slider = QSlider(Qt.Orientation.Horizontal)
        self.green_slider.setRange(0, 255)
        self.green_slider.setValue(0)
        self.green_slider.setObjectName("green_slider")

        # Blue
        self.blue_label = QLabel("B: 0")
        self.blue_slider = QSlider(Qt.Orientation.Horizontal)
        self.blue_slider.setRange(0, 255)
        self.blue_slider.setValue(0)
        self.blue_slider.setObjectName("blue_slider")

        # Add to grid
        rgb_layout.addWidget(QLabel("Red:"), 0, 0)
        rgb_layout.addWidget(self.red_slider, 0, 1)
        rgb_layout.addWidget(self.red_label, 0, 2)

        rgb_layout.addWidget(QLabel("Green:"), 1, 0)
        rgb_layout.addWidget(self.green_slider, 1, 1)
        rgb_layout.addWidget(self.green_label, 1, 2)

        rgb_layout.addWidget(QLabel("Blue:"), 2, 0)
        rgb_layout.addWidget(self.blue_slider, 2, 1)
        rgb_layout.addWidget(self.blue_label, 2, 2)

        # Random color button
        self.random_button = QPushButton("Random Color")

        layout.addWidget(self.color_preview)
        layout.addLayout(rgb_layout)
        layout.addWidget(self.random_button)

    def connect_signals(self):
        """Connect slider and button signals."""
        self.red_slider.valueChanged.connect(self.on_color_changed)
        self.green_slider.valueChanged.connect(self.on_color_changed)
        self.blue_slider.valueChanged.connect(self.on_color_changed)
        self.random_button.clicked.connect(self.set_random_color)

    def update_color_preview(self):
        """Update the color preview area."""
        color = self._current_color
        palette = self.color_preview.palette()
        palette.setColor(QPalette.ColorRole.Window, color)
        self.color_preview.setPalette(palette)
        self.color_preview.update()

    def on_color_changed(self):
        """Handle color changes from sliders."""
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()

        self._current_color = QColor(r, g, b)
        self.red_label.setText(f"R: {r}")
        self.green_label.setText(f"G: {g}")
        self.blue_label.setText(f"B: {b}")

        self.update_color_preview()

        # Emit the status update signal to update the status bar
        status_data = {
            "pos": self._mouse_pos,
            "relative": QPoint(0, 0),  # Center offset
            "color": self._current_color,
            "zoom": self._zoom_level,
        }
        self.status_updated.emit(status_data)

    def set_random_color(self):
        """Set a random color."""
        import random

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        self.red_slider.setValue(r)
        self.green_slider.setValue(g)
        self.blue_slider.setValue(b)

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
        self._zoom_level = zoom_level
        # Emit signal to update status bar
        status_data = {
            "pos": self._mouse_pos,
            "relative": self.get_center_offset(),
            "color": self._current_color,
            "zoom": self._zoom_level,
        }
        self.status_updated.emit(status_data)


def create_color_picker_view(tab_number=1):
    """Factory function to create a color picker view."""
    return ColorPickerWidget()


def main():
    app = QApplication(sys.argv)

    # Configuration for the color picker example
    APP_CONFIG = {
        "title": "Qt Ingot - Color Picker Example",
        "version": "1.5.0",
        "author": "My Name",
    }

    VIEW_CONFIG = {
        "view_factory": create_color_picker_view,
    }

    # Create the main application window with canvas workspace
    main_window = IngotApp(
        view_config=VIEW_CONFIG, config=APP_CONFIG, workspace_type="canvas"
    )

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
