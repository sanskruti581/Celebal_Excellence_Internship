# E-Commerce Order Analytics System

## Overview

This project was developed as part of my Data Engineering internship assignment. The goal was to create a complete data pipeline starting from generating raw e-commerce data to performing business analysis using SQL.

The project includes generating realistic datasets with some intentional errors, cleaning the data using Python (Pandas), loading it into a SQLite database, and writing SQL queries to generate useful business reports.

---

## Technologies Used

* Python
* Pandas
* Faker
* SQLite
* SQL
* Jupyter Notebook

---

## Project Workflow

### 1. Dataset Generation

Generated four datasets using Python and the Faker library.

* Customers
* Products
* Orders
* Order Items

To make the data more realistic, I intentionally added issues such as:

* Missing values
* Duplicate records
* Invalid dates
* Incorrect foreign keys

These datasets were exported as CSV files.

---

### 2. Data Cleaning

The generated datasets were cleaned using Pandas.

The cleaning process included:

* Removing duplicate records
* Handling missing values
* Fixing incorrect data types
* Standardizing date formats
* Validating relationships between tables

After cleaning, new CSV files were created for loading into the database.

---

### 3. Database Creation

A SQLite database was created with separate tables for:

* Customers
* Products
* Orders
* Order Items

The cleaned CSV files were imported into these tables.

---

### 4. SQL Analysis

SQL queries were written to answer business-related questions such as:

* Total revenue
* Revenue by customer
* Revenue by product category
* Monthly sales
* Top-selling products
* Average order value
* Orders placed by each customer

---

## Project Structure

```
Ecommerce_Order_Analytics/
│
├── data/
│   ├── raw/
│   └── cleaned/
│
├── notebooks/
│
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── load_database.py
│   └── reports.py
│
├── sql/
│   └── analytics.sql
│
├── ecommerce.db
│
└── README.md
```

---

## How to Run

1. Generate the datasets.

```
python generate_data.py
```

2. Clean the generated datasets.

```
python clean_data.py
```

3. Load the cleaned data into SQLite.

```
python load_database.py
```

4. Run the SQL queries from the `sql` folder or use the reporting script.

---

## Sample Reports

The project can generate reports such as:

* Total Revenue
* Revenue by Category
* Monthly Sales
* Top 10 Products
* Average Order Value
* Customer Purchase Summary

---

## What I Learned

While working on this project, I learned how to:

* Generate realistic datasets using Python
* Clean messy data using Pandas
* Work with relational databases
* Write SQL queries for business analysis
* Connect Python with SQLite
* Organize a small data engineering project from start to finish

---

## Future Improvements

Some improvements that can be added later are:

* Interactive dashboard using Power BI or Streamlit
* Support for PostgreSQL or MySQL
* Automated ETL pipeline
* Data validation before loading
* Scheduled report generation

---

## Author

**Sanskruti Shinde**

B.Tech Computer Engineering Student

Data Engineering Intern
