from PyQt6 import QtWidgets, QtGui, QtCore
from ui.widgets import FileListWidget
from core.repo_handler import clone_repository, get_folder_contents
from core.pdf_generator import generate_pdf
from utils.helpers import format_size
import os

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project to PDF Generator")
        self.root_folder = None
        self.current_path = ""
        self.selection_states = {}
        self.setup_ui()

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # Sidebar: Tree View
        self.tree_view = QtWidgets.QTreeView()
        self.tree_model = QtGui.QFileSystemModel()  # Corrected import
        self.tree_model.setRootPath(QtCore.QDir.rootPath())
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setMaximumWidth(300)
        self.tree_view.selectionModel().selectionChanged.connect(self.update_list_widget)
        main_layout.addWidget(self.tree_view)

        # Main Content Area
        content_layout = QtWidgets.QVBoxLayout()

        # Top Bar
        top_layout = QtWidgets.QHBoxLayout()
        self.open_button = QtWidgets.QPushButton("Open Folder")
        self.open_button.clicked.connect(self.open_folder)
        top_layout.addWidget(self.open_button)

        self.add_repo_button = QtWidgets.QPushButton("Add Repository")
        self.add_repo_button.clicked.connect(self.add_repository)
        top_layout.addWidget(self.add_repo_button)

        self.path_label = QtWidgets.QLabel("No folder selected")
        top_layout.addWidget(self.path_label)
        top_layout.addStretch()
        content_layout.addLayout(top_layout)

        # File List Widget
        self.list_widget = FileListWidget(self)
        content_layout.addWidget(self.list_widget)

        # Selection Controls
        selection_layout = QtWidgets.QHBoxLayout()
        self.select_all_button = QtWidgets.QPushButton("Select All")
        self.select_all_button.clicked.connect(lambda: self.list_widget.toggle_selection(True))
        selection_layout.addWidget(self.select_all_button)

        self.deselect_all_button = QtWidgets.QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(lambda: self.list_widget.toggle_selection(False))
        selection_layout.addWidget(self.deselect_all_button)

        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["All", ".py", ".txt", ".md"])
        self.filter_combo.currentTextChanged.connect(self.update_list_widget)
        selection_layout.addWidget(self.filter_combo)
        content_layout.addLayout(selection_layout)

        # Generate Button
        self.generate_button = QtWidgets.QPushButton("Generate PDF")
        self.generate_button.clicked.connect(self.generate_pdf)
        content_layout.addWidget(self.generate_button)

        main_layout.addLayout(content_layout)

        # Styling (shades of black and grey)
        self.setStyleSheet("""
            QWidget { background-color: #1E1E1E; color: #D3D3D3; font-family: Arial; }
            QPushButton { background-color: #333333; padding: 8px; border: 1px solid #444444; }
            QPushButton:hover { background-color: #444444; }
            QTreeView, QListWidget { background-color: #2A2A2A; border: 1px solid #333333; }
            QLabel { color: #A9A9A9; }
            QComboBox { background-color: #2A2A2A; border: 1px solid #333333; }
        """)

        # Drag and Drop
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.set_root_folder(path)
            elif path.startswith("http"):
                self.add_repository_from_url(path)

    def open_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.set_root_folder(folder)

    def add_repository(self):
        url, ok = QtWidgets.QInputDialog.getText(self, "Add Repository", "Enter URL:")
        if ok and url:
            self.add_repository_from_url(url)

    def add_repository_from_url(self, url):
        try:
            folder = clone_repository(url)
            self.set_root_folder(folder)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to clone repository: {e}")

    def set_root_folder(self, folder):
        self.root_folder = folder
        self.current_path = ""
        self.selection_states = {}
        self.tree_model.setRootPath(folder)
        root_index = self.tree_model.index(folder)
        self.tree_view.setRootIndex(root_index)
        self.update_list_widget()

    def update_list_widget(self):
        selected = self.tree_view.selectedIndexes()
        path = self.root_folder if not selected else self.tree_model.filePath(selected[0])
        self.current_path = os.path.relpath(path, self.root_folder) if self.root_folder else ""
        self.path_label.setText(path)
        filter_ext = self.filter_combo.currentText() if self.filter_combo.currentText() != "All" else None
        self.list_widget.update_contents(path, filter_ext)

    def generate_pdf(self):
        if not self.root_folder:
            QtWidgets.QMessageBox.warning(self, "Error", "No folder selected.")
            return
        selected_files = self.list_widget.get_selected_files()
        if not selected_files:
            QtWidgets.QMessageBox.warning(self, "Error", "No files selected.")
            return
        pdf_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save PDF", filter="PDF Files (*.pdf)")
        if pdf_path:
            generate_pdf(self.root_folder, selected_files, pdf_path)
            QtWidgets.QMessageBox.information(self, "Success", f"PDF saved at: {pdf_path}")