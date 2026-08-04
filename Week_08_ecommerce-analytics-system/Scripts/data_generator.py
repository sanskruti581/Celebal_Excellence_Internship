import csv
import random
from datetime import datetime
from faker import Faker

fake = Faker()
random.seed(42)

NUM_CUSTOMERS = 500
NUM_PRODUCTS = 500
NUM_ORDERS = 800
NUM_ORDER_ITEMS = 2000

CATEGORIES = {
    "Electronics": ["Mobiles", "Laptops", "Accessories", "Cameras"],
    "Clothing": ["Men", "Women", "Kids", "Footwear"],
    "Home": ["Furniture", "Kitchen", "Decor", "Bedding"],
    "Books": ["Fiction", "Non-Fiction", "Comics", "Academic"]
}

STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST"]

DUPLICATE_RATE = 0.02  # ~2% of rows get an exact duplicate appended


def inject_duplicates(rows):
    """Append exact-copy duplicate rows for ~DUPLICATE_RATE of the given rows.
    Simulates the kind of dirty data (double-submitted forms, re-exports, etc.)
    that clean_data.py's dedupe step is expected to catch."""
    num_dupes = int(len(rows) * DUPLICATE_RATE)
    dupes = [row[:] for row in random.sample(rows, num_dupes)]
    combined = rows + dupes
    random.shuffle(combined)
    return combined


def generate_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        name = fake.name()
        if random.random() < 0.02:
            email = fake.user_name()  # invalid: no @ or domain
        else:
            email = fake.email()
        reg_date = fake.date_time_between(start_date="-2y", end_date="now")
        customers.append([
            i, name, email,
            reg_date.strftime("%Y-%m-%d %H:%M:%S"),
            random.choice(CUSTOMER_TYPES)
        ])

    unique_ids = [c[0] for c in customers]
    customers = inject_duplicates(customers)

    with open("data/Raw/customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "customer_name", "email", "registration_date", "customer_type"])
        writer.writerows(customers)

    print(f"Generated {len(customers)} customer rows ({len(customers) - len(unique_ids)} duplicates) -> data/Raw/customers.csv")
    return unique_ids


def generate_products():
    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        base_name = fake.word().capitalize() + " " + subcategory

        name = base_name
        if random.random() < 0.15:  # ~15% messy names
            messy_variants = [
                "  " + base_name.upper() + "  ",
                base_name.lower(),
                base_name + "   ",
                "   " + base_name
            ]
            name = random.choice(messy_variants)

        cost_price = round(random.uniform(50, 5000), 2)
        products.append([i, name, category, subcategory, cost_price])

    with open("data/Raw/products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category", "subcategory", "cost_price"])
        writer.writerows(products)

    print(f"Generated {len(products)} products -> data/Raw/products.csv")
    return [p[0] for p in products]


def generate_orders(customer_ids):
    orders = []
    for i in range(1, NUM_ORDERS + 1):
        if random.random() < 0.05:  # 5% missing customer_id
            customer_id = ""
        else:
            customer_id = random.choice(customer_ids)

        order_datetime = fake.date_time_between(start_date="-1y", end_date="now")

        if random.random() < 0.10:  # 10% wrong date format
            order_date_str = order_datetime.strftime("%d-%m-%Y")
        else:
            order_date_str = order_datetime.strftime("%Y-%m-%d %H:%M:%S")

        orders.append([i, customer_id, order_date_str, random.choice(STATUSES), random.choice(REGIONS)])

    unique_ids = [o[0] for o in orders]
    orders = inject_duplicates(orders)

    with open("data/Raw/orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "customer_id", "order_date", "status", "region_code"])
        writer.writerows(orders)

    print(f"Generated {len(orders)} order rows ({len(orders) - len(unique_ids)} duplicates) -> data/Raw/orders.csv")
    return unique_ids


def generate_order_items(order_ids, product_ids):
    items = []
    for i in range(1, NUM_ORDER_ITEMS + 1):
        order_id = random.choice(order_ids)      # guarantees it exists in orders.csv
        product_id = random.choice(product_ids)

        quantity = random.randint(1, 10)
        if random.random() < 0.03:  # 3% negative quantity (returns)
            quantity = -abs(quantity)

        unit_price = round(random.uniform(50, 6000), 2)
        discount_percent = round(random.uniform(0, 100), 2)

        items.append([i, order_id, product_id, quantity, unit_price, discount_percent])

    with open("data/Raw/order_items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])
        writer.writerows(items)

    print(f"Generated {len(items)} order_items -> data/Raw/order_items.csv")


if __name__ == "__main__":
    cust_ids = generate_customers()
    prod_ids = generate_products()
    ord_ids = generate_orders(cust_ids)
    generate_order_items(ord_ids, prod_ids)
    print("All CSV files generated successfully in the 'data' folder.")