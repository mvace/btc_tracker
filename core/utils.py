from decimal import Decimal
import requests
from dotenv import load_dotenv
import os

load_dotenv()


def get_current_price():
    """
    Fetches the current price of Bitcoin (BTC) in US Dollars (USD) from the CryptoCompare API.

    Uses the 'min-api.cryptocompare.com' endpoint to request the latest price of BTC in USD.
    Requires an API key set as an environment variable 'CRYPTOCOMPARE_API_KEY'.

    Returns:
    - Decimal: The current price of one Bitcoin in US Dollars.
    """
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
