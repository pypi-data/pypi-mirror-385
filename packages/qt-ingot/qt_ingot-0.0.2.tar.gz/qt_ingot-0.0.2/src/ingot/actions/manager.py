# src/ingot/actions/manager.py

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction
from typing import Dict, Any

class ActionManager:
    """
    Manages the creation, registration, and retrieval of all QActions.
    It serves as a single source of truth for application-wide actions
    and is responsible for building the menu bar.
    """
    def __init__(self, parent):
        self._parent = parent
        self._actions: Dict[str, QAction] = {}

    def register_action(self, action_id: str, action: QAction) -> None:
        """Registers a QAction in the central registry."""
        if action_id in self._actions:
            # Optionally, log a warning here
            print(f"Warning: Overwriting action with ID '{action_id}'")
        self._actions[action_id] = action

    def get_action(self, action_id: str) -> QAction | None:
        """Retrieves a QAction from the registry by its ID."""
        return self._actions.get(action_id)

    def build_menu_from_dict(self, menu_data: Dict[str, Any], menu_bar: QMenuBar) -> None:
        """
        Parses a dictionary to construct or update a QMenuBar and register actions.

        Args:
            menu_data: A dictionary defining the menu structure.
            menu_bar: An existing QMenuBar to add menus to.
        """
        for menu_name, menu_items in menu_data.items():
            menu = menu_bar.findChild(QMenu, menu_name)
            if not menu:
                menu = QMenu(menu_name, menu_bar)
                menu_bar.addMenu(menu)

            for item in menu_items:
                if item.get("separator"):
                    menu.addSeparator()
                    continue

                action_id = item.get("id")
                if not action_id:
                    print(f"Warning: Menu item '{item['name']}' has no 'id'. It will not be registered.")
                    continue

                # Create the QAction
                action = QAction(item["name"], self._parent)
                if "shortcut" in item:
                    action.setShortcut(item["shortcut"])
                if "function" in item:
                    action.triggered.connect(item["function"])
                if "checkable" in item:
                    action.setCheckable(item["checkable"])

                # Register it and add it to the menu
                self.register_action(action_id, action)
                menu.addAction(action)
