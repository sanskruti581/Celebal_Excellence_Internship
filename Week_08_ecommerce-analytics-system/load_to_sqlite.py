import sqlite3
import pandas as pd

DB_PATH = "ecommerce.db"
CLEANED_DIR = "data/cleaned"
SCHEMA_PATH = "sql/schema.sql"


def apply_schema(conn):
    """Create tables with PK / FK / NOT NULL constraints from schema.sql"""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    print(f"Applied schema from {SCHEMA_PATH}")


def load_data():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    apply_schema(conn)

    customers = pd.read_csv(f"{CLEANED_DIR}/customers.csv")
    products = pd.read_csv(f"{CLEANED_DIR}/products.csv")
    orders = pd.read_csv(f"{CLEANED_DIR}/orders.csv")
    order_items = pd.read_csv(f"{CLEANED_DIR}/order_items.csv")

    # customer_id can be NaN (missing) -> convert to Python None for SQLite NULL
    orders["customer_id"] = orders["customer_id"].where(orders["customer_id"].notna(), None)

    # append=True because schema.sql already created the tables with constraints
    customers.to_sql("customers", conn, if_exists="append", index=False)
    products.to_sql("products", conn, if_exists="append", index=False)
    orders.to_sql("orders", conn, if_exists="append", index=False)
    order_items.to_sql("order_items", conn, if_exists="append", index=False)

    # verify row counts match source CSVs
    cur = conn.cursor()
    for table, df in [("customers", customers), ("products", products),
                       ("orders", orders), ("order_items", order_items)]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        db_count = cur.fetchone()[0]
        status = "OK" if db_count == len(df) else "MISMATCH"
        print(f"  {table}: CSV rows={len(df)}, DB rows={db_count} [{status}]")

    conn.commit()
    conn.close()
    print(f"Loaded all 4 tables into {DB_PATH} using sql/schema.sql")


if __name__ == "__main__":
    load_data()
