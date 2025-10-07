# AI-Powered Automated Report Generator

This project is an automated report generation system built in Python using the Streamlit framework and Google's Gemini API.

The application allows a user to provide a topic and upload various source documents (PDF, DOCX, XLSX, CSV). It then performs a web search for real-time information, combines all data, and uses a Generative AI to produce a structured report complete with text summaries and data visualizations. The final report is available for download as a PDF.

## Tech Stack
- **Language:** Python
- **AI Model:** Google Gemini API (`gemini-pro-latest`)
- **Framework:** Streamlit
- **Key Libraries:** PyPDF2, python-docx, pandas, matplotlib, fpdf2, python-dotenv
