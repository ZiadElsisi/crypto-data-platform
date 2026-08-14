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
