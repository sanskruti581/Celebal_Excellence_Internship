
# Notebooks

PySpark notebooks implementing the Medallion architecture (Bronze → Silver → Gold), run in order on Azure Databricks.

**Files:**
1. `01_bronze_ingestion` — reads raw CSVs, writes them as Delta tables (verified counts: 20,400 orders / 18,600 payments / 200 products / 2,000 customers)
2. `02_silver_cleansing` — builds parallel "bad" (raw pass-through) and "good" (deduplicated, type-cast, SCD2-filtered) Silver tables
3. `03_gold_analytics` — joins Silver tables into `fact_revenue_bad` and `fact_revenue_good`, runs anomaly detection (missing payments, orphan payments, price-mismatch tolerance band), exports Gold tables as CSV for Power BI

See the [root README](../README.md) for the reasoning behind the deduplication logic, the Unity Catalog workaround, and the price-tolerance-band decision.
