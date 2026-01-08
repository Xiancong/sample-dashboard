from data_tools import load_all_data
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pandas as pd
import polars as pl
import streamlit as st
import streamlit.components.v1 as components
import sweetviz as sv
import tempfile


# check if data is loaded. if not load data
if 'full_df' not in st.session_state or 'budget_df' not in st.session_state:
    load_all_data()

df = st.session_state.full_df
budget_df = st.session_state.budget_df
st.header('Raw Datasets')
st.dataframe(df)

st.subheader('Budget')
st.dataframe(budget_df)

# Sweetviz
st.subheader("Exploratory Data Analysis - Sweetviz")
@st.cache_resource
def eda(df, title):
    # 1. Create a named temporary file that Cloud Run can handle in /tmp
    # This ensures we don't have permission issues or persistent file clutter
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        report_path = tmp.name
        
    # 2. Generate the report to that temp path
    report = sv.analyze([df, title])
    report.show_html(filepath=report_path, open_browser=False, layout='vertical')
    
    # 3. Read the content back
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 4. Cleanup: Remove the temp file to free up Cloud Run memory
    if os.path.exists(report_path):
        os.remove(report_path)

    return html_content

# Actual columns removed
campaign_df = df.group_by('Date').agg([
    pl.col(c).sum() 
    for c in ['Revenue','Cost']
])
html_report = eda(campaign_df.to_pandas(), 'Campaign Level')
components.html(html_report, width=1100, height=1200, scrolling=True)
