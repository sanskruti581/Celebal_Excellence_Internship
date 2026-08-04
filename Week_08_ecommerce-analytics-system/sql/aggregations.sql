-- ============================================================
-- aggregations.sql
-- Step 4: SQL Analytics - Joins & Aggregations
-- ============================================================

-- ------------------------------------------------------------
-- Query 0: Average Order Value (AOV) by customer segment
-- (customer_type: REGULAR / PREMIUM / VIP)
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
)
SELECT
    c.customer_type,
    COUNT(ov.order_id) AS total_orders,
    ROUND(AVG(ov.order_value), 2) AS avg_order_value
FROM order_value ov
JOIN customers c ON ov.customer_id = c.customer_id
GROUP BY c.customer_type
ORDER BY avg_order_value DESC;

-- ------------------------------------------------------------
-- Query 1: Total revenue per category
-- ------------------------------------------------------------
SELECT 
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;;

-- ------------------------------------------------------------
-- Query 2: Top 10 customers by total order value
-- ------------------------------------------------------------
SELECT 
    o.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;;

-- ------------------------------------------------------------
-- Query 3: Month-wise order count for the last 12 months
-- ------------------------------------------------------------
SELECT 
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE order_date >= date('now', '-12 months')
GROUP BY order_month
ORDER BY order_month;;

-- ------------------------------------------------------------
-- Query 4: Customers who placed orders but never had any item delivered
-- ------------------------------------------------------------
SELECT DISTINCT c.customer_id, c.customer_name
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id NOT IN (
    SELECT customer_id FROM orders WHERE status = 'DELIVERED' AND customer_id IS NOT NULL
);;

-- ------------------------------------------------------------
-- Query 5: Products that were ordered but had more returns than purchases
-- ------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS purchased_qty,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS returned_qty
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name
HAVING returned_qty > purchased_qty;;

-- ------------------------------------------------------------
-- Query 6: Return rate (returned items / total items) per category
-- ------------------------------------------------------------
SELECT 
    p.category,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS returned_qty,
    SUM(ABS(oi.quantity)) AS total_qty,
    ROUND(
        SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) * 100.0 / SUM(ABS(oi.quantity)), 
        2
    ) AS return_rate_percent
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_percent DESC;;

