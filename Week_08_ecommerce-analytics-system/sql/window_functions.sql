-- ============================================================
-- window_functions.sql
-- Step 5: SQL Analytics - Window Functions & CTEs
-- ============================================================

-- ------------------------------------------------------------
-- Query 7: Running total of revenue per region, ordered by date
-- ------------------------------------------------------------
WITH daily_rev AS (
    SELECT 
        o.region_code,
        DATE(o.order_date) AS order_date,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.region_code, DATE(o.order_date)
)
SELECT 
    region_code,
    order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code 
        ORDER BY order_date
    ), 2) AS running_total
FROM daily_rev
ORDER BY region_code, order_date;;

-- ------------------------------------------------------------
-- Query 8: Rank products by total revenue within each category (DENSE_RANK)
-- ------------------------------------------------------------
WITH product_rev AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (
        PARTITION BY category 
        ORDER BY total_revenue DESC
    ) AS rank_in_category
FROM product_rev
ORDER BY category, rank_in_category;;

-- ------------------------------------------------------------
-- Query 9: Days between consecutive orders per customer (LAG), flag "At Risk"
-- ------------------------------------------------------------
WITH customer_orders AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date
        ) AS previous_order_date
    FROM orders
    WHERE customer_id IS NOT NULL AND customer_id != ''
),
gaps AS (
    SELECT 
        customer_id,
        order_date,
        previous_order_date,
        CASE 
            WHEN previous_order_date IS NOT NULL 
            THEN JULIANDAY(order_date) - JULIANDAY(previous_order_date)
            ELSE NULL 
        END AS days_gap
    FROM customer_orders
),
avg_gaps AS (
    SELECT customer_id, AVG(days_gap) AS avg_gap
    FROM gaps
    WHERE days_gap IS NOT NULL
    GROUP BY customer_id
)
SELECT 
    g.customer_id,
    g.order_date,
    g.previous_order_date,
    ROUND(g.days_gap, 1) AS days_gap,
    CASE WHEN a.avg_gap > 30 THEN 'At Risk' ELSE 'Active' END AS customer_status
FROM gaps g
JOIN avg_gaps a ON g.customer_id = a.customer_id
ORDER BY g.customer_id, g.order_date;;

-- ------------------------------------------------------------
-- Query 10: CTE with Multiple Levels - customer categorization by monthly revenue
-- ------------------------------------------------------------
WITH monthly_customer_revenue AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS monthly_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL AND o.customer_id != ''
    GROUP BY o.customer_id, order_month
),
categorized AS (
    SELECT 
        customer_id,
        order_month,
        monthly_revenue,
        CASE 
            WHEN monthly_revenue > 10000 THEN 'High'
            WHEN monthly_revenue BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS revenue_category
    FROM monthly_customer_revenue
)
SELECT 
    order_month,
    revenue_category,
    COUNT(DISTINCT customer_id) AS customer_count
FROM categorized
GROUP BY order_month, revenue_category
ORDER BY order_month, revenue_category;;

-- ------------------------------------------------------------
-- Query 11: NTILE for Segmentation - quartiles based on lifetime value
-- ------------------------------------------------------------
WITH customer_ltv AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL AND o.customer_id != ''
    GROUP BY o.customer_id
)
SELECT 
    customer_id,
    ROUND(total_value, 2) AS total_value,
    NTILE(4) OVER (ORDER BY total_value DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_value DESC)
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
    END AS quartile_label
FROM customer_ltv
ORDER BY total_value DESC;;

-- ------------------------------------------------------------
-- Query 12: Year-over-Year Comparison
-- ------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT 
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY year, month
)
SELECT 
    curr.year,
    curr.month,
    ROUND(curr.revenue, 2) AS revenue,
    ROUND(prev.revenue, 2) AS prev_year_revenue,
    CASE 
        WHEN prev.revenue IS NOT NULL AND prev.revenue != 0
        THEN ROUND((curr.revenue - prev.revenue) * 100.0 / prev.revenue, 2)
        ELSE NULL
    END AS yoy_growth_percent
FROM monthly_revenue curr
LEFT JOIN monthly_revenue prev 
    ON curr.year = prev.year + 1 AND curr.month = prev.month
ORDER BY curr.year, curr.month;;

-- ------------------------------------------------------------
-- Query 13: First/Last Value Analysis - first vs most recent purchased category
-- ------------------------------------------------------------
WITH customer_category_orders AS (
    SELECT 
        o.customer_id,
        o.order_date,
        p.category,
        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date ASC
        ) AS first_category,
        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date DESC
        ) AS last_category
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.customer_id IS NOT NULL AND o.customer_id != ''
)
SELECT DISTINCT
    customer_id,
    first_category,
    last_category,
    CASE WHEN first_category != last_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM customer_category_orders
ORDER BY customer_id;;

-- ------------------------------------------------------------
-- Query 14: Cumulative Distribution - % of revenue from top N% of customers
-- ------------------------------------------------------------
WITH customer_revenue AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL AND o.customer_id != ''
    GROUP BY o.customer_id
),
ranked AS (
    SELECT 
        customer_id,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
        SUM(revenue) OVER () AS total_revenue
    FROM customer_revenue
)
SELECT 
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND(cumulative_revenue * 100.0 / total_revenue, 2) AS cumulative_percent
FROM ranked
ORDER BY revenue DESC;;

