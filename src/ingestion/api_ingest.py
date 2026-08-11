import requests
import json
import datetime
from dotenv import load_dotenv
import os

#  I used dotenv library to use my .env variables
load_dotenv()

CRYPTO_API_KEY = os.getenv("CRYPTO_API_KEY")
if CRYPTO_API_KEY is None:
    raise ValueError("API key not set in environment variables")
# The Api url :
url = ('https://pro-api.coinmarketcap.com')

def CMC_API_INGEST(limit=100 , date_string=None):
    # if we didn't mention the date it will work on now data
    if date_string is None:
        date = datetime.datetime.now()
        furl = f'{url}/v3/cryptocurrency/listings/latest?limit={limit}'
    else:
        # if we mention a data string in %Y-%m-%d  format we create date object from it and get the historical data
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        furl = f'{url}/v1/cryptocurrency/listings/historical?date={date.strftime("%Y-%m-%dT%H:%M:%S.000Z")}&limit={limit}'
    # we added the token in the header as it's an http auth
    headers = {"X-CMC_PRO_API_KEY": f"{CRYPTO_API_KEY}"}
    r = requests.get(furl, headers=headers)
    if r.status_code != 200:
        print("Error : " + r.text)
    else:
        # getting the absloute path of the file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # go up two levels to project root, then into data/raw
        RAW_DIR = os.path.join(BASE_DIR, "..", "..", "data", "raw")
        path = os.path.join(RAW_DIR, f'Crypto_data_at_{date.strftime("%Y-%m-%d_%H-%M-%S")}.json')
        # i create a file in row folder with the ingested data in the fomat Crypto_data_at_%Y-%m-%d_%H-%M-%S for good readibility
        with open(path, "w") as f:
            json.dump(r.json(), f) # write json into the file


