from PyQt6.QtWidgets import QWidget, QVBoxLayout


class BaseView(QWidget):
    """
    The base class for any widget intended to be used as a tab in the
    WorkspaceManager. It provides a default vertical layout.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
