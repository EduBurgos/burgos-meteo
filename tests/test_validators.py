"""Test di validate_city_name: casi validi, invalidi e normalizzazione."""
import pytest

from meteo.exceptions import InvalidCityInputError
from meteo.validators import validate_city_name


class TestValidInput:
    @pytest.mark.parametrize('city, expected', [
        ('Roma',              'Roma'),
        ('  Roma  ',          'Roma'),       # strip spazi
        ('New York',          'New York'),   # spazio interno
        ("L'Aquila",          "L'Aquila"),   # apostrofo
        ('Reggio-Emilia',     'Reggio-Emilia'),  # trattino
        ('St. Louis',         'St. Louis'),  # punto
        ('Frankfurt am Main', 'Frankfurt am Main'),
        ('Köln',              'Köln'),       # umlaut tedesco
        ('Łódź',              'Łódź'),       # caratteri polacchi
        ('ab',                'ab'),         # lunghezza minima esatta
    ])
    def test_valid_city_names_are_accepted(self, city, expected):
        assert validate_city_name(city) == expected

    def test_strips_leading_and_trailing_whitespace(self):
        assert validate_city_name('  Milano  ') == 'Milano'

    def test_returns_normalized_string(self):
        result = validate_city_name('  Torino  ')
        assert isinstance(result, str)
        assert not result.startswith(' ')
        assert not result.endswith(' ')


class TestEmptyAndWhitespace:
    def test_empty_string_raises(self):
        with pytest.raises(InvalidCityInputError, match='vuoto'):
            validate_city_name('')

    def test_whitespace_only_raises(self):
        with pytest.raises(InvalidCityInputError, match='vuoto'):
            validate_city_name('   ')

    def test_tab_only_raises(self):
        with pytest.raises(InvalidCityInputError, match='vuoto'):
            validate_city_name('\t')


class TestLengthConstraints:
    def test_single_char_raises(self):
        with pytest.raises(InvalidCityInputError, match='almeno'):
            validate_city_name('R')

    def test_exactly_min_length_is_valid(self):
        assert validate_city_name('Ro') == 'Ro'

    def test_exactly_max_length_is_valid(self):
        assert validate_city_name('A' * 100) == 'A' * 100

    def test_over_max_length_raises(self):
        with pytest.raises(InvalidCityInputError, match='superare'):
            validate_city_name('A' * 101)


class TestInvalidCharacters:
    @pytest.mark.parametrize('city', [
        '123',           # solo cifre
        'Roma1',         # lettera + cifra
        'Roma!',         # punto esclamativo
        'Roma@city',     # chiocciola
        'Roma#',         # cancelletto
        'Roma$',         # dollaro
        'C1tà',          # cifra nel mezzo
    ])
    def test_invalid_chars_raise(self, city):
        with pytest.raises(InvalidCityInputError):
            validate_city_name(city)

    def test_error_message_contains_invalid_char(self):
        with pytest.raises(InvalidCityInputError, match='non validi'):
            validate_city_name('Roma!')

    def test_only_numbers_raises(self):
        with pytest.raises(InvalidCityInputError):
            validate_city_name('12345')


class TestNoAlphabeticCharacter:
    @pytest.mark.parametrize('city', [
        '---',
        "'''",
        '...',
        '- -',
    ])
    def test_no_letter_raises(self, city):
        with pytest.raises(InvalidCityInputError, match='lettera'):
            validate_city_name(city)


class TestExceptionHierarchy:
    def test_invalid_city_input_error_is_value_error(self):
        with pytest.raises(ValueError):
            validate_city_name('')

    def test_invalid_city_input_error_is_meteo_error(self):
        from meteo.exceptions import MeteoError
        with pytest.raises(MeteoError):
            validate_city_name('')
