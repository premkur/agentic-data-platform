#!/usr/bin/env python3
"""Load ./data/*.csv into AGENTIC_RAW.ECOM (full refresh of each table).

Env vars: SNOWFLAKE_ACCOUNT (orgname-accountname), SNOWFLAKE_PRIVATE_KEY_PATH
"""
import os
from pathlib import Path

import snowflake.connector

TABLES = {
    "customers": "customer_id NUMBER, email VARCHAR, full_name VARCHAR, country VARCHAR, "
                 "signup_date DATE, marketing_opt_in BOOLEAN",
    "products": "product_id NUMBER, product_name VARCHAR, category VARCHAR, "
                "unit_price NUMBER(10,2), is_active BOOLEAN",
    "orders": "order_id NUMBER, customer_id NUMBER, order_ts TIMESTAMP_NTZ, status VARCHAR, "
              "currency VARCHAR, updated_at TIMESTAMP_NTZ",
    "order_items": "order_item_id NUMBER, order_id NUMBER, product_id NUMBER, "
                   "quantity NUMBER, unit_price NUMBER(10,2)",
    "payments": "payment_id NUMBER, order_id NUMBER, payment_ts TIMESTAMP_NTZ, "
                "amount NUMBER(12,2), method VARCHAR, status VARCHAR",
}


def main():
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user="DBT_LOADER_USER",
        private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
        role="AGENTIC_LOADER_ROLE",
        warehouse="AGENTIC_WH",
        database="AGENTIC_RAW",
        schema="ECOM",
    )
    cur = conn.cursor()
    cur.execute("CREATE FILE FORMAT IF NOT EXISTS csv_ff TYPE=CSV SKIP_HEADER=1 "
                "FIELD_OPTIONALLY_ENCLOSED_BY='\"' NULL_IF=('') EMPTY_FIELD_AS_NULL=TRUE")
    cur.execute("CREATE STAGE IF NOT EXISTS raw_stage FILE_FORMAT=csv_ff")
    for table, cols in TABLES.items():
        path = (Path("data") / f"{table}.csv").resolve().as_posix()
        cur.execute(f"CREATE OR REPLACE TABLE {table} ({cols})")
        cur.execute(f"PUT 'file://{path}' @raw_stage/{table} OVERWRITE=TRUE AUTO_COMPRESS=TRUE")
        cur.execute(f"COPY INTO {table} FROM @raw_stage/{table} "
                    f"FILE_FORMAT=(FORMAT_NAME=csv_ff) PURGE=TRUE")
        n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"loaded {table}: {n} rows")
    conn.close()


if __name__ == "__main__":
    main()
