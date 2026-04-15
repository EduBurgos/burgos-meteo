"""Test di GeocodingRepository: parsing risposta API e gestione errori."""
import pytest
import httpx
from pytest_httpx import HTTPXMock

from meteo.exceptions import ApiError, ApiResponseError, CityNotFoundError, NetworkError
from meteo.repositories.geocoding_repository import GeocodingRepository

_VALID_RESPONSE = {
    'results': [
        {
            'name': 'Roma',
            'latitude': 41.89474,
            'longitude': 12.48234,
            'country': 'Italia',
            'timezone': 'Europe/Rome',
        }
    ]
}


class TestGeocodingRepository:
    def setup_method(self):
        self.repo = GeocodingRepository()

    def test_returns_location_on_valid_response(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json=_VALID_RESPONSE)

        location = self.repo.get_location('Roma')

        assert location.name == 'Roma'
        assert location.latitude == pytest.approx(41.89474)
        assert location.longitude == pytest.approx(12.48234)
        assert location.country == 'Italia'
        assert location.timezone == 'Europe/Rome'

    def test_raises_city_not_found_when_empty_results(
            self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={'results': []})

        with pytest.raises(CityNotFoundError, match='XYZ'):
            self.repo.get_location('XYZ')

    def test_raises_city_not_found_when_no_results_key(
            self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={})

        with pytest.raises(CityNotFoundError):
            self.repo.get_location('CittàInesistente')

    def test_raises_api_error_on_http_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(status_code=500)

        with pytest.raises(ApiError, match='500'):
            self.repo.get_location('Roma')

    def test_raises_api_error_on_client_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(status_code=429)

        with pytest.raises(ApiError, match='429'):
            self.repo.get_location('Roma')

    def test_raises_network_error_on_timeout(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(httpx.TimeoutException('timeout'))

        with pytest.raises(NetworkError, match='Timeout'):
            self.repo.get_location('Roma')

    def test_raises_network_error_on_connect_error(
            self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(httpx.ConnectError('refused'))

        with pytest.raises(NetworkError, match='connettersi'):
            self.repo.get_location('Roma')

    def test_raises_api_response_error_on_missing_key(
            self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={'results': [{'name': 'Roma'}]})

        with pytest.raises(ApiResponseError):
            self.repo.get_location('Roma')

    def test_uses_only_first_result(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            json={
                'results': [
                    {'name': 'Roma', 'latitude': 41.89,
                     'longitude': 12.48, 'country': 'Italia',
                     'timezone': 'Europe/Rome'},
                    {'name': 'Roma', 'latitude': 35.0,
                     'longitude': 14.0, 'country': 'USA',
                     'timezone': 'America/New_York'},
                ]
            }
        )

        location = self.repo.get_location('Roma')

        assert location.country == 'Italia'

    def test_network_error_preserves_original_cause(
            self, httpx_mock: HTTPXMock):
        original = httpx.TimeoutException('timeout')
        httpx_mock.add_exception(original)

        with pytest.raises(NetworkError) as exc_info:
            self.repo.get_location('Roma')

        assert exc_info.value.__cause__ is original
