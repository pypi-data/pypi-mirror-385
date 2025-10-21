# src/ingot/layouts.py
from dataclasses import dataclass
from typing import List, Union, Tuple, Dict, Type, Any
from PyQt6.QtWidgets import QWidget


@dataclass
class Leaf:
    """
    Represents a placeholder for a widget within the layout tree.
    The 'name' corresponds to a key in the 'factories' dictionary
    used by the layout builder.
    """

    name: str


@dataclass
class HSplit:
    """
    Represents a horizontal QSplitter node in the layout tree.
    Children can be other HSplit, VSplit, or Leaf nodes.
    """

    children: List["LayoutNode"]
    sizes: Tuple[int, ...] = ()  # Optional: Initial sizes for the splitter panes


@dataclass
class VSplit:
    """
    Represents a vertical QSplitter node in the layout tree.
    Children can be other HSplit, VSplit, or Leaf nodes.
    """

    children: List["LayoutNode"]
    sizes: Tuple[int, ...] = ()  # Optional: Initial sizes for the splitter panes


# A type hint for any valid node in our layout tree
LayoutNode = Union[Leaf, HSplit, VSplit]

# Optional: Type hint for the factories dictionary
# Key: str (name from Leaf), Value: callable returning a QWidget
WidgetFactoryDict = Dict[str, Type[QWidget]]
