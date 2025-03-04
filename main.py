# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.styles import apply_neon_dark_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_neon_dark_theme(app)
    window = MainWindow()
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())