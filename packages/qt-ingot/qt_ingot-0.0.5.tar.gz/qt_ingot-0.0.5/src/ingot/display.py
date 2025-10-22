from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QWidget,
    QStatusBar,
    QHBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QColor


class Display(QFrame):
    """
    The main display area for the application, using a grid layout.
    This allows for flexible arrangement of widgets, like a toolbar,
    main content area, side panels, and a bottom status bar.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Create the status bar at the bottom
        self.status_bar = StatusBar()
        self.status_bar.setObjectName("ingotStatusBar")

    def set_toolbar(self, widget: QWidget):
        """Sets the toolbar widget."""
        self.layout.addWidget(widget, 0, 0, 1, 3)  # Row 0, spans all columns

    def set_main_widget(self, widget: QWidget):
        """Sets the main central widget."""
        self.layout.addWidget(widget, 1, 1)  # Row 1, column 1

    def set_side_panel(self, widget: QWidget, position: str = "left"):
        """
        Adds a widget to the side panel position.

        Args:
            widget: The widget to add.
            position: 'left' or 'right'.
        """
        if position == "left":
            self.layout.addWidget(widget, 1, 0)  # Row 1, column 0
        elif position == "right":
            self.layout.addWidget(widget, 1, 2)  # Row 1, column 2

    def add_status_bar(self):
        """Adds the status bar to the bottom of the display."""
        self.layout.addWidget(self.status_bar, 2, 0, 1, 3)  # Row 2, spans all columns

    def get_status_bar(self):
        """Returns the status bar widget."""
        return self.status_bar


class StatusBar(QWidget):
    """
    A status bar widget that shows zoom level, color picker info, and mouse coordinates.
    """

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Set up the status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # Zoom indicator
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setObjectName("ingotZoomLabel")

        # Coordinates indicator
        self.coords_label = QLabel("Pos: (0, 0) | Center: (0, 0)")
        self.coords_label.setObjectName("ingotCoordsLabel")

        # Color visualization box
        self.color_visualization = QWidget()
        self.color_visualization.setFixedSize(20, 20)
        self.color_visualization.setObjectName("ingotColorVisualization")

        # Color picker indicator with styled text
        self.color_label = QLabel("Color: (255, 255, 255, 255)")
        self.color_label.setObjectName("ingotColorLabel")

        layout.addWidget(self.zoom_label)
        layout.addWidget(self.coords_label)
        layout.addStretch()  # Add stretch to push color label to the right
        layout.addWidget(self.color_visualization)
        layout.addWidget(self.color_label)

    def update_zoom(self, zoom_level: float):
        """Update the zoom level display."""
        self.zoom_label.setText(f"Zoom: {int(zoom_level * 100)}%")

    def update_color(self, color_str: str):
        """Update the color display with RGB values in their respective colors."""
        # Extract the color values from the string format "(r, g, b, a)"
        try:
            # Remove parentheses and split
            color_values = color_str.strip("()").split(",")
            r = int(color_values[0].strip())
            g = int(color_values[1].strip())
            b = int(color_values[2].strip())
            a = int(color_values[3].strip())

            # Update the color visualization box - color is passed via property for SCSS styling
            self.color_visualization.setProperty(
                "currentColor", f"rgba({r}, {g}, {b}, {a})"
            )
            # Force style sheet re-application to pick up the new property value
            self.color_visualization.style().unpolish(self.color_visualization)
            self.color_visualization.style().polish(self.color_visualization)

            # Create HTML-styled text for the color label with colored numbers
            styled_color_text = f"Color: (<span style='color: red; font-style: italic;'>{r}</span>, <span style='color: green; font-style: italic;'>{g}</span>, <span style='color: blue; font-style: italic;'>{b}</span>, {a})"
            self.color_label.setText(styled_color_text)
            self.color_label.setTextFormat(Qt.TextFormat.RichText)  # Enable rich text

        except:
            # Fallback if parsing fails
            self.color_visualization.setProperty("currentColor", "rgb(255, 255, 255)")
            # Force style sheet re-application to pick up the new property value
            self.color_visualization.style().unpolish(self.color_visualization)
            self.color_visualization.style().polish(self.color_visualization)
            self.color_label.setText(f"Color: {color_str}")

    def update_coordinates(self, pos_str: str, center_offset_str: str):
        """Update the coordinate display."""
        self.coords_label.setText(f"Pos: {pos_str} | Center: {center_offset_str}")

    @pyqtSlot(dict)
    def update_from_canvas(self, data: dict):
        """A public slot to receive all data from the canvas."""
        # Use .get() for safety, providing defaults
        pos = data.get("pos", QPoint(0, 0))
        rel = data.get("relative", QPoint(0, 0))
        color = data.get("color", QColor(255, 255, 255, 255))
        zoom = data.get("zoom", 1.0)

        pos_str = f"({pos.x()}, {pos.y()})"
        center_str = f"({rel.x()}, {rel.y()})"
        color_str = f"({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"

        # Call your existing private-like methods
        self.update_coordinates(pos_str, center_str)
        self.update_color(color_str)
        self.update_zoom(zoom)
