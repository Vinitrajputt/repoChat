# core/repo_manager.py
import os
from git import Repo
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QObject

class RepoManager(QObject):
    repo_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_folder = None
        self.current_path = ""
        self.selection_states = {}
        self.temp_dir = "temp_repo"

    @property
    def current_dir(self):
        return os.path.join(self.root_folder, self.current_path) if self.root_folder else ""

    def open_repo_dialog(self):
        folder = QFileDialog.getExistingDirectory(None, "Select Repository Folder")
        if folder:
            self.open_repo(folder)

    def open_repo(self, path_or_url: str):
        if path_or_url.startswith("http") or path_or_url.startswith("git@"):
            self.clone_repo(path_or_url)
        else:
            self.root_folder = path_or_url
            self.current_path = ""
            self.selection_states = {}
            self.repo_updated.emit()

    def clone_repo(self, url: str):
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
            Repo.clone_from(url, self.temp_dir)
            self.root_folder = self.temp_dir
            self.current_path = ""
            self.selection_states = {}
            self.repo_updated.emit()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to clone repo: {e}")

    def get_current_items(self):
        items = []
        try:
            for item in sorted(os.listdir(self.current_dir), key=lambda x: (not os.path.isdir(os.path.join(self.current_dir, x)), x.lower())):
                abs_path = os.path.join(self.current_dir, item)
                rel_path = os.path.join(self.current_path, item) if self.current_path else item
                is_dir = os.path.isdir(abs_path)
                lw_item = QListWidgetItem(item)
                lw_item.setData(Qt.ItemDataRole.UserRole, rel_path)
                lw_item.setData(Qt.ItemDataRole.UserRole + 1, is_dir)
                lw_item.setFlags(lw_item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                state = self.get_selection_state(rel_path)
                lw_item.setCheckState(Qt.CheckState.Checked if state else Qt.CheckState.Unchecked)
                items.append({"item": lw_item, "is_dir": is_dir})
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to list directory: {e}")
        return items

    def get_selection_state(self, rel_path: str) -> bool:
        file_state = self.selection_states.get(rel_path, True)
        parts = rel_path.split(os.sep)
        for i in range(1, len(parts)):
            parent = os.path.join(*parts[:i])
            if parent in self.selection_states and not self.selection_states[parent]:
                return False
        return file_state

    def get_absolute_path(self, rel_path: str) -> str:
        return os.path.join(self.root_folder, rel_path)

    def select_all_children(self, item):
        rel_path = item.data(Qt.ItemDataRole.UserRole)
        for root, _, files in os.walk(self.get_absolute_path(rel_path)):
            rel_root = os.path.relpath(root, self.root_folder)
            for file in files:
                child_path = os.path.join(rel_root, file) if rel_root != "." else file
                self.selection_states[child_path] = True
        self.repo_updated.emit()

    def deselect_all_children(self, item):
        rel_path = item.data(Qt.ItemDataRole.UserRole)
        for root, _, files in os.walk(self.get_absolute_path(rel_path)):
            rel_root = os.path.relpath(root, self.root_folder)
            for file in files:
                child_path = os.path.join(rel_root, file) if rel_root != "." else file
                self.selection_states[child_path] = False
        self.repo_updated.emit()

    def collect_selected_files(self):
        selected_files = []
        for root, _, files in os.walk(self.root_folder):
            rel_root = os.path.relpath(root, self.root_folder)
            if rel_root == ".":
                rel_root = ""
            for file in files:
                rel_path = os.path.join(rel_root, file) if rel_root else file
                if self.get_selection_state(rel_path):
                    selected_files.append(rel_path)
        return sorted(selected_files)