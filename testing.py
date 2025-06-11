import pandas as pd
from city_feed import CityFeed
from open_weather import OpenWeather

#city_feed = CityFeed()
#data_city = city_feed.get_city_data_df("Toulouse")

open_weather = OpenWeather()
data_weather = open_weather.get_current_weather(43.6043, 1.4437)

data = open_weather.get_cities_current_weather_df(["Paris", "Marseille", "Lyon", "Toulouse", "Nice"])