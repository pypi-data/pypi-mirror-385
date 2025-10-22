# """
# qt-ingot: A lightweight, themeable boilerplate for creating tab-based PyQt applications.

# This __init__.py file exposes the primary classes of the library, allowing for
# clean and direct imports.

# Example:
#     from qt_ingot import IngotApp, BaseView
# """

# __version__ = "0.0.1"

# # Import the core components to make them accessible at the top-level
# from .app import IngotApp
# from .workspace import WorkspaceManager
# from .views.base import BaseView
# from .theming.manager import ThemeManager

# # Define the public API of the package.
# # This controls what `from qt_ingot import *` will import.
# __all__ = [
#     "IngotApp",
#     "WorkspaceManager",
#     "BaseView",
#     "ThemeManager",
# ]
