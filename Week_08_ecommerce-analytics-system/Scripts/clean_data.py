import os
import re
import pandas as pd

INPUT_DIR = "data/Raw"
OUTPUT_DIR = "data/cleaned"
os.makedirs(OUTPUT_DIR, exist_ok=True)

issues_report = []

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def dedupe_customers(df):
    before = len(df)
    df = df.drop_duplicates(subset=["customer_id"], keep="first").reset_index(drop=True)
    removed = before - len(df)
    issues_report.append(f"dedupe_customers: removed {removed} duplicate customer rows")
    print(f"dedupe_customers() done. Removed {removed} duplicate rows.")
    return df


def dedupe_orders(df):
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first").reset_index(drop=True)
    removed = before - len(df)
    issues_report.append(f"dedupe_orders: removed {removed} duplicate order rows")
    print(f"dedupe_orders() done. Removed {removed} duplicate rows.")
    return df


def clean_orders():
    df = pd.read_csv(f"{INPUT_DIR}/orders.csv", dtype={"customer_id": "object"})

    df = dedupe_orders(df)

    # order_date comes in as either "YYYY-MM-DD HH:MM:SS" or the bad "DD-MM-YYYY" format.
    # Try the correct format first, fall back to the bad one and reformat it.
    good = pd.to_datetime(df["order_date"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    bad = pd.to_datetime(df["order_date"], format="%d-%m-%Y", errors="coerce")
    fixed_count = int(good.isna().sum() - bad[good.isna()].isna().sum())

    df["order_date"] = good.fillna(bad)
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # NULL / empty customer_id -> pandas NaN, kept (not dropped) so it's still
    # visible as a data-quality issue downstream instead of silently disappearing.
    df["customer_id"] = df["customer_id"].replace(["", "NULL"], pd.NA)
    null_customer_count = int(df["customer_id"].isna().sum())

    df.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)

    issues_report.append(f"clean_orders: fixed {fixed_count} bad date formats")
    issues_report.append(f"clean_orders: found {null_customer_count} orders with missing customer_id")
    print(f"clean_orders() done. Fixed {fixed_count} dates, {null_customer_count} missing customer_ids.")


def clean_products():
    df = pd.read_csv(f"{INPUT_DIR}/products.csv")

    original_names = df["product_name"].copy()
    df["product_name"] = df["product_name"].str.strip().str.split().str.join(" ").str.title()
    changed_count = int((df["product_name"] != original_names).sum())

    df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)

    issues_report.append(f"clean_products: normalized {changed_count} product names")
    print(f"clean_products() done. Normalized {changed_count} product names.")


def validate_emails():
    df = pd.read_csv(f"{INPUT_DIR}/customers.csv", dtype={"email": "object"})
    invalid_mask = ~df["email"].fillna("").str.match(EMAIL_PATTERN)
    invalid_customer_ids = df.loc[invalid_mask, "customer_id"].tolist()

    issues_report.append(f"validate_emails: found {len(invalid_customer_ids)} invalid emails")
    print(f"validate_emails() done. Found {len(invalid_customer_ids)} invalid emails.")
    return invalid_customer_ids


def check_referential_integrity():
    orders_df = pd.read_csv(f"{INPUT_DIR}/orders.csv")
    items_df = pd.read_csv(f"{INPUT_DIR}/order_items.csv")

    order_ids = set(orders_df["order_id"])
    orphan_mask = ~items_df["order_id"].isin(order_ids)
    orphan_items = items_df.loc[orphan_mask, "item_id"].tolist()

    issues_report.append(f"check_referential_integrity: found {len(orphan_items)} orphan order_items")
    print(f"check_referential_integrity() done. Found {len(orphan_items)} orphan order_items.")
    return orphan_items


def clean_customers():
    df = pd.read_csv(f"{INPUT_DIR}/customers.csv", dtype={"customer_id": "object", "email": "object"})
    df = dedupe_customers(df)
    df.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)


def copy_order_items():
    # order_items has no duplicate/format issues by design (item_id is unique per
    # row from generation), so it just passes through unchanged.
    df = pd.read_csv(f"{INPUT_DIR}/order_items.csv")
    df.to_csv(f"{OUTPUT_DIR}/order_items.csv", index=False)
    print("Copied order_items.csv to cleaned folder (no changes needed).")


def write_report():
    with open(f"{OUTPUT_DIR}/cleaning_report.txt", "w", encoding="utf-8") as f:
        f.write("DATA CLEANING REPORT\n")
        f.write("=" * 40 + "\n")
        for line in issues_report:
            f.write(line + "\n")
    print(f"Report written to {OUTPUT_DIR}/cleaning_report.txt")


if __name__ == "__main__":
    clean_orders()
    clean_products()
    clean_customers()
    validate_emails()
    check_referential_integrity()
    copy_order_items()
    write_report()
