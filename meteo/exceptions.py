"""Gerarchia delle eccezioni dell'applicazione Meteo."""


class MeteoError(Exception):
    """Eccezione base per tutte le eccezioni dell'applicazione."""


class InvalidCityInputError(MeteoError, ValueError):
    """Il nome della città non ha superato la validazione dell'input."""


class CityNotFoundError(MeteoError):
    """La città non è stata trovata dall'API di geocoding."""


class NetworkError(MeteoError):
    """Errore di rete: timeout, connessione rifiutata o DNS non risolto."""


class ApiError(MeteoError):
    """L'API ha restituito un codice di errore HTTP (4xx / 5xx)."""


class ApiResponseError(MeteoError):
    """La risposta dell'API ha una struttura inattesa o dati mancanti."""
