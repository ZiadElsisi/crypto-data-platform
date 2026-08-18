import os

import pandas as pd
import logging

real_time_expected = {
    "id"                   : "int64",
    "name"                 : "str",      # VARCHAR → object in pandas
    "symbol"               : "str",
    "cmc_rank"             : "int64",
    "last_updated"         : "str",  # TIMESTAMPTZ
    "circulating_supply"   : "float64",     # DOUBLE → float64
    "max_supply"           : "float64",
    "price"                : "float64",
    "market_cap"           : "float64",
    "volume_24h"           : "float64",
    "volume_change_24h"    : "float64",
    "percent_change_1h"    : "float64",
    "percent_change_24h"   : "float64",
    "percent_change_7d"    : "float64",
    "market_cap_dominance" : "float64",
    "percent_change_90d"   : "float64",
}

historical_expected = {
    "id"                   : "int64",
    "name"                 : "str",
    "symbol"               : "str",
    "cmc_rank"             : "int64",
    "last_updated"         : "str",
    "circulating_supply"   : "float64",
    "max_supply"           : "float64",
    "price"                : "float64",
    "market_cap"           : "float64",
    "volume_24h"           : "float64",
    "percent_change_1h"    : "float64",
    "percent_change_24h"   : "float64",
    "percent_change_7d"    : "float64",
}

def validate_file(path,d_type):
    if not os.path.isfile(path): ## Checks if there is a file there
        raise FileNotFoundError(f"File {path} does not exist")

    df = pd.read_csv(path)
    if d_type == "Historical":
        if not sorted(historical_expected.keys()) == sorted(df.columns):
            logging.warning(f"Columns do not match scheme")
            return False
        else:
            expected = historical_expected.copy()
    elif d_type == "Real_time" :
        if not sorted(real_time_expected.keys()) == sorted(df.columns):
            logging.warning(f"Columns do not match scheme")
            return False
        else:
            expected = real_time_expected.copy()

    else:
        raise ValueError("Restricted CMC Type ")



    for col, expected_dtype in expected.items():

        actual_dtype = str(df[col].dtype)
        if actual_dtype != expected_dtype:
            logging.warning(f"Column {col}: expected {expected_dtype}, got {actual_dtype}")
            return False



    for col in ['name','symbol','last_updated','price','market_cap'] :
        if df[col].isnull().values.any():
            logging.warning(f"Column {col} is null")
            return False

    if df.duplicated(subset=['id']).any() :
        logging.warning(f"id is duplicated")
        return False

    for col in ['price','market_cap','volume_24h','circulating_supply']:
        if not df[df[col]<0].empty:
            logging.warning(f"Column {col} is negative")
            return False

    return True


