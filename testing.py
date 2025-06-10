import pandas as pd
from city_feed import CityFeed
from open_weather import OpenWeather

city_feed = CityFeed()
data_city = city_feed.get_city_data_df("Toulouse")

open_weather = OpenWeather()
data_weather = open_weather.get_daily_weather_df(43.6043, 1.4437, "2023-10-01")