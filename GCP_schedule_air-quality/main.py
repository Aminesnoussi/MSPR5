from city_feed import CityFeed
from google.cloud import storage
import pandas as pd
import datetime
import os

def run_script_air(request):
    cities = ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"]  # Change these to your desired cities
    city_feed = CityFeed()
    df = city_feed.get_cities_data_df(cities)

    # Save to CSV in memory
    csv_data = df.to_csv(index=False)

    # GCS upload
    bucket_name = os.environ["GCS_BUCKET"]
    folder = "raw_air_quality_data"
    timestamp = datetime.datetime.now(tz=city_feed.tz).strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{folder}/air-quality_{timestamp}.csv"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(csv_data, content_type="text/csv")

    return f"Uploaded file {filename} to bucket {bucket_name}.", 200