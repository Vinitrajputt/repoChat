from PyQt6 import QtWidgets, QtCore
from utils.helpers import format_size
import os

class FileListWidget(QtWidgets.QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.itemChanged.connect(self.handle_item_changed)
        self.itemDoubleClicked.connect(self.handle_item_double_clicked)
        self.setSortingEnabled(True)

    def update_contents(self, path, filter_ext=None):
        self.clear()
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                rel_path = os.path.relpath(abs_path, self.main_window.root_folder)
                if filter_ext and not item.endswith(filter_ext) and not os.path.isdir(abs_path):
                    continue
                lw_item = QtWidgets.QListWidgetItem()
                lw_item.setText(f"{item} ({format_size(abs_path)})")
                lw_item.setData(QtCore.Qt.ItemDataRole.UserRole, rel_path)
                lw_item.setFlags(lw_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                state = self.main_window.selection_states.get(rel_path, True)
                lw_item.setCheckState(QtCore.Qt.CheckState.Checked if state else QtCore.Qt.CheckState.Unchecked)
                if os.path.isdir(abs_path):
                    lw_item.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
                else:
                    lw_item.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon))
                self.addItem(lw_item)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to list directory: {e}")

    def handle_item_changed(self, item):
        rel_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.main_window.selection_states[rel_path] = item.checkState() == QtCore.Qt.CheckState.Checked

    def handle_item_double_clicked(self, item):
        rel_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        abs_path = os.path.join(self.main_window.root_folder, rel_path)
        if os.path.isdir(abs_path):
            index = self.main_window.tree_model.index(abs_path)
            self.main_window.tree_view.setCurrentIndex(index)

    def toggle_selection(self, state):
        for i in range(self.count()):
            item = self.item(i)
            item.setCheckState(QtCore.Qt.CheckState.Checked if state else QtCore.Qt.CheckState.Unchecked)
            self.handle_item_changed(item)

    def get_selected_files(self):
        return [self.item(i).data(QtCore.Qt.ItemDataRole.UserRole) for i in range(self.count())
                if self.item(i).checkState() == QtCore.Qt.CheckState.Checked
                and not os.path.isdir(os.path.join(self.main_window.root_folder, self.item(i).data(QtCore.Qt.ItemDataRole.UserRole)))]