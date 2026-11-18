"""RAW -> REFINED transformations."""
from pyspark.sql import functions as F
from utils.config import RAW, REFINED
from utils.helpers import write_table, read_table, log

def _raw(spark, t):
    return read_table(spark, RAW, t)

def refine_sales(spark):
    base = _raw(spark, "sales_transactions").select(
        F.trim("txn_id").alias("txn_id"),
        F.to_date("txn_date", "yyyy-MM-dd").alias("txn_date"),
        F.upper(F.trim("store_id")).alias("store_id"),
        F.upper(F.trim("customer_id")).alias("customer_id"),
        F.upper(F.trim("product_id")).alias("product_id"),
        F.col("qty").cast("int").alias("quantity"),
        F.col("unit_price").cast("decimal(10,2)").alias("unit_price"),
        F.coalesce(F.col("discount").cast("decimal(10,2)"), F.lit(0).cast("decimal(10,2)")).alias("discount_amt"),
        F.upper(F.trim("payment_mode")).alias("payment_mode"),
    ).withColumn("net_amount",
        (F.col("quantity") * F.col("unit_price") - F.col("discount_amt")).cast("decimal(12,2)"))
    is_valid = F.coalesce(
        F.expr("txn_id IS NOT NULL AND txn_date IS NOT NULL AND quantity > 0 AND unit_price >= 0"),
        F.lit(False))
    write_table(base.filter(~is_valid), REFINED, "sales_rejected")   # quarantine bad rows
    write_table(base.filter(is_valid).dropDuplicates(["txn_id"]), REFINED, "sales")

def refine_customers(spark):
    df = _raw(spark, "customers").select(
        F.upper(F.trim("customer_id")).alias("customer_id"),
        F.initcap(F.concat_ws(" ", F.trim("first_name"), F.trim("last_name"))).alias("full_name"),
        F.lower(F.trim("email")).alias("email"),
        F.expr("right(regexp_replace(phone, '[^0-9]', ''), 10)").alias("phone"),
        F.initcap(F.trim("city")).alias("city"),
        F.initcap(F.trim("state")).alias("state"),
        F.to_date("signup_date", "yyyy-MM-dd").alias("signup_date"))
    df = df.withColumn("email", F.when(F.col("email").rlike(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"), F.col("email")))
    write_table(df.filter("customer_id IS NOT NULL").dropDuplicates(["customer_id"]), REFINED, "customers")

def refine_products(spark):
    df = _raw(spark, "products").select(
        F.upper(F.trim("product_id")).alias("product_id"),
        F.upper(F.trim("sku")).alias("sku"),
        F.trim("product_name").alias("product_name"),
        F.initcap(F.trim("category")).alias("category"),
        F.initcap(F.trim("brand")).alias("brand"),
        F.col("cost_price").cast("decimal(10,2)").alias("cost_price"),
        F.col("mrp").cast("decimal(10,2)").alias("mrp"))
    write_table(df.filter("product_id IS NOT NULL AND cost_price >= 0 AND mrp >= cost_price")
                  .dropDuplicates(["product_id"]), REFINED, "products")

def refine_stores(spark):
    df = _raw(spark, "stores").select(
        F.upper(F.trim("store_id")).alias("store_id"),
        F.initcap(F.trim("store_name")).alias("store_name"),
        F.initcap(F.trim("city")).alias("city"),
        F.initcap(F.trim("state")).alias("state"),
        F.initcap(F.trim("region")).alias("region"),
        F.col("open_date").cast("date").alias("open_date"))
    write_table(df.filter("store_id IS NOT NULL").dropDuplicates(["store_id"]), REFINED, "stores")

def refine_store_inventory(spark):
    df = _raw(spark, "store_inventory").select(
        F.upper(F.trim("store_id")).alias("store_id"),
        F.upper(F.trim("product_id")).alias("product_id"),
        F.col("stock_qty").cast("int").alias("stock_qty"),
        F.to_date("snapshot_date", "yyyy-MM-dd").alias("snapshot_date"))
    write_table(df.filter("stock_qty >= 0 AND snapshot_date IS NOT NULL")
                  .dropDuplicates(["store_id", "product_id", "snapshot_date"]), REFINED, "store_inventory")

def run(spark):
    for fn in (refine_sales, refine_customers, refine_products, refine_stores, refine_store_inventory):
        fn(spark)
        log.info("REFINED %s done", fn.__name__)
