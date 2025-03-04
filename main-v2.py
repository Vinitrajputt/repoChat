import os
import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project to PDF Generator")
        
        # Global state
        self.root_folder = None      # Absolute path of the selected project folder
        self.current_path = ""       # Relative path (from the root) of the current folder view
        self.navigation_stack = []   # For "Back" navigation
        self.selection_states = {}   # Mapping: relative path -> bool (True if selected, else False).
                                    # If an item is not present, default is True.
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Top navigation controls
        top_layout = QtWidgets.QHBoxLayout()
        self.open_button = QtWidgets.QPushButton("Open Folder")
        self.open_button.clicked.connect(self.open_folder)
        top_layout.addWidget(self.open_button)
        
        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        top_layout.addWidget(self.back_button)
        
        self.path_label = QtWidgets.QLabel("No folder selected")
        top_layout.addWidget(self.path_label)
        
        layout.addLayout(top_layout)
        
        # List widget for current folder contents
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemChanged.connect(self.handle_item_changed)
        self.list_widget.itemDoubleClicked.connect(self.handle_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Button to generate the PDF
        self.generate_button = QtWidgets.QPushButton("Generate PDF")
        self.generate_button.clicked.connect(self.generate_pdf)
        layout.addWidget(self.generate_button)

    def open_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.root_folder = folder
            self.current_path = ""
            self.navigation_stack = []
            self.selection_states = {}  # reset selection states (default True)
            self.update_folder_view()

    def update_folder_view(self):
        """Load and display the contents of the current folder."""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        current_dir = os.path.join(self.root_folder, self.current_path) if self.root_folder else ""
        self.path_label.setText(current_dir)
        
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to list directory: {e}")
            self.list_widget.blockSignals(False)
            return
        
        # Sort: show folders first, then files
        items.sort(key=lambda x: (not os.path.isdir(os.path.join(current_dir, x)), x.lower()))
        for item in items:
            abs_path = os.path.join(current_dir, item)
            # Relative path from root (used for storing selection state)
            rel_path = os.path.join(self.current_path, item) if self.current_path else item
            is_dir = os.path.isdir(abs_path)
            
            lw_item = QtWidgets.QListWidgetItem(item)
            # Store relative path and type in the item data
            lw_item.setData(QtCore.Qt.ItemDataRole.UserRole, rel_path)
            lw_item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, is_dir)
            # Make the item checkable
            lw_item.setFlags(lw_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            # Determine initial check state (default True if not set)
            state = self.get_selection_state(rel_path)
            lw_item.setCheckState(QtCore.Qt.CheckState.Checked if state else QtCore.Qt.CheckState.Unchecked)
            # Optionally, add an icon for folders
            if is_dir:
                lw_item.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
            else:
                lw_item.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon))
            self.list_widget.addItem(lw_item)
        
        self.list_widget.blockSignals(False)
        self.back_button.setEnabled(len(self.navigation_stack) > 0)

    def handle_item_changed(self, item):
        """Update selection state when a checkbox is toggled."""
        rel_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        state = item.checkState() == QtCore.Qt.CheckState.Checked
        self.selection_states[rel_path] = state

    def handle_item_double_clicked(self, item):
        """If a folder is double-clicked, navigate into it."""
        is_dir = item.data(QtCore.Qt.ItemDataRole.UserRole + 1)
        if is_dir:
            rel_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
            # Save the current folder in the navigation stack and update current_path
            self.navigation_stack.append(self.current_path)
            self.current_path = os.path.join(self.current_path, item.text()) if self.current_path else item.text()
            self.update_folder_view()

    def go_back(self):
        """Navigate back to the parent folder."""
        if self.navigation_stack:
            self.current_path = self.navigation_stack.pop()
            self.update_folder_view()

    def get_selection_state(self, rel_path):
        """
        Determine the effective selection state for an item.
        If an item is explicitly set in the mapping, use that.
        Otherwise, default to True unless a parent folder has been deselected.
        """
        # Start with the item state (default True)
        file_state = self.selection_states.get(rel_path, True)
        parts = rel_path.split(os.sep)
        # Check each parent folder; if any parent is explicitly unchecked
        for i in range(1, len(parts)):
            parent = os.path.join(*parts[:i])
            if parent in self.selection_states and self.selection_states[parent] is False:
                # If the item itself hasn’t been explicitly reselected, treat it as unselected.
                if self.selection_states.get(rel_path, None) is not True:
                    return False
        return file_state

    def collect_selected_files(self):
        """
        Recursively scan the entire project folder and collect the relative paths of
        all files that are effectively selected.
        """
        selected_files = []
        for root, dirs, files in os.walk(self.root_folder):
            rel_root = os.path.relpath(root, self.root_folder)
            if rel_root == ".":
                rel_root = ""
            for file in files:
                rel_path = os.path.join(rel_root, file) if rel_root else file
                if self.get_selection_state(rel_path):
                    selected_files.append(rel_path)
        return selected_files

    def build_tree_structure_text(self, selected_files):
        """
        Build a simple textual tree representation from the selected file paths.
        """
        tree_dict = {}
        for path in selected_files:
            parts = path.split(os.sep)
            current = tree_dict
            for part in parts:
                current = current.setdefault(part, {})
        lines = []
        def traverse(d, indent=""):
            for key in sorted(d.keys()):
                lines.append(indent + key)
                traverse(d[key], indent + "    ")
        traverse(tree_dict)
        return "\n".join(lines)

    def generate_pdf(self):
        if not self.root_folder:
            QtWidgets.QMessageBox.warning(self, "No Folder Selected", "Please open a folder first.")
            return
        selected_files = self.collect_selected_files()
        if not selected_files:
            QtWidgets.QMessageBox.warning(self, "No Files Selected", "No files selected to include in PDF.")
            return
        pdf_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save PDF", filter="PDF Files (*.pdf)")
        if not pdf_path:
            return
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Project structure section at the top of the PDF
        story.append(Paragraph("Project Structure", styles['Heading1']))
        story.append(Spacer(1, 12))
        tree_text = self.build_tree_structure_text(selected_files)
        story.append(Preformatted(tree_text, styles['Code']))
        story.append(Spacer(1, 24))
        
        # Append contents of each selected file
        for rel_path in selected_files:
            story.append(Paragraph(rel_path, styles['Heading2']))
            story.append(Spacer(1, 12))
            abs_path = os.path.join(self.root_folder, rel_path)
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {e}"
            story.append(Preformatted(content, styles['Code']))
            story.append(Spacer(1, 24))
        
        try:
            doc.build(story)
            QtWidgets.QMessageBox.information(self, "PDF Generated", f"PDF file generated at:\n{pdf_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error generating PDF:\n{e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
