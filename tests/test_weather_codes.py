"""Test del mapping codici WMO → descrizione e icona."""
import pytest

from meteo.ui.weather_codes import get_description, get_icon


class TestGetDescription:
    @pytest.mark.parametrize('code, expected', [
        (0,  'Cielo sereno'),
        (1,  'Prevalentemente sereno'),
        (2,  'Parzialmente nuvoloso'),
        (3,  'Nuvoloso'),
        (45, 'Nebbia'),
        (61, 'Pioggia leggera'),
        (63, 'Pioggia moderata'),
        (71, 'Neve leggera'),
        (95, 'Temporale'),
    ])
    def test_known_codes_return_correct_description(self, code, expected):
        assert get_description(code) == expected

    def test_unknown_code_returns_fallback(self):
        assert get_description(9999) == 'Condizioni sconosciute'

    def test_returns_string(self):
        assert isinstance(get_description(0), str)


class TestGetIcon:
    @pytest.mark.parametrize('code', [0, 1, 2, 3, 45, 61, 71, 95])
    def test_known_codes_return_non_empty_icon(self, code):
        icon = get_icon(code)
        assert isinstance(icon, str)
        assert len(icon.strip()) > 0

    def test_unknown_code_returns_fallback_icon(self):
        assert '❓' in get_icon(9999)

    def test_sunny_icon(self):
        assert '☀' in get_icon(0)

    def test_thunderstorm_icon(self):
        assert '⛈' in get_icon(95)
