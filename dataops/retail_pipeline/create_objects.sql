CREATE CATALOG IF NOT EXISTS retail;
CREATE SCHEMA  IF NOT EXISTS retail.raw;
CREATE SCHEMA  IF NOT EXISTS retail.refined;
CREATE SCHEMA  IF NOT EXISTS retail.curated;
CREATE VOLUME  IF NOT EXISTS retail.raw.landing;
-- Then upload to the volume:
--   sales/sales_transactions.csv   customers/customers.csv
--   products/products.parquet      stores/stores.parquet
--   inventory/store_inventory.txt
