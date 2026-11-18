import logging, uuid, shutil
from pyspark.sql import SparkSession, functions as F
from utils.config import IS_DATABRICKS, WAREHOUSE, fqn

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("retail-etl")

def get_spark() -> SparkSession:
    if IS_DATABRICKS:
        return SparkSession.builder.getOrCreate()
    spark = (SparkSession.builder.master("local[*]").appName("retail-etl-local")
             .config("spark.sql.shuffle.partitions", "4")
             .config("spark.ui.enabled", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark

def new_batch_id() -> str:
    return uuid.uuid4().hex[:12]

def reset_local_warehouse():
    """Local runs start clean, because RAW is append-only and would double on every run."""
    if not IS_DATABRICKS and WAREHOUSE.exists():
        shutil.rmtree(WAREHOUSE)

def add_meta(df, batch_id: str):
    return (df.withColumn("_ingest_ts", F.current_timestamp())
              .withColumn("_source_file", F.col("_metadata.file_path"))
              .withColumn("_batch_id", F.lit(batch_id)))

def write_table(df, layer: str, table: str, mode: str = "overwrite"):
    """Databricks -> Delta table retail.<layer>.<table>. Local -> parquet folder warehouse/<layer>/<table>."""
    if IS_DATABRICKS:
        w = df.write.mode(mode).format("delta")
        if mode == "overwrite":
            w = w.option("overwriteSchema", "true")
        w.saveAsTable(fqn(layer, table))
    else:
        df.write.mode(mode).parquet(str(WAREHOUSE / layer / table))
    log.info("Wrote %s.%s (%s)", layer, table, mode)

def read_table(spark, layer: str, table: str):
    if IS_DATABRICKS:
        return spark.table(fqn(layer, table))
    return spark.read.parquet(str(WAREHOUSE / layer / table))
