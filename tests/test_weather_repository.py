"""Test di WeatherRepository: parsing risposta API meteo e gestione errori."""
from datetime import date

import httpx
import pytest
from pytest_httpx import HTTPXMock

from meteo.exceptions import ApiError, ApiResponseError, NetworkError
from meteo.models.location import Location
from meteo.repositories.weather_repository import WeatherRepository

_VALID_RESPONSE = {
    'current': {
        'temperature_2m': 20.5,
        'apparent_temperature': 18.0,
        'relative_humidity_2m': 60,
        'wind_speed_10m': 15.0,
        'weather_code': 0,
    },
    'daily': {
        'time': ['2026-03-28', '2026-03-29'],
        'temperature_2m_max': [22.0, 19.0],
        'temperature_2m_min': [10.0, 8.0],
        'precipitation_sum': [0.0, 2.5],
        'weather_code': [0, 61],
    },
}


@pytest.fixture
def location() -> Location:
    return Location(
        name='Roma',
        latitude=41.89,
        longitude=12.48,
        country='Italia',
        timezone='Europe/Rome',
    )


class TestWeatherRepository:
    def setup_method(self):
        self.repo = WeatherRepository()

    def test_returns_report_with_correct_current_weather(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_response(json=_VALID_RESPONSE)

        report = self.repo.get_weather(location)

        assert report.current.temperature == 20.5
        assert report.current.apparent_temperature == 18.0
        assert report.current.humidity == 60
        assert report.current.wind_speed == 15.0
        assert report.current.weather_code == 0

    def test_returns_report_with_correct_forecast(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_response(json=_VALID_RESPONSE)

        report = self.repo.get_weather(location)

        assert len(report.forecast) == 2
        assert report.forecast[0].date == date(2026, 3, 28)
        assert report.forecast[0].temp_max == 22.0
        assert report.forecast[1].precipitation == 2.5
        assert report.forecast[1].weather_code == 61

    def test_precipitation_none_becomes_zero(
            self, httpx_mock: HTTPXMock, location):
        response = dict(_VALID_RESPONSE)
        response['daily'] = dict(_VALID_RESPONSE['daily'])
        response['daily']['precipitation_sum'] = [None, None]
        httpx_mock.add_response(json=response)

        report = self.repo.get_weather(location)

        assert report.forecast[0].precipitation == 0.0
        assert report.forecast[1].precipitation == 0.0

    def test_location_is_preserved_in_report(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_response(json=_VALID_RESPONSE)

        report = self.repo.get_weather(location)

        assert report.location.name == 'Roma'
        assert report.location.timezone == 'Europe/Rome'

    def test_raises_api_error_on_server_error(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_response(status_code=503)

        with pytest.raises(ApiError, match='503'):
            self.repo.get_weather(location)

    def test_raises_network_error_on_timeout(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_exception(httpx.TimeoutException('timeout'))

        with pytest.raises(NetworkError, match='Timeout'):
            self.repo.get_weather(location)

    def test_raises_network_error_on_connect_error(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_exception(httpx.ConnectError('refused'))

        with pytest.raises(NetworkError, match='connettersi'):
            self.repo.get_weather(location)

    def test_raises_api_response_error_on_missing_current_key(
            self, httpx_mock: HTTPXMock, location):
        httpx_mock.add_response(json={'daily': _VALID_RESPONSE['daily']})

        with pytest.raises(ApiResponseError):
            self.repo.get_weather(location)

    def test_raises_api_response_error_on_malformed_daily(
            self, httpx_mock: HTTPXMock, location):
        bad = dict(_VALID_RESPONSE)
        bad['daily'] = {'time': ['2026-03-28'], 'temperature_2m_max': []}
        httpx_mock.add_response(json=bad)

        with pytest.raises(ApiResponseError):
            self.repo.get_weather(location)

    def test_network_error_preserves_original_cause(
            self, httpx_mock: HTTPXMock, location):
        original = httpx.ConnectError('refused')
        httpx_mock.add_exception(original)

        with pytest.raises(NetworkError) as exc_info:
            self.repo.get_weather(location)

        assert exc_info.value.__cause__ is original
