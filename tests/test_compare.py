"""Test del comando compare: fetch parallelo e gestione errori per città."""
from datetime import date
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from meteo.cli import app
from meteo.exceptions import CityNotFoundError, NetworkError
from meteo.models.location import Location
from meteo.models.weather import CurrentWeather, DailyForecast, WeatherReport

_SERVICE_PATH = 'meteo.cli._service'

runner = CliRunner()


def _make_report(name: str, country: str, temp: float) -> WeatherReport:
    return WeatherReport(
        location=Location(
            name=name, latitude=0.0, longitude=0.0,
            country=country, timezone='Europe/Rome'),
        current=CurrentWeather(
            temperature=temp, apparent_temperature=temp - 2,
            humidity=60, wind_speed=10.0, weather_code=0),
        forecast=[
            DailyForecast(
                date=date(2026, 4, 14), temp_max=temp + 2,
                temp_min=temp - 5, precipitation=0.0, weather_code=0)
        ],
    )


class TestCompareCommand:
    def test_compare_two_cities_exits_ok(self):
        roma = _make_report('Roma', 'Italia', 20.0)
        milano = _make_report('Milano', 'Italia', 15.0)

        with patch(_SERVICE_PATH) as mock_service:
            mock_service.get_report.side_effect = lambda city, **_: (
                roma if city == 'Roma' else milano)

            result = runner.invoke(app, ['compare', 'Roma', 'Milano'])

        assert result.exit_code == 0

    def test_compare_shows_city_names(self):
        roma = _make_report('Roma', 'Italia', 20.0)
        milano = _make_report('Milano', 'Italia', 15.0)

        with patch(_SERVICE_PATH) as mock_service:
            mock_service.get_report.side_effect = lambda city, **_: (
                roma if city == 'Roma' else milano)

            result = runner.invoke(app, ['compare', 'Roma', 'Milano'])

        assert 'Roma' in result.output
        assert 'Milano' in result.output

    def test_compare_single_city_exits_with_error(self):
        result = runner.invoke(app, ['compare', 'Roma'])
        assert result.exit_code == 1

    def test_compare_skips_invalid_city_and_continues(self):
        roma = _make_report('Roma', 'Italia', 20.0)
        milano = _make_report('Milano', 'Italia', 15.0)

        def side_effect(city, **_):
            if city == 'XYZ123':
                raise CityNotFoundError('XYZ123')
            return roma if city == 'Roma' else milano

        with patch(_SERVICE_PATH) as mock_service:
            mock_service.get_report.side_effect = side_effect

            result = runner.invoke(app, ['compare', 'Roma', 'Milano', 'XYZ123'])

        assert 'Roma' in result.output
        assert 'Milano' in result.output

    def test_compare_fails_if_fewer_than_two_valid_cities(self):
        def side_effect(city, **_):
            raise CityNotFoundError(city)

        with patch(_SERVICE_PATH) as mock_service:
            mock_service.get_report.side_effect = side_effect

            result = runner.invoke(app, ['compare', 'AAA', 'BBB'])

        assert result.exit_code == 1

    def test_compare_no_cache_flag_passed_to_service(self):
        roma = _make_report('Roma', 'Italia', 20.0)
        milano = _make_report('Milano', 'Italia', 15.0)
        calls = []

        def side_effect(city, use_cache=True):
            calls.append(use_cache)
            return roma if city == 'Roma' else milano

        with patch(_SERVICE_PATH) as mock_service:
            mock_service.get_report.side_effect = side_effect
            runner.invoke(app, ['compare', 'Roma', 'Milano', '--no-cache'])

        assert all(use_cache is False for use_cache in calls)
