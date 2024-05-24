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
    api_key = str(os.getenv("CRYPTOCOMPARE_API_KEY"))

    if not api_key:
        print("Error: CRYPTOCOMPARE_API_KEY is not set.")
        return None

    params = {
        "fsym": "BTC",  # From symbol (Bitcoin)
        "tsyms": "USD",  # To symbol (US Dollar)
        "api_key": api_key,
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        data = response.json()

        if "USD" in data:
            current_price = Decimal(data["USD"])
            return current_price
        else:
            print(f"Error: Unexpected response format: {data}")
            return None

    except requests.exceptions.RequestException as e:
        # Handle any requests-related errors (network issues, invalid responses, etc.)
        print(f"Error fetching data from CryptoCompare API: {e}")
        return None

    except (ValueError, KeyError) as e:
        # Handle JSON decoding errors or missing data in the response
        print(f"Error processing API response: {e}")
        return None
