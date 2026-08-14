
from src.ingestion import api_ingest
from src.transformation import api_transform
import time
import duckdb
from src.storage import DuckDB
import pandas as pd


# ingest_path = api_ingest.CMC_API_INGEST()
# print(ingest_path)
# time.sleep(5)
# api_transform.CMC_API_Transform(ingest_path)
#

conn= duckdb.connect(DuckDB.DB_Path)

highest_market_cap = conn.execute('''
                                    SELECT  name,MAX(market_cap) FROM CMC_Real_time
                                    
                                    GROUP BY name

                                     HAVING MAX(market_cap) = (SELECT MAX(market_cap) FROM CMC_Real_time)
                                     ''').df()
print(highest_market_cap)

