import requests
import json
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
CRYPTO_API_KEY = os.getenv("CRYPTO_API_KEY")

if CRYPTO_API_KEY is None:
    raise ValueError("API key not set in environment variables")

print(CRYPTO_API_KEY)  # confirms it loaded
url = ('https://pro-api.coinmarketcap.com')
def get_cryto_list(limit=100):
    furl = f'{url}/v3/cryptocurrency/listings/latest?limit={limit}'
    headers = {"X-CMC_PRO_API_KEY": f"{CRYPTO_API_KEY}"}
    r = requests.get(furl, headers=headers)
    with open(f"../../data/raw/{datetime.datetime.now()}", "w") as f:
        json.dump(r.json(), f)

get_cryto_list()