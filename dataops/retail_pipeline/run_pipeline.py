"""Orchestrator: raw -> refined -> curated. Runs locally (VS Code) or on Databricks.

Usage:
  python dataops/run_pipeline.py                  # all three layers
  python dataops/run_pipeline.py --layer raw      # one layer (used by the Databricks job tasks)
"""
import sys, pathlib, argparse
try:
    ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "utils").is_dir())
except NameError:                       # Databricks notebook: set the repo path manually
    ROOT = pathlib.Path("/Workspace/Repos/<you>/retail-etl-pipeline")
sys.path.insert(0, str(ROOT))

from utils.config import IS_DATABRICKS
from utils.helpers import get_spark, new_batch_id, reset_local_warehouse, log
from src.code.row import raw_ingest
from src.code.refine import refine_transform
from src.code.refine.refine_schemas import REFINED_DDL
from src.code.confirm import curated_transform
from src.code.confirm.curated_schemas import CURATED_DDL

def main(layer: str = "all"):
    spark = get_spark()
    batch_id = new_batch_id()
    log.info("Batch %s started (%s, layer=%s)", batch_id, "Databricks" if IS_DATABRICKS else "local", layer)

    if layer in ("raw", "all") and not IS_DATABRICKS:
        reset_local_warehouse()          # local RAW is append-only, so start clean
    if IS_DATABRICKS:
        ddl = (REFINED_DDL if layer in ("refined", "all") else []) + \
              (CURATED_DDL if layer in ("curated", "all") else [])
        for stmt in ddl:
            spark.sql(stmt)

    if layer in ("raw", "all"):
        raw_ingest.run(spark, batch_id)
    if layer in ("refined", "all"):
        refine_transform.run(spark)
    if layer in ("curated", "all"):
        curated_transform.run(spark)
    log.info("Batch %s finished", batch_id)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", choices=["raw", "refined", "curated", "all"], default="all")
    main(ap.parse_known_args()[0].layer)
