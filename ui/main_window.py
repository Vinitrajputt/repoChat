# ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QTextEdit, QProgressBar, QMenu, QStackedWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction
from core.repo_manager import RepoManager
from core.pdf_generator import PDFGenerator
from core.llm_optimizer import LLMOptimizer
from ui.dashboard import Dashboard
from ui.formatting_toolbox import FormattingToolbox
from ui.settings_dialog import SettingsDialog
from utils.styles import apply_neon_stylesheet
from utils.animations import fade_in
from utils.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Repo to PDF Generator")
        self.repo_manager = RepoManager(self)
        self.pdf_generator = PDFGenerator()
        self.llm_optimizer = LLMOptimizer()
        self.setup_ui()
        self.connect_signals()
        self.setAcceptDrops(True)
        self.show_dashboard()

    def setup_ui(self):
        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack = QStackedWidget()
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stack)

        # Main UI widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        # Top Bar
        top_bar = QHBoxLayout()
        self.open_button = QPushButton("Open Repo")
        self.generate_button = QPushButton("Generate PDF")
        self.format_button = QPushButton("Format")
        self.settings_button = QPushButton("Settings")
        top_bar.addWidget(self.open_button)
        top_bar.addWidget(self.generate_button)
        top_bar.addWidget(self.format_button)
        top_bar.addWidget(self.settings_button)
        top_bar.addStretch()
        self.main_layout.addLayout(top_bar)

        # Main Content
        content_layout = QHBoxLayout()
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.preview_pane = QTextEdit()
        self.preview_pane.setReadOnly(True)
        self.pdf_preview = QTextEdit()
        self.pdf_preview.setReadOnly(True)
        content_layout.addWidget(self.sidebar, 1)
        content_layout.addWidget(self.preview_pane, 2)
        content_layout.addWidget(self.pdf_preview, 2)
        self.main_layout.addLayout(content_layout)

        # Bottom Dock
        dock_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Ready")
        dock_layout.addWidget(self.progress_bar)
        dock_layout.addStretch()
        dock_layout.addWidget(self.status_label)
        self.main_layout.addLayout(dock_layout)

        # Dashboard and Toolbox
        self.dashboard = Dashboard(self.repo_manager, self)
        self.toolbox = FormattingToolbox(self)
        self.toolbox.hide()

        # Add widgets to stack
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.main_widget)

        apply_neon_stylesheet(self)
        # fade_in(self)

    def connect_signals(self):
        self.open_button.clicked.connect(self.repo_manager.open_repo_dialog)
        self.generate_button.clicked.connect(self.generate_pdf)
        self.format_button.clicked.connect(self.show_toolbox)
        self.settings_button.clicked.connect(self.show_settings)
        self.sidebar.itemClicked.connect(self.show_preview)
        self.sidebar.customContextMenuRequested.connect(self.show_context_menu)
        self.repo_manager.repo_updated.connect(self.update_sidebar)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def hide_dashboard(self):
        self.stack.setCurrentWidget(self.main_widget)

    def update_sidebar(self):
        self.sidebar.clear()
        for item_data in self.repo_manager.get_current_items():
            item = item_data["item"]
            self.sidebar.addItem(item)
        self.status_label.setText(f"Loaded: {self.repo_manager.current_dir}")

    def show_preview(self, item):
        rel_path = item.data(Qt.ItemDataRole.UserRole)
        abs_path = self.repo_manager.get_absolute_path(rel_path)
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                self.preview_pane.setText(f.read())
        except Exception:
            self.preview_pane.setText("Cannot preview this file.")

    def show_context_menu(self, pos: QPoint):
        item = self.sidebar.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        select_all = QAction("Select All Children", self)
        deselect_all = QAction("Deselect All Children", self)
        menu.addAction(select_all)
        menu.addAction(deselect_all)
        select_all.triggered.connect(lambda: self.repo_manager.select_all_children(item))
        deselect_all.triggered.connect(lambda: self.repo_manager.deselect_all_children(item))
        menu.exec(self.sidebar.mapToGlobal(pos))

    def generate_pdf(self):
        self.progress_bar.setVisible(True)
        settings = self.toolbox.get_settings()
        self.llm_optimizer.set_chunk_size(settings["chunk_size"])
        self.pdf_generator.generate_pdf(self.repo_manager, self.preview_pdf, self.progress_bar)
        self.progress_bar.setVisible(False)

    def preview_pdf(self, content: str):
        self.pdf_preview.setText(content)

    def show_toolbox(self):
        self.toolbox.show()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString()
            self.repo_manager.open_repo(url)
        elif event.mimeData().hasText():
            self.repo_manager.open_repo(event.mimeData().text())
        self.hide_dashboard()