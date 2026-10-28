#!/usr/bin/env python3
"""Synthetic e-commerce data generator for the agentic SDLC prototype.

Writes 5 CSV files into ./data: customers, products, orders, order_items, payments.

Baseline data contains realistic *but handleable* mess (dup order rows, messy country
spellings, missing emails). Use --drift to inject upstream changes that SHOULD break
the data tests (new payment status, orphan orders) -- this powers the feedback loop.

Usage:
    python scripts/generate_data.py                 # baseline
    python scripts/generate_data.py --drift         # baseline + upstream drift
"""
import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

COUNTRY_VARIANTS = {
    "US": ["US", "us", "USA", "United States"],
    "CA": ["CA", "Canada"],
    "BR": ["BR", "Brazil"],
    "GB": ["GB", "UK", "United Kingdom"],
    "DE": ["DE", "Germany"],
    "FR": ["FR", "France"],
    "IN": ["IN", "India"],
    "AU": ["AU", "Australia"],
    "JP": ["JP", "Japan"],
    "SG": ["SG", "Singapore"],
}
COUNTRY_WEIGHTS = [30, 6, 4, 12, 8, 6, 10, 8, 4, 2]
FIRST = ["Ava", "Liam", "Noah", "Mia", "Zoe", "Ethan", "Priya", "Arjun", "Chen", "Yuki",
         "Sofia", "Lucas", "Hana", "Omar", "Elena", "Mateo", "Isla", "Kai", "Nina", "Leo"]
LAST = ["Smith", "Patel", "Nguyen", "Garcia", "Muller", "Tanaka", "Silva", "Brown", "Kim",
        "Dubois", "Singh", "Jones", "Rossi", "Lee", "Khan", "Taylor", "Wong", "Evans"]
FMT = "%Y-%m-%d %H:%M:%S"


class Ids:
    order = item = payment = 0


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def make_products(rng):
    cats = {"Electronics": (20, 300), "Home": (10, 120), "Apparel": (15, 90),
            "Books": (8, 40), "Sports": (12, 150)}
    rows, pid = [], 1
    for cat, (lo, hi) in cats.items():
        for i in range(8):
            rows.append({"product_id": pid, "product_name": f"{cat} Item {i + 1}",
                         "category": cat, "unit_price": round(rng.uniform(lo, hi), 2),
                         "is_active": "true" if rng.random() > 0.05 else "false"})
            pid += 1
    return rows


def make_customers(rng, n, start, end):
    rows = []
    codes = list(COUNTRY_VARIANTS)
    for cid in range(1, n + 1):
        code = rng.choices(codes, weights=COUNTRY_WEIGHTS)[0]
        signup = (start - timedelta(days=90)) + timedelta(
            days=rng.randint(0, (end - start).days + 90))
        rows.append({
            "customer_id": cid,
            "email": f"user{cid}@example.com" if rng.random() > 0.01 else "",
            "full_name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
            "country": rng.choice(COUNTRY_VARIANTS[code]),
            "signup_date": signup.strftime("%Y-%m-%d"),
            "marketing_opt_in": "true" if rng.random() > 0.4 else "false",
        })
    return rows


def build_order(rng, ids, customer_id, order_ts, end, products):
    ids.order += 1
    oid = ids.order
    age_days = (end - order_ts).days
    if age_days < 1:
        status = "placed"
    elif age_days < 4:
        status = "shipped"
    else:
        status = rng.choices(["delivered", "cancelled", "returned"], [85, 9, 6])[0]
    updated = order_ts if status == "placed" else min(end, order_ts + timedelta(hours=rng.randint(1, 72)))
    order = {"order_id": oid, "customer_id": customer_id, "order_ts": order_ts.strftime(FMT),
             "status": status, "currency": "USD", "updated_at": updated.strftime(FMT)}

    items, total = [], 0.0
    for _ in range(rng.choices([1, 2, 3, 4], [50, 30, 15, 5])[0]):
        ids.item += 1
        p = rng.choice(products)
        qty = rng.choices([1, 2, 3], [70, 22, 8])[0]
        items.append({"order_item_id": ids.item, "order_id": oid, "product_id": p["product_id"],
                      "quantity": qty, "unit_price": p["unit_price"]})
        total += p["unit_price"] * qty
    total = round(total, 2)

    payments = []

    def pay(pstatus, when, amount):
        ids.payment += 1
        payments.append({"payment_id": ids.payment, "order_id": oid,
                         "payment_ts": min(end, when).strftime(FMT), "amount": amount,
                         "method": method, "status": pstatus})

    method = rng.choice(["card", "paypal", "apple_pay"])
    when = order_ts + timedelta(minutes=rng.randint(1, 30))
    if status == "cancelled":
        if rng.random() < 0.5:
            pay("failed", when, total)
    else:
        if rng.random() < 0.03:
            pay("failed", when, total)
            when += timedelta(minutes=5)
        pay("captured", when, total)
        if status == "returned":
            pay("refunded", when + timedelta(days=rng.randint(2, 10)), total)
    return order, items, payments, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customers", type=int, default=1500)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--drift", action="store_true", help="inject upstream drift")
    ap.add_argument("--out", default="data")
    a = ap.parse_args()

    rng = random.Random(a.seed)
    end = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    start = end - timedelta(days=a.days)

    products = make_products(rng)
    customers = make_customers(rng, a.customers, start, end)
    ids = Ids()
    orders, items, payments, totals = [], [], [], {}

    for c in customers:
        signup = datetime.strptime(c["signup_date"], "%Y-%m-%d")
        lo = max(signup, start)
        if lo >= end:
            continue
        for _ in range(rng.choices([0, 1, 2, 3, 4, 5, 8], [25, 30, 20, 10, 7, 5, 3])[0]):
            ts = lo + timedelta(seconds=rng.randint(0, int((end - lo).total_seconds())))
            o, i, p, t = build_order(rng, ids, c["customer_id"], ts, end, products)
            orders.append(o); items += i; payments += p; totals[o["order_id"]] = t
            # ~0.5% of settled orders also appear as a stale earlier version (CDC-style duplicate)
            if o["status"] != "placed" and rng.random() < 0.005:
                orders.append({**o, "status": "placed", "updated_at": o["order_ts"]})

    if a.drift:
        d = random.Random(a.seed + 1)
        for k in range(25):  # orders for customers that don't exist (late-arriving dimension)
            ts = end - timedelta(hours=d.randint(1, 72))
            o, i, p, t = build_order(d, ids, 900000 + k, ts, end, products)
            orders.append(o); items += i; payments += p; totals[o["order_id"]] = t
        delivered = [o["order_id"] for o in orders if o["status"] == "delivered"]
        for oid in d.sample(delivered, 15):  # new upstream payment status
            ids.payment += 1
            payments.append({"payment_id": ids.payment, "order_id": oid,
                             "payment_ts": end.strftime(FMT), "amount": totals[oid],
                             "method": "card", "status": "chargeback"})

    out = Path(a.out)
    out.mkdir(exist_ok=True)
    write_csv(out / "customers.csv", customers,
              ["customer_id", "email", "full_name", "country", "signup_date", "marketing_opt_in"])
    write_csv(out / "products.csv", products,
              ["product_id", "product_name", "category", "unit_price", "is_active"])
    write_csv(out / "orders.csv", orders,
              ["order_id", "customer_id", "order_ts", "status", "currency", "updated_at"])
    write_csv(out / "order_items.csv", items,
              ["order_item_id", "order_id", "product_id", "quantity", "unit_price"])
    write_csv(out / "payments.csv", payments,
              ["payment_id", "order_id", "payment_ts", "amount", "method", "status"])
    print(f"drift={a.drift} customers={len(customers)} products={len(products)} "
          f"orders={len(orders)} items={len(items)} payments={len(payments)} -> {out}/")


if __name__ == "__main__":
    main()
