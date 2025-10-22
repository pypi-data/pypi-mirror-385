"""
SceneView Example - The "Ultimate Canvas"

This example demonstrates the new SceneView architecture.
It loads an empty scene, allowing you to test:
- The "Emptiness" radial gradient background.
- Zoom functionality (Ctrl+Plus, Ctrl+Minus, Ctrl+0).
- The togglable cursor scope (Ctrl+H).
- Real-time status bar updates for position, zoom, and metadata.
"""
import sys
from PyQt6.QtWidgets import QApplication
from ingot.app import IngotApp

# --- 1. Define your application's configuration ---
APP_CONFIG = {
    "title": "My New SceneView App",
    "icon": "img.template"  # A rune-lib friendly path
}

# --- 2. Define your menu structure ---
# We add the new "Toggle Scope" shortcut here
MENU_CONFIG = {
    "File": [
        {"id": "file.exit", "name": "Exit", "shortcut": "Ctrl+Q", "function": sys.exit}
    ],
    "View": [
        # Standard zoom actions
        {
            "id": "view.zoom_in",
            "name": "Zoom In",
            "shortcut": "Ctrl+Plus",
            # The IngotApp/CanvasWorkspace will automatically handle this
        },
        {
            "id": "view.zoom_out",
            "name": "Zoom Out",
            "shortcut": "Ctrl+Minus",
        },
        {
            "id": "view.reset_zoom",
            "name": "Reset Zoom",
            "shortcut": "Ctrl+0",
        },
        {"separator": True},
        # New Scope Toggle Action
        {
            "id": "view.toggle_scope",
            "name": "Toggle Cursor Scope",
            "shortcut": "Ctrl+H",
            # This ID will be automatically connected by the new integration
        },
    ],
    "Help": [
        {"id": "help.about", "name": "About", "function": lambda: print("About this App!")}
    ]
}

# --- 3. Define the content for your tabs ---
#
# This is the new Developer Experience (DX)!
# Instead of creating a widget, you write a function
# that *populates* a scene. For an empty scene,
# this function simply does nothing.
#
def populate_empty_scene(scene):
    """
    A factory function that populates a SceneView.
    In this case, we add no Drawable items,
    leaving the scene empty.
    """
    print("New empty scene created.")
    # To add items, you would do:
    # my_item = MyDrawableItem(position, size)
    # scene.add_item(my_item)
    pass

# --- 4. Define the View Configuration ---
VIEW_CONFIG = {
    # This key tells the CanvasWorkspace to call
    # our `populate_empty_scene` function
    # every time a new tab is created.
    "scene_factory": populate_empty_scene,
}

# --- 5. Launch the app ---
def main():
    app = QApplication(sys.argv)
    
    # Use workspace_type="canvas" to get the SceneView
    main_window = IngotApp(
        view_config=VIEW_CONFIG, 
        config=APP_CONFIG,
        workspace_type="canvas" # This is critical
    )
    
    # Set the menu, which includes our new shortcuts
    main_window.set_menu(MENU_CONFIG)

    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()