-- ============================================================
-- segmentation.sql
-- Step 7: Customer Segmentation (Frequency, Spend Tier, RFM)
-- ============================================================

-- ------------------------------------------------------------
-- Query 17: Segment customers by purchase frequency
-- one-time (1 order), occasional (2-4 orders), loyal (5+ orders)
-- ------------------------------------------------------------
WITH order_counts AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT
    customer_id,
    order_count,
    CASE
        WHEN order_count = 1 THEN 'One-time'
        WHEN order_count BETWEEN 2 AND 4 THEN 'Occasional'
        ELSE 'Loyal'
    END AS frequency_segment
FROM order_counts
ORDER BY order_count DESC;


-- ------------------------------------------------------------
-- Query 18: Segment customers by spend tier
-- low / medium / high, based on total lifetime revenue
-- ------------------------------------------------------------
WITH customer_spend AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_spend
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    ROUND(total_spend, 2) AS total_spend,
    CASE
        WHEN total_spend < 5000 THEN 'Low'
        WHEN total_spend BETWEEN 5000 AND 20000 THEN 'Medium'
        ELSE 'High'
    END AS spend_tier
FROM customer_spend
ORDER BY total_spend DESC;


-- ------------------------------------------------------------
-- Query 19: Average Order Value (AOV) by customer segment
-- (combines frequency segment with AOV)
-- ------------------------------------------------------------
WITH order_value AS (
    SELECT
        o.order_id,
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.order_id, o.customer_id
),
order_counts AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
segmented AS (
    SELECT
        ov.customer_id,
        ov.order_value,
        CASE
            WHEN oc.order_count = 1 THEN 'One-time'
            WHEN oc.order_count BETWEEN 2 AND 4 THEN 'Occasional'
            ELSE 'Loyal'
        END AS frequency_segment
    FROM order_value ov
    JOIN order_counts oc ON ov.customer_id = oc.customer_id
)
SELECT
    frequency_segment,
    COUNT(*) AS num_orders,
    ROUND(AVG(order_value), 2) AS avg_order_value
FROM segmented
GROUP BY frequency_segment
ORDER BY avg_order_value DESC;


-- ------------------------------------------------------------
-- Query 20: RFM Analysis (Recency, Frequency, Monetary)
-- Recency  = days since last order (lower = better -> higher score)
-- Frequency = number of orders (higher = better)
-- Monetary  = total spend (higher = better)
-- Each dimension is scored 1-5 using NTILE, then combined into
-- an rfm_segment label.
-- ------------------------------------------------------------
WITH last_order AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
monetary AS (
    SELECT
        o.customer_id,
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
        recency_days,
        frequency,
        ROUND(monetary, 2) AS monetary,
        -- lower recency_days = more recent = better -> score 5 for smallest recency
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
    FROM rfm_base
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 12 THEN 'Champion'
        WHEN (r_score + f_score + m_score) >= 9  THEN 'Loyal'
        WHEN (r_score + f_score + m_score) >= 6  THEN 'At Risk'
        ELSE 'Lost'
    END AS rfm_segment
FROM rfm_scored
ORDER BY rfm_total DESC;


-- ------------------------------------------------------------
-- Query 21: Churned vs Repeat customers
-- churned = last order more than 60 days before the most recent
-- order date in the whole dataset; repeat = placed 2+ orders
-- ------------------------------------------------------------
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        MAX(order_date) AS last_order_date
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
dataset_max_date AS (
    SELECT MAX(order_date) AS max_date FROM orders
)
SELECT
    co.customer_id,
    co.order_count,
    co.last_order_date,
    CAST(JULIANDAY(d.max_date) - JULIANDAY(co.last_order_date) AS INTEGER) AS days_since_last_order,
    CASE
        WHEN JULIANDAY(d.max_date) - JULIANDAY(co.last_order_date) > 60 THEN 'Churned'
        ELSE 'Active'
    END AS churn_status,
    CASE WHEN co.order_count > 1 THEN 'Repeat' ELSE 'One-time' END AS repeat_status
FROM customer_orders co, dataset_max_date d
ORDER BY days_since_last_order DESC;
