"""
Abstract Drawable interface for the SceneView architecture.

This defines the contract that all drawable items must implement.
"""

from abc import ABC, abstractmethod
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QRect


class Drawable(ABC):
    """
    Abstract base class for all drawable items in the SceneView.

    This class defines the interface that all scene objects must implement.
    """

    def __init__(self, z_index: int = 0, visible: bool = True, locked: bool = False):
        """
        Initialize the drawable item.

        Args:
            z_index: The drawing order index (higher values are drawn on top)
            visible: Whether the item should be rendered
            locked: Whether the item is locked from interaction
        """
        self.z_index = z_index
        self.visible = visible
        self.locked = locked

    @abstractmethod
    def paint(self, painter: QPainter) -> None:
        """
        Draw the item using the provided painter.

        Args:
            painter: The QPainter to use for drawing
        """
        pass

    @abstractmethod
    def get_bounding_box(self) -> QRect:
        """
        Get the bounding box of the drawable item.

        Returns:
            QRect representing the bounding box of the item
        """
        pass

    def hit_at(self, pos: QPoint) -> dict | None:
        """
        Check if the item is hit at the specified position.

        This is an optional method that can be overridden to provide
        hit detection functionality.

        Args:
            pos: The position to check for a hit

        Returns:
            A dictionary with hit information, or None if not hit
        """
        # Default implementation returns None
        return None
