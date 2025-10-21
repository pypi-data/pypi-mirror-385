# src/ingot/app.py

from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QWidget
from PyQt6.QtGui import QIcon, QAction  # Import QAction for type hinting

from .workspace import WorkspaceManager
from .theming.manager import ThemeManager
from .views.base import BaseView

# --- MODIFICATION START ---
# Replace the MenuBarManager with the new ActionManager
from .actions.manager import ActionManager

# --- MODIFICATION END ---
# --- NEW IMPORT ---
from .workspaces.canvas import CanvasWorkspace

# --- END NEW IMPORT ---
from .display import Display

# --- NEW IMPORT FOR PHASE 1 ---
from .toolbar import MainToolbar


class IngotApp(QMainWindow):
    """
    The main application window, providing the core structure.
    It integrates a workspace, theming, and basic window management.
    """

    def __init__(
        self,
        view_config: dict,
        config: dict | None = None,
        workspace_type: str = "standard",
    ):
        super().__init__()
        self.resize(1080, 720)
        self._load_configuration(config)

        # --- MODIFICATION START ---
        # Initialize the ActionManager and Display
        self.action_manager = ActionManager(self)
        self.display = Display()
        # NEW: Assign a consistent name to the main display frame
        self.display.setObjectName("ingotDisplay")

        # NEW: Don't create the menu bar since we're using the toolbar menu now
        # self.setMenuBar(QMenuBar(self))

        # Pass the ActionManager to the ThemeManager
        self.theme_manager = ThemeManager(self, self.action_manager)
        # --- MODIFICATION END ---

        # New: Workspace selection logic based on workspace_type
        if workspace_type == "canvas":
            # CanvasWorkspace expects the view_config dictionary
            canvas_config = (
                config.get("canvas", {}) if config else {}
            )  # Extract canvas-specific config if present
            self.workspace = CanvasWorkspace(
                view_config=view_config, canvas_config=canvas_config
            )
        elif workspace_type == "standard":
            # Standard workspace still expects the view_config dictionary
            self.workspace = WorkspaceManager(view_config=view_config)
        else:
            raise ValueError(
                f"Unknown workspace_type: '{workspace_type}'. Valid options: 'standard', 'canvas'"
            )

        # Ensure consistent naming for theming, regardless of workspace type chosen
        self.workspace.setObjectName("ingotWorkspace")
        if hasattr(
            self.workspace, "tabBar"
        ):  # Check if the workspace has a tabBar method (standard and canvas do)
            self.workspace.tabBar().setObjectName("ingotWorkspaceTabBar")

        # NEW: Create and set up the main toolbar for Phase 1
        self.main_toolbar = MainToolbar()
        
        # Set up the toolbar menu using ActionManager
        # Create a menu from the menu configuration
        self._setup_toolbar_menu()
        
        # NEW: Add navigation history stacks for back/forward functionality
        self.back_stack = []
        self.forward_stack = []
        self._previous_tab_index = -1
        
        # Connect tab change signal for navigation history and updating toolbar label
        self.workspace.currentChanged.connect(self._on_tab_changed)

        # Set up the main layout - add toolbar first, then main content, then status bar
        self.display.set_toolbar(self.main_toolbar)
        self.display.set_main_widget(self.workspace)
        
        # Add the status bar at the bottom
        self.display.add_status_bar()
        self.status_bar = self.display.get_status_bar()
        
        # Connect to workspace zoom changes if it has zoom functionality
        if hasattr(self.workspace, 'zoom_in'):
            # Connect the workspace's zoom methods to update the status bar
            self._connect_zoom_signals()
        
        self.setCentralWidget(self.display)

        # NEW: Explicitly remove any default menu bar and apply theme
        # Apply user theme
        self.theme_manager.apply_theme("theme")
        
        # Ensure no menu bar is visible
        self.setMenuBar(None)

    def _setup_toolbar_menu(self):
        """Sets up the toolbar menu using ActionManager."""
        # The toolbar menu button will show the same menu as the old menu bar
        # but using the ActionManager to build it into a QMenu
        menu = QMenu(self)
        
        # For Phase 1, we'll use the same menu bar structure but populate a QMenu
        # We'll need to add this functionality to the ActionManager
        # For now, we'll temporarily handle this differently
        pass
    
    def _connect_zoom_signals(self):
        """Connect zoom functionality to update status bar."""
        # Override zoom methods to update status bar
        original_zoom_in = self.workspace.zoom_in
        original_zoom_out = self.workspace.zoom_out
        original_reset_zoom = self.workspace.reset_zoom
        
        def zoom_in_wrapper(*args, **kwargs):
            original_zoom_in(*args, **kwargs)
            self._update_status_bar_zoom()
            
        def zoom_out_wrapper(*args, **kwargs):
            original_zoom_out(*args, **kwargs)
            self._update_status_bar_zoom()
            
        def reset_zoom_wrapper(*args, **kwargs):
            original_reset_zoom(*args, **kwargs)
            self._update_status_bar_zoom()
        
        # Replace the workspace methods with wrapped versions
        self.workspace.zoom_in = zoom_in_wrapper
        self.workspace.zoom_out = zoom_out_wrapper
        self.workspace.reset_zoom = reset_zoom_wrapper
        
        # Update status bar initially
        self._update_status_bar_zoom()
    
    def _update_status_bar_zoom(self):
        """Update the status bar with current zoom level."""
        current_scroll_area = self.workspace.currentWidget()
        if current_scroll_area:
            content_widget = current_scroll_area.widget()
            if content_widget and hasattr(content_widget, 'get_zoom_level'):
                zoom_level = content_widget.get_zoom_level()
                self.status_bar.update_zoom(zoom_level)
    
    def update_status_bar_coordinates(self):
        """Update the status bar with current coordinates."""
        current_scroll_area = self.workspace.currentWidget()
        if current_scroll_area:
            content_widget = current_scroll_area.widget()
            if content_widget and hasattr(content_widget, 'get_mouse_position') and hasattr(content_widget, 'get_center_offset'):
                mouse_pos = content_widget.get_mouse_position()
                center_offset = content_widget.get_center_offset()
                
                pos_str = f"({mouse_pos.x()}, {mouse_pos.y()})"
                center_str = f"({center_offset.x()}, {center_offset.y()})"
                
                self.status_bar.update_coordinates(pos_str, center_str)
    
    def update_status_bar_from_canvas(self):
        """Update status bar from canvas widget - called when canvas data changes."""
        current_scroll_area = self.workspace.currentWidget()
        if current_scroll_area:
            content_widget = current_scroll_area.widget()
            if content_widget and hasattr(content_widget, 'get_mouse_position') and hasattr(content_widget, 'get_center_offset'):
                mouse_pos = content_widget.get_mouse_position()
                center_offset = content_widget.get_center_offset()
                
                pos_str = f"({mouse_pos.x()}, {mouse_pos.y()})"
                center_str = f"({center_offset.x()}, {center_offset.y()})"
                
                self.status_bar.update_coordinates(pos_str, center_str)
            
            if content_widget and hasattr(content_widget, 'get_current_color'):
                color = content_widget.get_current_color()
                color_str = f"({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
                self.status_bar.update_color(color_str)
            
            if content_widget and hasattr(content_widget, 'get_zoom_level'):
                zoom_level = content_widget.get_zoom_level()
                self.status_bar.update_zoom(zoom_level)

    def set_menu(self, menu_data: dict):
        """Builds and sets the toolbar menu from a dictionary."""
        # Create a menu for the toolbar's hamburger button
        toolbar_menu = QMenu(self)
        self.action_manager.build_menu_for_toolbar(toolbar_menu, menu_data)
        
        # Set the toolbar menu
        self.main_toolbar.set_menu(toolbar_menu)
        
        # Connect toolbar button signals
        self.main_toolbar.connect_left_panel_toggle_clicked(
            lambda: self._toggle_side_panel("left")
        )
        self.main_toolbar.connect_right_panel_toggle_clicked(
            lambda: self._toggle_side_panel("right")
        )
        self.main_toolbar.connect_back_clicked(self._navigate_back)
        self.main_toolbar.connect_forward_clicked(self._navigate_forward)

    # --- NEW METHOD ---
    def get_action(self, action_id: str) -> QAction | None:
        """Public accessor for retrieving a registered action."""
        return self.action_manager.get_action(action_id)

    # --- END NEW METHOD ---

    def _toggle_side_panel(self, position: str):
        """Toggles the visibility of a side panel."""
        # Find the side panel widget
        panel_widget = self.findChild(QWidget, f"ingotSidePanel_{position}")
        if panel_widget:
            new_visibility = not panel_widget.isVisible()
            panel_widget.setVisible(new_visibility)
            print(f"Toggled {position} panel visibility: {new_visibility}")

    def _on_tab_changed(self, current_index: int):
        """Handle tab change to update navigation history and toolbar label."""
        # Add the previous tab to back stack if we've moved from a valid tab
        if self._previous_tab_index >= 0 and self._previous_tab_index != current_index:
            self.back_stack.append(self._previous_tab_index)
            # Clear forward stack when we navigate to a new tab
            self.forward_stack.clear()
        
        self._previous_tab_index = current_index
        
        # Update the current tab label in the toolbar
        if current_index >= 0:
            tab_text = self.workspace.tabText(current_index)
            self.main_toolbar.update_current_tab_label(tab_text)

    def _navigate_back(self):
        """Navigate to the previous tab in history."""
        if self.back_stack:
            previous_index = self.back_stack.pop()
            self.forward_stack.append(self.workspace.currentIndex())
            self.workspace.setCurrentIndex(previous_index)

    def _navigate_forward(self):
        """Navigate to the next tab in history."""
        if self.forward_stack:
            next_index = self.forward_stack.pop()
            self.back_stack.append(self.workspace.currentIndex())
            self.workspace.setCurrentIndex(next_index)

    def set_side_panel(self, widget, position: str = "left"):
        """Adds a widget to the side panel."""
        # NEW: Automatically set the object name for theming
        # This makes styling specific to 'left' or 'right' panels possible
        widget.setObjectName(f"ingotSidePanel_{position}")
        self.display.set_side_panel(widget, position)

    def _load_configuration(self, config: dict | None):
        # This method's content remains unchanged.
        self.setWindowTitle("Ingot Application")
        if config:
            self.setWindowTitle(config.get("title", "Ingot Application"))
            if "icon" in config:
                try:
                    from rune import assets
                    import logging

                    icon_path_str = config["icon"]
                    path_parts = icon_path_str.split(".")
                    current_asset = assets
                    for part in path_parts:
                        current_asset = getattr(current_asset, part)
                    icon_path = current_asset
                    self.setWindowIcon(QIcon(str(icon_path)))
                except ImportError:
                    logging.warning(
                        "rune-lib is not installed. Cannot load the application icon."
                    )
                except (AttributeError, FileNotFoundError):
                    logging.warning(
                        f"Icon asset path '{config['icon']}' could not be found."
                    )
