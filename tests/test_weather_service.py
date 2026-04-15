"""Test di WeatherService: coordinamento tra repository (con mock)."""
from datetime import date
from unittest.mock import patch

import pytest

from meteo.exceptions import CityNotFoundError, InvalidCityInputError, NetworkError
from meteo.models.location import Location
from meteo.models.weather import CurrentWeather, DailyForecast, WeatherReport
from meteo.services.weather_service import WeatherService

_GEO_PATH = 'meteo.services.weather_service.GeocodingRepository'
_WEATHER_PATH = 'meteo.services.weather_service.WeatherRepository'
_CACHE_PATH = 'meteo.services.weather_service.WeatherCache'


@pytest.fixture
def sample_location() -> Location:
    return Location(
        name='Roma', latitude=41.89, longitude=12.48,
        country='Italia', timezone='Europe/Rome')


@pytest.fixture
def sample_report(sample_location) -> WeatherReport:
    return WeatherReport(
        location=sample_location,
        current=CurrentWeather(
            temperature=20.5, apparent_temperature=18.0,
            humidity=60, wind_speed=15.0, weather_code=0),
        forecast=[
            DailyForecast(
                date=date(2026, 3, 28), temp_max=22.0,
                temp_min=10.0, precipitation=0.0, weather_code=0)])


class TestWeatherService:
    def test_get_report_calls_geocoding_then_weather(
            self, sample_location, sample_report):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                with patch(_WEATHER_PATH) as mock_weather_cls:
                    mock_cache_cls.return_value.get.return_value = None
                    mock_geo_cls.return_value.get_location.return_value = (
                        sample_location)
                    mock_weather_cls.return_value.get_weather.return_value = (
                        sample_report)

                    service = WeatherService()
                    result = service.get_report('Roma')

                    mock_geo_cls.return_value.get_location.assert_called_once_with(
                        'Roma')
                    get_weather = mock_weather_cls.return_value.get_weather
                    get_weather.assert_called_once_with(sample_location)
                    assert result == sample_report

    def test_get_report_propagates_city_not_found(self):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                mock_cache_cls.return_value.get.return_value = None
                mock_geo_cls.return_value.get_location.side_effect = (
                    CityNotFoundError('XYZ'))

                service = WeatherService()

                with pytest.raises(CityNotFoundError):
                    service.get_report('XYZ')

    def test_get_report_propagates_network_error(self):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                mock_cache_cls.return_value.get.return_value = None
                mock_geo_cls.return_value.get_location.side_effect = (
                    NetworkError('timeout'))

                service = WeatherService()

                with pytest.raises(NetworkError):
                    service.get_report('Roma')

    def test_get_report_rejects_invalid_input_before_network(self):
        with patch(_CACHE_PATH):
            with patch(_GEO_PATH) as mock_geo_cls:
                service = WeatherService()

                with pytest.raises(InvalidCityInputError):
                    service.get_report('Roma1')

                mock_geo_cls.return_value.get_location.assert_not_called()

    def test_get_report_strips_whitespace_before_geocoding(
            self, sample_location, sample_report):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                with patch(_WEATHER_PATH) as mock_weather_cls:
                    mock_cache_cls.return_value.get.return_value = None
                    mock_geo_cls.return_value.get_location.return_value = (
                        sample_location)
                    mock_weather_cls.return_value.get_weather.return_value = (
                        sample_report)

                    WeatherService().get_report('  Roma  ')

                    mock_geo_cls.return_value.get_location.assert_called_once_with(
                        'Roma')

    def test_get_report_passes_location_to_weather_repo(
            self, sample_location, sample_report):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                with patch(_WEATHER_PATH) as mock_weather_cls:
                    mock_cache_cls.return_value.get.return_value = None
                    mock_geo_cls.return_value.get_location.return_value = (
                        sample_location)
                    mock_weather_cls.return_value.get_weather.return_value = (
                        sample_report)

                    service = WeatherService()
                    service.get_report('Roma')

                    # Verifica che la location dal geocoding sia passata al repo
                    passed = (
                        mock_weather_cls.return_value.get_weather.call_args[0][0])
                    assert passed.name == 'Roma'
                    assert passed.latitude == 41.89

    def test_get_report_returns_cached_data_without_calling_api(
            self, sample_report):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                mock_cache_cls.return_value.get.return_value = sample_report

                service = WeatherService()
                result = service.get_report('Roma')

                assert result == sample_report
                mock_geo_cls.return_value.get_location.assert_not_called()

    def test_get_report_bypasses_cache_when_use_cache_false(
            self, sample_location, sample_report):
        with patch(_CACHE_PATH) as mock_cache_cls:
            with patch(_GEO_PATH) as mock_geo_cls:
                with patch(_WEATHER_PATH) as mock_weather_cls:
                    mock_geo_cls.return_value.get_location.return_value = (
                        sample_location)
                    mock_weather_cls.return_value.get_weather.return_value = (
                        sample_report)

                    WeatherService().get_report('Roma', use_cache=False)

                    mock_cache_cls.return_value.get.assert_not_called()
                    mock_geo_cls.return_value.get_location.assert_called_once()
