# Spark Assignment — Week 5: Data Cleaning, Transformation & Aggregation

## Objective
Understand Spark fundamentals and perform data cleaning, transformation, and aggregation using DataFrames.

## Dataset
A Superstore sales transactions dataset (`dataset.csv`) containing ~9,800 records and 18 columns, covering customer, product, shipping, and sales information.

## What Was Done
- **Spark Fundamentals:** Explained the limitations of MapReduce (disk-based, high latency, poor fit for iterative jobs) and the advantages of Spark (in-memory computation, fault tolerance via RDD lineage, unified SQL/Streaming/ML support).
- **Dataset Exploration:** Loaded the CSV into a Spark DataFrame, reviewed schema, row/column counts, summary statistics, and checked for missing/duplicate values.
- **Data Cleaning:**
  - Removed duplicate rows using `dropDuplicates()`.
  - Checked and handled missing values, filling nulls in the `Sales` column with `0`.
  - Renamed key columns (`Customer ID` → `user_id`, `Order Date` → `transaction_date`, `Category` → `product_category`, `Sales` → `sale_amount`) to align with assignment requirements.
  - Converted `transaction_date` from string to a proper date type.
  - Demonstrated DataFrame immutability — filtering creates a new DataFrame while the original remains unchanged.
- **Filtering & Aggregation:**
  - Filtered records by region (`West`) and product category (`Technology`).
  - Calculated average sales by product category for the West region.
  - Counted records by city, filtering to cities with more than 100 records.
  - Used `.agg()` to compute minimum, maximum, and average sales in a single operation.
  - Calculated total sales by region and by product category, and record counts by customer segment.
- **Transformation & Pipeline:**
  - Added derived columns (`age`, `subscription`, `email`, `status`) to demonstrate schema modification.
  - Filtered records where age is between 18–30 (inclusive) and subscription is `Premium`.
  - Filled null `status` values with `'Unknown'`.
  - Cast `transaction_date` to a `TimestampType` column named `event_time` for time-based analysis.
  - Removed records with null/empty identifying fields.
  - Built a final end-to-end pipeline: deduplicate → fill nulls → group by `product_category` → aggregate total and average sales.
  - Exported final pipeline results to `output/results.csv`.

## What Was Observed
- The dataset had no duplicate rows at the row level (9,800 total = 9,800 distinct), so `dropDuplicates()` served as a validation step rather than visibly reducing the dataset.
- Handling nulls before aggregation is essential — `sum()`/`avg()` silently ignore nulls by default, which can distort results if not addressed first.
- `groupBy()` operations trigger a **shuffle** (wide transformation), since Spark must move matching keys to the same partition before aggregating — this is the most performance-sensitive step in the pipeline.
- Spark's immutable DataFrame API makes chained cleaning/transformation steps predictable: each operation returns a new DataFrame rather than modifying data in place.

## Folder Structure
```
spark-assignment/
│── data/
│   └── dataset.csv
│── notebook/
│   └── spark_basics.ipynb
│── output/
│   └── results.csv
│── README.md
```

## How to Run
1. Ensure `data/dataset.csv` contains the Superstore dataset (or your own dataset with equivalent columns).
2. Open `notebook/spark_basics.ipynb` in Jupyter or Google Colab with PySpark installed (`!pip install pyspark`).
3. Run all cells top to bottom.
4. Final aggregated results are saved to `output/results.csv`.
