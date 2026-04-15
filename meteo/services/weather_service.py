from meteo.cache import WeatherCache
from meteo.exceptions import InvalidCityInputError  # noqa: F401 (re-export)
from meteo.models.weather import WeatherReport
from meteo.repositories.geocoding_repository import GeocodingRepository
from meteo.repositories.weather_repository import WeatherRepository
from meteo.validators import validate_city_name


class WeatherService:
    """Coordina geocoding e recupero meteo esponendo un'unica interfaccia."""

    def __init__(self) -> None:
        self._geocoding = GeocodingRepository()
        self._weather = WeatherRepository()
        self._cache = WeatherCache()

    def get_report(self, city: str, use_cache: bool = True) -> WeatherReport:
        """Restituisce il report meteo completo per una città.

        Controlla prima la cache locale (TTL 1 ora). Se i dati sono ancora
        validi li restituisce senza chiamare le API. Altrimenti recupera
        i dati freschi e li salva in cache.

        Raises:
            InvalidCityInputError: se il nome della città non è valido.
            CityNotFoundError: se la città non viene trovata dall'API.
            NetworkError: per timeout o problemi di connessione.
            ApiError: se l'API risponde con un codice HTTP di errore.
            ApiResponseError: se la risposta ha una struttura inattesa.
        """
        city = validate_city_name(city)
        if use_cache:
            cached = self._cache.get(city)
            if cached:
                return cached
        location = self._geocoding.get_location(city)
        report = self._weather.get_weather(location)
        if use_cache:
            self._cache.set(city, report)
        return report
