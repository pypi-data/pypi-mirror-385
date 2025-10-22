"""
src/ingot/toolbar.py

A modern toolbar widget that replaces the traditional QMenuBar.
Contains left section with menu button, center section with title/spacer,
and right section with panel toggle and navigation buttons.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class MainToolbar(QFrame):
    """
    A modern toolbar widget that houses the main application controls.
    Contains three sections: left (menu button), center (title/spacer), right (controls).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ingotMainToolbar")
        self.setup_ui()

    def setup_ui(self):
        """Set up the toolbar UI with three sections."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Left section - menu button and app icon
        self.left_frame = QFrame()
        self.left_frame.setObjectName("ingotToolbarLeft")
        self.left_layout = QHBoxLayout(self.left_frame)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(5)

        # Hamburger menu button
        self.menu_button = QPushButton("☰")
        self.menu_button.setObjectName("ingotMenuButton")
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setToolTip("Menu")

        # App icon/label
        self.app_icon = QLabel(".qt-ingot")
        self.app_icon.setObjectName("ingotAppIcon")

        self.left_layout.addWidget(self.app_icon)
        self.left_layout.addWidget(self.menu_button)

        # Center section - current tab label
        self.center_frame = QFrame()
        self.center_frame.setObjectName("ingotToolbarCenter")
        self.center_layout = QHBoxLayout(self.center_frame)
        self.center_layout.setContentsMargins(0, 0, 0, 0)

        # Label to show the current focused tab
        self.current_tab_label = QLabel("Tab 1")
        self.current_tab_label.setObjectName("ingotCurrentTabLabel")
        self.current_tab_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(self.current_tab_label)

        # Set a minimum width for the center area
        self.center_frame.setMinimumWidth(200)

        # Right section - panel toggles and navigation
        self.right_frame = QFrame()
        self.right_frame.setObjectName("ingotToolbarRight")
        self.right_layout = QHBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)

        # Back and forward buttons
        self.back_button = QPushButton("←")
        self.back_button.setObjectName("ingotBackButton")
        self.back_button.setFixedSize(30, 30)
        self.back_button.setToolTip("Back")

        self.forward_button = QPushButton("→")
        self.forward_button.setObjectName("ingotForwardButton")
        self.forward_button.setFixedSize(30, 30)
        self.forward_button.setToolTip("Forward")

        # Panel toggle buttons
        self.left_panel_toggle = QPushButton("◀")
        self.left_panel_toggle.setObjectName("ingotLeftPanelToggle")
        self.left_panel_toggle.setFixedSize(30, 30)
        self.left_panel_toggle.setToolTip("Toggle Left Panel")

        self.right_panel_toggle = QPushButton("▶")
        self.right_panel_toggle.setObjectName("ingotRightPanelToggle")
        self.right_panel_toggle.setFixedSize(30, 30)
        self.right_panel_toggle.setToolTip("Toggle Right Panel")

        self.right_layout.addWidget(self.back_button)
        self.right_layout.addWidget(self.forward_button)
        self.right_layout.addWidget(self.left_panel_toggle)
        self.right_layout.addWidget(self.right_panel_toggle)

        # Add sections to main layout
        layout.addWidget(self.left_frame)
        layout.addStretch()  # Center spacer
        layout.addWidget(self.right_frame)

    def set_menu(self, menu):
        """Set the menu that will be triggered by the menu button."""
        self.menu_button.setMenu(menu)

    def connect_back_clicked(self, callback):
        """Connect the back button clicked signal to a callback."""
        self.back_button.clicked.connect(callback)

    def connect_forward_clicked(self, callback):
        """Connect the forward button clicked signal to a callback."""
        self.forward_button.clicked.connect(callback)

    def connect_left_panel_toggle_clicked(self, callback):
        """Connect the left panel toggle button clicked signal to a callback."""
        self.left_panel_toggle.clicked.connect(callback)

    def connect_right_panel_toggle_clicked(self, callback):
        """Connect the right panel toggle button clicked signal to a callback."""
        self.right_panel_toggle.clicked.connect(callback)

    def update_current_tab_label(self, text: str):
        """Update the current tab label text."""
        self.current_tab_label.setText(text)

    def get_current_tab_label(self) -> str:
        """Get the current tab label text."""
        return self.current_tab_label.text()
