"""Test dei modelli Pydantic: validazione dati e costruzione oggetti."""
from datetime import date

import pytest
from pydantic import ValidationError

from meteo.models.location import Location
from meteo.models.weather import CurrentWeather, DailyForecast, WeatherReport


class TestLocation:
    def test_valid_location(self):
        loc = Location(
            name='Roma',
            latitude=41.89,
            longitude=12.48,
            country='Italia',
            timezone='Europe/Rome',
        )
        assert loc.name == 'Roma'
        assert loc.latitude == 41.89

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            Location(  # type: ignore[call-arg]
                name='Roma', latitude=41.89,
                longitude=12.48, country='Italia')


class TestCurrentWeather:
    def test_valid_current_weather(self):
        cw = CurrentWeather(
            temperature=20.5,
            apparent_temperature=18.0,
            humidity=60,
            wind_speed=15.0,
            weather_code=0,
        )
        assert cw.temperature == 20.5
        assert cw.humidity == 60

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            CurrentWeather(
                temperature='caldo',  # type: ignore[arg-type]
                apparent_temperature=18.0,
                humidity=60,
                wind_speed=15.0,
                weather_code=0,
            )


class TestDailyForecast:
    def test_valid_forecast(self):
        df = DailyForecast(
            date=date(2026, 3, 28),
            temp_max=22.0,
            temp_min=10.0,
            precipitation=0.0,
            weather_code=0,
        )
        assert df.temp_max == 22.0
        assert df.date == date(2026, 3, 28)


class TestWeatherReport:
    def test_valid_report(
            self, sample_location, sample_current, sample_forecasts):
        report = WeatherReport(
            location=sample_location,
            current=sample_current,
            forecast=sample_forecasts,
        )
        assert report.location.name == 'Roma'
        assert len(report.forecast) == 2
        assert report.current.temperature == 20.5

    def test_empty_forecast_list_is_valid(
            self, sample_location, sample_current):
        report = WeatherReport(
            location=sample_location,
            current=sample_current,
            forecast=[],
        )
        assert report.forecast == []


# --- Fixtures condivise ---

@pytest.fixture
def sample_location() -> Location:
    return Location(
        name='Roma',
        latitude=41.89,
        longitude=12.48,
        country='Italia',
        timezone='Europe/Rome',
    )


@pytest.fixture
def sample_current() -> CurrentWeather:
    return CurrentWeather(
        temperature=20.5,
        apparent_temperature=18.0,
        humidity=60,
        wind_speed=15.0,
        weather_code=0,
    )


@pytest.fixture
def sample_forecasts() -> list[DailyForecast]:
    return [
        DailyForecast(
            date=date(2026, 3, 28), temp_max=22.0,
            temp_min=10.0, precipitation=0.0, weather_code=0),
        DailyForecast(
            date=date(2026, 3, 29), temp_max=19.0,
            temp_min=8.0, precipitation=2.5, weather_code=61),
    ]
