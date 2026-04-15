"""Cache su file per i dati meteo (TTL: 1 ora)."""
import json
import time
from pathlib import Path

from pydantic import ValidationError

from meteo.models.weather import WeatherReport

_CACHE_FILE = Path.home() / '.meteo_cache.json'
_TTL = 3600  # secondi


class WeatherCache:
    """Salva e recupera WeatherReport da un file JSON locale."""

    def get(self, city: str) -> WeatherReport | None:
        """Restituisce il report in cache se ancora valido, altrimenti None."""
        entry = self._load().get(city.lower())
        if entry and time.time() - entry['timestamp'] < _TTL:
            try:
                return WeatherReport.model_validate(entry['report'])
            except (ValidationError, KeyError, TypeError):
                return None
        return None

    def set(self, city: str, report: WeatherReport) -> None:
        """Salva il report in cache con il timestamp corrente."""
        data = self._load()
        data[city.lower()] = {
            'timestamp': time.time(),
            'report': report.model_dump(mode='json'),
        }
        _CACHE_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    def _load(self) -> dict:
        try:
            return json.loads(_CACHE_FILE.read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
