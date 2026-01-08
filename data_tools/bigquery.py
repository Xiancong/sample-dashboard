from google.cloud import bigquery
import streamlit as st
import pandas as pd
import polars as pl

# set up client
client = bigquery.Client(project="b1")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_bq_data_cached(sql, permissions, email, force_refresh=False):
    """Cached version of fetch_bq_data"""
    return _fetch_bq_data_internal(sql, permissions, email)

def query_builder(sql, permissions, email):
    if permissions:
        query = f'''
            with permissions as 
            (select * from S.p where email = "{email}")
            , base as 
            ({sql})
            
            select b.* from
            (
              (select * from base) b
              inner join permissions p
              on 
                -- actual joins removed
                True
            )
        '''
    else:
        query = sql
        
    return query
    
def _fetch_bq_data_internal(sql, permissions, email):
    """Internal function to fetch data from BQ"""
    try:        
        with st.spinner("Fetching data via Storage API..."):
            final_sql = query_builder(sql, permissions, email)

            query_job = client.query(final_sql)
            
            arrow_table = query_job.to_arrow(create_bqstorage_client=True)
            
            return pl.from_arrow(arrow_table)
                
    except Exception as e:
        error_msg = str(e)
        return pd.DataFrame()
