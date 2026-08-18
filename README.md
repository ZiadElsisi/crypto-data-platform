Ingestion

Responsibility:
Acquire data from the coinmarketcap API and store the original data in the raw layer.

Input:
External data source [ coinmarketcap API ] and required request configuration.

Output:
Raw, unmodified data stored in data/raw/.

Error handling:

Failed or invalid requests should not be treated as successful ingestion.

Configuration:

Source credentials and request parameters should not be hard-coded.

                 get_crypto_list()
                       │
             date_string provided?
                 /            \
               No              Yes
               │                │
        Current data       Historical data
               │                │
               └───────┬────────┘
                       ↓
                  API response
                       ↓
                  status check
                    /     \
                  error    success
                            ↓
                       JSON response
                            ↓
                        data/raw/


# Data Transformation

## Goal

Transform the raw CoinMarketCap API JSON files into structured processed datasets that can be used by the next stages of the pipeline.

## Technologies

- **Python**
- **Pandas** — create DataFrames and export processed data
- **JSON** — read raw API responses
- **OS** — file/path management
- **CSV** — processed data output

## What I Did

### 1. Inspected the Raw Data

Inspected the CoinMarketCap API responses and identified the fields needed for the processed dataset.

Selected fields include:

- `id`
- `name`
- `symbol`
- `cmc_rank`
- `last_updated`
- `price`
- `market_cap`
- `market_cap_dominance`
- `volume_24h`
- `volume_change_24h`
- `percent_change_1h`
- `percent_change_24h`
- `percent_change_7d`
- `percent_change_90d`
- `circulating_supply`
- `max_supply`

### 2. Defined the Processed Schema

Defined the fields, data types, and purpose of the processed dataset before implementing the transformation.

### 3. Built the Transformation Function

Created a Python transformation function that:

1. Checks whether the input file exists.
2. Determines whether the data is **Real-time** or **Historical** from the file path.
3. Reads the raw JSON.
4. Extracts the required fields.
5. Handles the differences between the Real-time and Historical API schemas.
6. Creates a Pandas DataFrame.
7. Saves the processed data as a CSV file.

### 4. Handled Missing Values

Handled fields that can be unavailable or `null`.

For example:

```python
data.get("max_supply")

```

# Storage Component

## Introduction

After the ingestion and transformation processes, the transformed cryptocurrency data needs to be stored in a way that makes it easy to query and analyze.

For this project, I chose **DuckDB** as the analytical database.

## Why DuckDB?

DuckDB is suitable for this project because:

- It is lightweight and requires no separate database server.
- It is designed for analytical workloads.
- It works well with CSV and Parquet files.
- It provides SQL querying capabilities.
- It is simple to integrate with Python.

## Storage Structure

The processed data is separated into two categories:

- **Real-time**
- **Historical**

Instead of keeping every processed CSV as a separate database table, the files are loaded into one DuckDB database:

    CMC.duckdb
    │
    ├── CMC_Real_time
    │
    └── CMC_Historical

Each table contains the records from all processed files belonging to its category.

## Real-time Table

The `CMC_Real_time` table stores the real-time cryptocurrency data.

It contains fields such as:

- `id`
- `name`
- `symbol`
- `cmc_rank`
- `last_updated`
- `circulating_supply`
- `max_supply`
- `price`
- `market_cap`
- `volume_24h`
- `volume_change_24h`
- `percent_change_1h`
- `percent_change_24h`
- `percent_change_7d`
- `market_cap_dominance`
- `percent_change_90d`
- `Date_of_file`

The primary key is:

    (id, Date_of_file)

This allows the same cryptocurrency to appear multiple times as long as each record belongs to a different file/timestamp.

## Historical Table

The `CMC_Historical` table stores historical cryptocurrency data.

Its schema is slightly different from the real-time table because the Historical API does not provide exactly the same fields.

It contains:

- `id`
- `name`
- `symbol`
- `cmc_rank`
- `last_updated`
- `circulating_supply`
- `max_supply`
- `price`
- `market_cap`
- `volume_24h`
- `percent_change_1h`
- `percent_change_24h`
- `percent_change_7d`
- `Date_of_file`

It also uses:

    (id, Date_of_file)

as the primary key.

## Loading Process

The storage component reads the processed CSV files and inserts their records into the appropriate DuckDB table.

The process is:

    Processed CSV
          ↓
    Identify Data Category
          ↓
       Read File
          ↓
    Validate Structure
          ↓
    Add File Timestamp
          ↓
    Insert into DuckDB

The file timestamp is extracted from the filename and stored in `Date_of_file`.

This allows the database to preserve when each processed file was generated.

## Duplicate Handling

The storage process needs to be safe to run multiple times.

The primary key:

    (id, Date_of_file)

helps identify duplicate records.

The loader supports two actions:

- `ignore` — ignore records that already exist.
- `update` — update an existing record when a conflict occurs.

This makes the loading process **idempotent** and prevents accidentally creating duplicate records when the pipeline is executed again.

## Result

The final storage layer provides a single analytical database containing both Real-time and Historical cryptocurrency data.

    Raw JSON
       ↓
    Transformation
       ↓
    Processed CSV
       ↓
    Data Quality
       ↓
    CMC.duckdb
       ├── CMC_Real_time
       └── CMC_Historical

This structure provides a simple foundation for the next stage of the project: querying and analyzing the cryptocurrency data using SQL.

