import pandas as pd
import requests
import os
from datetime import datetime,timedelta, tzinfo
from concurrent.futures import ThreadPoolExecutor, as_completed

class Mytz(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=2)  # UTC+2 for Paris
    def dst(self, dt):
        return timedelta(hours=1)  # Assume DST is 1 hour

class OpenWeather:
    def __init__(self):
        self.historical_api_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.current_api_url = "https://api.openweathermap.org/data/2.5"
        self.geo_api_url = "https://api.openweathermap.org/geo/1.0"
        self.api_token = os.environ["OPENWEATHER_APIKEY"]
        self.tz = Mytz()

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
        url = f"{self.historical_api_url}/day_summary?lat={lat}&lon={lon}&date={date}&appid={self.api_token}&units=metric"
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

    def get_time_frame_weather_df(self, lat, lon, start_date, end_date):
        """
        Fetches weather data for a given latitude and longitude over a specified time frame.
        Uses multithreading to speed up API calls (I/O-bound).
        """
        date_range = pd.date_range(start=start_date, end=end_date)

        def fetch(date):
            return self.get_daily_weather_df(lat, lon, date.strftime('%Y-%m-%d'))

        weather_data = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks
            future_to_date = {executor.submit(fetch, date): date for date in date_range}
            for future in as_completed(future_to_date):
                try:
                    daily_data = future.result()
                    weather_data.append(daily_data)
                except Exception as e:
                    print(f"Error fetching data for {future_to_date[future]}: {e}")

        return pd.concat(weather_data, ignore_index=True) if weather_data else pd.DataFrame()

    def get_current_weather(self, lat, lon):
        """
               Fetches current weather data for a given latitude and longitude.

               Args:
                   lat (float): The latitude of the location.
                   lon (float): The longitude of the location.

               Returns:
                   dict: The daily weather data for the specified location.
               """
        url = f"{self.current_api_url}/weather?lat={lat}&lon={lon}&appid={self.api_token}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Extract relevant data
            data = extract_weather_data(data)
            return data
        else:
            raise ConnectionError(f"Failed to connect to API: {response.text}")

    def get_current_weather_df(self, lat, lon):
        """
                Fetches current weather data for a given latitude and longitude and converts it to a DataFrame.

                Args:
                    lat (float): The latitude of the location.
                    lon (float): The longitude of the location.

                Returns:
                    pd.DataFrame: A DataFrame containing the daily weather data for the specified location.
                """
        data = self.get_current_weather(lat, lon)
        df = pd.DataFrame(data)
        df['lat'] = lat
        df['lon'] = lon
        return df

    def get_cities_current_weather_df(self, cities: list):
        """
        Fetches current weather data for a given list of cities using multithreading.

        :param cities: List of city names.
        :return: Pandas DataFrame with weather data.
        """

        def fetch(city):
            try:
                city_data = self.get_city_coords(city)
                if city_data:
                    lat = city_data['lat']
                    lon = city_data['lon']
                    df = self.get_current_weather_df(lat, lon)
                    df['city'] = city
                    return df
                else:
                    print(f"City {city} not found.")
            except Exception as e:
                print(f"Error fetching weather for {city}: {e}")
            return None

        weather_data = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch, city): city for city in cities}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    weather_data.append(result)

        return pd.concat(weather_data, ignore_index=True) if weather_data else pd.DataFrame()

    def get_city_coords(self, city : str, country : str = "FR"):

        url = f"{self.geo_api_url}/direct?q={city},,{country}&limit={1}&appid={self.api_token}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        else:
            raise ConnectionError(f"Failed to connect to API: {response.text}")

def extract_weather_data(data: dict) -> pd.DataFrame:
    timezone_offset = data.get('timezone', 0)  # in seconds
    tz_delta = timedelta(seconds=timezone_offset)

    def to_local_time(utc_ts):
        if utc_ts is not None:
            return pd.to_datetime(utc_ts, unit='s') + tz_delta
        return None

    extracted = {
        'city': data.get('name'),
        'lat': data.get('coord', {}).get('lat'),
        'lon': data.get('coord', {}).get('lon'),
        'temp': data.get('main', {}).get('temp'),
        'feels_like': data.get('main', {}).get('feels_like'),
        'temp_min': data.get('main', {}).get('temp_min'),
        'temp_max': data.get('main', {}).get('temp_max'),
        'pressure': data.get('main', {}).get('pressure'),
        'humidity': data.get('main', {}).get('humidity'),
        'sea_level': data.get('main', {}).get('sea_level'),
        'grnd_level': data.get('main', {}).get('grnd_level'),
        'visibility': data.get('visibility'),
        'wind_speed': data.get('wind', {}).get('speed'),
        'wind_deg': data.get('wind', {}).get('deg'),
        'clouds': data.get('clouds', {}).get('all'),
        'weather_main': data.get('weather', [{}])[0].get('main'),
        'weather_description': data.get('weather', [{}])[0].get('description'),
        'weather_icon': data.get('weather', [{}])[0].get('icon'),
        'timestamp_utc': pd.to_datetime(data.get('dt'), unit='s'),
        'timestamp_local': to_local_time(data.get('dt')),
        'sunrise_local': to_local_time(data.get('sys', {}).get('sunrise')),
        'sunset_local': to_local_time(data.get('sys', {}).get('sunset')),
        'country': data.get('sys', {}).get('country')
    }

    return pd.DataFrame([extracted])