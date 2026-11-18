-- Databricks Free Edition: use the built-in "workspace" catalog (new catalogs cannot be created).
-- On a full workspace you can use your own catalog: change `workspace` here and CATALOG in utils/config.py.
CREATE SCHEMA IF NOT EXISTS workspace.raw;
CREATE SCHEMA IF NOT EXISTS workspace.refined;
CREATE SCHEMA IF NOT EXISTS workspace.curated;
CREATE VOLUME IF NOT EXISTS workspace.raw.landing;
-- Then upload to the volume (Catalog > workspace > raw > landing):
--   sales/sales_transactions.csv   customers/customers.csv
--   products/products.parquet      stores/stores.parquet
--   inventory/store_inventory.txt
