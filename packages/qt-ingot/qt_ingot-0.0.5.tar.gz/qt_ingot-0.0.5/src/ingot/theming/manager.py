# src/ingot/theming/manager.py

import sass
import importlib.resources as pkg_resources
from PyQt6.QtWidgets import QWidget
import logging
from rune import assets, AssetNotFoundError

# --- MODIFICATION START ---
# We need the ActionManager for type hinting and interaction
from ..actions.manager import ActionManager
# --- MODIFICATION END ---


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class ThemeManager:
    """Manages the loading, application, and scaffolding of SASS stylesheets."""

    def __init__(self, target_widget: QWidget, action_manager: ActionManager):
        self._target = target_widget
        # --- MODIFICATION START ---
        # Store the ActionManager instance instead of the MenuBar
        self._action_manager = action_manager
        self._build_theme_menu()
        # --- MODIFICATION END ---

    def _build_theme_menu(self):
        """
        Discovers themes and generates a menu data dictionary,
        which is then used to build the actual menu via the ActionManager.
        """
        theme_menu_items = []
        try:
            discovered_themes = assets.themes.discover("*.scss")
            if not discovered_themes:
                raise AssetNotFoundError("No themes discovered", assets.themes, [])

            for theme_name in discovered_themes:
                theme_menu_items.append(
                    {
                        "id": f"view.themes.{theme_name}",
                        "name": theme_name.capitalize(),
                        "function": lambda checked, name=theme_name: self.apply_theme(
                            name
                        ),
                    }
                )
        except (AttributeError, AssetNotFoundError):
            theme_menu_items.append(
                {"id": "view.themes.none", "name": "No Themes Found"}
            )

        # The complete data structure for the "View" menu
        view_menu_data = {"View": [{"separator": True}, *theme_menu_items]}

        # NEW: Since we're not using the menuBar anymore, we'll just register the actions
        # The toolbar will handle displaying them
        for menu_name, menu_items in view_menu_data.items():
            for item in menu_items:
                if item.get("separator"):
                    continue

                action_id = item.get("id")
                if not action_id:
                    continue

                # Register theme actions so they're available
                # Create the QAction
                from PyQt6.QtGui import QAction

                action = QAction(item["name"], self._target)
                if "function" in item:
                    action.triggered.connect(item["function"])

                # Register it in the action manager
                self._action_manager.register_action(action_id, action)

    def apply_theme(self, theme_name: str):
        """Compiles a SASS file and applies it to the target widget."""
        try:
            scss_path = assets.themes.get(theme_name)
            if not scss_path or not scss_path.exists():
                raise FileNotFoundError

            include_paths = [str(scss_path.parent)]
            with open(scss_path, "r") as f:
                compiled_css = sass.compile(
                    string=f.read(), include_paths=include_paths
                )
                self._target.setStyleSheet(compiled_css)

        except (AttributeError, FileNotFoundError):
            logging.warning(
                f"Theme '{theme_name}' not found. Applying the built-in default theme as a fallback."
            )
            self.apply_default_theme()
        except Exception as e:
            logging.error(f"Error applying theme {theme_name}: {e}")

    def apply_default_theme(self):
        """Applies the default theme bundled with qt-ingot."""
        try:
            # This logic can be simplified for future versions, but is fine for now
            with pkg_resources.path(
                "ingot.resources.themes", "theme.scss"
            ) as scss_path:
                include_paths = [str(scss_path.parent)]
                compiled_css = sass.compile(
                    filename=str(scss_path), include_paths=include_paths
                )
                self._target.setStyleSheet(compiled_css)
        except Exception as e:
            logging.error(f"Error applying default theme: {e}")
