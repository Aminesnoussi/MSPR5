from open_weather import OpenWeather
from google.cloud import storage
import pandas as pd
import datetime
import os

def run_script(request):
    cities = ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"]  # Change these to your desired cities
    weather = OpenWeather()
    df = weather.get_cities_current_weather_df(cities)

    # Save to CSV in memory
    csv_data = df.to_csv(index=False)

    # GCS upload
    bucket_name = os.environ["GCS_BUCKET"]
    folder = "raw_weather_data"
    timestamp = datetime.datetime.now(tz=weather.tz).strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{folder}/weather_{timestamp}.csv"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(csv_data, content_type="text/csv")

    return f"Uploaded file {filename} to bucket {bucket_name}.", 200