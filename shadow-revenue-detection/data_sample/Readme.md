
# Data Sample

Raw input datasets used by the Bronze ingestion notebook.

**Files:**
- `orders.csv` — order-level transactions (20,400 rows, includes 400 duplicate order_ids)
- `payments.csv` — payment records (18,600 rows, includes 600 orphan payments)
- `products.csv` — product catalog, SCD Type 2 (200 rows)
- `customers.csv` — customer master (2,000 rows)

These are the exact raw files ingested in `01_bronze_ingestion` — no cleaning applied. See the [root README](../README.md) for the known data-quality issues in this dataset and how the "good" pipeline handles them.
