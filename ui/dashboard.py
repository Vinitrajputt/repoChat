# ui/dashboard.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton
from PyQt6.QtCore import Qt
from utils.styles import apply_neon_stylesheet
from utils.animations import fade_in

class Dashboard(QWidget):
    def __init__(self, repo_manager, parent=None):
        super().__init__(parent)
        self.repo_manager = repo_manager
        self.setup_ui()
        self.setAcceptDrops(True)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Repo to PDF Generator")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00D4FF;")
        layout.addWidget(title)

        # Drop Zone
        self.drop_label = QLabel("Drop Repo Link or Folder Here")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet("font-size: 18px; color: #D400FF; border: 2px dashed #00D4FF; padding: 20px;")
        layout.addWidget(self.drop_label)

        # Recent Repos
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(200)
        layout.addWidget(QLabel("Recent Repositories"))
        layout.addWidget(self.recent_list)

        # Open Button
        open_button = QPushButton("Open Repo Manually")
        open_button.clicked.connect(self.repo_manager.open_repo_dialog)
        layout.addWidget(open_button)

        layout.addStretch()
        apply_neon_stylesheet(self)
        fade_in(self)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
            self.drop_label.setText("Drop to Load Repository")
            self.drop_label.setStyleSheet("font-size: 18px; color: #FFFFFF; border: 2px solid #D400FF; padding: 20px;")

    def dragLeaveEvent(self, event):
        self.drop_label.setText("Drop Repo Link or Folder Here")
        self.drop_label.setStyleSheet("font-size: 18px; color: #D400FF; border: 2px dashed #00D4FF; padding: 20px;")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString()
            self.repo_manager.open_repo(url)
        elif event.mimeData().hasText():
            self.repo_manager.open_repo(event.mimeData().text())
        self.parent().hide_dashboard()