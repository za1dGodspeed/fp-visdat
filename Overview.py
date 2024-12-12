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

@st.cache_data
def calculate_kpis(data: pd.DataFrame) -> List[float]:
    total_peminat = data['peminat'].astype("Int64").sum()
    format_total_peminat = f"{total_peminat / 1:,.0f}".replace(",", ".")
    total_kuota = data['daya_tampung'].astype("Int64").sum()
    format_total_kuota = f"{total_kuota / 1:,.0f}".replace(",", ".")
    rasio_peminat = 0
    if total_peminat != 0 :
        rasio_peminat= "1:"+f"{round((total_kuota / total_peminat) * 100)}"
    return [format_total_peminat, format_total_kuota, rasio_peminat]

def display_kpi_metrics(kpis: List[float], kpi_names: List[str]):
    st.header("KPI Metrics")
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(3), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)
        
        

data = load_data()
data['nama_prodi'] = data['nama_prodi'].str.title()
data['nama_univ'] = data['nama_univ'].str.title()
dynamic_filters = DynamicFilters(data, filters=['tahun','kabupaten/kota', 'provinsi', 'jenjang', 'nama_univ', 'nama_prodi'])
# dynamic_filters = DynamicFilters(data, filters=['nama_prodi'])
dynamic_filters.display_filters(location='sidebar') 
filtered_df = dynamic_filters.filter_df(except_filter=None)
    
st.title("📊 Dashboard Admisi Perguruan Tinggi")

kpis = calculate_kpis(filtered_df)
kpi_names = ["Total Peminat", "Total Kuota", "Rasio antara Kuota dan Peminat"]
display_kpi_metrics(kpis, kpi_names)

fig =   alt.Chart(filtered_df).mark_bar().encode(
        x='tahun:O',
        y='sum(daya_tampung):Q',
        
)
st.altair_chart(fig) # perbandingan merupakan group bar chart

col1,col2 = st.columns(2)
# get the top 10 best selling products
top_product_sales = filtered_df.groupby('nama_univ')['daya_tampung'].sum()
top_product_sales = top_product_sales.nlargest(10)
top_product_sales = pd.DataFrame(top_product_sales).reset_index()

# get the top 10 most profitable products
top_product_profit = filtered_df.groupby('nama_univ')['peminat'].sum()
top_product_profit = top_product_profit.nlargest(10)
top_product_profit = pd.DataFrame(top_product_profit).reset_index()

top_prodi_peminat = filtered_df.groupby('nama_prodi')['peminat'].sum()
top_prodi_peminat = top_prodi_peminat.nlargest(10)
top_prodi_peminat = pd.DataFrame(top_prodi_peminat).reset_index()

# create the altair chart
with col1:
    chart = alt.Chart(filtered_df).mark_bar(opacity=0.9,color="#9FC131").encode(
            x='sum(daya_tampung):Q',
            y=alt.Y('nama_univ:N', sort='-x'),
            color='tahun:N'
            ).transform_window(
            rank='rank(daya_tampung)',
            sort=[alt.SortField('daya_tampung', order='descending')]
            ).transform_filter(
            (alt.datum.rank < 10)
    )
    chart = chart.properties(title="Top 10 Daya Tampung Tertinggi")

    st.altair_chart(chart,use_container_width=True)

# create the altair chart
with col2:
    chart = alt.Chart(top_product_profit).mark_bar(opacity=0.9,color="#9FC131").encode(
            x='sum(peminat):Q',
            y=alt.Y('nama_univ:N', sort='-x')
        )
    chart = chart.properties(title="Top 10 Peminat Tertinggi")

    st.altair_chart(chart,use_container_width=True)
    
col4, col5 = st.columns(2)

with col4:
    # filtered_df.loc[filtered_df['peminat'] < 100, 'nama_prodi'] = 'Prodi Lain'
    fig = px.pie(filtered_df, values='daya_tampung', names='jenjang', title='Persentase Daya Tampung tiap Jenjang', hole=.3, color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update(layout_showlegend=False)

    st.plotly_chart(fig,use_container_width=True)

with col5:
    chart = alt.Chart(top_prodi_peminat).mark_bar(opacity=0.9,color="#9FC131").encode(
            x='sum(peminat):Q',
            y=alt.Y('nama_prodi:N', sort='-x')   
        )
    chart = chart.properties(title="Top 10 Prodi dengan Peminat Tertinggi")

    st.altair_chart(chart,use_container_width=True)       