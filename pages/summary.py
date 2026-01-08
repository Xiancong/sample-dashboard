from data_tools import load_all_data
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, ColumnsAutoSizeMode
import pandas as pd
import numpy as np
import polars as pl
import streamlit as st

# check if data is loaded. if not load data
if 'full_df' not in st.session_state or 'budget_df' not in st.session_state:
    load_all_data()

# definitions
percentage_columns = []
numeric_columns = []

# initialise dataframes
df = st.session_state.full_df
budget_df = st.session_state.budget_df

# find the max month
max_mth = df['mth'].max()

# define base aggregation columns
base_columns = ['Account']

# convert to lazyframe
budget_lf = budget_df.lazy()
lf = df.lazy()

### CLEAN AND TRANSFORM DATA
# specify open budget
budget_lf = budget_lf.with_columns(pl.when(pl.col('Budget')>=9999999).then(None).otherwise(pl.col('Budget')).alias('Budget'))

# MTD rev for the latest month available for each aggregation group
lf = lf.with_columns([
    pl.col('Revenue').filter(pl.col('mth') == max_mth).sum().over(base_columns).alias('latest_MTD_Rev'),
    pl.col('Cost').filter(pl.col('mth') == max_mth).sum().over(base_columns).alias('latest_MTD_Cost'),
])

lf = lf.with_columns((pl.col('latest_MTD_Rev')/pl.col('latest_MTD_Cost')).alias('latest_MTD_ROI'))

# configure lookback period
no_of_days = 3

date_set = (
    lf.select(pl.col("Date").unique())
    .sort("Date", descending=True)
    .head(no_of_days)
    .collect()
    .get_column('Date')
    .to_list()
)

# sort ascending
date_set.sort(reverse = False)

lf = lf.group_by(base_columns+['latest_MTD_Rev', 'latest_MTD_Cost', 'latest_MTD_ROI']).agg([
    pl.col('Revenue').filter(pl.col('Date')==d).sum().alias(str(d))
    for d in date_set
])

# join budget table
lf = lf.join(budget_lf,on=base_columns,how="left")

# Calculate FFR and budget exceeded
lf = lf.with_columns([
    (pl.col('latest_MTD_Rev')/pl.col('Budget').cast(pl.Float64)).alias('FFR %')
])

# convert dates to string
date_set = [str(d) for d in date_set]

# # multiply percentage columns by 100 to handle formatting
# lf = lf.with_columns([
#     (pl.col(c)*100).alias(c)
#     for c in percentage_columns
# ])

# define column order
col_order = base_columns+['latest_MTD_Rev','latest_MTD_Cost','latest_MTD_ROI','Budget','FFR %']+date_set

# rearrange column order
lf = lf.select(col_order)

# remove null rows
lf = lf.filter(
    (pl.col('Account').is_not_null())
    & ((pl.col('latest_MTD_Rev') > 0) | (pl.col('latest_MTD_Cost') > 0))
)

# sort table
lf = lf.sort(
    by = base_columns
)

df = lf.collect().to_pandas()

gb = GridOptionsBuilder.from_dataframe(df)

# --- NUMBER FORMATTING ---
# Column with Commas and 2 Decimal Places
numeric_columns = numeric_columns + date_set
for c in numeric_columns:
    dp = 2
    gb.configure_column(
        c, 
        type=["numericColumn","numberColumnFilter"], 
        valueFormatter=f"Math.floor(value).toLocaleString() + (value % 1).toFixed({dp}).slice(1)"
    )

# Format budget column
budget_formatter = JsCode("""
    function(params) {
        if (params.value === null || params.value === undefined || params.value === '') {
            return 'Open';
        }
        return Math.floor(params.value).toLocaleString('en-US', {
            minimumFractionDigits: 0, 
            maximumFractionDigits: 0
        });
    }
""")

gb.configure_column(
    "Budget",
    headerName="Budget",
    valueFormatter=budget_formatter,
    type=["numberColumnFilter"], # We avoid "numericColumn" to prevent formatting conflicts
)

# Column with Percentage and 2 Decimal Places
percentage_columns = ['FFR %']
for c in percentage_columns:
    gb.configure_column(
        c, 
        valueFormatter="x.toLocaleString(undefined, {style: 'percent', minimumFractionDigits: 1})"
    )

gb.configure_default_column(
    resizable=True, 
    wrapText=False,
    headerClass='center-header',
    cellStyle={'wordBreak': 'normal','text-align': 'center'},
    # Optional: Set a minimum width so columns don't disappear
    minWidth=60
)

# --- ZEBRA STRIPING ---
# This JS function runs on every row. Even if you sort, the colors stay alternating.
row_style_jscode = JsCode("""
function(params) {
    if (params.node.rowIndex % 2 === 0) {
        return {
            'backgroundColor': '#e3e3e3',
        }
    }
};
""")

other_options = {'suppressColumnVirtualisation': True}
gb.configure_grid_options(**other_options)

gridOptions = gb.build()
gridOptions['getRowStyle'] = row_style_jscode

# custom_css = {".ag-header-cell-text": {"font-size": "12px", 'text-overflow': 'revert;', 'font-weight': 700},
#       ".ag-theme-streamlit": {'transform': "scale(0.8)", "transform-origin": '0 0'}}
custom_css = {
    ".ag-header-cell-label": {
        "justify-content": "center"
    }
}
# Display
st.subheader('Summary Table')
AgGrid(
    df, 
    gridOptions=gridOptions, 
    allow_unsafe_jscode=True, 
    update_mode='NO_UPDATE',
    custom_css=custom_css,
    # CHANGE: Use FIT_CONTENTS (Mode 2)
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    theme='streamlit'
)
