"""
Tests for connection error handling in DMM client.
"""

# pylint: disable=protected-access
# mypy: disable-error-code="attr-defined"

from unittest.mock import patch

import pytest
import requests

from py_dmmjp.client import DMMClient
from py_dmmjp.exceptions import DMMAPIError


class TestDMMClientConnectionErrors:
    """Test connection error scenarios."""

    @pytest.fixture
    def client(self) -> DMMClient:
        """Create a DMM client instance for testing."""

        return DMMClient(api_key="test_key", affiliate_id="test_id", timeout=10)

    def test_connection_error_on_get_products(self, client: DMMClient) -> None:
        """Test connection error when fetching products."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

    def test_connection_error_on_get_actresses(self, client: DMMClient) -> None:
        """Test connection error when fetching actresses."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_actresses(keyword="test")

    def test_connection_error_on_get_floors(self, client: DMMClient) -> None:
        """Test connection error when fetching floors."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_floors()

    def test_connection_error_on_get_genres(self, client: DMMClient) -> None:
        """Test connection error when fetching genres."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_genres(floor_id=43)

    def test_connection_error_on_get_makers(self, client: DMMClient) -> None:
        """Test connection error when fetching makers."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_makers(floor_id=43)

    def test_connection_error_on_get_series(self, client: DMMClient) -> None:
        """Test connection error when fetching series."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_series(floor_id=27)

    def test_connection_error_on_get_authors(self, client: DMMClient) -> None:
        """Test connection error when fetching authors."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_authors(floor_id=27)

    def test_connection_error_on_get_product_by_cid(self, client: DMMClient) -> None:
        """Test connection error when fetching product by CID."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_product_by_cid(cid="test123", site="FANZA")

    def test_connection_error_on_get_product_by_product_id(
        self, client: DMMClient
    ) -> None:
        """Test connection error when fetching product by product ID."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_product_by_product_id(product_id="ABP-477", site="FANZA")

    def test_connection_error_with_custom_message(self, client: DMMClient) -> None:
        """Test connection error with custom error message."""

        error = requests.exceptions.ConnectionError("DNS resolution failed")

        with patch.object(client._session, "get", side_effect=error):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(site="FANZA", service="digital", floor="videoa")

            assert "Connection error occurred" in str(exc_info.value)

    def test_connection_error_preserves_original_exception(
        self, client: DMMClient
    ) -> None:
        """Test that connection error preserves the original exception."""

        original_error = requests.exceptions.ConnectionError("Network unreachable")

        with patch.object(client._session, "get", side_effect=original_error):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(site="FANZA", service="digital", floor="videoa")

            assert exc_info.value.__cause__ is not None
            assert exc_info.value.__cause__ is original_error

    def test_connection_error_during_retry(self, client: DMMClient) -> None:
        """Test connection error that occurs during retry attempts."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_actresses(keyword="test", hits=5)

    def test_connection_error_with_partial_data(self, client: DMMClient) -> None:
        """Test connection error with partial data received."""

        with patch.object(
            client._session,
            "get",
            side_effect=requests.exceptions.ConnectionError("Connection reset by peer"),
        ):
            with pytest.raises(DMMAPIError) as exc_info:
                client.get_products(
                    site="FANZA",
                    service="digital",
                    floor="videoa",
                    keyword="test",
                    hits=50,
                )

            assert "Connection error occurred" in str(exc_info.value)

    def test_multiple_connection_errors(self, client: DMMClient) -> None:
        """Test multiple consecutive connection errors."""

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_products(site="FANZA", service="digital", floor="videoa")

            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_actresses(keyword="test")

            with pytest.raises(DMMAPIError, match="Connection error occurred"):
                client.get_floors()
