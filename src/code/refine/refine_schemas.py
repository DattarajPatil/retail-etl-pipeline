"""REFINED layer table definitions (typed, cleaned, deduplicated)."""
REFINED_DDL = [
"""CREATE TABLE IF NOT EXISTS retail.refined.sales (
  txn_id STRING, txn_date DATE, store_id STRING, customer_id STRING, product_id STRING,
  quantity INT, unit_price DECIMAL(10,2), discount_amt DECIMAL(10,2),
  net_amount DECIMAL(12,2), payment_mode STRING)""",
"""CREATE TABLE IF NOT EXISTS retail.refined.customers (
  customer_id STRING, full_name STRING, email STRING, phone STRING,
  city STRING, state STRING, signup_date DATE)""",
"""CREATE TABLE IF NOT EXISTS retail.refined.products (
  product_id STRING, sku STRING, product_name STRING, category STRING,
  brand STRING, cost_price DECIMAL(10,2), mrp DECIMAL(10,2))""",
"""CREATE TABLE IF NOT EXISTS retail.refined.stores (
  store_id STRING, store_name STRING, city STRING, state STRING, region STRING, open_date DATE)""",
"""CREATE TABLE IF NOT EXISTS retail.refined.store_inventory (
  store_id STRING, product_id STRING, stock_qty INT, snapshot_date DATE)""",
]
