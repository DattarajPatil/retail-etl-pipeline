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

## On Databricks
1. Run `dataops/retail_pipeline/create_objects.sql` in the SQL editor.
2. Upload the five files from `src/code/data/sample/` to the volume `retail.raw.landing`
   (folders: sales, customers, products, stores, inventory).
3. Push this repo to GitHub, then in Jobs & Pipelines open the job > three dots > Edit as YAML and paste
   `workflow_job_defination.yml` (or: `databricks jobs create --json "@dataops/retail_pipeline/workflow_job_defination.json"`).
4. Edit: node_type_id (m5.xlarge = AWS only) and the on_failure email. Click Run now.

Tasks: raw_ingest -> refine_transform -> confirm_curated. Each runs `run_pipeline.py --layer <name>`.
The same code uses Delta tables on Databricks and parquet folders locally (auto-detected).

## Expected row counts with the sample data
raw sales 10,644 | refined sales 10,549 | sales_rejected 35 | fact_sales 10,549 |
dim_customer 300 | dim_product 40 | dim_store 10 | agg_inventory_status 400
