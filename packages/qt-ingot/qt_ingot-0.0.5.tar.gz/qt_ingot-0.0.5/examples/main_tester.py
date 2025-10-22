"""
Phase 1 implementation: Modernizing the Main UI and Navigation
This file implements the first phase of the qt-ingot modernization plan.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QMenu,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

from rune import AssetNotFoundError, assets

from ingot.app import IngotApp
from ingot.views.base import BaseView


# Simple view that displays the current tab number
class TabNumberView(BaseView):
    """A simple custom view that displays the current tab number."""

    def __init__(self, tab_number=1):
        super().__init__()
        self.tab_number = tab_number

        # Create a container widget that will hold all content using absolute positioning
        self.canvas_widget = QWidget()
        self.canvas_widget.setFixedSize(2000, 2000)  # Large to ensure scrolling

        # Create the main tab number label
        self.main_label = QLabel(f"Tab Number: {self.tab_number}", self.canvas_widget)
        self.main_label.setGeometry(100, 100, 400, 150)  # Positioned at top
        self.main_label.setObjectName(
            "ingotTabNumberLabel"
        )  # Add object name for styling
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add instruction text
        instruction_label = QLabel(
            "SCROLL DOWN TO SEE MORE CONTENT", self.canvas_widget
        )
        instruction_label.setGeometry(100, 300, 400, 50)
        instruction_label.setObjectName(
            "ingotInstructionLabel"
        )  # Add object name for styling
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add some content further down to make scrolling necessary
        lower_content = QLabel(
            "This is content further down to enable scrolling", self.canvas_widget
        )
        lower_content.setGeometry(100, 1500, 400, 50)
        lower_content.setObjectName(
            "ingotLowerContentLabel"
        )  # Add object name for styling
        lower_content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add ending label
        end_label = QLabel("END OF CONTENT - SCROLL UP", self.canvas_widget)
        end_label.setGeometry(100, 1800, 400, 50)
        end_label.setObjectName("ingotEndLabel")  # Add object name for styling
        end_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the canvas widget to the view's layout
        self.layout().addWidget(self.canvas_widget)

    def set_tab_number(self, number):
        """Update the displayed tab number."""
        self.tab_number = number
        # Update the main label text
        self.main_label.setText(f"Tab Number: {self.tab_number}")


# --- Application Configuration ---
APP_CONFIG = {
    "title": "Qt Ingot - Phase 1 Test",
    "version": "1.4.0",
    "author": "My Name",
    "icon": "img.template",  # A rune-lib friendly path
}


from ingot.views.canvas import GradientCanvasView, SmallWidgetCanvasView


# --- View Configuration for the Workspace ---
# Use canvas examples for the workspace



# Create a more complex view configuration with multiple canvas types
def create_canvas_view(scene_view):
    """Factory function to populate the scene view with drawable items."""
    # For now, we'll just add a simple drawable item to demonstrate the concept
    # This is a placeholder - in a real implementation, we would create Drawable objects
    # and add them to the scene_view using scene_view.add_item()
    print(f"Populating scene view with drawable items")

    # Here you would normally do:
    # my_drawable = MyDrawableItem(...)
    # scene_view.add_item(my_drawable)

    # For now, just show that the function is called
    pass


VIEW_CONFIG = {
    "view_factory": create_canvas_view,
}


# --- Helper functions for new menu actions ---
current_app_instance = (
    None  # Global variable to hold the main window instance for actions
)
# Track panel visibility state
left_panel_visible = True
right_panel_visible = True


def exit_app():
    """Exit the application."""
    sys.exit()


def toggle_side_panel(position: str):
    """Toggles the visibility of the specified side panel."""
    global current_app_instance, left_panel_visible, right_panel_visible
    if current_app_instance:
        # Access the display object which manages the side panels
        display_widget = current_app_instance.display  # This is the Display instance
        # Find the side panel widget based on position
        # The object name was set in Phase 1: f"ingotSidePanel_{position}"
        panel_widget = current_app_instance.findChild(
            QWidget, f"ingotSidePanel_{position}"
        )
        if panel_widget:
            # Toggle visibility based on current state and update tracking variable
            if position == "left":
                left_panel_visible = not left_panel_visible
                panel_widget.setVisible(left_panel_visible)
            elif position == "right":
                right_panel_visible = not right_panel_visible
                panel_widget.setVisible(right_panel_visible)
            print(f"Toggled {position} panel visibility: {panel_widget.isVisible()}")
        else:
            print(
                f"Side panel for position '{position}' not found (object name 'ingotSidePanel_{position}')."
            )


# --- Define the Menu Structure with IDs and New Actions ---
MENU_CONFIG = {
    "File": [
        {
            "id": "file.new_tab",
            "name": "New Tab",
            "shortcut": "Ctrl+T",
            "function": lambda: current_app_instance.workspace.new_tab()
            if current_app_instance
            else None,
        },  # Example: Use lambda to capture main_window later
        {
            "id": "file.close_tab",
            "name": "Close Tab",
            "shortcut": "Ctrl+W",
            "function": lambda: current_app_instance.workspace.close_tab(
                current_app_instance.workspace.currentIndex()
            )
            if current_app_instance
            else None,
        },  # Example: Use lambda
        {"id": "file.exit", "name": "Exit", "shortcut": "Ctrl+Q", "function": exit_app},
    ],
    "View": [
        # Add separator and panel toggling actions
        {"separator": True},
        {
            "id": "view.toggle_left_panel",
            "name": "Toggle Left Panel",
            "shortcut": "Ctrl+L",
            "function": lambda: toggle_side_panel("left"),
        },
        {
            "id": "view.toggle_right_panel",
            "name": "Toggle Right Panel",
            "shortcut": "Ctrl+R",
            "function": lambda: toggle_side_panel("right"),
        },
        # Add zoom actions
        {"separator": True},
        {
            "id": "view.zoom_in",
            "name": "Zoom In",
            "shortcut": "Ctrl+Plus",
            "function": lambda: current_app_instance.workspace.zoom_in()
            if current_app_instance
            else None,
        },
        {
            "id": "view.zoom_out",
            "name": "Zoom Out",
            "shortcut": "Ctrl+Minus",
            "function": lambda: current_app_instance.workspace.zoom_out()
            if current_app_instance
            else None,
        },
        {
            "id": "view.reset_zoom",
            "name": "Reset Zoom",
            "shortcut": "Ctrl+0",
            "function": lambda: current_app_instance.workspace.reset_zoom()
            if current_app_instance
            else None,
        },
    ],
    "Help": [
        {
            "id": "help.about",
            "name": "About",
            "function": lambda: print("Qt Ingot Phase 1 Test v1.4.0!"),
        }
    ],
}


# --- The Main Application Logic ---
def main():
    app = QApplication(sys.argv)

    # --- Use `qt-ingot` to build the window ---
    # Use the canvas configuration
    workspace_type_to_use = "canvas"
    main_window = IngotApp(
        view_config=VIEW_CONFIG, config=APP_CONFIG, workspace_type=workspace_type_to_use
    )

    # Assign the main window instance to the global variable for menu actions
    global current_app_instance
    current_app_instance = main_window

    # --- Set the Menu Bar ---
    main_window.set_menu(MENU_CONFIG)

    # --- Add Left Side Panel ---
    # The layout system allows adding widgets to the side.
    # The new naming from Phase 1 allows specific styling in theme.scss
    left_panel = QLabel(
        "Left Panel\n(Demonstrates\nObject Naming)\n\nPress Ctrl+L to toggle me!"
    )
    # Note: The setObjectName will now happen automatically inside main_window.set_side_panel
    # due to the changes in Phase 1. The theme.scss targets ingotSidePanel_left/right.
    main_window.set_side_panel(left_panel, position="left")

    # --- Add Right Side Panel ---
    right_panel = QLabel(
        "Right Panel\n(Demonstrates\nObject Naming)\n\nPress Ctrl+R to toggle me!"
    )
    main_window.set_side_panel(right_panel, position="right")

    main_window.show()

    # Add shortcut for ESC to exit
    from PyQt6.QtGui import QKeySequence, QShortcut

    shortcut = QShortcut(QKeySequence("Escape"), main_window)
    shortcut.activated.connect(sys.exit)

    sys.exit(app.exec())


def setup_canvas_mouse_tracking(main_window):
    """Setup mouse tracking for the current canvas to update color and coordinates in status bar."""
    current_scroll_area = main_window.workspace.currentWidget()
    if current_scroll_area:
        canvas_widget = current_scroll_area.widget()
        if canvas_widget and hasattr(canvas_widget, "setMouseTracking"):
            # Enable mouse tracking on the canvas widget (already done in CanvasWidget)

            # Connect mouse move event to update color and coordinates in status bar
            original_mouse_move = getattr(canvas_widget, "mouseMoveEvent", None)

            def mouse_move_with_tracking(event):
                # If the canvas widget has methods to get color and coordinates, use them
                if hasattr(canvas_widget, "get_current_color"):
                    color = canvas_widget.get_current_color()
                    main_window.status_bar.update_color(
                        f"({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
                    )

                # Update coordinates
                if hasattr(main_window, "update_status_bar_coordinates"):
                    main_window.update_status_bar_coordinates()

                # Call the original mouse move event if it exists
                if original_mouse_move:
                    original_mouse_move(event)

            canvas_widget.mouseMoveEvent = mouse_move_with_tracking


if __name__ == "__main__":
    main()
