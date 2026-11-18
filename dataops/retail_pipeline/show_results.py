"""Local only: print row counts + samples for every table and export curated tables to output/*.csv."""
import sys, pathlib
ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "utils").is_dir())
sys.path.insert(0, str(ROOT))
from utils.config import WAREHOUSE, EXPORT_DIR
from utils.helpers import get_spark

TABLES = {
 "raw":     ["sales_transactions", "customers", "products", "stores", "store_inventory"],
 "refined": ["sales", "sales_rejected", "customers", "products", "stores", "store_inventory"],
 "curated": ["dim_customer", "dim_product", "dim_store", "dim_date", "fact_sales",
             "agg_daily_store_sales", "agg_inventory_status"],
}

def main():
    spark = get_spark()
    EXPORT_DIR.mkdir(exist_ok=True)
    print("\n=== ROW COUNTS ===")
    for layer, tables in TABLES.items():
        for t in tables:
            df = spark.read.parquet(str(WAREHOUSE / layer / t))
            print(f"{layer:8s} {t:24s} {df.count():>8,d} rows")
            if layer == "curated":
                df.toPandas().to_csv(EXPORT_DIR / f"{t}.csv", index=False)
    print(f"\nCurated tables exported to: {EXPORT_DIR}")
    print("\n=== TOP 5 STORES BY REVENUE ===")
    spark.read.parquet(str(WAREHOUSE / "curated/agg_daily_store_sales")).createOrReplaceTempView("a")
    spark.read.parquet(str(WAREHOUSE / "curated/dim_store")).createOrReplaceTempView("s")
    spark.sql("""SELECT s.store_name, round(sum(a.revenue),2) revenue, sum(a.units) units
                 FROM a JOIN s USING (store_key) GROUP BY s.store_name ORDER BY revenue DESC LIMIT 5""").show(truncate=False)
    print("=== STOCK FLAGS ===")
    spark.read.parquet(str(WAREHOUSE / "curated/agg_inventory_status")).groupBy("stock_flag").count().show()

if __name__ == "__main__":
    main()
