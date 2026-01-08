from data_tools import fetch_bq_data_cached
from streamlit_extras.stylable_container import stylable_container
import streamlit as st
import os

PAGE_CONFIG = {
    "page_title": "Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

def get_spreadsheet_config():
    return os.environ.get('SPREADSHEET_ID'), os.environ.get('SHEET_NAME'), os.environ.get('RANGE')

def get_cloud_function_url():
    return os.environ.get("CLOUD_FUNCTION_URL")

def initialize_app():
    st.set_page_config(
        **PAGE_CONFIG
    )
    
    st.header('Sample Dashboard')

    # Create pages
    raw_data_page = st.Page("pages/raw_data.py", title="Raw Data")
    summary_page = st.Page("pages/summary.py", title="Summary")
    

    # Create the navigation in your specific order
    pg = st.navigation([summary_page, raw_data_page])

    pg.run()
    
    with st.sidebar: 
        if 'is_logged_in' in st.user and st.user.is_logged_in:
            with stylable_container(
                key="bottom_logout_button",
                css_styles="""
                    {
                        position: fixed;
                        bottom: 2rem;
                        width: 100%;
                    }
                """,
            ):
                if st.button("🔄 Refresh Data"):
                    st.session_state.clear()
                    st.rerun()
                if st.button("Log out"):
                    st.logout()
                
        else:
            if st.button("Log in with Google"):
                st.login()
            st.stop()
        
