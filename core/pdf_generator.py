from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
import os

def generate_pdf(root_folder, selected_files, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Project Files", styles['Heading1']), Spacer(1, 12)]

    for rel_path in selected_files:
        abs_path = os.path.join(root_folder, rel_path)
        story.append(Paragraph(f"--- File: {rel_path} ---", styles['Heading2']))
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = [f"{i+1}: {line}" for i, line in enumerate(f.readlines())]
                content = "".join(lines)
            story.append(Preformatted(content, styles['Code']))
        except Exception as e:
            story.append(Paragraph(f"Error reading file: {e}", styles['Normal']))
        story.append(Spacer(1, 24))

    doc.build(story)