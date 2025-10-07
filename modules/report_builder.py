# modules/report_builder.py

import streamlit as st
import os
from fpdf import FPDF
import re

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_report(report_text, chart_image_paths, topic):
    """
    Combines the text report and a list of chart images into a downloadable PDF file.
    """
    st.info("Assembling the final PDF report...")
    try:
        pdf = PDF()
        pdf.set_title(f"Report on: {topic}")
        pdf.add_page()
        
        sections = re.split(r'(\*\*.*?\*\*)', report_text)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            if section.startswith('**') and section.endswith('**'):
                pdf.set_font('Arial', 'B', 14)
                header_text = section.replace('**', '').strip()
                pdf.ln(5) # Add space before headers
                pdf.cell(0, 10, header_text, 0, 1, 'L')
                pdf.ln(2)
            else: # Body text
                pdf.set_font('Arial', '', 11)
                # --- FIX: Handle bullet points ---
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('* '):
                        pdf.ln(2)
                        pdf.set_x(15) # Indent for bullet point
                        pdf.multi_cell(0, 8, f'- {line[2:]}')
                    elif line:
                        pdf.set_x(10) # Reset indent
                        pdf.multi_cell(0, 8, line)
                pdf.ln(5)

        # Embed all charts, each on a new page for clarity
        if chart_image_paths:
            for chart_path in chart_image_paths:
                if os.path.exists(chart_path):
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 14)
                    pdf.cell(0, 10, "Visualized Data", 0, 1, 'L')
                    pdf.ln(5)
                    pdf.image(chart_path, x=10, y=None, w=pdf.w - 20)
        
        output_filename = f"Report - {topic.replace(' ', '_')}.pdf"
        output_path = os.path.join("outputs", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        
        st.success("PDF report assembled successfully.")
        return output_path, output_filename

    except Exception as e:
        st.error(f"Failed to create PDF report: {e}")
        return None, None