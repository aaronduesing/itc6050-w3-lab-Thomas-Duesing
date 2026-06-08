from pymongo import MongoClient
from sqlalchemy import create_engine
import pandas as pd

PG = create_engine("postgresql+psycopg2://itc6050:itc6050@localhost:5432/shop_lab")
MG = MongoClient("mongodb://itc6050:itc6050@localhost:27017/?authSource=admin")

db = MG["shop_lab"]

# --- Wipe any prior runs ---
for c in ["customer", "product", "orders", "orders_embedded"]:
    db.drop_collection(c)

# --- Helper: safe insert ---
def safe_insert(collection, df):
    if df.empty:
        print(f"Skipped {collection.name}: no data")
        return
    collection.insert_many(df.to_dict(orient="records"))

# --- Customers (simple 1:1) ---
customers = pd.read_sql("SELECT * FROM shop.customer", PG)
safe_insert(db.customer, customers)
print(f"Loaded {db.customer.count_documents({})} customers")

# --- Products ---
products = pd.read_sql("""
    SELECT p.product_id,
           p.name,
           p.price,
           c.name AS category
    FROM shop.product p
    JOIN shop.category c USING (category_id)
""", PG)

safe_insert(db.product, products)
print(f"Loaded {db.product.count_documents({})} products")

# --- Orders (referenced) ---
orders = pd.read_sql("SELECT * FROM shop.orders", PG)
safe_insert(db.orders, orders)

# --- Orders (embedded) ---
embedded = pd.read_sql("""
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.status,
        o.total,
        json_agg(
            json_build_object(
                'product_id', oi.product_id,
                'quantity', oi.quantity,
                'unit_price', oi.unit_price
            )
        ) AS items
    FROM shop.orders o
    JOIN shop.order_item oi USING (order_id)
    GROUP BY o.order_id, o.customer_id, o.order_date, o.status, o.total
""", PG)

# PostgreSQL already returns Python objects for json_agg in most setups
# So we only fix null cases
embedded["items"] = embedded["items"].apply(lambda x: x if x is not None else [])

safe_insert(db.orders_embedded, embedded)

print(f"Loaded {db.orders.count_documents({})} reference-style orders")
print(f"Loaded {db.orders_embedded.count_documents({})} embedded-style orders")

# --- Indexes (safe re-run) ---
db.customer.create_index("customer_id", unique=True)
db.customer.create_index("email", unique=True)

db.product.create_index("product_id", unique=True)

db.orders.create_index([("order_date", 1)])
db.orders.create_index("customer_id")

db.orders_embedded.create_index([("order_date", 1)])
db.orders_embedded.create_index("customer_id")

print("✅ Indexes created.")