# modules/chart_generator.py

import streamlit as st
import os
import google.generativeai as genai
import json
import matplotlib.pyplot as plt

@st.cache_data
def extract_chart_data(context):
    st.info("Detecting all numeric data for visualization...")
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')

        # --- FIX: Strengthen the prompt to be even stricter about data types ---
        prompt = f"""
        You are a data analyst. Your task is to find all distinct datasets within the provided text context and format them as a list of JSON objects.
        You must only use the numbers and labels explicitly present in the text. Do not invent, infer, or calculate any new data.

        Analyze the following context STRICTLY:
        ---
        {context}
        ---

        Return a Python list of JSON objects. Each JSON object must have the following structure:
        {{
          "chart_type": "bar", "pie", or "line",
          "title": "A descriptive title for the chart based on the context",
          "x_axis_label": "A label for the X-axis (for bar/line charts, leave blank for pie)",
          "y_axis_label": "A label for the Y-axis (for bar/line charts, leave blank for pie)",
          "labels": ["label1", "label2", ...],
          "values": [value1, value2, ...]
        }}
        
        CRITICAL: The "values" array must ONLY contain numbers (integers or floats). Do not include any text strings in the "values" array.
        Choose 'line' if the data represents a trend over time.
        If no suitable data for a chart is found, return an empty list [].
        Do not return any text or explanation outside of the list of JSON objects.
        """

        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").replace("`", "")
        
        chart_data_list = json.loads(cleaned_response)
        st.success(f"Found {len(chart_data_list)} potential chart(s).")
        return chart_data_list

    except Exception as e:
        st.warning(f"Could not extract chart data: {e}")
        return []

def create_chart_images(chart_data_list):
    image_paths = []
    if not chart_data_list:
        return image_paths
    for i, chart_data in enumerate(chart_data_list):
        try:
            # --- FIX: Add data validation to check if values are numeric ---
            if not chart_data or not all(isinstance(v, (int, float)) for v in chart_data.get("values", [])):
                st.warning(f"Skipping chart '{chart_data.get('title', 'Untitled')}' due to non-numeric data.")
                continue

            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#F3F4F6')
            ax.set_facecolor('#FFFFFF')
            colors = ['#2E86C1', '#28B463', '#F39C12', '#E74C3C', '#8E44AD']

            if chart_data["chart_type"] == "bar":
                ax.bar(chart_data["labels"], chart_data["values"], color=colors)
                ax.set_xlabel(chart_data["x_axis_label"], fontsize=12)
                ax.set_ylabel(chart_data["y_axis_label"], fontsize=12)
                plt.xticks(rotation=45, ha="right")
            elif chart_data["chart_type"] == "pie":
                ax.pie(chart_data["values"], labels=chart_data["labels"], autopct='%1.1f%%', startangle=90, colors=colors)
                ax.axis('equal')
            elif chart_data["chart_type"] == "line":
                ax.plot(chart_data["labels"], chart_data["values"], marker='o', linestyle='-', color=colors[0])
                ax.set_xlabel(chart_data["x_axis_label"], fontsize=12)
                ax.set_ylabel(chart_data["y_axis_label"], fontsize=12)
                plt.xticks(rotation=45, ha="right")
                plt.grid(True, linestyle='--', alpha=0.6)

            ax.set_title(chart_data["title"], fontsize=16)
            plt.tight_layout()
            
            output_path = f"outputs/chart_{i+1}.png"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, facecolor=fig.get_facecolor())
            plt.close(fig)
            
            image_paths.append(output_path)
        except Exception as e:
            st.error(f"Failed to create chart image #{i+1}: {e}")
            continue
            
    st.success("Chart images generated.")
    return image_paths