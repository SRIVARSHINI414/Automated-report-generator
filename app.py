# app.py

import streamlit as st
import os
from modules.data_ingestion import extract_text_from_files, perform_web_search
from modules.llm_processing import generate_report_from_context
from modules.chart_generator import extract_chart_data, create_chart_images
from modules.report_builder import create_pdf_report 
from dotenv import load_dotenv

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    st.set_page_config(page_title="Automated Report Generator", page_icon="🤖", layout="wide")
    st.title("Automated Report Generation System 📈")
    st.markdown("This tool helps you generate comprehensive reports by combining your documents with real-time web data.")

    with st.sidebar:
        st.header("1. Configure Your Report")
        topic = st.text_input("Enter the main topic or question for your report:", placeholder="e.g., Market trends in renewable energy for 2025")
        
        uploaded_files = st.file_uploader(
            "Upload relevant documents (PDF, DOCX, XLSX, CSV):", 
            accept_multiple_files=True, 
            type=['pdf', 'docx', 'xlsx', 'csv']
        )
        
        st.header("2. Customize Output (Optional)")
        
        report_tone = st.selectbox(
            "Select the report tone:",
            ("Professional", "Casual", "Technical")
        )

        # --- REMOVED: The language selection dropdown was here ---

    st.header("3. Your Generated Report")

    if st.button("✨ Generate Report"):
        if not topic:
            st.error("Please enter a topic for the report.")
        else:
            with st.spinner("Processing... This may take a moment. 🧠"):
                document_text = extract_text_from_files(uploaded_files)
                web_text = perform_web_search(topic)
                
                final_context = ""
                if document_text:
                    final_context += "--- START OF DOCUMENT CONTEXT ---\n" + document_text + "\n--- END OF DOCUMENT CONTEXT ---\n\n"
                if web_text:
                    final_context += "--- START OF WEB CONTEXT ---\n" + web_text + "\n--- END OF WEB CONTEXT ---"

                if not final_context:
                    st.error("Could not gather any context.")
                else:
                    # --- UPDATE: Removed the language parameter from the function call ---
                    report_text = generate_report_from_context(final_context, report_tone)
                    
                    charts_data = extract_chart_data(final_context)
                    chart_image_paths = create_chart_images(charts_data) if charts_data else []
                    
                    if report_text:
                        st.markdown("---")
                        st.markdown(report_text)
                    if chart_image_paths:
                        st.markdown("---")
                        st.subheader("Visualized Data")
                        for path in chart_image_paths:
                            st.image(path)
                    
                    if report_text:
                        pdf_path, pdf_filename = create_pdf_report(report_text, chart_image_paths, topic)
                        if pdf_path:
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Report as PDF",
                                    data=pdf_file,
                                    file_name=pdf_filename,
                                    mime="application/pdf"
                                )

if __name__ == '__main__':
    main()