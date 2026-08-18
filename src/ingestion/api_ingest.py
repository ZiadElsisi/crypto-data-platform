import requests
import json
import datetime
from dotenv import load_dotenv
import os


#  Using dotenv library to use .env variables
load_dotenv()
CRYPTO_API_KEY = os.getenv("CRYPTO_API_KEY")

# Check if the Key Doesn't Exist
if CRYPTO_API_KEY is None:
    raise ValueError("API key not set in environment variables")

# The Api url :
url = ('https://pro-api.coinmarketcap.com')

def cmc_api_ingest(limit=100 , date_string=None):
    # Check Limit parameter between (1 to 1000) Currency
    if limit < 1 or limit > 1000 :
        raise ValueError('limit value must be between 1 and 1000 ')

    # if we didn't mention the date it will work on now data
    if date_string is None:

        date = datetime.datetime.now(datetime.timezone.utc) # for utc Timezone
        furl = f'{url}/v3/cryptocurrency/listings/latest?limit={limit}'
        Type = "Real_time"

    else:
        try:
            # if we mention a data string in %Y-%m-%d  format we create date object from it and get the historical data
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            raise ValueError("date_string must be in YYYY-MM-DD format")

        furl = f'{url}/v1/cryptocurrency/listings/historical?date={date_string}&limit={limit}'
        Type = "Historical"

    # we added the token in the header as it's an http auth
    headers = {"X-CMC_PRO_API_KEY": f"{CRYPTO_API_KEY}"}

    r = requests.get(furl, headers=headers,timeout=10) # 10 sec allowed time for response
    if r.status_code != 200:
        raise requests.HTTPError(f"{furl} returned status code {r.status_code}")

    # getting the absloute path of the file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    RAW_DIR = os.path.join(BASE_DIR, "..", "..", "data", "raw", "CMC", Type)
    os.makedirs(RAW_DIR, exist_ok=True)

    full_path = os.path.join(RAW_DIR, f'{date.strftime("%Y-%m-%d_%H-%M-%S")}.json')
    # i create a file in row folder with the ingested data in the fomat Crypto_data_at_%Y-%m-%d_%H-%M-%S for good readibility
    with open(full_path, "w") as f:
        json.dump(r.json(), f)  # write json into the file

    return full_path

