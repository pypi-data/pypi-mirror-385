from PyQt6.QtWidgets import QTabWidget, QPushButton, QSplitter, QWidget
from PyQt6.QtCore import Qt
from typing import Callable
from .views.base import BaseView

# NEW: Import the layout structures and typing
from .layouts import LayoutNode, Leaf, HSplit, VSplit, WidgetFactoryDict


class WorkspaceManager(QTabWidget):
    """A tabbed workspace that dynamically creates new views using a factory."""

    def __init__(self, view_config: dict):
        super().__init__()
        # Store the entire configuration dictionary
        self._view_config = view_config
        # Extract the factory or layout template from the config
        self._view_factory_callable = view_config.get(
            "view_factory"
        )  # For backward compatibility
        self._scene_factory = view_config.get(
            "scene_factory"
        )  # For the new SceneView architecture
        self._layout_template = view_config.get(
            "layout_template"
        )  # The new declarative layout
        self._widget_factories = view_config.get(
            "widget_factories", {}
        )  # Factories for the layout

        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        # Add a "new tab" button to the corner
        add_button = QPushButton("+")
        add_button.setObjectName("ingotAddTabButton")
        add_button.clicked.connect(self.new_tab)
        self.setCornerWidget(add_button, Qt.Corner.TopRightCorner)

        # Start with one tab open
        self.new_tab()

    def new_tab(self):
        """Creates a new tab based on the view_config."""
        if self._layout_template and self._widget_factories:
            # New behavior: Build from a layout template
            content_widget = self._build_layout_from_template(
                self._layout_template, self._widget_factories
            )
        elif self._view_factory_callable and callable(self._view_factory_callable):
            # Old behavior: For backward compatibility
            content_widget = self._view_factory_callable()
        else:
            raise ValueError(
                "view_config must provide either 'view_factory' (callable) or 'layout_template' and 'widget_factories'."
            )

        index = self.addTab(content_widget, f"Tab {self.count() + 1}")
        self.setCurrentIndex(index)
        return content_widget

    def close_tab(self, index: int):
        """Closes the tab at the given index."""
        if self.count() > 1:
            self.removeTab(index)
        else:
            # Maybe show a message or prevent closing the last tab
            print("Cannot close the last tab.")

    def _build_layout_from_template(
        self, template: LayoutNode, factories: WidgetFactoryDict
    ) -> QWidget:
        """
        Recursively builds a QWidget hierarchy from a LayoutNode template.
        """
        if isinstance(template, Leaf):
            # Base case: Instantiate the widget from the factory dictionary
            widget_class = factories.get(template.name)
            if not widget_class or not issubclass(widget_class, QWidget):
                raise ValueError(
                    f"No valid QWidget factory found for placeholder '{template.name}' in factories: {list(factories.keys())}"
                )
            return widget_class()

        elif isinstance(template, (HSplit, VSplit)):
            # Recursive step: Create a splitter
            orientation = (
                Qt.Orientation.Horizontal
                if isinstance(template, HSplit)
                else Qt.Orientation.Vertical
            )
            splitter = QSplitter(orientation)

            for child_template in template.children:
                child_widget = self._build_layout_from_template(
                    child_template, factories
                )
                splitter.addWidget(child_widget)

            if template.sizes:
                splitter.setSizes(list(template.sizes))  # setSizes expects a list

            return splitter

        else:
            raise TypeError(f"Invalid layout template node type: {type(template)}")

    def zoom_in(self):
        """Zoom in the current canvas."""
        canvas = self.get_current_canvas()
        if canvas and hasattr(canvas, "set_zoom_level"):
            canvas.set_zoom_level(canvas.get_zoom_level() * 1.2)

    def zoom_out(self):
        """Zoom out the current canvas."""
        canvas = self.get_current_canvas()
        if canvas and hasattr(canvas, "set_zoom_level"):
            canvas.set_zoom_level(canvas.get_zoom_level() / 1.2)

    def reset_zoom(self):
        """Reset zoom to 100% for the current canvas."""
        canvas = self.get_current_canvas()
        if canvas and hasattr(canvas, "set_zoom_level"):
            canvas.set_zoom_level(1.0)

    def toggle_scope(self):
        """Toggle the scope visibility on the current canvas."""
        canvas = self.get_current_canvas()
        if canvas and hasattr(canvas, "toggle_scope"):
            canvas.toggle_scope()

    def get_current_canvas(self):
        """Get the current canvas widget from the active tab."""
        current_widget = self.currentWidget()
        if current_widget:
            # Look for canvas widget within the current tab's widget hierarchy
            canvas = current_widget.findChild(QWidget, "ingotCanvasWidget")
            return canvas
        return None
