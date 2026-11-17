"""RAW layer schemas. CSV/TXT columns are all STRING so bad values never fail the load.
Metadata columns added at load: _ingest_ts, _source_file, _batch_id."""
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType

def _strs(*cols):
    return StructType([StructField(c, StringType(), True) for c in cols])

RAW_SCHEMAS = {
    "sales_transactions": _strs("txn_id", "txn_date", "store_id", "customer_id",
                                "product_id", "qty", "unit_price", "discount", "payment_mode"),
    "customers": _strs("customer_id", "first_name", "last_name", "email",
                       "phone", "city", "state", "signup_date"),
    "store_inventory": _strs("store_id", "product_id", "stock_qty", "snapshot_date"),
    # Parquet carries its own schema; listed here for documentation / validation
    "products": StructType([
        StructField("product_id", StringType()), StructField("sku", StringType()),
        StructField("product_name", StringType()), StructField("category", StringType()),
        StructField("brand", StringType()), StructField("cost_price", DoubleType()),
        StructField("mrp", DoubleType())]),
    "stores": StructType([
        StructField("store_id", StringType()), StructField("store_name", StringType()),
        StructField("city", StringType()), StructField("state", StringType()),
        StructField("region", StringType()), StructField("open_date", DateType())]),
}
