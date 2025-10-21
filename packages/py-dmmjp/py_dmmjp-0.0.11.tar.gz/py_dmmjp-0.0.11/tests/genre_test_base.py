"""
Base classes for genre testing with abstract test methods.
"""

from abc import abstractmethod
from typing import Any, Dict

import pytest


class GenreTestBase:
    """Abstract base class for genre tests."""

    @pytest.fixture
    @abstractmethod
    def genre_data(self) -> Dict[str, Any]:
        """Mock genre data - must be implemented by subclasses."""

    @abstractmethod
    def test_genre_basic_fields(self, genre_data: Dict[str, Any]) -> None:
        """Test basic genre fields (genre_id, name, ruby, list_url)."""

    @abstractmethod
    def test_genre_from_dict(self, genre_data: Dict[str, Any]) -> None:
        """Test creating genre from dictionary."""

    @abstractmethod
    def test_genre_id_type(self, genre_data: Dict[str, Any]) -> None:
        """Test genre ID is string type."""

    @abstractmethod
    def test_genre_name_validation(self, genre_data: Dict[str, Any]) -> None:
        """Test genre name validation."""

    @abstractmethod
    def test_genre_ruby_validation(self, genre_data: Dict[str, Any]) -> None:
        """Test genre ruby (phonetic) validation."""

    @abstractmethod
    def test_genre_list_url_validation(self, genre_data: Dict[str, Any]) -> None:
        """Test genre list URL validation."""

    @abstractmethod
    def test_genre_empty_data_handling(self, genre_data: Dict[str, Any]) -> None:
        """Test handling of empty or missing data."""

    @abstractmethod
    def test_genre_default_values(self, genre_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class GenreSearchResultTestBase:
    """Abstract base class for genre search result tests."""

    @pytest.fixture
    @abstractmethod
    def result_data(self) -> Dict[str, Any]:
        """Mock genre search result data - must be implemented by subclasses."""

    @abstractmethod
    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        """Test basic result fields (status, counts, positions)."""

    @abstractmethod
    def test_result_site_fields(self, result_data: Dict[str, Any]) -> None:
        """Test site-related fields (site_name, site_code)."""

    @abstractmethod
    def test_result_service_fields(self, result_data: Dict[str, Any]) -> None:
        """Test service-related fields (service_name, service_code)."""

    @abstractmethod
    def test_result_floor_fields(self, result_data: Dict[str, Any]) -> None:
        """Test floor-related fields (floor_id, floor_name, floor_code)."""

    @abstractmethod
    def test_result_genre_list(self, result_data: Dict[str, Any]) -> None:
        """Test genre list parsing."""

    @abstractmethod
    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        """Test creating result from dictionary."""

    @abstractmethod
    def test_result_nested_genres(self, result_data: Dict[str, Any]) -> None:
        """Test nested genre objects."""

    @abstractmethod
    def test_result_empty_genres(self, result_data: Dict[str, Any]) -> None:
        """Test result with empty genre list."""

    @abstractmethod
    def test_result_multiple_genres(self, result_data: Dict[str, Any]) -> None:
        """Test result with multiple genres."""

    @abstractmethod
    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test status code validation."""

    @abstractmethod
    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test count fields (result_count, total_count, first_position)."""

    @abstractmethod
    def test_result_genre_type(self, result_data: Dict[str, Any]) -> None:
        """Test genre field type is list."""

    @abstractmethod
    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class GenreSearchResponseTestBase:
    """Abstract base class for genre search response tests."""

    @pytest.fixture
    @abstractmethod
    def response_data(self) -> Dict[str, Any]:
        """Mock genre search response data - must be implemented by subclasses."""

    @abstractmethod
    def test_response_structure(self, response_data: Dict[str, Any]) -> None:
        """Test response structure (request, result)."""

    @abstractmethod
    def test_response_from_dict(self, response_data: Dict[str, Any]) -> None:
        """Test creating response from dictionary."""

    @abstractmethod
    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        """Test request object in response."""

    @abstractmethod
    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        """Test result object in response."""

    @abstractmethod
    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test raw_response property access."""

    @abstractmethod
    def test_response_genres_property(self, response_data: Dict[str, Any]) -> None:
        """Test genres property accessor."""

    @abstractmethod
    def test_response_genre_count_property(self, response_data: Dict[str, Any]) -> None:
        """Test genre_count property accessor."""

    @abstractmethod
    def test_response_total_genres_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test total_genres property accessor."""

    @abstractmethod
    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test status property accessor."""

    @abstractmethod
    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test consistency between properties and result fields."""
