"""CURATED layer (star schema + aggregates)."""
CURATED_DDL = [
"""CREATE TABLE IF NOT EXISTS retail.curated.dim_customer (
  customer_key BIGINT, customer_id STRING, full_name STRING, email STRING,
  phone STRING, city STRING, state STRING, signup_date DATE)""",
"""CREATE TABLE IF NOT EXISTS retail.curated.dim_product (
  product_key BIGINT, product_id STRING, sku STRING, product_name STRING,
  category STRING, brand STRING, cost_price DECIMAL(10,2), mrp DECIMAL(10,2))""",
"""CREATE TABLE IF NOT EXISTS retail.curated.dim_store (
  store_key BIGINT, store_id STRING, store_name STRING, city STRING,
  state STRING, region STRING, open_date DATE)""",
"""CREATE TABLE IF NOT EXISTS retail.curated.dim_date (
  date_key INT, full_date DATE, year INT, quarter INT, month INT,
  month_name STRING, week INT, day_of_week STRING, is_weekend BOOLEAN)""",
"""CREATE TABLE IF NOT EXISTS retail.curated.fact_sales (
  txn_id STRING, date_key INT, store_key BIGINT, customer_key BIGINT, product_key BIGINT,
  quantity INT, unit_price DECIMAL(10,2), discount_amt DECIMAL(10,2),
  net_amount DECIMAL(12,2), gross_margin DECIMAL(12,2), payment_mode STRING)""",
"""CREATE TABLE IF NOT EXISTS retail.curated.agg_daily_store_sales (
  txn_date DATE, store_key BIGINT, revenue DECIMAL(14,2), units BIGINT,
  transactions BIGINT, avg_basket_value DECIMAL(12,2))""",
"""CREATE TABLE IF NOT EXISTS retail.curated.agg_inventory_status (
  store_key BIGINT, product_key BIGINT, stock_qty INT, units_sold_30d BIGINT,
  days_of_cover DOUBLE, stock_flag STRING)""",
]
