from datetime import date

import httpx

from meteo.exceptions import ApiError, ApiResponseError, NetworkError
from meteo.models.location import Location
from meteo.models.weather import CurrentWeather, DailyForecast, WeatherReport

_WEATHER_URL = 'https://api.open-meteo.com/v1/forecast'

_CURRENT_FIELDS = ','.join([
    'temperature_2m',
    'apparent_temperature',
    'relative_humidity_2m',
    'wind_speed_10m',
    'weather_code',
])

_DAILY_FIELDS = ','.join([
    'temperature_2m_max',
    'temperature_2m_min',
    'precipitation_sum',
    'weather_code',
])


class WeatherRepository:
    """Recupera i dati meteo attuali e le previsioni da Open-Meteo."""

    def __init__(self, timeout: float = 10.0, forecast_days: int = 7) -> None:
        self._timeout = timeout
        self._forecast_days = forecast_days

    def get_weather(self, location: Location) -> WeatherReport:
        """Recupera meteo attuale e previsioni per una Location.

        Raises:
            NetworkError: per timeout o problemi di connessione.
            ApiError: se l'API risponde con un codice HTTP di errore.
            ApiResponseError: se la risposta ha una struttura inattesa.
        """
        data = self._fetch(location)
        return self._parse(location, data)

    def _fetch(self, location: Location) -> dict:
        try:
            with httpx.Client(timeout=self._timeout, verify=True) as client:
                response = client.get(
                    _WEATHER_URL,
                    params={
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'current': _CURRENT_FIELDS,
                        'daily': _DAILY_FIELDS,
                        'timezone': location.timezone,
                        'forecast_days': self._forecast_days,
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise NetworkError(
                'Timeout: il server meteo non risponde.') from exc
        except httpx.ConnectError as exc:
            raise NetworkError(
                'Impossibile connettersi al server meteo.'
                ' Verifica la connessione.') from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise ApiError(
                f'Il server meteo ha risposto con errore {status}.') from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f'Errore di rete inatteso: {exc}') from exc

    @staticmethod
    def _parse(location: Location, data: dict) -> WeatherReport:
        try:
            current = WeatherRepository._parse_current(data['current'])
            forecast = WeatherRepository._parse_forecast(data['daily'])
            return WeatherReport(
                location=location, current=current, forecast=forecast)
        except (KeyError, TypeError, IndexError, ValueError) as exc:
            raise ApiResponseError(
                'Risposta inattesa dal server meteo.') from exc

    @staticmethod
    def _parse_current(raw: dict) -> CurrentWeather:
        return CurrentWeather(
            temperature=raw['temperature_2m'],
            apparent_temperature=raw['apparent_temperature'],
            humidity=raw['relative_humidity_2m'],
            wind_speed=raw['wind_speed_10m'],
            weather_code=raw['weather_code'],
        )

    @staticmethod
    def _parse_forecast(raw: dict) -> list[DailyForecast]:
        return [
            DailyForecast(
                date=date.fromisoformat(raw['time'][i]),
                temp_max=raw['temperature_2m_max'][i],
                temp_min=raw['temperature_2m_min'][i],
                precipitation=raw['precipitation_sum'][i] or 0.0,
                weather_code=raw['weather_code'][i],
            )
            for i in range(len(raw['time']))
        ]
