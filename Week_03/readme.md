# SQL Advanced Analytics on Superstore Dataset

## 📌 Project Overview

This project demonstrates the use of **Advanced SQL** concepts to analyze the Superstore dataset. The analysis focuses on customer sales, order performance, and business insights using SQL techniques such as **Subqueries, Common Table Expressions (CTEs), JOINs, and Window Functions**.

The project was completed using **MySQL Workbench** as part of an SQL analytics assignment.

---

## 🎯 Objective

- Load the Superstore dataset into a staging table (`superstore_raw`).
- Create normalized tables (`customers`, `orders`, and `products`).
- Analyze sales data using advanced SQL queries.
- Apply Subqueries, CTEs, and Window Functions.
- Generate customer sales rankings and business insights.

---

## 🛠️ Technologies Used

- MySQL Workbench 8.x
- SQL
- GitHub

---

## 📂 Dataset

**Dataset:** Sample Superstore Dataset

The dataset contains information related to:

- Customers
- Orders
- Products
- Sales
- Profit
- Discounts
- Shipping Details

---

## 📁 Project Structure

```
SQL-Advanced-Analytics/
│
├── README.md
├── SQL_Advanced_Analytics.sql
├── SQL_Analysis_Report.pdf
└── Sample-Superstore.csv
```

---

## 📋 Project Tasks

### Step 1: Database Setup

- Imported the Superstore dataset into `superstore_raw`
- Created the following tables:
  - `customers`
  - `orders`
  - `products`

---

### Step 2: Advanced SQL Queries

Implemented the following SQL operations:

- Find orders with sales greater than the average sales (Subquery)
- Find the highest sales order for each customer (Subquery)
- Calculate total sales for each customer (CTE)
- Identify customers with above-average total sales (CTE + Subquery)
- Rank customers based on total sales (Window Function)
- Assign row numbers to customer orders (ROW_NUMBER + PARTITION BY)
- Display the top 3 customers based on total sales (DENSE_RANK)

---

### Step 3: Final Combined Query

Created a query using:

- JOIN
- Common Table Expression (CTE)
- Window Function (RANK)

to display:

- Customer Name
- Total Sales
- Customer Rank

---

## 📊 Customer Sales Insights

The project answers the following business questions:

- Top 5 customers by total sales
- Bottom 5 customers by total sales
- Customers who placed only one order
- Customers with above-average sales
- Highest order value for each customer

---

## 📚 SQL Concepts Used

- SELECT
- WHERE
- GROUP BY
- ORDER BY
- Aggregate Functions
- JOIN
- Subqueries
- Common Table Expressions (CTEs)
- ROW_NUMBER()
- RANK()
- DENSE_RANK()

---

## 📈 Key Insights

- Identified the highest-performing customers based on total sales.
- Ranked customers using SQL window functions.
- Determined customers with above-average sales.
- Identified customers who placed only one order.
- Analyzed the highest-value order placed by each customer.

---


## 👩‍💻 Author

**Sanskruti Dnyaneshwar Shinde**


