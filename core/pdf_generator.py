# core/pdf_generator.py
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
import os

class PDFGenerator:
    def generate_pdf(self, repo_manager, preview_callback, progress_bar):
        if not repo_manager.root_folder:
            QMessageBox.warning(None, "Error", "Please open a repository first.")
            return
        selected_files = repo_manager.collect_selected_files()
        if not selected_files:
            QMessageBox.warning(None, "Error", "No files selected.")
            return
        pdf_path, _ = QFileDialog.getSaveFileName(None, "Save PDF", filter="PDF Files (*.pdf)")
        if not pdf_path:
            return

        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add repo structure
        story.append(Paragraph("Repository Structure", styles['Heading1']))
        story.append(Spacer(1, 12))
        tree_text = self.build_tree_structure(selected_files)
        story.append(Preformatted(tree_text, styles['Code']))
        story.append(Spacer(1, 24))

        # Add file contents
        progress_bar.setMaximum(len(selected_files))
        preview_text = "Repository Structure\n\n" + tree_text + "\n\n"
        for i, rel_path in enumerate(selected_files):
            progress_bar.setValue(i + 1)
            abs_path = repo_manager.get_absolute_path(rel_path)
            story.append(Paragraph(rel_path, styles['Heading2']))
            story.append(Spacer(1, 12))
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {e}"
            story.append(Preformatted(content, styles['Code']))
            story.append(Spacer(1, 24))
            preview_text += f"{rel_path}\n\n{content}\n\n"

            # Update preview in real-time
            preview_callback(preview_text)

        try:
            doc.build(story)
            QMessageBox.information(None, "Success", f"PDF generated at:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error generating PDF:\n{e}")

    def build_tree_structure(self, selected_files):
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
                traverse(d[key], indent + "  ")
        traverse(tree_dict)
        return "\n".join(lines)