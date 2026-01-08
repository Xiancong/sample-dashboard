from .bigquery import fetch_bq_data_cached
import pandas as pd
import streamlit as st

def load_data(sql, **kwargs):
    permissions = kwargs['permissions']
    email = kwargs['email']
    df = fetch_bq_data_cached(sql, permissions, email)
    return df

def load_all_data():
    if 'full_df' not in st.session_state:
        df = load_data(
            f'''
                select 
                    *, 
                    DATE_TRUNC(Date, month) mth
                from S.mc
            '''
            , permissions = True
            , email = st.user.email
        )
        st.session_state.full_df = df
    # load data only if not in session state (i.e. already loaded previously)
    # Query does not contain actual table names as this is just a sample
    if 'budget_df' not in st.session_state:
        budget_df = load_data('select * from S.b where A is not null', permissions = False, email = st.user.email)
        st.session_state.budget_df = budget_df
