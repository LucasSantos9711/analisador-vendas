"""
Sales Analytics Module

Provides functions to analyze sales data stored in SQLite.
Each function returns a DataFrame or dict, ready to use in dashboards.

Usage:
    from src.analysis import get_summary_stats, get_revenue_by_month
"""
import sqlite3
from pathlib import Path
import pandas as pd

# Paths
BASE_DIR = Path(__file__).parent.parent
DB_FILE = BASE_DIR / "data" / "vendas.db"


# ---------- Connection ----------

def get_connection():
    """Open SQLite connection. Raises if DB doesn't exist yet."""
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_FILE}\n"
            f"Run 'python src/ingest.py' first to create it."
        )
    return sqlite3.connect(DB_FILE)


# ---------- Core analytics ----------

def get_summary_stats() -> dict:
    """Overall KPIs of the sales dataset."""
    query = """
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
    """
    with get_connection() as conn:
        row = pd.read_sql_query(query, conn).iloc[0]
    return row.to_dict()


def get_revenue_by_month() -> pd.DataFrame:
    """Monthly revenue trend."""
    query = """
        SELECT 
            strftime('%Y-%m', data_venda)         AS mes,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        GROUP BY mes
        ORDER BY mes
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    df["mes"] = pd.to_datetime(df["mes"])
    return df


def get_revenue_by_region() -> pd.DataFrame:
    """Revenue by Brazilian region."""
    query = """
        SELECT 
            regiao,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        GROUP BY regiao
        ORDER BY receita DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_revenue_by_category() -> pd.DataFrame:
    """Revenue by product category."""
    query = """
        SELECT 
            categoria,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        GROUP BY categoria
        ORDER BY receita DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_products(n: int = 10) -> pd.DataFrame:
    """Top N products by revenue."""
    query = f"""
        SELECT 
            produto,
            categoria,
            SUM(valor_total)                      AS receita,
            SUM(quantidade)                       AS quantidade
        FROM vendas
        GROUP BY produto
        ORDER BY receita DESC
        LIMIT {int(n)}
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_sellers(n: int = 10) -> pd.DataFrame:
    """Top N sellers by revenue."""
    query = f"""
        SELECT 
            vendedor,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        GROUP BY vendedor
        ORDER BY receita DESC
        LIMIT {int(n)}
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_customers(n: int = 10) -> pd.DataFrame:
    """Top N customers by revenue."""
    query = f"""
        SELECT 
            cliente,
            SUM(valor_total)                      AS receita,
            COUNT(*)                              AS num_vendas
        FROM vendas
        GROUP BY cliente
        ORDER BY receita DESC
        LIMIT {int(n)}
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_revenue_by_weekday() -> pd.DataFrame:
    """Revenue distribution by day of week."""
    query = """
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
        GROUP BY dia_semana, dia_num
        ORDER BY dia_num
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


# ---------- Auto insights ----------

def generate_insights() -> list:
    """Generate human-readable business insights from the data."""
    stats = get_summary_stats()
    by_region = get_revenue_by_region()
    by_category = get_revenue_by_category()
    by_month = get_revenue_by_month()
    by_day = get_revenue_by_weekday()

    insights = []

    # Total revenue
    insights.append(
        f"📊 Receita total: R$ {stats['receita_total']:,.2f} "
        f"em {stats['total_vendas']} vendas"
    )

    # Top region
    top = by_region.iloc[0]
    pct = (top["receita"] / stats["receita_total"]) * 100
    insights.append(
        f"🌎 Região líder: {top['regiao']} com {pct:.1f}% da receita total"
    )

    # Top category
    top_cat = by_category.iloc[0]
    pct = (top_cat["receita"] / stats["receita_total"]) * 100
    insights.append(
        f"📦 Categoria líder: {top_cat['categoria']} com {pct:.1f}% da receita"
    )

    # Month over month
    if len(by_month) >= 2:
        last = by_month.iloc[-1]["receita"]
        prev = by_month.iloc[-2]["receita"]
        change = ((last - prev) / prev) * 100
        emoji = "📈" if change > 0 else "📉"
        last_label = by_month.iloc[-1]["mes"].strftime("%Y-%m")
        insights.append(f"{emoji} {last_label}: variação de {change:+.1f}% vs mês anterior")

    # Best weekday
    best_day = by_day.loc[by_day["receita"].idxmax()]
    insights.append(f"📅 Melhor dia da semana: {best_day['dia_semana']}")

    # Average ticket
    insights.append(f"💰 Ticket médio: R$ {stats['ticket_medio']:,.2f}")

    return insights


# ---------- CLI test ----------

if __name__ == "__main__":
    print("=" * 60)
    print("ANALISE DE VENDAS")
    print("=" * 60)

    stats = get_summary_stats()
    print("\n📊 RESUMO GERAL")
    print(f"   Vendas:        {stats['total_vendas']}")
    print(f"   Receita total: R$ {stats['receita_total']:,.2f}")
    print(f"   Ticket medio:  R$ {stats['ticket_medio']:,.2f}")
    print(f"   Clientes:      {stats['total_clientes']}")
    print(f"   Periodo:       {stats['primeira_venda']} -> {stats['ultima_venda']}")

    print("\n🌎 POR REGIAO")
    print(get_revenue_by_region().to_string(index=False))

    print("\n📦 POR CATEGORIA")
    print(get_revenue_by_category().to_string(index=False))

    print("\n🏆 TOP 5 PRODUTOS")
    print(get_top_products(5).to_string(index=False))

    print("\n💡 INSIGHTS AUTOMATICOS")
    for line in generate_insights():
        print(f"   {line}")
