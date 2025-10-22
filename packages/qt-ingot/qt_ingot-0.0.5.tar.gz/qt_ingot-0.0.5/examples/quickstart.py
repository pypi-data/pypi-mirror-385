import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt


def main() -> None:
    """
    A minimal, generic PyQt6 application entry point.
    This script uses NO custom library imports.
    """
    app = QApplication(sys.argv)

    # Create a completely standard QMainWindow
    window = QMainWindow()
    window.setWindowTitle("Pure PyQt6 Test")
    window.setGeometry(200, 200, 500, 300)  # x, y, width, height

    # Create a simple label to show it's working
    label = QLabel("This is a generic PyQt6 window.\nIt works.", parent=window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)

    # Show the window and start the application
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    """
    This is the entry point of the application.
    It prints a simple startup message and runs the main function.
    """
    # Mimic the startup message of your other projects
    print("\033[2J\033[1;1H", end="")
    print("\033[92mMinimal PyQt Test\033[0m")
    print("Author(s): \033[94mYrrrrrf\033[0m", end="\n\n")

    main()
