# ui/formatting_toolbox.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QCheckBox, QPushButton
from PyQt6.QtCore import Qt
from utils.styles import apply_neon_stylesheet
from utils.animations import slide_in

class FormattingToolbox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setup_ui()
        self.move(parent.width() - 300, 100)  # Position near top-right

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("PDF Formatting Options"))
        
        # Font Size Slider
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setMinimum(8)
        self.font_slider.setMaximum(16)
        self.font_slider.setValue(12)
        layout.addWidget(QLabel("Font Size"))
        layout.addWidget(self.font_slider)

        # Chunk Size for LLM
        self.chunk_slider = QSlider(Qt.Orientation.Horizontal)
        self.chunk_slider.setMinimum(1000)
        self.chunk_slider.setMaximum(128000)
        self.chunk_slider.setValue(16000)
        layout.addWidget(QLabel("LLM Chunk Size (tokens)"))
        layout.addWidget(self.chunk_slider)

        # Include Metadata
        self.metadata_check = QCheckBox("Include Metadata Tags")
        self.metadata_check.setChecked(True)
        layout.addWidget(self.metadata_check)

        # Apply Button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.hide)
        layout.addWidget(apply_button)

        self.setFixedWidth(250)
        apply_neon_stylesheet(self)
        slide_in(self)

    def get_settings(self):
        return {
            "font_size": self.font_slider.value(),
            "chunk_size": self.chunk_slider.value(),
            "include_metadata": self.metadata_check.isChecked()
        }