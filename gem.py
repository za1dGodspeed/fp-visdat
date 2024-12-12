from typing import List, Tuple
from streamlit_dynamic_filters import DynamicFilters

import pandas as pd
import plotly.express as px
import streamlit as st
import altair as alt
import requests

geojson = requests.get(
    "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
).json()


def set_page_config():
    st.set_page_config(
        page_title="Dashboard Admisi Perguruan Tinggi",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)
    
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel('snmptn_all.xlsx', sheet_name=None, index_col=None)
    data = pd.concat(df.values())
    return data

def filter_data(data: pd.DataFrame, column: str, values: List[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data

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
        
        
def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    st.sidebar.header("Filters")
    start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['ORDERDATE'].min().date()))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", data['ORDERDATE'].max().date()))

    product_lines = sorted(data['PRODUCTLINE'].unique())
    selected_product_lines = st.sidebar.multiselect("Product lines", product_lines, product_lines)

    selected_countries = st.sidebar.multiselect("Select Countries", data['COUNTRY'].unique())

    selected_statuses = st.sidebar.multiselect("Select Order Statuses", data['STATUS'].unique())

    return selected_product_lines, selected_countries, selected_statuses

def display_charts(data: pd.DataFrame):
    combine_product_lines = st.checkbox("Combine Product Lines", value=True)

    if combine_product_lines:
        fig = px.area(data, x='ORDERDATE', y='SALES',
                      title="Sales by Product Line Over Time", width=900, height=500)
    else:
        fig = px.area(data, x='ORDERDATE', y='SALES', color='PRODUCTLINE',
                      title="Sales by Product Line Over Time", width=900, height=500)

    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    fig.update_xaxes(rangemode='tozero', showgrid=False)
    fig.update_yaxes(rangemode='tozero', showgrid=True)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top 10 Customers")
        top_customers = data.groupby('CUSTOMERNAME')['SALES'].sum().reset_index().sort_values('SALES',
                                                                                              ascending=False).head(10)
        st.write(top_customers)

    with col2:
        st.subheader("Top 10 Products by Sales")
        top_products = data.groupby(['PRODUCTCODE', 'PRODUCTLINE'])['SALES'].sum().reset_index().sort_values('SALES',
                                                                                                             ascending=False).head(
            10)
        st.write(top_products)

    with col3:
        st.subheader("Total Sales by Product Line")
        total_sales_by_product_line = data.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
        st.write(total_sales_by_product_line)

def main():
    set_page_config()
    # page = st_navbar(["Home", "Documentation", "Examples", "Community", "About"])
    # st.write(page)
    

    data = load_data()
    data['nama_prodi'] = data['nama_prodi'].str.title()
    data['nama_univ'] = data['nama_univ'].str.title()
    dynamic_filters = DynamicFilters(data, filters=['tahun','kabupaten/kota', 'provinsi', 'jenjang', 'nama_univ', 'nama_prodi'])
    dynamic_filters.display_filters(location='sidebar') 
    filtered_df = dynamic_filters.filter_df(except_filter=None)
    # dynamic_filters.display_df()
    

          
    # with st.sidebar:
    #     st.write("Apply filters in any order")
    
        
    st.title("📊 Dashboard Admisi Perguruan Tinggi")

    # selected_product_lines, selected_countries, selected_statuses = display_sidebar(data)

    # filtered_data = data.copy()
    # filtered_data = filter_data(filtered_data, 'PRODUCTLINE', selected_product_lines)
    # filtered_data = filter_data(filtered_data, 'COUNTRY', selected_countries)
    # filtered_data = filter_data(filtered_data, 'STATUS', selected_statuses)

    kpis = calculate_kpis(filtered_df)
    kpi_names = ["Total Peminat", "Total Kuota", "Rasio antara Kuota dan Peminat"]
    display_kpi_metrics(kpis, kpi_names)

    # dtest = filtered_df["daya_tampung"].value_counts().rename_axis('unique_values').reset_index(name='counts')
    # st.bar_chart(filtered_df, x="tahun", y=["daya_tampung", "peminat"])
    # st.bar_chart(dtest)
    # display_charts(filtered_data)
    # wow = px.data.tips()
    # filtered_df['tahun'] = pd.to_datetime(filtered_df['tahun'], format='%y')
    
    fig =   alt.Chart(filtered_df).mark_bar().encode(
            x='tahun:O',
            y='sum(daya_tampung):Q',
            
)
    st.altair_chart(fig) # perbandingan merupakan group bar chart
    
    # fig = px.histogram(filtered_df, x="tahun", y=['daya_tampung', 'peminat'],
    #          barmode='group',
    #          height=400)
    # st.plotly_chart(fig)
    
    # create columna for both graph
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
        
     # get the top 10 most profitable products
    # with col3:
        # chart = alt.Chart(top_prodi_peminat).mark_bar(opacity=0.9,color="#9FC131").encode(
        #         x='sum(peminat):Q',
        #         y=alt.Y('nama_prodi:N', sort='-x')   
        #     )
        # chart = chart.properties(title="Top 10 Prodi dengan Peminat Tertinggi")

        # st.altair_chart(chart,use_container_width=True)
            
    # with col3:
    #         filtered_df.loc[filtered_df['peminat'] < 100, 'nama_prodi'] = 'Prodi Lain'
    #         fig = px.pie(filtered_df, values='peminat', names='nama_prodi', title='Sebaran Peminat Program Studi')
    #         fig.update_traces(textposition='inside', textinfo='percent+label')
    #         fig.update(layout_showlegend=False)

    #         st.plotly_chart(fig,use_container_width=True)
    
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
        
    # with col5:
    #     fig = px.choropleth_mapbox(filtered_df, geojson=geojson, locations='provinsi', color='nama_univ',
    #                        color_continuous_scale="Viridis",
    #                        range_color=(0, 12),
    #                        mapbox_style="carto-positron",
    #                        zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
    #                        opacity=0.5,
    #                        labels={'nama_univ':'Banyak Jumlah Kampus'}
    #                       )
    #     fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #     fig.update(layout_showlegend=False) #count jumlah univ untuk tiap wilayah
        
    #     st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    main()                