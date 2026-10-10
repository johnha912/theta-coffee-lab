"""Table storage: a SQLite file by default, PostgreSQL when DATABASE_URL is set.

The CSV files in data/ are seed data only. On first run each table is created
from SCHEMA and filled from its CSV; after that the app reads and writes the
database, so related writes (a sale and its stock deduction) commit together.
"""
import io
import os
import zipfile
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

SEED_DIR = Path(__file__).parent / "data"

Text, Float, Integer = sa.Text, sa.Float, sa.BigInteger
SCHEMA = {
    "sales": {"Date": Text, "Order_ID": Text, "Product": Text, "Quantity": Integer, "Unit_Price": Float,
              "Total": Float, "Promo": Float, "Net_Total": Float, "Location": Text},
    "inventory": {"ID": Integer, "Name": Text, "Quantity": Float, "Unit": Text, "Avg_Cost": Float, "Date": Text},
    "products": {"Name": Text, "Price": Float, "COGS": Float, "Profit": Float},
    "product_recipe": {"Product": Text, "Ingredient": Text, "Quantity": Float, "Unit": Text},
    "operational_costs": {"Date": Text, "Type": Text, "Amount": Float},
    "inventory_transactions": {"Date": Text, "Material": Text, "Quantity": Float, "Unit": Text,
                               "Unit_Cost": Float, "Total_Cost": Float, "Type": Text},
}


@lru_cache
def engine():
    url = os.environ.get("DATABASE_URL") or f"sqlite:///{SEED_DIR / 'theta.db'}"
    # Hosted Postgres URLs often start with postgres://; SQLAlchemy needs a driver name.
    url = url.replace("postgres://", "postgresql+psycopg://", 1).replace("postgresql://", "postgresql+psycopg://", 1)
    eng = sa.create_engine(url)
    _init(eng)
    return eng


def _seed_frame(table):
    path = SEED_DIR / f"{table}.csv"
    df = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=list(SCHEMA[table]))
    return df.reindex(columns=list(SCHEMA[table]))


def _init(eng):
    """Create missing tables and fill new ones from the seed CSVs (runs once per process)."""
    meta = sa.MetaData()
    for name, cols in SCHEMA.items():
        sa.Table(name, meta, *(sa.Column(col, typ) for col, typ in cols.items()))
    new = [name for name in SCHEMA if not sa.inspect(eng).has_table(name)]
    meta.create_all(eng)
    with eng.begin() as conn:
        for name in new:
            _write(conn, name, _seed_frame(name))


def load(table):
    with engine().connect() as conn:
        return pd.read_sql_table(table, conn)


@contextmanager
def transaction():
    """Yield save(table, df); every save inside the block commits or rolls back together."""
    with engine().begin() as conn:
        yield lambda table, df: _write(conn, table, df)


def _write(conn, table, df):
    # DELETE (not DROP) keeps the schema and, on SQLite, opens the transaction
    conn.execute(sa.text(f'DELETE FROM "{table}"'))
    df.reindex(columns=list(SCHEMA[table])).to_sql(table, conn, if_exists="append", index=False)


def save(table, df):
    with transaction() as write:
        write(table, df)


def reset():
    """Replace every table with its seed CSV, in one transaction."""
    with transaction() as write:
        for table in SCHEMA:
            write(table, _seed_frame(table))


def export_zip():
    """Every table as <table>.csv inside one ZIP file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for table in SCHEMA:
            z.writestr(f"{table}.csv", load(table).to_csv(index=False))
    return buf.getvalue()


def import_frames(frames):
    """Replace the given tables ({table: DataFrame}) in one transaction, after checking columns."""
    for table, df in frames.items():
        if table not in SCHEMA:
            raise ValueError(f"{table}.csv does not match a table ({', '.join(SCHEMA)})")
        missing = [c for c in SCHEMA[table] if c not in df.columns]
        if missing:
            raise ValueError(f"{table}.csv is missing columns: {', '.join(missing)}")
    with transaction() as write:
        for table, df in frames.items():
            write(table, df)


def read_upload(name, data):
    """{table: DataFrame} from an uploaded <table>.csv or a ZIP of them (as export_zip writes)."""
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            return {Path(n).stem: pd.read_csv(z.open(n)) for n in z.namelist() if n.lower().endswith(".csv")}
    return {Path(name).stem: pd.read_csv(io.BytesIO(data))}
