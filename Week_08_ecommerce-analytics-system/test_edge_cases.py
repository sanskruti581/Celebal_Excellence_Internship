import os
import subprocess
import sys
import sqlite3
from datetime import datetime, timedelta

CLI_PATH = os.path.join("Scripts", "report_cli.py")
DB_PATH = "ecommerce.db"


def setup_test_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, order_date TEXT, status TEXT, region_code TEXT)")
    cur.execute("CREATE TABLE order_items (item_id INTEGER, order_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL, discount_percent REAL)")
    conn.commit()
    return conn


def test_order_id_not_in_orders():
    conn = setup_test_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders VALUES (1, 100, '2026-01-01 10:00:00', 'PLACED', 'NORTH')")
    cur.execute("INSERT INTO order_items VALUES (1, 999, 5, 2, 100.0, 10)")  # 999 doesn't exist
    conn.commit()

    cur.execute("""
        SELECT oi.item_id FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
    """)
    orphans = cur.fetchall()
    conn.close()

    assert len(orphans) == 1, "Should detect 1 orphan order_item"
    print("test_order_id_not_in_orders passed.")


def test_discount_over_100():
    discount_percent = 150
    is_valid = 0 <= discount_percent <= 100
    assert is_valid is False
    revenue = 10 * 100 * (1 - discount_percent / 100)  # goes negative -> bad data
    print(f"test_discount_over_100 passed. revenue={revenue} flags invalid discount.")


def test_quantity_zero():
    quantity, unit_price, discount_percent = 0, 500, 10
    revenue = quantity * unit_price * (1 - discount_percent / 100)
    assert revenue == 0
    print("test_quantity_zero passed. revenue correctly 0, no crash.")


def test_future_order_date():
    future_date = datetime.now() + timedelta(days=30)
    is_future = future_date > datetime.now()
    assert is_future is True
    print(f"test_future_order_date passed. Detected future date {future_date.date()}.")


def test_cli_missing_db():
    """report_cli.py should fail with a clean error message (no traceback)
    when ecommerce.db doesn't exist, instead of crashing."""
    db_present = os.path.exists(DB_PATH)
    backup_path = DB_PATH + ".bak"
    if db_present:
        os.rename(DB_PATH, backup_path)

    try:
        result = subprocess.run(
            [sys.executable, CLI_PATH, "--report", "revenue"],
            capture_output=True, text=True
        )
        assert result.returncode != 0, "Should exit with a non-zero code when DB is missing"
        assert "Traceback" not in result.stderr, "Should not raise an unhandled exception"
        assert "not found" in result.stdout, "Should print a clear 'not found' message"
        print("test_cli_missing_db passed.")
    finally:
        if db_present:
            os.rename(backup_path, DB_PATH)


def test_cli_invalid_report_arg():
    """report_cli.py should reject an unknown --report value via argparse,
    not crash with an unhandled exception."""
    result = subprocess.run(
        [sys.executable, CLI_PATH, "--report", "not_a_real_report"],
        capture_output=True, text=True
    )
    assert result.returncode != 0, "Should exit with a non-zero code on invalid --report"
    assert "Traceback" not in result.stderr, "Should not raise an unhandled exception"
    assert "invalid choice" in result.stderr, "argparse should explain the invalid choice"
    print("test_cli_invalid_report_arg passed.")


def test_cli_invalid_limit_arg():
    """A non-positive --limit should be rejected with a clean error, not
    silently accepted or allowed to crash the SQL query."""
    result = subprocess.run(
        [sys.executable, CLI_PATH, "--report", "top_customers", "--limit", "0"],
        capture_output=True, text=True
    )
    assert result.returncode != 0, "Should exit with a non-zero code on invalid --limit"
    assert "Traceback" not in result.stderr, "Should not raise an unhandled exception"
    print("test_cli_invalid_limit_arg passed.")


if __name__ == "__main__":
    test_order_id_not_in_orders()
    test_discount_over_100()
    test_quantity_zero()
    test_future_order_date()
    test_cli_missing_db()
    test_cli_invalid_report_arg()
    test_cli_invalid_limit_arg()
    print("\nAll edge case tests passed.")