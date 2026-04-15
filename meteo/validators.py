"""Validazione dell'input utente per i nomi di città."""
from meteo.exceptions import InvalidCityInputError

_MIN_LENGTH = 2
_MAX_LENGTH = 100
_ALLOWED_NON_ALPHA = frozenset(" -'.,")


def validate_city_name(city: str) -> str:
    """Valida e normalizza il nome della città.

    Applica strip degli spazi, controlla lunghezza e caratteri ammessi.
    I caratteri non alfabetici permessi sono: spazio, trattino, apostrofo,
    punto e virgola (es. 'L'Aquila', 'Reggio-Emilia', 'St. Louis').

    Args:
        city: il nome della città inserito dall'utente.

    Returns:
        Il nome della città normalizzato (strip applicato).

    Raises:
        InvalidCityInputError: se il nome non supera la validazione.
    """
    city = city.strip()

    if not city:
        raise InvalidCityInputError(
            'Il nome della città non può essere vuoto.')

    if len(city) < _MIN_LENGTH:
        raise InvalidCityInputError(
            f'Il nome deve contenere almeno {_MIN_LENGTH} caratteri.')

    if len(city) > _MAX_LENGTH:
        raise InvalidCityInputError(
            f'Il nome non può superare {_MAX_LENGTH} caratteri.')

    if not any(c.isalpha() for c in city):
        raise InvalidCityInputError(
            'Il nome della città deve contenere almeno una lettera.')

    invalid_chars = {
        c for c in city if not c.isalpha() and c not in _ALLOWED_NON_ALPHA
    }
    if invalid_chars:
        chars = ', '.join(sorted(repr(c) for c in invalid_chars))
        raise InvalidCityInputError(
            f'Caratteri non validi nel nome: {chars}.')

    return city
