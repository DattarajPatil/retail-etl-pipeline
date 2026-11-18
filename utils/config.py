"""Central config. Works locally (VS Code) and on Databricks without code changes."""
import os, pathlib

IS_DATABRICKS = "DATABRICKS_RUNTIME_VERSION" in os.environ
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

# Unity Catalog catalog name. If your workspace does not allow CREATE CATALOG (e.g. Free Edition),
# the default below is "workspace" (the catalog Free Edition provides). Set env var RETAIL_CATALOG to override.
CATALOG = os.getenv("RETAIL_CATALOG", "workspace")
RAW, REFINED, CURATED = "raw", "refined", "curated"

# Where the source files live
if IS_DATABRICKS:
    LANDING = f"/Volumes/{CATALOG}/{RAW}/landing"
    def _p(folder): return f"{LANDING}/{folder}/"
else:
    LANDING = PROJECT_ROOT / "src" / "code" / "data" / "sample"
    def _p(folder): return (LANDING / folder).as_uri()

# Where local output tables are written (parquet folders). Not used on Databricks.
WAREHOUSE = PROJECT_ROOT / "warehouse"
EXPORT_DIR = PROJECT_ROOT / "output"

# 2 CSV, 2 Parquet, 1 TXT (pipe-delimited)
SOURCES = {
    "sales_transactions": {"path": _p("sales"),     "format": "csv"},
    "customers":          {"path": _p("customers"), "format": "csv"},
    "products":           {"path": _p("products"),  "format": "parquet"},
    "stores":             {"path": _p("stores"),    "format": "parquet"},
    "store_inventory":    {"path": _p("inventory"), "format": "txt", "sep": "|"},
}

def fqn(layer: str, table: str) -> str:
    return f"{CATALOG}.{layer}.{table}"
