<h1 align="center">
  <img src="https://raw.githubusercontent.com/Yrrrrrf/qt-ingot/main/resources/img/template.png" alt="qt-ingot Icon" width="128" height="128">
  <div align="center">qt-ingot</div>
</h1>

<div align="center">

[![GitHub: Repo](https://img.shields.io/badge/qt--ingot-58A6FF?&logo=github)](https://github.com/Yrrrrrf/qt-ingot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/qt-ingot)](https://pypi.org/project/qt-ingot/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/qt-ingot)](https://pypi.org/project/qt-ingot/)

</div>

> A lightweight, themeable boilerplate for creating tab-based PyQt applications.

`qt-ingot` is a Python library designed to accelerate desktop application development by providing a self-configuring main window, an intelligent SASS-based theming engine, a data-driven menu bar, and a flexible layout system.

## 🚦 Getting Started

### Installation

```bash
uv add qt-ingot
```

#### Quick Start

Here's a minimal example to get you started:

```python
# your_project/main.py
import sys
from PyQt6.QtWidgets import QApplication, QLabel
from ingot.app import IngotApp
from ingot.views.base import BaseView

# 1. Define your application's configuration
APP_CONFIG = {
    "title": "My Awesome Ingot App",
    "icon": "img.my_icon"  # A rune-lib friendly path
}

# 2. Define your menu structure
MENU_CONFIG = {
    "File": [
        {"name": "Exit", "shortcut": "Esc", "function": sys.exit}
    ],
    "Help": [
        {"name": "About", "function": lambda: print("About This App!")}
    ]
}

# 3. Define the content for your tabs
class MyCustomView(BaseView):
    def __init__(self):
        super().__init__()
        self.layout().addWidget(QLabel("This is my application's content!"))

# 4. Launch the app
def main():
    app = QApplication(sys.argv)
    
    main_window = IngotApp(view_factory=MyCustomView, config=APP_CONFIG)
    main_window.set_menu(MENU_CONFIG)

    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.
