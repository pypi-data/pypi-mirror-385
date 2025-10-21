"""
Tests for timeout error handling in DMM client.
"""

# pylint: disable=protected-access

from unittest.mock import patch

import pytest
import requests

from py_dmmjp.client import DMMClient
from py_dmmjp.exceptions import DMMAPIError


class TestDMMClientTimeoutErrors:
    """Test timeout error scenarios."""

    @pytest.fixture
    def client(self) -> DMMClient:
        """Create a DMM client instance for testing."""

        return DMMClient(api_key="test_key", affiliate_id="test_id", timeout=1)

    def test_timeout_with_custom_timeout_value(self) -> None:
        """Test client with custom timeout value."""

        client = DMMClient(api_key="test_key", affiliate_id="test_id", timeout=5)

        assert client._timeout == 5

        with patch.object(
            client._session, "get", side_effect=requests.exceptions.Timeout()
        ):
            with pytest.raises(DMMAPIError, match="Request timed out"):
                client.get_products(site="FANZA", service="digital", floor="videoa")
