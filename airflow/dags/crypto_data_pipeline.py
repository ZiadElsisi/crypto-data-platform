from airflow.sdk import dag, task
from datetime import datetime, timedelta

@dag(
    dag_id="crypto_data_pipeline",
    schedule="0 * * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["crypto", "coinmarketcap", "duckdb"],
)
def crypto_data_pipeline():

    @task(retries=3,
    retry_delay=timedelta(minutes=2),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=15),)

    def ingest() -> str:
        from src.ingestion.api_ingest import cmc_api_ingest
        return cmc_api_ingest()

    @task
    def transform(raw_file: str) -> str:
        from src.transformation.api_transform import cmc_api_transform
        return cmc_api_transform(raw_file, d_type="Real_time")

    @task
    def validate(processed_file: str) -> str:
        from src.DataQuality.Validation import validate_file

        if not validate_file(processed_file, d_type="Real_time"):
            raise ValueError("Data-quality validation failed")
        return processed_file

    @task
    def load(processed_file: str) -> str:
        from src.storage.DuckDB import Update_CMC_DuckDB

        Update_CMC_DuckDB(path=processed_file, d_type="Real_time")
        return processed_file

    @task
    def verify(processed_file: str) -> None:
        from src.storage.DuckDB import verify_load

        if not verify_load(processed_file, d_type="Real_time"):
            raise ValueError("DuckDB load verification failed")

    raw_file = ingest()
    processed_file = transform(raw_file)
    validated_file = validate(processed_file)
    loaded_file = load(validated_file)
    verify(loaded_file)


crypto_data_pipeline()