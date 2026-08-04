-- ============================================================
-- cohort_analysis.sql
-- Step 6: Cohort & Retention Analysis
-- (Query 16 - frequently bought together - included as bonus
--  basket analysis, related to customer behavior patterns)
-- ============================================================

-- ------------------------------------------------------------
-- Query 15: Cohort Analysis - retention by registration month
-- ------------------------------------------------------------
WITH cohorts AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_orders AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month
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
ORDER BY ca.cohort_month, ca.month_number;;

-- ------------------------------------------------------------
-- Query 16: Self-Join - products frequently bought together
-- ------------------------------------------------------------
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 
    ON oi1.order_id = oi2.order_id 
    AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
ORDER BY times_bought_together DESC
LIMIT 20;;

