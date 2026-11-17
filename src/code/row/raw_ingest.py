"""Source files -> RAW tables. No cleansing, append only, add lineage metadata."""
from utils.config import SOURCES, RAW
from utils.helpers import add_meta, write_table, log
from src.code.row.raw_schemas import RAW_SCHEMAS

def ingest_table(spark, name: str, batch_id: str):
    src = SOURCES[name]
    if src["format"] == "parquet":
        df = spark.read.parquet(src["path"])
    else:  # csv or pipe-delimited txt
        df = (spark.read.option("header", True)
                        .option("sep", src.get("sep", ","))
                        .schema(RAW_SCHEMAS[name])
                        .csv(src["path"]))
    write_table(add_meta(df, batch_id), RAW, name, mode="append")
    log.info("RAW %s loaded", name)

def run(spark, batch_id: str):
    for name in SOURCES:
        ingest_table(spark, name, batch_id)
