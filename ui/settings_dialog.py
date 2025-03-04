# ui/settings_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel
from utils.styles import apply_neon_stylesheet

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Theme Selection
        layout.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Neon Dark", "Light"])
        layout.addWidget(self.theme_combo)

        # Save Button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button)

        apply_neon_stylesheet(self)