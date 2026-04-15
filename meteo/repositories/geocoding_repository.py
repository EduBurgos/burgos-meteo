import httpx

from meteo.exceptions import ApiError, ApiResponseError, CityNotFoundError, NetworkError
from meteo.models.location import Location

_GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'


class GeocodingRepository:
    """Recupera le coordinate geografiche dato il nome di una città."""

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def get_location(self, city: str) -> Location:
        """Converte il nome di una città in un oggetto Location con coordinate.

        Raises:
            CityNotFoundError: se la città non esiste nell'API.
            NetworkError: per timeout o problemi di connessione.
            ApiError: se l'API risponde con un codice HTTP di errore.
            ApiResponseError: se la risposta ha una struttura inattesa.
        """
        data = self._fetch(city)
        return self._parse(city, data)

    def _fetch(self, city: str) -> dict:
        try:
            with httpx.Client(timeout=self._timeout, verify=True) as client:
                response = client.get(
                    _GEOCODING_URL,
                    params={
                        'name': city,
                        'count': 1,
                        'language': 'it',
                        'format': 'json',
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise NetworkError(
                'Timeout: il server di geocoding non risponde.') from exc
        except httpx.ConnectError as exc:
            raise NetworkError(
                'Impossibile connettersi al server di geocoding.'
                ' Verifica la connessione.') from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise ApiError(
                f'Il server di geocoding ha risposto con errore {status}.'
            ) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f'Errore di rete inatteso: {exc}') from exc

    @staticmethod
    def _parse(city: str, data: dict) -> Location:
        try:
            results = data.get('results')
            if not results:
                raise CityNotFoundError(f"Città '{city}' non trovata.")
            r = results[0]
            return Location(
                name=r['name'],
                latitude=r['latitude'],
                longitude=r['longitude'],
                country=r.get('country', ''),
                timezone=r.get('timezone', 'auto'),
            )
        except CityNotFoundError:
            raise
        except (KeyError, TypeError, IndexError) as exc:
            raise ApiResponseError(
                'Risposta inattesa dal server di geocoding.') from exc
