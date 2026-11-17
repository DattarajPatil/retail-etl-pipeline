"""RAW -> REFINED column mapping: (raw column, refined column, refined type, rule)."""
MAPPING = {
 "sales": [
  ("txn_id", "txn_id", "STRING", "trim; not null; dedupe key"),
  ("txn_date", "txn_date", "DATE", "to_date yyyy-MM-dd"),
  ("store_id", "store_id", "STRING", "trim, upper"),
  ("customer_id", "customer_id", "STRING", "trim, upper"),
  ("product_id", "product_id", "STRING", "trim, upper"),
  ("qty", "quantity", "INT", "cast; must be > 0"),
  ("unit_price", "unit_price", "DECIMAL(10,2)", "cast; must be >= 0"),
  ("discount", "discount_amt", "DECIMAL(10,2)", "cast; null -> 0"),
  ("(derived)", "net_amount", "DECIMAL(12,2)", "quantity*unit_price - discount_amt"),
  ("payment_mode", "payment_mode", "STRING", "trim, upper")],
 "customers": [
  ("customer_id", "customer_id", "STRING", "trim, upper; dedupe key"),
  ("first_name + last_name", "full_name", "STRING", "initcap(trim(first) + ' ' + trim(last))"),
  ("email", "email", "STRING", "lower; regex validated else null"),
  ("phone", "phone", "STRING", "digits only, last 10"),
  ("city", "city", "STRING", "initcap"),
  ("state", "state", "STRING", "initcap"),
  ("signup_date", "signup_date", "DATE", "to_date yyyy-MM-dd")],
 "products": [
  ("product_id", "product_id", "STRING", "trim, upper; dedupe key"),
  ("sku", "sku", "STRING", "trim, upper"),
  ("product_name", "product_name", "STRING", "trim"),
  ("category", "category", "STRING", "initcap"),
  ("brand", "brand", "STRING", "initcap"),
  ("cost_price", "cost_price", "DECIMAL(10,2)", ">= 0"),
  ("mrp", "mrp", "DECIMAL(10,2)", ">= cost_price")],
 "stores": [
  ("store_id", "store_id", "STRING", "trim, upper; dedupe key"),
  ("store_name", "store_name", "STRING", "initcap"),
  ("city", "city", "STRING", "initcap"),
  ("state", "state", "STRING", "initcap"),
  ("region", "region", "STRING", "initcap"),
  ("open_date", "open_date", "DATE", "cast")],
 "store_inventory": [
  ("store_id", "store_id", "STRING", "trim, upper"),
  ("product_id", "product_id", "STRING", "trim, upper"),
  ("stock_qty", "stock_qty", "INT", "cast; >= 0"),
  ("snapshot_date", "snapshot_date", "DATE", "to_date; key = store+product+snapshot_date")],
}
