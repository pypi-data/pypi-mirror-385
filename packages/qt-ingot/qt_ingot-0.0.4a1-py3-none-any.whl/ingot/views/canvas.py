"""
src/ingot/views/canvas.py
Simplified canvas views with comprehensive logging and core functionality
"""
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter, QRadialGradient, QPen, QColor, QCursor
from PyQt6.QtCore import Qt, QPoint
from .base import BaseView
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Global reference to the main app for status bar updates
current_app_instance = None


class CanvasWidget(QWidget):
    """
    Base canvas widget with zoom, coordinate tracking, and color picking.
    Serves as a container for any type of content with proper coordinate system.
    """
    def __init__(self, width=4096, height=4096):
        super().__init__()
        self.setFixedSize(width, height)
        self._zoom_level = 1.0
        self._canvas_center = QPoint(2048, 2048)  # Center of the large canvas
        self._mouse_pos = QPoint(0, 0)
        self._current_color = QColor(128, 128, 128, 255)  # Default gray
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Enable mouse tracking for real-time coordinate updates
        self.setMouseTracking(True)
        logger.info("CanvasWidget initialized with size 4096x4096, center at (2048,2048)")

    def paintEvent(self, event):
        """Paint the canvas with gray background and gizmos."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background with gray
        painter.fillRect(self.rect(), QColor(128, 128, 128))
        
        # Apply zoom transformation - scale around center
        painter.save()  # Save the current state
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        painter.translate(center_x, center_y)
        painter.scale(self._zoom_level, self._zoom_level)
        painter.translate(-center_x, -center_y)
        
        # Draw gizmos - crosshairs at center
        pen = QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(0, center_y, self.width(), center_y)  # Horizontal line
        painter.drawLine(center_x, 0, center_x, self.height())  # Vertical line
        
        # Draw center point
        painter.setPen(QPen(QColor(255, 0, 0), 4))
        painter.drawPoint(center_x, center_y)
        
        # Draw coordinate label
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(center_x + 10, center_y - 10, f"Center (0,0)")
        
        # Draw current mouse position relative to center
        mouse_rel_x = self._mouse_pos.x() - center_x
        mouse_rel_y = self._mouse_pos.y() - center_y
        painter.drawText(10, 20, f"Mouse: ({mouse_rel_x}, {mouse_rel_y}) from center")
        
        painter.restore()  # Restore the original state

        # Call the subclass's specific drawing method
        self.paint_content(painter)
    
    def paint_content(self, painter):
        """Override this method in subclasses to paint specific content."""
        pass

    def mouseMoveEvent(self, event):
        """Handle mouse movement for coordinate tracking and color sampling."""
        self._mouse_pos = event.pos()
        
        # Update current color at mouse position
        self._current_color = self._get_color_at_position(self._mouse_pos)
        
        # Log real-time updates
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        rel_x = self._mouse_pos.x() - center_x
        rel_y = self._mouse_pos.y() - center_y
        logger.info(f"Position: ({self._mouse_pos.x()}, {self._mouse_pos.y()}), "
                   f"Relative to center: ({rel_x}, {rel_y}), "
                   f"Color: ({self._current_color.red()}, {self._current_color.green()}, "
                   f"{self._current_color.blue()}, {self._current_color.alpha()})")
        
        # Update the display
        self.update()
        
        # Update the status bar if we have access to the main app
        global current_app_instance
        if current_app_instance:
            try:
                current_app_instance.update_status_bar_from_canvas()
            except:
                pass  # Ignore if update fails
        
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for color sampling."""
        self._mouse_pos = event.pos()
        self._current_color = self._get_color_at_position(self._mouse_pos)
        logger.info(f"Mouse pressed at ({self._mouse_pos.x()}, {self._mouse_pos.y()}), "
                   f"Color: ({self._current_color.red()}, {self._current_color.green()}, "
                   f"{self._current_color.blue()}, {self._current_color.alpha()})")
        super().mousePressEvent(event)
    
    def _get_color_at_position(self, pos):
        """Override this method in subclasses to provide proper color sampling."""
        return QColor(128, 128, 128, 255)  # Default gray background
    
    def set_zoom_level(self, zoom_level):
        """Set the zoom level for the canvas."""
        self._zoom_level = max(0.1, min(3.0, zoom_level))  # Limit zoom between 0.1x and 3x
        logger.info(f"Zoom level set to: {self._zoom_level:.2f}x ({self._zoom_level * 100:.0f}%)")
        self.update()
        
        # Update the status bar if we have access to the main app
        global current_app_instance
        if current_app_instance:
            try:
                current_app_instance.update_status_bar_from_canvas()
            except:
                pass  # Ignore if update fails
    
    def get_zoom_level(self):
        """Get the current zoom level."""
        return self._zoom_level
    
    def get_mouse_position(self):
        """Get the current mouse position."""
        return self._mouse_pos
    
    def get_center_offset(self):
        """Get the offset from the center."""
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        dx = self._mouse_pos.x() - center_x
        dy = self._mouse_pos.y() - center_y
        return QPoint(dx, dy)
    
    def get_current_color(self):
        """Get the current color at the cursor position."""
        return self._current_color


class GradientCanvasWidget(CanvasWidget):
    """
    Canvas widget that displays a large gradient circle for testing color picking.
    The gradient is centered at (0,0) which is at (2048,2048) in canvas coordinates.
    """
    
    def __init__(self):
        super().__init__()
        logger.info("GradientCanvasWidget initialized")
    
    def paint_content(self, painter):
        """Draw the gradient circle."""
        # Apply the same transformation as the base class, so we draw at the canvas center
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        
        # Create radial gradient centered at (center_x, center_y)
        gradient = QRadialGradient(center_x, center_y, 0, center_x, center_y, 512)
        gradient.setColorAt(0, QColor(255, 0, 0))      # Red center
        gradient.setColorAt(0.5, QColor(0, 255, 0))    # Green middle
        gradient.setColorAt(1, QColor(0, 0, 255))      # Blue edge
        
        # Draw the gradient circle (1024x1024)
        painter.fillRect(center_x - 512, center_y - 512, 1024, 1024, gradient)
    
    def _get_color_at_position(self, pos):
        """Get color based on gradient position."""
        center_x, center_y = self._canvas_center.x(), self._canvas_center.y()
        dx = pos.x() - center_x
        dy = pos.y() - center_y
        distance = (dx*dx + dy*dy)**0.5
        
        # If within the gradient circle (radius 512)
        if distance <= 512:
            ratio = min(distance / 512.0, 1.0)
            red = max(0, min(255, int(255 * (1 - ratio))))
            green = max(0, min(255, int(255 * ratio)))
            blue = max(0, min(255, int(255 * ratio * 1.5)))
            return QColor(red, green, blue, 255)
        else:
            # Outside the gradient circle - return background color
            return QColor(128, 128, 128, 255)


class SmallWidgetCanvasWidget(CanvasWidget):
    """
    Canvas widget that demonstrates a small widget placed on a large canvas.
    """
    
    def __init__(self):
        super().__init__()
        logger.info("SmallWidgetCanvasWidget initialized")
        
        # Create a small widget to place on the canvas
        self.small_widget = QLabel("Small Widget\n(256x256)")
        self.small_widget.setFixedSize(256, 256)
        self.small_widget.setStyleSheet(
            "background-color: rgba(255, 100, 100, 150); "
            "border: 2px solid red; "
            "color: white; "
            "font-weight: bold; "
            "padding: 20px; "
            "text-align: center;"
        )
        self.small_widget.setParent(self)  # Make it a child of the canvas
        # Position it at (1024, 1024) on the canvas
        self.small_widget.move(1024, 1024)
    
    def paint_content(self, painter):
        """Draw additional content if needed - currently empty."""
        pass
    
    def _get_color_at_position(self, pos):
        """Get color based on whether the position is over the small widget."""
        widget_x, widget_y = 1024, 1024
        widget_width, widget_height = 256, 256
        
        # Check if the position is within the small widget
        if (widget_x <= pos.x() <= widget_x + widget_width and 
            widget_y <= pos.y() <= widget_y + widget_height):
            # Return the widget's color
            return QColor(255, 100, 100, 150)  # Red with some transparency
        else:
            # Return the background color
            return QColor(128, 128, 128, 255)


class GradientCanvasView(BaseView):
    """
    A canvas view that displays a gradient circle for testing all features.
    """
    
    def __init__(self):
        super().__init__()
        self.canvas_widget = GradientCanvasWidget()
        self.layout().addWidget(self.canvas_widget)


class SmallWidgetCanvasView(BaseView):
    """
    A canvas view that demonstrates a small widget on a large canvas.
    """
    
    def __init__(self):
        super().__init__()
        self.canvas_widget = SmallWidgetCanvasWidget()
        self.layout().addWidget(self.canvas_widget)