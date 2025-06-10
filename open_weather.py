import pandas as pd
import requests
from dotenv import dotenv_values

class OpenWeather:
    def __init__(self):
        self.api_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.env_var = dotenv_values(".env")
        self.api_token = self.env_var["open_weather_apikey"]

    def get_daily_weather(self, lat, lon, date):
        """
        Fetches daily weather data for a given latitude and longitude.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.
            date (int): The date for which to fetch the weather data.

        Returns:
            dict: The daily weather data for the specified location.
        """
        url = f"{self.api_url}/day_summary?lat={lat}&lon={lon}&date={date}&appid={self.api_token}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise ConnectionError(f"Failed to connect to API: {response.text}")

    def get_daily_weather_df(self, lat, lon, date):
        """
        Fetches daily weather data for a given latitude and longitude and converts it to a DataFrame.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.
            date (int): The date for which to fetch the weather data.

        Returns:
            pd.DataFrame: A DataFrame containing the daily weather data for the specified location.
        """
        data = self.get_daily_weather(lat, lon, date)
        df = pd.DataFrame(data)
        df['lat'] = lat
        df['lon'] = lon
        return df