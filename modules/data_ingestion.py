# modules/data_ingestion.py

import PyPDF2
import io
import streamlit as st
import os
import google.generativeai as genai
import docx
import pandas as pd

@st.cache_data
def extract_text_from_files(uploaded_files):
    """
    Accepts a list of uploaded files (PDF, DOCX, XLSX, CSV), extracts text from each,
    and returns a single consolidated string.
    """
    combined_text = ""
    if not uploaded_files:
        return combined_text

    for file in uploaded_files:
        try:
            if file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        combined_text += page_text + "\n\n"
            
            elif file.name.endswith('.docx'):
                document = docx.Document(io.BytesIO(file.getvalue()))
                for para in document.paragraphs:
                    if para.text:
                        combined_text += para.text + "\n"
                combined_text += "\n"

            elif file.name.endswith('.xlsx'):
                excel_file = pd.ExcelFile(io.BytesIO(file.getvalue()))
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    combined_text += f"--- Content from Excel Sheet: {sheet_name} ---\n"
                    combined_text += df.to_string(index=False) + "\n\n"
            
            # --- NEW: Add support for CSV files ---
            elif file.name.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file.getvalue()))
                combined_text += f"--- Content from CSV File: {file.name} ---\n"
                combined_text += df.to_string(index=False) + "\n\n"

        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            
    return combined_text

@st.cache_data
def perform_web_search(query):
    st.info(f"Performing web search and summarization for: '{query}'...")
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.error("Gemini API key not found. Please set it in your .env file.")
            return ""
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        prompt = f"You are a helpful research assistant. Find and summarize the most relevant, up-to-date information on the web regarding the following topic: '{query}'. Consolidate your findings into a detailed summary. Do not include any introductory phrases like 'Certainly, here is a summary...'. Provide only the summarized text."
        response = model.generate_content(prompt)
        st.success("Web search and summarization completed.")
        return response.text
    except Exception as e:
        st.error(f"An error occurred during the Gemini web search: {e}")
        return ""