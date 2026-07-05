/*=========================================================
Project: SQL Advanced Analytics on Superstore Dataset
Author: Sanskruti Dnyaneshwar Shinde
=========================================================*/

/*=========================================================
STEP 1 : DATABASE SETUP
=========================================================*/

-- Select Database
USE superstore_db;

-----------------------------------------------------------
-- Create Customers Table
-----------------------------------------------------------

CREATE TABLE customers AS
SELECT DISTINCT
    `Customer ID`,
    `Customer Name`,
    Segment,
    Country,
    City,
    State,
    `Postal Code`,
    Region
FROM superstore_raw;


-----------------------------------------------------------
-- Create Orders Table
-----------------------------------------------------------

CREATE TABLE orders AS
SELECT DISTINCT
    `Order ID`,
    `Order Date`,
    `Ship Date`,
    `Ship Mode`,
    `Customer ID`,
    Sales,
    Quantity,
    Discount,
    Profit
FROM superstore_raw;


-----------------------------------------------------------
-- Create Products Table
-----------------------------------------------------------

CREATE TABLE products AS
SELECT DISTINCT
    `Product ID`,
    Category,
    `Sub-Category`,
    `Product Name`
FROM superstore_raw;


-----------------------------------------------------------
-- Verify Tables
-----------------------------------------------------------

SHOW TABLES;



/*=========================================================
STEP 2 : REQUIRED SQL QUERIES
=========================================================*/


-----------------------------------------------------------
-- Query 1
-- Find all orders where Sales are greater than
-- the average Sales.
-- (Subquery)
-----------------------------------------------------------

SELECT *
FROM orders
WHERE Sales >
(
    SELECT AVG(Sales)
    FROM orders
);



-----------------------------------------------------------
-- Query 2
-- Find the highest sales order for each customer.
-- (Subquery)
-----------------------------------------------------------

SELECT o.*
FROM orders o
JOIN
(
    SELECT
        `Customer ID`,
        MAX(Sales) AS Highest_Sales
    FROM orders
    GROUP BY `Customer ID`
) max_sales
ON o.`Customer ID` = max_sales.`Customer ID`
AND o.Sales = max_sales.Highest_Sales;



-----------------------------------------------------------
-- Query 3
-- Calculate total sales for each customer.
-- (CTE)
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer ID`,
    c.`Customer Name`,
    cs.Total_Sales
FROM CustomerSales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`
ORDER BY cs.Total_Sales DESC;



-----------------------------------------------------------
-- Query 4
-- Find customers whose total sales are above average.
-- (CTE + Subquery)
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer ID`,
    c.`Customer Name`,
    cs.Total_Sales
FROM CustomerSales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`
WHERE cs.Total_Sales >
(
    SELECT AVG(Total_Sales)
    FROM CustomerSales
)
ORDER BY cs.Total_Sales DESC;



-----------------------------------------------------------
-- Query 5
-- Rank all customers based on total sales.
-- (Window Function)
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer ID`,
    c.`Customer Name`,
    cs.Total_Sales,
    RANK() OVER
    (
        ORDER BY cs.Total_Sales DESC
    ) AS Customer_Rank
FROM CustomerSales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`
ORDER BY Customer_Rank;



-----------------------------------------------------------
-- Query 6
-- Assign row numbers to each order within a customer.
-- (Window Function + PARTITION BY)
-----------------------------------------------------------

SELECT
    `Customer ID`,
    `Order ID`,
    Sales,

    ROW_NUMBER() OVER
    (
        PARTITION BY `Customer ID`
        ORDER BY Sales DESC
    ) AS Order_Row_Number

FROM orders;



-----------------------------------------------------------
-- Query 7
-- Display Top 3 customers based on total sales.
-- (Window Function)
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
),

RankedCustomers AS
(
    SELECT
        `Customer ID`,
        Total_Sales,

        DENSE_RANK() OVER
        (
            ORDER BY Total_Sales DESC
        ) AS Customer_Rank

    FROM CustomerSales
)

SELECT
    c.`Customer ID`,
    c.`Customer Name`,
    rc.Total_Sales,
    rc.Customer_Rank

FROM RankedCustomers rc
JOIN customers c
ON rc.`Customer ID` = c.`Customer ID`

WHERE rc.Customer_Rank <= 3
ORDER BY rc.Customer_Rank;



/*=========================================================
STEP 3 : FINAL COMBINED QUERY
JOIN + CTE + WINDOW FUNCTION
=========================================================*/

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer Name`,
    cs.Total_Sales,

    RANK() OVER
    (
        ORDER BY cs.Total_Sales DESC
    ) AS Customer_Rank

FROM CustomerSales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`
ORDER BY Customer_Rank;



/*=========================================================
MINI PROJECT : CUSTOMER SALES INSIGHTS
=========================================================*/


-----------------------------------------------------------
-- Question 1
-- Who are the Top 5 Customers?
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer Name`,
    cs.Total_Sales
FROM CustomerSales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`
ORDER BY cs.Total_Sales DESC
LIMIT 5;



-----------------------------------------------------------
-- Question 2
-- Who are the Bottom 5 Customers?
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer Name`,
    cs.Total_Sales
FROM CustomerSales cs
JOIN customers c
ON cs.`Customer ID` = c.`Customer ID`
ORDER BY cs.Total_Sales ASC
LIMIT 5;



-----------------------------------------------------------
-- Question 3
-- Which customers made only one order?
-----------------------------------------------------------

SELECT
    c.`Customer Name`,
    COUNT(o.`Order ID`) AS Total_Orders

FROM customers c
JOIN orders o

ON c.`Customer ID` = o.`Customer ID`

GROUP BY
    c.`Customer ID`,
    c.`Customer Name`

HAVING COUNT(o.`Order ID`) = 1;



-----------------------------------------------------------
-- Question 4
-- Which customers have above-average sales?
-----------------------------------------------------------

WITH CustomerSales AS
(
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)

SELECT
    c.`Customer Name`,
    cs.Total_Sales

FROM CustomerSales cs
JOIN customers c

ON cs.`Customer ID` = c.`Customer ID`

WHERE cs.Total_Sales >
(
    SELECT AVG(Total_Sales)
    FROM CustomerSales
)

ORDER BY cs.Total_Sales DESC;



-----------------------------------------------------------
-- Question 5
-- What is the highest order value per customer?
-----------------------------------------------------------

SELECT

    c.`Customer Name`,

    MAX(o.Sales) AS Highest_Order_Value

FROM customers c
JOIN orders o

ON c.`Customer ID` = o.`Customer ID`

GROUP BY

    c.`Customer ID`,
    c.`Customer Name`

ORDER BY Highest_Order_Value DESC;



/*=========================================================
END OF PROJECT
=========================================================*/