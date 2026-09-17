# Crypto Data Platform

A Python data pipeline that collects cryptocurrency market data from the CoinMarketCap API, validates and transforms it, then stores it in DuckDB. Apache Airflow orchestrates the real-time pipeline so each stage can be scheduled, monitored, retried, and debugged independently.

## Pipeline

```text
CoinMarketCap API
        |
        v
  Ingestion (raw JSON)
        |
        v
Transformation (CSV)
        |
        v
 Data-quality validation
        |
        v
   DuckDB load
        |
        v
 Load verification
```

## Project structure

```text
src/
├── ingestion/api_ingest.py          # CoinMarketCap API request and raw JSON output
├── transformation/api_transform.py  # JSON-to-CSV transformation
├── DataQuality/Validation.py        # schema and value checks
└── storage/DuckDB.py                # DuckDB table creation, loading, verification

pipelines/cmc_pipeline.py            # run the full pipeline with Python
airflow/dags/crypto_data_pipeline.py # scheduled Airflow DAG
data/raw/                             # generated raw API responses (ignored by Git)
data/processed/                       # generated CSV files (ignored by Git)
DuckDB/CMC.duckdb                     # generated analytical database (ignored by Git)
```

## Components

### Ingestion

`cmc_api_ingest()` fetches up to 1,000 currencies from CoinMarketCap.

- Without `date_string`, it requests real-time listings.
- With `date_string` in `YYYY-MM-DD` format, it requests historical listings.
- It saves unmodified API responses as timestamped JSON in `data/raw/CMC/<type>/`.
- Invalid parameters, missing credentials, timeouts, and non-200 API responses raise errors.

### Transformation

`cmc_api_transform()` reads raw JSON, extracts selected market fields, and writes timestamped CSV files to `data/processed/CMC/<type>/`.

### Data quality

`validate_file()` checks expected columns and data types, required values, unique coin IDs, and non-negative numeric values.

### Storage and verification

`Update_CMC_DuckDB()` loads a processed CSV into `DuckDB/CMC.duckdb`.

- Real-time data goes to `CMC_Real_time`.
- Historical data goes to `CMC_Historical`.
- `(id, Date_of_file)` is the primary key, making repeated loads safe.
- `verify_load()` checks that loaded rows match the CSV row count.

## Local Python setup

1. Create a `.env` file in the repository root:

   ```text
   CRYPTO_API_KEY=your_coinmarketcap_api_key
   ```

2. Install dependencies:

   ```bash
   pipenv install
   ```

3. Run the pipeline directly:

   ```bash
   pipenv run python pipelines/cmc_pipeline.py
   ```

The `.env`, generated data, and DuckDB database are ignored by Git.

## Airflow orchestration

The DAG ID is `crypto_data_pipeline`. It has one task for each component:

```text
ingest -> transform -> validate -> load -> verify
```

The DAG at `airflow/dags/crypto_data_pipeline.py` imports your existing `src/` functions rather than duplicating pipeline logic. Its schedule uses a cron expression:

```python
schedule="0 * * * *"  # start of every hour
```

Examples:

```python
schedule="*/30 * * * *"  # every 30 minutes
schedule="0 9 * * *"     # daily at 09:00
schedule=None             # manual runs only
```

Airflow schedules in UTC unless a timezone is configured.

### Run Airflow locally

Ensure Docker is running and that `.env` contains `CRYPTO_API_KEY`, then run:

```bash
docker compose up --build
```

Open [http://localhost:8080](http://localhost:8080), find `crypto_data_pipeline`, unpause it, and select **Trigger DAG**. Use Grid view to see task status; use a task's **Logs** to investigate failures.

To stop the environment:

```bash
docker compose down
```

## Retry behaviour

The ingestion task retries because external API calls can fail temporarily. To use exponential backoff, configure its task decorator like this:

```python
from datetime import datetime, timedelta

@task(
    retries=3,
    retry_delay=timedelta(minutes=2),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=15),
)
def ingest() -> str:
    ...
```

This waits progressively longer between failed attempts instead of retrying at a fixed interval.

## Useful Airflow commands

```bash
# List DAGs known to Airflow.
docker compose exec airflow airflow dags list

# Trigger the crypto pipeline from the terminal.
docker compose exec airflow airflow dags trigger crypto_data_pipeline

# Follow Airflow container logs.
docker compose logs -f airflow
```

## Notes

This Docker setup is for local development and learning. A production deployment needs a production-grade Airflow executor, external metadata storage, and a secrets-management solution rather than a local `.env` file.
