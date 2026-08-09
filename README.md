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