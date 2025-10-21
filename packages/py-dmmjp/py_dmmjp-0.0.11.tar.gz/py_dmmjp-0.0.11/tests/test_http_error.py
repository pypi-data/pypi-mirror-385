"""
Tests for HTTP and request error handling in DMM client.
"""

# pylint: disable=protected-access
# mypy: disable-error-code="attr-defined"

from unittest.mock import Mock, patch

import pytest
import requests

from py_dmmjp.client import DMMClient
from py_dmmjp.exceptions import DMMAPIError, DMMAuthError


class TestDMMClientHTTPErrors:
    """Test HTTP error scenarios."""

    @pytest.fixture
    def client(self) -> DMMClient:
        """Create a DMM client instance for testing."""

        return DMMClient(api_key="test_key", affiliate_id="test_id", timeout=10)

    def test_http_error_401_unauthorized(self, client: DMMClient) -> None:
        """Test HTTP 401 unauthorized error."""

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAuthError, match="Invalid API key"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_403_forbidden(self, client: DMMClient) -> None:
        """Test HTTP 403 forbidden error."""

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAuthError, match="Access forbidden"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_404_not_found(self, client: DMMClient) -> None:
        """Test HTTP 404 not found error."""

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 404"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_500_internal_server_error(self, client: DMMClient) -> None:
        """Test HTTP 500 internal server error."""

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 500"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_502_bad_gateway(self, client: DMMClient) -> None:
        """Test HTTP 502 bad gateway error."""

        mock_response = Mock()
        mock_response.status_code = 502
        mock_response.text = "Bad Gateway"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 502"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_503_service_unavailable(self, client: DMMClient) -> None:
        """Test HTTP 503 service unavailable error."""

        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 503"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_504_gateway_timeout(self, client: DMMClient) -> None:
        """Test HTTP 504 gateway timeout error."""

        mock_response = Mock()
        mock_response.status_code = 504
        mock_response.text = "Gateway Timeout"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 504"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_400_bad_request(self, client: DMMClient) -> None:
        """Test HTTP 400 bad request error."""

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 400"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_429_too_many_requests(self, client: DMMClient) -> None:
        """Test HTTP 429 too many requests error."""

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 429"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_http_error_preserves_status_code(self, client: DMMClient) -> None:
        """Test that HTTP error preserves status code."""

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(site="FANZA", service="digital", floor="videoa")

            assert exc_info.value.status_code is not None
            assert exc_info.value.status_code == 500

    def test_http_error_preserves_response_data(self, client: DMMClient) -> None:
        """Test that HTTP error preserves response data."""

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error Details"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(site="FANZA", service="digital", floor="videoa")

            assert exc_info.value.response_data is not None
            assert exc_info.value.response_data == "Internal Server Error Details"

    def test_http_error_401_on_get_actresses(self, client: DMMClient) -> None:
        """Test HTTP 401 error when fetching actresses."""

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAuthError, match="Invalid API key"):
                client.get_actresses(keyword="test")

    def test_http_error_403_on_get_floors(self, client: DMMClient) -> None:
        """Test HTTP 403 error when fetching floors."""

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAuthError, match="Access forbidden"):
                client.get_floors()

    def test_http_error_500_on_get_genres(self, client: DMMClient) -> None:
        """Test HTTP 500 error when fetching genres."""

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 500"):
                client.get_genres(floor_id=43)

    def test_http_error_404_on_get_makers(self, client: DMMClient) -> None:
        """Test HTTP 404 error when fetching makers."""

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError, match="HTTP 404"):
                client.get_makers(floor_id=43)


class TestDMMClientRequestErrors:
    """Test generic request error scenarios."""

    @pytest.fixture
    def client(self) -> DMMClient:
        """Create a DMM client instance for testing."""

        return DMMClient(api_key="test_key", affiliate_id="test_id", timeout=10)

    def test_generic_request_exception(self, client: DMMClient) -> None:
        """Test generic request exception."""

        with patch.object(
            client._session,
            "get",
            side_effect=requests.exceptions.RequestException("Generic error"),
        ):
            with pytest.raises(DMMAPIError, match="Request failed"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_request_exception_with_custom_message(self, client: DMMClient) -> None:
        """Test request exception with custom error message."""

        error = requests.exceptions.RequestException("Custom request error")

        with patch.object(client._session, "get", side_effect=error):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(site="FANZA", service="digital", floor="videoa")

            assert "Request failed" in str(exc_info.value)
            assert "Custom request error" in str(exc_info.value)

    def test_request_exception_preserves_original_error(
        self, client: DMMClient
    ) -> None:
        """Test that request exception preserves the original exception."""

        original_error = requests.exceptions.RequestException("Original error")

        with patch.object(client._session, "get", side_effect=original_error):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(site="FANZA", service="digital", floor="videoa")

            assert exc_info.value.__cause__ is not None
            assert exc_info.value.__cause__ is original_error

    def test_invalid_json_response(self, client: DMMClient) -> None:
        """Test invalid JSON response."""

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON"
        mock_response.raise_for_status = Mock()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(
                DMMAPIError, match="Error while formatting DMM Response"
            ):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_malformed_json_response(self, client: DMMClient) -> None:
        """Test malformed JSON response."""

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"incomplete": "json"'
        mock_response.raise_for_status = Mock()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(
                DMMAPIError, match="Error while formatting DMM Response"
            ):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_empty_response(self, client: DMMClient) -> None:
        """Test empty response."""

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.raise_for_status = Mock()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(
                DMMAPIError, match="Error while formatting DMM Response"
            ):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_request_exception_on_get_series(self, client: DMMClient) -> None:
        """Test request exception when fetching series."""

        with patch.object(
            client._session,
            "get",
            side_effect=requests.exceptions.RequestException("Network error"),
        ):
            with pytest.raises(DMMAPIError, match="Request failed"):
                client.get_series(floor_id=27)

    def test_request_exception_on_get_authors(self, client: DMMClient) -> None:
        """Test request exception when fetching authors."""

        with patch.object(
            client._session,
            "get",
            side_effect=requests.exceptions.RequestException("Connection reset"),
        ):
            with pytest.raises(DMMAPIError, match="Request failed"):
                client.get_authors(floor_id=27)

    def test_invalid_json_on_get_actresses(self, client: DMMClient) -> None:
        """Test invalid JSON response when fetching actresses."""

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Not a JSON"
        mock_response.raise_for_status = Mock()

        with patch.object(client._session, "get", return_value=mock_response):
            with pytest.raises(
                DMMAPIError, match="Error while formatting DMM Response"
            ):
                client.get_actresses(keyword="test")

    def test_multiple_consecutive_errors(self, client: DMMClient) -> None:
        """Test multiple consecutive errors."""

        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.raise_for_status.side_effect = requests.exceptions.HTTPError()

        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.text = "Server Error"
        mock_response_500.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with patch.object(client._session, "get", return_value=mock_response_401):
            with pytest.raises(DMMAuthError):
                client.get_products(site="FANZA", service="digital", floor="videoa")

        with patch.object(client._session, "get", return_value=mock_response_500):
            with pytest.raises(DMMAPIError, match="HTTP 500"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.Timeout()
        ):
            with pytest.raises(DMMAPIError, match="Request timed out"):
                client.get_products(site="FANZA", service="digital", floor="videoa")
