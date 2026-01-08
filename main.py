from config import initialize_app
from data_tools import load_all_data
from utils import inject_google_analytics
import pandas as pd
import polars as pl
import streamlit as st

# GA
inject_google_analytics()

def main():
    # add headers, logo etc
    initialize_app()
    
    email = st.user.email
    st.markdown(f"Logged in as {email}")
    load_all_data()

if __name__ == '__main__':
    main()
