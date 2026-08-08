import argparse
import os
import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"

REVENUE_QUERY = """
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;
"""

TOP_CUSTOMERS_QUERY = """
SELECT
    o.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT ?;
"""

RETENTION_QUERY = """
WITH cohorts AS (
    SELECT customer_id, strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_orders AS (
    SELECT o.customer_id, strftime('%Y-%m', o.order_date) AS order_month
    FROM orders o
    WHERE o.customer_id IS NOT NULL AND o.customer_id != ''
),
cohort_activity AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        co.order_month,
        (CAST(strftime('%Y', co.order_month || '-01') AS INTEGER) * 12 + CAST(strftime('%m', co.order_month || '-01') AS INTEGER))
        -
        (CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER) * 12 + CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER))
        AS month_number
    FROM cohorts c
    JOIN customer_orders co ON c.customer_id = co.customer_id
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM cohorts
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.month_number,
    COUNT(DISTINCT ca.customer_id) AS customers_active,
    cs.cohort_size,
    ROUND(COUNT(DISTINCT ca.customer_id) * 100.0 / cs.cohort_size, 2) AS retention_rate_percent
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
WHERE ca.month_number BETWEEN 0 AND 3
GROUP BY ca.cohort_month, ca.month_number
ORDER BY ca.cohort_month, ca.month_number;
"""

SEGMENTATION_QUERY = """
WITH last_order AS (
    SELECT customer_id, MAX(order_date) AS last_order_date, COUNT(DISTINCT order_id) AS frequency
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
monetary AS (
    SELECT o.customer_id,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS monetary
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
rfm_base AS (
    SELECT
        lo.customer_id,
        CAST(JULIANDAY((SELECT MAX(order_date) FROM orders)) - JULIANDAY(lo.last_order_date) AS INTEGER) AS recency_days,
        lo.frequency,
        m.monetary
    FROM last_order lo
    JOIN monetary m ON lo.customer_id = m.customer_id
),
rfm_scored AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
    FROM rfm_base
),
rfm_labeled AS (
    SELECT
        customer_id,
        CASE
            WHEN (r_score + f_score + m_score) >= 12 THEN 'Champion'
            WHEN (r_score + f_score + m_score) >= 9  THEN 'Loyal'
            WHEN (r_score + f_score + m_score) >= 6  THEN 'At Risk'
            ELSE 'Lost'
        END AS rfm_segment
    FROM rfm_scored
)
SELECT rfm_segment, COUNT(*) AS customer_count
FROM rfm_labeled
GROUP BY rfm_segment
ORDER BY customer_count DESC;
"""

LEGACY_REPORTS = {
    "revenue": (REVENUE_QUERY, None),
    "top_customers": (TOP_CUSTOMERS_QUERY, "limit"),
    "retention": (RETENTION_QUERY, None),
    "segmentation": (SEGMENTATION_QUERY, None),
}
PERIOD_REPORTS = {"daily", "weekly", "monthly"}


def parse_date(value):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Use YYYY-MM-DD.")


def format_table(rows, headers):
    if not rows:
        return "No data found."
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(str(value)))

    def fmt_row(vals):
        return " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(vals))

    border = "-+-".join("-" * width for width in widths)
    lines = [fmt_row(headers), border]
    lines.extend(fmt_row(row) for row in rows)
    return "\n".join(lines)


def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: database file '{DB_PATH}' not found. Run load_to_sqlite.py first.")
        sys.exit(1)
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"Error: could not connect to '{DB_PATH}': {e}")
        sys.exit(1)


def execute_query(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if params is None:
            cur.execute(query)
        else:
            cur.execute(query, params)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        return rows, headers
    except sqlite3.Error as e:
        print(f"Error running report: {e}")
        sys.exit(1)
    finally:
        conn.close()


def run_legacy_report(report_name, limit):
    query, needs_param = LEGACY_REPORTS[report_name]
    params = (limit,) if needs_param == "limit" else None
    rows, headers = execute_query(query, params)
    print(f"\n{report_name.upper()} REPORT")
    print("=" * 50)
    print(format_table(rows, headers))
    print()


def period_group_expression(report_name):
    if report_name == "daily":
        return "DATE(order_date)"
    if report_name == "weekly":
        return "strftime('%Y-%W', order_date)"
    return "strftime('%Y-%m', order_date)"


def pct_change(current, previous):
    if previous in (None, 0):
        return None
    return round(((current - previous) / abs(previous)) * 100, 2)


def run_period_report(report_name, start_date, end_date):
    bucket_sql = period_group_expression(report_name)
    query = f"""
        WITH filtered AS (
            SELECT
                o.order_id,
                o.customer_id,
                CAST(o.order_date AS TEXT) AS order_date,
                oi.product_id,
                oi.quantity,
                oi.unit_price,
                oi.discount_percent
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_date BETWEEN ? AND ?
        )
        SELECT
            {bucket_sql} AS period,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_id) AS unique_customers,
            ROUND(COALESCE(SUM(quantity * unit_price * (1 - discount_percent / 100.0)), 0), 2) AS revenue
        FROM filtered
        GROUP BY {bucket_sql}
        ORDER BY period;
    """
    summary_rows, summary_headers = execute_query(query, (start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")))

    product_query = """
        SELECT
            p.product_name,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 3;
    """
    product_rows, product_headers = execute_query(product_query, (start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")))

    delta_days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=delta_days - 1)
    prev_query = f"""
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS unique_customers,
            ROUND(COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 0), 2) AS revenue
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_date BETWEEN ? AND ?;
    """
    prev_rows, _ = execute_query(prev_query, (prev_start.strftime("%Y-%m-%d %H:%M:%S"), prev_end.strftime("%Y-%m-%d %H:%M:%S")))
    prev_total_orders = prev_rows[0][0] if prev_rows else 0
    prev_revenue = prev_rows[0][2] if prev_rows else 0.0

    total_orders = sum(int(row[1]) for row in summary_rows)
    total_revenue = sum(float(row[3]) for row in summary_rows)
    unique_customers = sum(int(row[2]) for row in summary_rows)

    print(f"\n{report_name.upper()} REPORT")
    print(f"Period: {start_date.isoformat()} to {end_date.isoformat()}")
    print("=" * 60)
    print(f"Total orders: {total_orders}")
    print(f"Revenue: {total_revenue:.2f}")
    print(f"Unique customers: {unique_customers}")
    print(f"Previous period revenue: {prev_revenue:.2f}")
    change = pct_change(total_revenue, prev_revenue)
    print(f"Revenue change vs previous period: {change}%" if change is not None else "Revenue change vs previous period: N/A")
    print("\nTop 3 products:")
    print(format_table(product_rows, product_headers))
    print("\nPeriod summary:")
    print(format_table(summary_rows, summary_headers))
    print()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="E-Commerce Report CLI Tool")
    parser.add_argument(
        "--report",
        choices=list(LEGACY_REPORTS.keys()) + list(PERIOD_REPORTS),
        required=True,
        help="Which report to generate",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Row limit for reports that support it (default: 10, used by top_customers)",
    )
    parser.add_argument("--start-date", type=parse_date, help="Start date for daily/weekly/monthly reports (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=parse_date, help="End date for daily/weekly/monthly reports (YYYY-MM-DD)")
    args = parser.parse_args(argv)

    if args.limit <= 0:
        parser.error("--limit must be a positive integer")

    if args.report in PERIOD_REPORTS:
        if args.start_date is None or args.end_date is None:
            parser.error("--start-date and --end-date are required for daily, weekly, and monthly reports")
        if args.start_date > args.end_date:
            parser.error("--start-date must be on or before --end-date")

    return args


if __name__ == "__main__":
    args = parse_args()
    if args.report in PERIOD_REPORTS:
        run_period_report(args.report, args.start_date, args.end_date)
    else:
        run_legacy_report(args.report, args.limit)
