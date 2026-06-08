from pymongo import MongoClient
from pprint import pprint
import time

def timed(label, func):
 t = time.time()
 result = list(func())
 print(f"{label:35s} {(time.time() - t) * 1000:7.1f} ms")
 return result

client = MongoClient(    "mongodb://itc6050:itc6050@localhost:27017/?authSource=admin")

db = client["shop_lab"]

# ──────────────────────────────────────────────
# Q1 — Monthly revenue trend
# Equivalent of: GROUP BY date_trunc('month', order_date)
# ──────────────────────────────────────────────

print("\n--- Q1: Monthly revenue ---")

q1 = timed(
    "Q1 Monthly Revenue",
    lambda: db.orders.aggregate([
        {"$group": {
            "_id": {
                "year": {"$year": "$order_date"},
                "month": {"$month": "$order_date"}
            },
            "orders": {"$sum": 1},
            "revenue": {"$sum": "$total"}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ])
)

for row in q1[:5]:
    pprint(row)

# ──────────────────────────────────────────────────────────────
# Q2 — Top 10 products by revenue
# HINT: use orders_embedded — $unwind the items array,
# then $group by product_id and $sort.
# ──────────────────────────────────────────────────────────────

print("\n--- Q2: Top 10 Products ---")
q2 = timed(
    "Q2 Top Products",
    lambda: db.orders_embedded.aggregate([
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "total_qty": {"$sum": "$items.quantity"},
                "revenue": {
                    "$sum": {
                        "$multiply": [
                            "$items.quantity",
                            "$items.unit_price_at_sale"
                        ]
                    }
                }
            }
        },
        {"$sort": {"revenue": -1}}
    ])
)

for row in q2[:5]:
    pprint(row)
# ──────────────────────────────────────────────────────────────
# Q3 — Order count + avg + median by status
# HINT: $group with $count, $avg.
# Median in Mongo: use $percentile (Mongo 7+) or $bucketAuto.
# ──────────────────────────────────────────────────────────────
print("\n--- Q3: Order Count ---")
q3 = timed(
    "Q3 Order Stats",
    lambda: db.orders.aggregate([
        {"$group": {
            "_id": "$status",
            "order_count": {"$sum": 1},
            "avg_total": {"$avg": "$total"},
            "totals": {"$push": "$total"}
        }},
        {"$project": {
            "order_count": 1,
            "avg_total": 1,
            "median_total": {
                "$percentile": {
                    "input": "$totals",
                    "p": [0.5],
                    "method": "approximate"
                }
            }
        }}
    ])
)

for row in q3[:5]:
    pprint(row)
# ──────────────────────────────────────────────────────────────
# Q4 — Dormant customers (no order in 90 days)
# HINT: aggregate orders to find max(order_date) per customer,
# then $lookup against customer, then $match.
# ──────────────────────────────────────────────────────────────
print("\n--- Q4: Dormant Customers ---")
from datetime import datetime, timedelta

cutoff = datetime.utcnow() - timedelta(days=90)

q4 = timed(
    "Q4 Dormant Customers",
    lambda: db.orders.aggregate([
        {
            "$group": {
                "_id": "$customer_id",
                "last_order_date": {"$max": "$order_date"}
            }
        },
        {
            "$lookup": {
                "from": "customer",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "customer"
            }
        },
        {"$unwind": "$customer"},
        {
            "$match": {
                "$or": [
                    {"last_order_date": None},
                    {"last_order_date": {"$lt": cutoff}}
                ]
            }
        },
        {
            "$project": {
                "customer_id": "$_id",
                "first_name": "$customer.first_name",
                "last_name": "$customer.last_name",
                "email": "$customer.email",
                "last_order_date": 1
            }
        },
        {"$sort": {"last_order_date": 1}}
    ])
)

for row in q4[:5]:
    pprint(row)
# ──────────────────────────────────────────────────────────────
# Q5 — Top 20 customers by lifetime spend
# Note: MongoDB doesn't have window functions — you'll need
# $setWindowFields (Mongo 5+) which is the closest equivalent.
# ──────────────────────────────────────────────────────────────
print("\n--- Q5: Top 20 Customers ---")

q5 = timed(
    "Q5 Lifetime Spend",
    lambda: db.orders.aggregate([
        {
            "$group": {
                "_id": "$customer_id",
                "lifetime_spend": {"$sum": "$total"}
            }
        },
        {
            "$lookup": {
                "from": "customer",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "customer"
            }
        },
        {"$unwind": "$customer"},
        {
            "$setWindowFields": {
                "sortBy": {"lifetime_spend": -1},
                "output": {
                    "rank": {"$rank": {}},
                    "prev_spend": {
                        "$shift": {
                            "output": "$lifetime_spend",
                            "by": 1,
                            "default": None
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "rank": 1,
                "email": "$customer.email",
                "lifetime_spend": 1,
                "gap_to_previous": {
                    "$subtract": [
                        "$lifetime_spend",
                        "$prev_spend"
                    ]
                }
            }
        },
        {"$sort": {"rank": 1}},
        {"$limit": 20}
    ])
)

for row in q5[:5]:
    pprint(row)