from decimal import Decimal
import requests
from dotenv import load_dotenv
import os

load_dotenv()


def get_current_price():
    endpoint = "https://min-api.cryptocompare.com/data/price"
    params = {
        "fsym": "BTC",  # From symbol (Bitcoin)
        "tsyms": "USD",  # To symbol (US Dollar)
        "api_key": str(os.getenv("CRYPTOCOMPARE_API_KEY")),
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    current_price = Decimal(data["USD"])
    return current_price
