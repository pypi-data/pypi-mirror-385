from PyQt6.QtWidgets import QFrame, QGridLayout, QWidget


class Display(QFrame):
    """
    The main display area for the application, using a grid layout.
    This allows for flexible arrangement of widgets, like a toolbar,
    main content area and side panels.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

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
