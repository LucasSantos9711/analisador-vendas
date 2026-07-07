"""
Sales Data Ingestion Pipeline

Reads messy sales CSV files, cleans and standardizes the data,
then persists it to a SQLite database for downstream analysis.

Usage:
    python src/ingest.py
"""
from pathlib import Path
import sys
import pandas as pd
import sqlite3

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "sample_vendas.csv"
DB_FILE = BASE_DIR / "data" / "vendas.db"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize sales data."""
    # Standardize column names (lowercase, no spaces)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Convert date column
    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")

    # Convert numeric columns
    for col in ["valor", "quantidade"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing critical fields
    df = df.dropna(subset=["data_venda", "valor"])

    # Calculate total sale value
    if "quantidade" in df.columns:
        df["valor_total"] = df["valor"] * df["quantidade"]

    # Standardize text fields (title case, trimmed)
    for col in ["produto", "categoria", "regiao", "vendedor", "cliente"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    return df


def ingest():
    """Run the ETL pipeline."""
    print(f"📂 Reading: {DATA_FILE.name}")

    if not DATA_FILE.exists():
        print(f"❌ File not found: {DATA_FILE}")
        sys.exit(1)

    # Extract
    df = pd.read_csv(DATA_FILE)
    print(f"   Loaded {len(df)} rows from CSV")

    # Transform
    df = clean_data(df)
    print(f"   Cleaned to {len(df)} valid rows")

    # Load
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("vendas", conn, if_exists="replace", index=False)
    conn.close()

    # Summary
    print(f"\n✅ Ingestion complete!")
    print(f"   Database: {DB_FILE}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {', '.join(df.columns)}")
    print(f"   Date range: {df['data_venda'].min().date()} → {df['data_venda'].max().date()}")
    print(f"   Total revenue: R$ {df['valor_total'].sum():,.2f}")


if __name__ == "__main__":
    ingest()
