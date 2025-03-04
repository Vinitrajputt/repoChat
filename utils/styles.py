# utils/styles.py
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def apply_neon_dark_theme(app):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1E1E1E"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#2A2A2A"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#3A3A3A"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#00D4FF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#D400FF"))
    app.setPalette(palette)
    app.setStyle("Fusion")

def apply_neon_stylesheet(widget):
    widget.setStyleSheet("""
        QWidget {
            font-family: 'JetBrains Mono', sans-serif;
            font-size: 14px;
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #3A3A3A;
            border: 1px solid #00D4FF;
            padding: 8px 16px;
            color: #00D4FF;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #505050;
            border-color: #D400FF;
            color: #D400FF;
        }
        QListWidget {
            background-color: #2A2A2A;
            border: 1px solid #00D4FF;
            border-radius: 4px;
            color: #FFFFFF;
        }
        QTextEdit {
            background-color: #2A2A2A;
            border: 1px solid #00D4FF;
            border-radius: 4px;
            color: #FFFFFF;
            padding: 8px;
        }
        QProgressBar {
            background-color: #3A3A3A;
            border: 1px solid #00D4FF;
            border-radius: 4px;
            text-align: center;
            color: #FFFFFF;
        }
        QProgressBar::chunk {
            background-color: #D400FF;
            border-radius: 4px;
        }
    """)