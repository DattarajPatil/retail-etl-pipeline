# retail-etl-pipeline
Medallion pipeline for 5 retail sources (2 CSV, 2 Parquet, 1 pipe-delimited TXT).
Folder map: `row` = RAW (bronze), `refine` = REFINED (silver), `confirm` = CURATED (gold).

```
retail-etl-pipeline/
├─ dataops/retail_pipeline/
│   ├─ run_pipeline.py                 orchestrator (--layer raw|refined|curated|all)
│   ├─ show_results.py                 local row counts + CSV export
│   ├─ create_objects.sql              catalog, schemas, landing volume (Databricks)
│   ├─ workflow_job_defination.json    Databricks job (JSON / API / CLI)
│   └─ workflow_job_defination.yml     same job for "Edit as YAML"
├─ src/code/
│   ├─ row/      raw_schemas.py, raw_ingest.py
│   ├─ refine/   refine_schemas.py, refine_mapping.py, refine_transform.py
│   ├─ confirm/  curated_schemas.py, curated_transform.py
│   └─ data/     generate_sample_data.py, sample/<sales|customers|products|stores|inventory>/
└─ utils/        config.py, helpers.py
```

## Run locally in VS Code (no Databricks needed)
1. Install Python 3.10+ and Java 17. Check: `java -version`
2. `python -m venv .venv` then `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python dataops/retail_pipeline/run_pipeline.py`   -> warehouse/raw, refined, curated (parquet)
5. `python dataops/retail_pipeline/show_results.py`   -> row counts, top stores, CSV exports in output/

Windows only: Spark needs winutils. Put winutils.exe + hadoop.dll (Hadoop 3.3.x) in C:\hadoop\bin
and set HADOOP_HOME=C:\hadoop. (Or use WSL.)

## On Databricks (Free Edition / serverless)
Uses the built-in `workspace` catalog (change `CATALOG` in `utils/config.py` if you have your own).
1. Run `dataops/retail_pipeline/create_objects.sql` in the SQL editor (creates schemas raw, refined, curated and volume `landing`).
2. Catalog > workspace > raw > landing: create folders `sales, customers, products, stores, inventory` and upload the
   matching file from `src/code/data/sample/` into each (Upload to this volume).
3. Push this repo to GitHub. In Jobs & Pipelines open the job > three dots > Edit as YAML, paste
   `dataops/retail_pipeline/workflow_job_defination.yml`, Save, then Run now.
   (JSON version for the CLI: `databricks jobs create --json "@dataops/retail_pipeline/workflow_job_defination.json"`)

Tasks: raw_ingest -> refine_transform -> confirm_curated, each running `run_pipeline.py --layer <name>` on serverless compute.
The same code uses Delta tables on Databricks and parquet folders locally (auto-detected).
Check: `SELECT COUNT(*) FROM workspace.curated.fact_sales;`

## Expected row counts with the sample data
raw sales 10,644 | refined sales 10,549 | sales_rejected 35 | fact_sales 10,549 |
dim_customer 300 | dim_product 40 | dim_store 10 | agg_inventory_status 400
