from datetime import date

from pydantic import BaseModel

from meteo.models.location import Location


class CurrentWeather(BaseModel):
    temperature: float
    apparent_temperature: float
    humidity: int
    wind_speed: float
    weather_code: int


class DailyForecast(BaseModel):
    date: date
    temp_max: float
    temp_min: float
    precipitation: float
    weather_code: int


class WeatherReport(BaseModel):
    location: Location
    current: CurrentWeather
    forecast: list[DailyForecast]
