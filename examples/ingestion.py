import kfp
from kfp import dsl
import requests
import pandas as pd


@dsl.component(base_image="python:3.9", packages_to_install=["requests", "pandas"])
def fetch_crypto_data(crypto_symbols: list, output_csv: dsl.OutputPath("CSV")):
    """Fetches cryptocurrency data from a free API and saves it to a CSV file."""

    base_url = "https://api.coingecko.com/api/v3/simple/price"
    crypto_data = []

    for symbol in crypto_symbols:
        params = {
            "ids": symbol.lower(),
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json().get(symbol.lower(), {})
            if data:
                usd_data = data.get("usd", {})
                crypto_data.append(
                    {
                        "symbol": symbol,
                        "price": usd_data.get("usd"),
                        "market_cap": usd_data.get("usd_market_cap"),
                        "volume_24h": usd_data.get("usd_24h_vol"),
                        "percent_change_24h": usd_data.get("usd_24h_change"),
                    }
                )
            else:
                print(f"No data found for {symbol}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}")

    if crypto_data:
        df = pd.DataFrame(crypto_data)
        df.to_csv(output_csv, index=False)
        print(f"Crypto data saved to {output_csv}")
    else:
        print("No crypto data fetched. CSV file not created.")


@dsl.pipeline(
    name="CryptoDataPipeline",
    description="Fetches cryptocurrency data and saves it to a CSV file.",
)
def crypto_data_pipeline(crypto_symbols: list = ["BTC", "ETH", "LTC"]):
    """Pipeline to fetch cryptocurrency data."""

    fetch_data_task = fetch_crypto_data(crypto_symbols=crypto_symbols)


# Compile the pipeline
pipeline_func = crypto_data_pipeline
pipeline_filename = pipeline_func.__dict__["component_spec"].name + ".pipeline.yaml"
kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename)

# Connect to the KFP cluster using the external endpoint
client = kfp.Client(host="http://192.168.58.2/apis")

# Upload the pipeline
pipeline = client.upload_pipeline(
    pipeline_filename, pipeline_name="Crypto Data Pipeline"
)
