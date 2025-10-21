"""Test configuration and fixtures."""

# pylint: disable=redefined-outer-name

import os

import pytest

from py_dmmjp import DMMClient


@pytest.fixture
def mock_api_key() -> str:
    """Provide a mock API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def mock_affiliate_key() -> str:
    """Provide a mock affiliate key for testing."""
    return "test_affiliate_key_67890"


@pytest.fixture
def mock_response_data() -> dict:
    """Provide mock response data from DMM API."""
    return {
        "result": {
            "total_count": 100,
            "items": [
                {
                    "content_id": "test123",
                    "title": "Test Product",
                    "comment": "Test description",
                    "prices": {"price": 1000},
                    "imageURL": {"large": "https://example.com/image.jpg"},
                    "floor_name": "digital",
                    "genre": ["action", "adventure"],
                },
                {
                    "content_id": "test456",
                    "title": "Another Product",
                    "comment": "Another description",
                    "prices": {"price": 2000},
                    "imageURL": {"large": "https://example.com/image2.jpg"},
                    "floor_name": "digital",
                    "genre": ["romance"],
                },
            ],
        }
    }


def get_env_or_skip(var_name: str) -> str:
    """Get environment variable or skip test if not found."""

    value = os.getenv(var_name)
    if not value:
        pytest.skip(f"Environment variable {var_name} not set")
    return value


@pytest.fixture
def app_id() -> str:
    """Get APP_ID from environment or skip test."""

    return get_env_or_skip("APP_ID")


@pytest.fixture
def aff_id() -> str:
    """Get AFF_ID from environment or skip test."""

    return get_env_or_skip("AFF_ID")


@pytest.fixture
def dmm_client(app_id: str, aff_id: str) -> DMMClient:
    """Create DMM client using environment variables."""

    return DMMClient(api_key=app_id, affiliate_id=aff_id)
