"""
Sales Analytics Module

Provides functions to analyze sales data stored in SQLite.
Each function returns a DataFrame or dict, ready to use in dashboards.
Supports optional filters for region, category, and date range.

Usage:
    from src.analysis import get_summary_stats, get_revenue_by_month
"""
import sqlite3
from pathlib import Path
import pandas as pd

# Paths
BASE_DIR = Path(__file__).parent.parent
DB_FILE = BASE_DIR / "data" / "vendas.db"


def get_connection():
    """Open SQLite connection. Raises if DB doesn't exist yet."""
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_FILE}\n"
            f"Run 'python src/ingest.py' first to create it."
        )
    return sqlite3.connect(DB_FILE)


def _build_where(region=None, category=None, date_from=None, date_to=None):
    """Build WHERE clause from optional filters."""
    clauses = []
    if region:
        clauses.append(f"regiao = '{region}'")
    if category:
        clauses.append(f"categoria = '{category}'")
    if date_from:
        clauses.append(f"data_venda >= '{date_from}'")
    if date_to:
        clauses.append(f"data_venda <= '{date_to}'")
    if clauses:
        return "WHERE " + " AND ".join(clauses)
    return ""


def get_summary_stats(region=None, category=None, date_from=None, date_to=None):
    """Overall KPIs of the sales dataset."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            COUNT(*)                              AS total_vendas,
            SUM(valor_total)                      AS receita_total,
            AVG(valor_total)                      AS ticket_medio,
            COUNT(DISTINCT cliente)               AS total_clientes,
            COUNT(DISTINCT produto)               AS total_produtos,
            COUNT(DISTINCT vendedor)              AS total_vendedores,
            MIN(data_venda)                       AS primeira_venda,
            MAX(data_venda)                       AS ultima_venda
        FROM vendas
        {where}
    """
    with get_connection() as conn:
        row = pd.read_sql_query(query, conn).iloc[0]
    return row.to_dict()


def get_revenue_by_month(region=None, category=None, date_from=None, date_to=None):
    """Monthly revenue trend."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            strftime('%Y-%m', data_venda)         AS mes,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        {where}
        GROUP BY mes
        ORDER BY mes
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    df["mes"] = pd.to_datetime(df["mes"])
    return df


def get_revenue_by_region(region=None, category=None, date_from=None, date_to=None):
    """Revenue by Brazilian region."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            regiao,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        {where}
        GROUP BY regiao
        ORDER BY receita DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_revenue_by_category(region=None, category=None, date_from=None, date_to=None):
    """Revenue by product category."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            categoria,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        {where}
        GROUP BY categoria
        ORDER BY receita DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_products(n=10, region=None, category=None, date_from=None, date_to=None):
    """Top N products by revenue."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            produto,
            categoria,
            SUM(valor_total)                      AS receita,
            SUM(quantidade)                       AS quantidade
        FROM vendas
        {where}
        GROUP BY produto
        ORDER BY receita DESC
        LIMIT {int(n)}
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_sellers(n=10, region=None, category=None, date_from=None, date_to=None):
    """Top N sellers by revenue."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            vendedor,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        {where}
        GROUP BY vendedor
        ORDER BY receita DESC
        LIMIT {int(n)}
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_customers(n=10, region=None, category=None, date_from=None, date_to=None):
    """Top N customers by revenue."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            cliente,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        {where}
        GROUP BY cliente
        ORDER BY receita DESC
        LIMIT {int(n)}
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_revenue_by_weekday(region=None, category=None, date_from=None, date_to=None):
    """Revenue distribution by day of week."""
    where = _build_where(region, category, date_from, date_to)
    query = f"""
        SELECT
            CASE strftime('%w', data_venda)
                WHEN '0' THEN 'Domingo'
                WHEN '1' THEN 'Segunda'
                WHEN '2' THEN 'Terca'
                WHEN '3' THEN 'Quarta'
                WHEN '4' THEN 'Quinta'
                WHEN '5' THEN 'Sexta'
                WHEN '6' THEN 'Sabado'
            END                                   AS dia_semana,
            strftime('%w', data_venda)            AS dia_num,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        {where}
        GROUP BY dia_semana, dia_num
        ORDER BY dia_num
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def generate_insights(region=None, category=None, date_from=None, date_to=None):
    """Generate human-readable business insights from the data."""
    stats = get_summary_stats(region, category, date_from, date_to)
    by_region = get_revenue_by_region(region, category, date_from, date_to)
    by_category = get_revenue_by_category(region, category, date_from, date_to)
    by_month = get_revenue_by_month(region, category, date_from, date_to)
    by_day = get_revenue_by_weekday(region, category, date_from, date_to)

    insights = []

    insights.append(
        f"📊 **Receita Total:** R$ {stats['receita_total']:,.2f} "
        f"em {stats['total_vendas']:,} vendas realizadas"
    )

    insights.append(
        f"💰 **Ticket Médio:** R$ {stats['ticket_medio']:,.2f} por venda"
    )

    if not by_region.empty:
        top = by_region.iloc[0]
        pct = (top["receita"] / stats["receita_total"]) * 100
        insights.append(
            f"🌎 **Região Líder:** {top['regiao']} domina com "
            f"{pct:.1f}% da receita (R$ {top['receita']:,.2f})"
        )

    if not by_category.empty:
        top_cat = by_category.iloc[0]
        pct = (top_cat["receita"] / stats["receita_total"]) * 100
        insights.append(
            f"📦 **Categoria Top:** {top_cat['categoria']} "
            f"representa {pct:.1f}% do faturamento"
        )

    if len(by_month) >= 2:
        last = by_month.iloc[-1]["receita"]
        prev = by_month.iloc[-2]["receita"]
        change = ((last - prev) / prev) * 100
        if change > 5:
            emoji = "🚀"
            label = "crescimento"
        elif change > 0:
            emoji = "📈"
            label = "leve alta"
        elif change > -5:
            emoji = "📉"
            label = "leve queda"
        else:
            emoji = "⚠️"
            label = "queda significativa"
        last_label = by_month.iloc[-1]["mes"].strftime("%B/%Y")
        insights.append(
            f"{emoji} **Tendência:** {last_label} teve {label} de "
            f"{change:+.1f}% vs mês anterior"
        )

    if not by_day.empty:
        best_day = by_day.loc[by_day["receita"].idxmax()]
        worst_day = by_day.loc[by_day["receita"].idxmin()]
        diff = ((best_day["receita"] - worst_day["receita"]) / worst_day["receita"]) * 100
        insights.append(
            f"📅 **Melhor Dia:** {best_day['dia_semana']} vende "
            f"{diff:.0f}% a mais que {worst_day['dia_semana']}"
        )

    insights.append(
        f"👥 **Base de Clientes:** {stats['total_clientes']} clientes únicos "
        f"atendidos por {stats['total_vendedores']} vendedores"
    )

    return insights
