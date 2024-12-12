from typing import List, Tuple
from streamlit_dynamic_filters import DynamicFilters

import pandas as pd
import plotly.express as px
import altair as alt
import streamlit as st

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel('snmptn_all.xlsx', sheet_name=None, index_col=None)
    data = pd.concat(df.values())
    return data

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

data = load_data()
data['nama_prodi'] = data['nama_prodi'].str.title()
data['nama_univ'] = data['nama_univ'].str.title()
# dynamic_filters = DynamicFilters(data, filters=['tahun','kabupaten/kota', 'provinsi', 'jenjang', 'nama_univ', 'nama_prodi'])
dynamic_filterss = DynamicFilters(data, filters=['nama_prodi'])
dynamic_filterss.display_filters(location='columns', num_columns=1) 
filtered_df = dynamic_filterss.filter_df(except_filter=None)
    
st.title("📊 Dashboard Admisi Perguruan Tinggi")

st.write('Program Studi ' + filtered_df['nama_prodi'].iloc[0])
