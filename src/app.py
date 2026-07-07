"""
Sales Analytics Dashboard

Interactive dashboard built with Streamlit + Plotly.
Reads from SQLite (created by ingest.py) and shows KPIs, charts, and insights.

Run with:
    streamlit run src/app.py
"""
import sys
from pathlib import Path

# Make src importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.analysis import (
    get_summary_stats,
    get_revenue_by_month,
    get_revenue_by_region,
    get_revenue_by_category,
    get_top_products,
    get_top_sellers,
    get_top_customers,
    get_revenue_by_weekday,
    generate_insights,
)

# Page config
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme color (matches profile)
PRIMARY = "#0EA5E9"
DARK = "#0369A1"

# Custom CSS for a polished look
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0EA5E9;
        margin-bottom: 0;
    }
    .sub-header {
        color: #6B7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown('<p class="main-header">📊 Sales Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">ETL pipeline → SQLite → interactive analytics</p>',
    unsafe_allow_html=True,
)

# Load data with friendly error
try:
    stats = get_summary_stats()
    df_month = get_revenue_by_month()
    df_region = get_revenue_by_region()
    df_category = get_revenue_by_category()
    df_products = get_top_products(10)
    df_sellers = get_top_sellers(10)
    df_customers = get_top_customers(10)
    df_weekday = get_revenue_by_weekday()
    insights = generate_insights()
except FileNotFoundError:
    st.error("❌ Database not found. Run `python src/ingest.py` first.")
    st.stop()

# Sidebar
st.sidebar.header("🔍 Filters")
regions = ["All"] + sorted(df_region["regiao"].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)
categories = ["All"] + sorted(df_category["categoria"].unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

st.sidebar.divider()
st.sidebar.caption(
    f"📅 Period: {str(stats['primeira_venda'])[:10]} → {str(stats['ultima_venda'])[:10]}"
)

# KPI Cards
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"R$ {stats['receita_total']:,.2f}")
col2.metric("Total Sales", f"{stats['total_vendas']:,}")
col3.metric("Avg Ticket", f"R$ {stats['ticket_medio']:,.2f}")
col4.metric("Unique Customers", f"{stats['total_clientes']:,}")

st.divider()

# Auto Insights
st.subheader("💡 Auto-Generated Insights")
for insight in insights:
    st.info(insight)

st.divider()

# Charts row 1: Trend + Region
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Monthly Revenue Trend")
    fig = px.line(
        df_month,
        x="mes",
        y="receita",
        markers=True,
        color_discrete_sequence=[PRIMARY],
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Month",
        yaxis_title="Revenue (R$)",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🌎 Revenue by Region")
    fig = px.bar(
        df_region,
        x="regiao",
        y="receita",
        color="receita",
        color_continuous_scale=["#0EA5E9", "#0369A1"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Region",
        yaxis_title="Revenue (R$)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# Charts row 2: Category + Weekday
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📦 Revenue by Category")
    fig = px.pie(
        df_category,
        values="receita",
        names="categoria",
        color_discrete_sequence=["#0EA5E9", "#0369A1", "#10B981", "#F59E0B", "#EF4444"],
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📅 Revenue by Weekday")
    fig = px.bar(
        df_weekday,
        x="dia_semana",
        y="receita",
        color="receita",
        color_continuous_scale=["#0EA5E9", "#0369A1"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Day",
        yaxis_title="Revenue (R$)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Top performers tables
st.subheader("🏆 Top Performers")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Top 10 Products**")
    st.dataframe(
        df_products[["produto", "categoria", "receita", "quantidade"]].style.format(
            {"receita": "R$ {:.2f}", "quantidade": "{:.0f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

with col2:
    st.markdown("**Top 10 Sellers**")
    st.dataframe(
        df_sellers.style.format({"receita": "R$ {:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

with col3:
    st.markdown("**Top 10 Customers**")
    st.dataframe(
        df_customers.style.format({"receita": "R$ {:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

# Footer
st.divider()
st.caption(
    "Built with Python + Pandas + Streamlit + Plotly · "
    "ETL pipeline: ingest.py → SQLite → analysis.py → app.py"
)
