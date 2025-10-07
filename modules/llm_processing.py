# modules/llm_processing.py

import streamlit as st
import os
import google.generativeai as genai

# --- UPDATE: Removed 'language' from the function definition ---
@st.cache_data
def generate_report_from_context(context, tone):
    """
    Takes the consolidated context and tone to generate a structured report.
    """
    # --- UPDATE: Removed language from the status message ---
    st.info(f"Generating structured report in a {tone} tone...")
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.error("Gemini API key not found for report generation.")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')

        # --- UPDATE: Removed the language instruction from the prompt ---
        prompt = f"""
        You are a research analyst. Your task is to generate a structured report based STRICTLY AND ONLY on the provided context. 
        Do not use any external knowledge or make assumptions. Do not add any information that is not explicitly present in the context.
        If the context does not contain information for a specific section, you must explicitly state 'Information not available in the provided context.'

        **CRITICAL INSTRUCTIONS:**
        1.  **Tone:** The report must be written in a '{tone}' tone.

        The report must include the following sections, in this exact order:
        1.  **Executive Summary:** A brief, high-level overview of the main findings from the context.
        2.  **Key Insights:** Detailed findings, data points, and important facts from the context. Use bullet points for clarity.
        3.  **Potential Risks or Limitations:** Identify any challenges, risks, or limitations mentioned.
        4.  **Conclusion:** A concluding summary based ONLY on the information given.

        Here is the ONLY context you are allowed to use:
        ---
        {context}
        ---
        """

        response = model.generate_content(prompt)
        st.success("Structured report generated successfully.")
        return response.text

    except Exception as e:
        st.error(f"An error occurred during report generation: {e}")
        return None