"""
Sales Analytics Dashboard - Professional Edition

Interactive dashboard with working filters, polished charts,
tabbed interface, and contextual insights.

Run with:
    streamlit run src/app.py
"""
import sys
from pathlib import Path

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
    page_title="Sales Analytics | Lucas Santos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Color palette
COLORS = {
    "primary": "#0EA5E9",
    "secondary": "#0369A1",
    "accent": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "bg": "#0d1117",
    "card": "#161b22",
    "text": "#ffffff",
    "muted": "#8b949e",
}

# Custom CSS
st.markdown(
    f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {COLORS['bg']} 0%, #0a0e14 100%);
    }}

    .hero {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(14, 165, 233, 0.15);
    }}

    .hero-title {{
        font-size: 2.4rem;
        font-weight: 700;
        color: white;
        margin: 0;
    }}

    .hero-subtitle {{
        font-size: 1.05rem;
        color: rgba(255, 255, 255, 0.85);
        margin-top: 0.5rem;
    }}

    .live-badge {{
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid {COLORS['accent']};
        color: {COLORS['accent']};
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.75rem;
    }}

    .live-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        background: {COLORS['accent']};
        border-radius: 50%;
        margin-right: 0.4rem;
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}

    .kpi-card {{
        background: {COLORS['card']};
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    }}

    .kpi-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: {COLORS['primary']};
    }}

    .kpi-icon {{
        font-size: 1.8rem;
        margin-bottom: 0.4rem;
    }}

    .kpi-label {{
        font-size: 0.78rem;
        color: {COLORS['muted']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }}

    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin: 0.3rem 0 0 0;
    }}

    .insight-card {{
        background: linear-gradient(135deg, {COLORS['card']} 0%, #1c2128 100%);
        border-left: 4px solid {COLORS['primary']};
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        color: {COLORS['text']};
    }}

    .section-title {{
        font-size: 1.4rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['card']};
        border-radius: 8px;
        color: {COLORS['muted']};
        padding: 0.6rem 1.25rem;
        border: 1px solid #30363d;
        font-weight: 600;
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLORS['primary']} !important;
        color: white !important;
        border-color: {COLORS['primary']} !important;
    }}

    [data-testid="stSidebar"] {{
        background: {COLORS['card']};
    }}
</style>
""",
    unsafe_allow_html=True,
)

# Hero
st.markdown(
    f"""
<div class="hero">
    <h1 class="hero-title">📊 Sales Analytics Dashboard</h1>
    <p class="hero-subtitle">Pipeline ETL completo · SQLite · Visualizações interativas · Atualizado em tempo real</p>
    <div class="live-badge"><span class="live-dot"></span>LIVE DATA</div>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar filters
with st.sidebar:
    st.markdown("### 🎛️ Painel de Controle")
    st.markdown("---")

    st.markdown("#### 🔍 Filtros")

    try:
        df_region_filter = get_revenue_by_region()
        df_category_filter = get_revenue_by_category()
    except Exception:
        df_region_filter = None
        df_category_filter = None

    regions = ["Todas"] + (
        sorted(df_region_filter["regiao"].unique().tolist())
        if df_region_filter is not None
        else []
    )
    region = st.selectbox("🌎 Região", regions, key="region_filter")

    categories = ["Todas"] + (
        sorted(df_category_filter["categoria"].unique().tolist())
        if df_category_filter is not None
        else []
    )
    category = st.selectbox("📦 Categoria", categories, key="category_filter")

    st.markdown("---")
    st.markdown("#### ℹ️ Sobre")
    st.markdown(
        "<small>Dashboard interativo construído com Python + Streamlit + Plotly. "
        "Dados processados via pipeline ETL → SQLite.</small>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<small>👨‍💻 Por <a href='https://github.com/LucasSantos9711' "
        f"style='color:{COLORS['primary']}'>Lucas Lopes dos Santos</a></small>",
        unsafe_allow_html=True,
    )

# Apply filters
region_filter = None if region == "Todas" else region
category_filter = None if category == "Todas" else category

# Load data with auto-bootstrap
try:
    stats = get_summary_stats(region=region_filter, category=category_filter)
    df_month = get_revenue_by_month(region=region_filter, category=category_filter)
    df_region = get_revenue_by_region(region=region_filter, category=category_filter)
    df_category = get_revenue_by_category(region=region_filter, category=category_filter)
    df_products = get_top_products(10, region=region_filter, category=category_filter)
    df_sellers = get_top_sellers(10, region=region_filter, category=category_filter)
    df_customers = get_top_customers(10, region=region_filter, category=category_filter)
    df_weekday = get_revenue_by_weekday(region=region_filter, category=category_filter)
    insights = generate_insights(region=region_filter, category=category_filter)
except FileNotFoundError:
    st.warning("🔄 Primeira execução — criando banco de dados...")
    import subprocess

    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "ingest.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        st.success("✅ Banco criado! Recarregando...")
        st.rerun()
    else:
        st.error(f"Erro ao criar banco:\n```\n{result.stderr}\n```")
        st.stop()

# KPI Cards
st.markdown(
    '<div class="section-title">📈 Indicadores Principais</div>',
    unsafe_allow_html=True,
)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Receita Total</div>
        <div class="kpi-value">R$ {stats['receita_total']:,.2f}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-icon">🛒</div>
        <div class="kpi-label">Total de Vendas</div>
        <div class="kpi-value">{stats['total_vendas']:,}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-label">Ticket Médio</div>
        <div class="kpi-value">R$ {stats['ticket_medio']:,.2f}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
    <div class="kpi-card">
        <div class="kpi-icon">👥</div>
        <div class="kpi-label">Clientes Únicos</div>
        <div class="kpi-value">{stats['total_clientes']:,}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Auto Insights
st.markdown(
    '<div class="section-title">💡 Insights Automáticos</div>',
    unsafe_allow_html=True,
)
for insight in insights:
    st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Visão Geral", "📦 Produtos", "👥 Pessoas", "🌎 Geografia"]
)

with tab1:
    st.markdown(
        '<div class="section-title">📈 Tendência Mensal de Receita</div>',
        unsafe_allow_html=True,
    )
    fig = px.line(
        df_month,
        x="mes",
        y="receita",
        markers=True,
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=10, line=dict(width=2, color="white")))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        yaxis_title="Receita (R$)",
        yaxis_gridcolor="#30363d",
        xaxis_gridcolor="#30363d",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            '<div class="section-title">📦 Por Categoria</div>',
            unsafe_allow_html=True,
        )
        fig = px.pie(
            df_category,
            values="receita",
            names="categoria",
            color_discrete_sequence=[
                COLORS["primary"],
                COLORS["secondary"],
                COLORS["accent"],
                COLORS["warning"],
                COLORS["danger"],
            ],
            hole=0.5,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=12)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown(
            '<div class="section-title">📅 Por Dia da Semana</div>',
            unsafe_allow_html=True,
        )
        fig = px.bar(
            df_weekday,
            x="dia_semana",
            y="receita",
            color="receita",
            color_continuous_scale=[COLORS["primary"], COLORS["secondary"]],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend=False,
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown(
        '<div class="section-title">🏆 Top 10 Produtos por Receita</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        df_products[["produto", "categoria", "receita", "quantidade"]]
        .reset_index(drop=True)
        .style.format({"receita": "R$ {:.2f}", "quantidade": "{:.0f}"}),
        use_container_width=True,
        height=500,
    )

    st.markdown(
        '<div class="section-title">📊 Receita por Categoria</div>',
        unsafe_allow_html=True,
    )
    fig = px.bar(
        df_category,
        x="categoria",
        y="receita",
        color="receita",
        color_continuous_scale=[COLORS["primary"], COLORS["secondary"]],
        text="receita",
    )
    fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(
            '<div class="section-title">🥇 Top 10 Vendedores</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            df_sellers.reset_index(drop=True).style.format({"receita": "R$ {:.2f}"}),
            use_container_width=True,
            height=500,
        )

    with col_r:
        st.markdown(
            '<div class="section-title">🏢 Top 10 Clientes</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            df_customers.reset_index(drop=True).style.format({"receita": "R$ {:.2f}"}),
            use_container_width=True,
            height=500,
        )

with tab4:
    st.markdown(
        '<div class="section-title">🌎 Receita por Região do Brasil</div>',
        unsafe_allow_html=True,
    )
    fig = px.bar(
        df_region,
        x="regiao",
        y="receita",
        color="receita",
        color_continuous_scale=[COLORS["primary"], COLORS["secondary"]],
        text="receita",
    )
    fig.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"<center><small>📊 Sales Analytics Dashboard · "
    f"Construído por <a href='https://github.com/LucasSantos9711' "
    f"style='color:{COLORS['primary']}'>Lucas Lopes dos Santos</a> · "
    f"Python + Pandas + Streamlit + Plotly</small></center>",
    unsafe_allow_html=True,
)
