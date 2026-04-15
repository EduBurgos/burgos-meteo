# Mapping WMO Weather interpretation codes → (descrizione italiana, emoji)
# https://open-meteo.com/en/docs#weathervariables

_CODES: dict[int, tuple[str, str]] = {
    0:  ('Cielo sereno',             '☀️ '),
    1:  ('Prevalentemente sereno',   '🌤️ '),
    2:  ('Parzialmente nuvoloso',    '⛅ '),
    3:  ('Nuvoloso',                 '☁️ '),
    45: ('Nebbia',                   '🌫️ '),
    48: ('Nebbia con brina',         '🌫️ '),
    51: ('Pioggerella leggera',      '🌦️ '),
    53: ('Pioggerella moderata',     '🌦️ '),
    55: ('Pioggerella fitta',        '🌧️ '),
    61: ('Pioggia leggera',          '🌧️ '),
    63: ('Pioggia moderata',         '🌧️ '),
    65: ('Pioggia forte',            '🌧️ '),
    71: ('Neve leggera',             '🌨️ '),
    73: ('Neve moderata',            '❄️ '),
    75: ('Neve forte',               '❄️ '),
    77: ('Granuli di neve',          '🌨️ '),
    80: ('Rovesci leggeri',          '🌦️ '),
    81: ('Rovesci moderati',         '🌧️ '),
    82: ('Rovesci violenti',         '⛈️ '),
    85: ('Rovesci di neve leggeri',  '🌨️ '),
    86: ('Rovesci di neve forti',    '❄️ '),
    95: ('Temporale',                '⛈️ '),
    96: ('Temporale con grandine',   '⛈️ '),
    99: ('Temporale, grandine forte','⛈️ '),
}

_FALLBACK = ('Condizioni sconosciute', '❓ ')


def get_description(code: int) -> str:
    return _CODES.get(code, _FALLBACK)[0]


def get_icon(code: int) -> str:
    return _CODES.get(code, _FALLBACK)[1]
