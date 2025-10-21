"""
Integration tests for DMM client with real API requests.
"""

# pylint: disable=redefined-outer-name,import-outside-toplevel


import os

import pytest

from py_dmmjp.client import DMMClient
from py_dmmjp.exceptions import DMMAuthError


@pytest.mark.integration
class TestDMMClientAuthenticationErrors:
    """Test authentication error scenarios."""

    def test_invalid_api_key(self):
        """Test client with invalid API key."""

        with pytest.raises(DMMAuthError):
            DMMClient(api_key="", affiliate_id="valid_id")

    def test_invalid_affiliate_id(self):
        """Test client with invalid affiliate ID."""

        with pytest.raises(DMMAuthError):
            DMMClient(api_key="valid_key", affiliate_id="")

    def test_both_invalid_credentials(self):
        """Test client with both invalid credentials."""

        with pytest.raises(DMMAuthError):
            DMMClient(api_key="", affiliate_id="")


@pytest.mark.integration
class TestDMMClientEnvironmentVariables:
    """Test environment variable handling."""

    def test_env_file_support(
        self,
    ):
        """Test loading credentials from .env file."""

        try:
            from dotenv import load_dotenv
        except ImportError:
            pytest.skip("python-dotenv not installed")

        original_dir = os.getcwd()
        try:
            load_dotenv()

            app_id = os.getenv("APP_ID")
            aff_id = os.getenv("AFF_ID")

            assert app_id is not None
            assert aff_id is not None

        finally:
            os.chdir(original_dir)

    def test_environment_variable_precedence(self):
        """Test that environment variables are properly loaded."""

        app_id = os.getenv("APP_ID")
        aff_id = os.getenv("AFF_ID")

        if app_id and aff_id:
            client = DMMClient(api_key=app_id, affiliate_id=aff_id)
            assert client.app_id == app_id
            assert client.affiliate_id == aff_id
        else:
            pytest.skip("Environment variables APP_ID and AFF_ID not set")
