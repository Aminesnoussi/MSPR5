import pandas as pd
import requests
from dotenv import dotenv_values

class CityFeed:
    def __init__(self):
        self.api_url = "https://api.waqi.info/feed"
        self.env_var = dotenv_values(".env")
        self.api_token = self.env_var["city_feed_apikey"]

    def get_city_data(self, city: str):
        """
        Fetches air quality data for a given city.

        Args:
            city (str): The name of the city to fetch data for.

        Returns:
            dict: The air quality data for the specified city.
        """
        url = f"{self.api_url}/{city}/?token={self.api_token}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ok':
                return data
            else:
                raise ValueError(f"Error fetching data: {data['data']}")
        else:
            raise ConnectionError(f"Failed to connect to API: {response.status_code}")

    def get_city_data_df(self, city: str):
        """
        Fetches air quality data for a given city and converts it to a DataFrame.

        Args:
            city (str): The name of the city to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the air quality data for the specified city.
        """
        data = self.get_city_data(city)
        df = pd.DataFrame(data['data']['iaqi'])
        df['city'] = city
        return df

    def get_point_data(self, lat, lon):
        """
        Fetches air quality data for a given latitude and longitude.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            dict: The air quality data for the specified location.
        """
        url = f"{self.api_url}/geo:{lat};{lon}/?token={self.api_token}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ok':
                return data
            else:
                raise ValueError(f"Error fetching data: {data['data']}")
        else:
            raise ConnectionError(f"Failed to connect to API: {response.status_code}")

    def get_point_data_df(self, lat, lon):
        """
        Fetches air quality data for a given latitude and longitude and converts it to a DataFrame.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            pd.DataFrame: A DataFrame containing the air quality data for the specified location.
        """
        data = self.get_point_data(lat, lon)
        df = pd.DataFrame(data['data']['iaqi'])
        df['location'] = f"{lat},{lon}"
        return df

    def get_cities_data_df(self, cities: list):
        """
        Fetches air quality data for multiple cities and converts it to a DataFrame.

        Args:
            cities (list): A list of city names to fetch data for.

        Returns:
            pd.DataFrame: A DataFrame containing the air quality data for the specified cities.
        """
        dfs = []
        for city in cities:
            df = self.get_city_data_df(city)
            dfs.append(df)
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
