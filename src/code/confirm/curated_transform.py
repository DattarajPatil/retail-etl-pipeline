"""REFINED -> CURATED transformations (dims first, then fact, then aggregates)."""
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from utils.config import REFINED, CURATED
from utils.helpers import write_table, read_table, log

def _ref(spark, t):
    return read_table(spark, REFINED, t)

def _with_key(df, key, order_col):
    keyed = df.withColumn(key, F.row_number().over(Window.orderBy(order_col)).cast("bigint"))
    return keyed.select(key, *[c for c in df.columns])

def build_dims(spark):
    write_table(_with_key(_ref(spark, "customers"), "customer_key", "customer_id"), CURATED, "dim_customer")
    write_table(_with_key(_ref(spark, "products"), "product_key", "product_id"), CURATED, "dim_product")
    write_table(_with_key(_ref(spark, "stores"), "store_key", "store_id"), CURATED, "dim_store")

    r = _ref(spark, "sales").agg(F.min("txn_date").alias("mn"), F.max("txn_date").alias("mx")).first()
    cal = spark.sql(f"SELECT explode(sequence(to_date('{r.mn}'), to_date('{r.mx}'), interval 1 day)) AS full_date")
    dd = cal.select(
        F.date_format("full_date", "yyyyMMdd").cast("int").alias("date_key"), "full_date",
        F.year("full_date").alias("year"), F.quarter("full_date").alias("quarter"),
        F.month("full_date").alias("month"), F.date_format("full_date", "MMMM").alias("month_name"),
        F.weekofyear("full_date").alias("week"), F.date_format("full_date", "EEEE").alias("day_of_week"),
        F.dayofweek("full_date").isin(1, 7).alias("is_weekend"))
    write_table(dd, CURATED, "dim_date")

def build_fact_sales(spark):
    ds = read_table(spark, CURATED, "dim_store").select("store_id", "store_key")
    dc = read_table(spark, CURATED, "dim_customer").select("customer_id", "customer_key")
    dp = read_table(spark, CURATED, "dim_product").select("product_id", "product_key", "cost_price")
    fact = (_ref(spark, "sales")
        .join(ds, "store_id").join(dc, "customer_id", "left").join(dp, "product_id")
        .withColumn("date_key", F.date_format("txn_date", "yyyyMMdd").cast("int"))
        .withColumn("gross_margin",
            (F.col("net_amount") - F.col("quantity") * F.col("cost_price")).cast("decimal(12,2)"))
        .select("txn_id", "date_key", "store_key", "customer_key", "product_key", "quantity",
                "unit_price", "discount_amt", "net_amount", "gross_margin", "payment_mode"))
    write_table(fact, CURATED, "fact_sales")

def build_aggregates(spark):
    ds = read_table(spark, CURATED, "dim_store").select("store_id", "store_key")
    dp = read_table(spark, CURATED, "dim_product").select("product_id", "product_key")
    sales = _ref(spark, "sales")

    daily = (sales.join(ds, "store_id").groupBy("txn_date", "store_key")
        .agg(F.sum("net_amount").cast("decimal(14,2)").alias("revenue"),
             F.sum("quantity").alias("units"),
             F.countDistinct("txn_id").alias("transactions"))
        .withColumn("avg_basket_value", (F.col("revenue") / F.col("transactions")).cast("decimal(12,2)")))
    write_table(daily, CURATED, "agg_daily_store_sales")

    inv = _ref(spark, "store_inventory")
    latest = inv.filter(F.col("snapshot_date") == inv.agg(F.max("snapshot_date")).first()[0])
    max_sale_date = sales.agg(F.max("txn_date")).first()[0]
    sold30 = (sales.filter(F.col("txn_date") > F.date_sub(F.lit(max_sale_date), 30))
              .groupBy("store_id", "product_id").agg(F.sum("quantity").alias("units_sold_30d")))
    status = (latest.join(sold30, ["store_id", "product_id"], "left")
        .na.fill({"units_sold_30d": 0})
        .withColumn("days_of_cover",
            F.when(F.col("units_sold_30d") > 0, F.col("stock_qty") / (F.col("units_sold_30d") / 30)))
        .withColumn("stock_flag",
            F.when(F.col("days_of_cover") < 7, "LOW")
             .when(F.col("days_of_cover") > 90, "OVERSTOCK").otherwise("OK"))
        .join(ds, "store_id").join(dp, "product_id")
        .select("store_key", "product_key", "stock_qty", "units_sold_30d", "days_of_cover", "stock_flag"))
    write_table(status, CURATED, "agg_inventory_status")

def run(spark):
    build_dims(spark); log.info("CURATED dims done")
    build_fact_sales(spark); log.info("CURATED fact done")
    build_aggregates(spark); log.info("CURATED aggregates done")
