import argparse
import os
import sqlite3
import sys

from tabulate import tabulate

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

# RFM scoring rolled up into a segment-level headcount, since a CLI report
# should read as a summary, not a dump of every customer's raw R/F/M score.
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

REPORTS = {
    "revenue": (REVENUE_QUERY, None),
    "top_customers": (TOP_CUSTOMERS_QUERY, "limit"),
    "retention": (RETENTION_QUERY, None),
    "segmentation": (SEGMENTATION_QUERY, None),
}


def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: database file '{DB_PATH}' not found. Run load_to_sqlite.py first.")
        sys.exit(1)
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"Error: could not connect to '{DB_PATH}': {e}")
        sys.exit(1)


def run_report(report_name, limit):
    query, needs_param = REPORTS[report_name]
    conn = get_connection()
    try:
        cur = conn.cursor()
        if needs_param == "limit":
            cur.execute(query, (limit,))
        else:
            cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
    except sqlite3.Error as e:
        print(f"Error running '{report_name}' report: {e}")
        sys.exit(1)
    finally:
        conn.close()

    print(f"\n{report_name.upper()} REPORT")
    print("=" * 50)
    if not rows:
        print("No data found for this report.")
    else:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    print()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="E-Commerce Report CLI Tool")
    parser.add_argument(
        "--report",
        choices=list(REPORTS.keys()),
        required=True,
        help="Which report to generate",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Row limit for reports that support it (default: 10, used by top_customers)",
    )
    args = parser.parse_args(argv)

    if args.limit <= 0:
        parser.error("--limit must be a positive integer")

    return args


if __name__ == "__main__":
    args = parse_args()
    run_report(args.report, args.limit)
