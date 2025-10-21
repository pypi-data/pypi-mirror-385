"""
Base classes for author testing with abstract test methods.
"""

from abc import abstractmethod
from typing import Any, Dict

import pytest


class AuthorTestBase:
    """Abstract base class for author tests."""

    @pytest.fixture
    @abstractmethod
    def author_data(self) -> Dict[str, Any]:
        """Mock author data - must be implemented by subclasses."""

    @abstractmethod
    def test_author_basic_fields(self, author_data: Dict[str, Any]) -> None:
        """Test basic author fields (author_id, name, ruby, list_url, another_name)."""

    @abstractmethod
    def test_author_from_dict(self, author_data: Dict[str, Any]) -> None:
        """Test creating author from dictionary."""

    @abstractmethod
    def test_author_id_type(self, author_data: Dict[str, Any]) -> None:
        """Test author ID is string type."""

    @abstractmethod
    def test_author_name_validation(self, author_data: Dict[str, Any]) -> None:
        """Test author name validation."""

    @abstractmethod
    def test_author_ruby_validation(self, author_data: Dict[str, Any]) -> None:
        """Test author ruby (phonetic) validation."""

    @abstractmethod
    def test_author_list_url_validation(self, author_data: Dict[str, Any]) -> None:
        """Test author list URL validation."""

    @abstractmethod
    def test_author_another_name_field(self, author_data: Dict[str, Any]) -> None:
        """Test author another_name (alias) field."""

    @abstractmethod
    def test_author_empty_data_handling(self, author_data: Dict[str, Any]) -> None:
        """Test handling of empty or missing data."""

    @abstractmethod
    def test_author_default_values(self, author_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class AuthorSearchResultTestBase:
    """Abstract base class for author search result tests."""

    @pytest.fixture
    @abstractmethod
    def result_data(self) -> Dict[str, Any]:
        """Mock author search result data - must be implemented by subclasses."""

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
    def test_result_author_list(self, result_data: Dict[str, Any]) -> None:
        """Test author list parsing."""

    @abstractmethod
    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        """Test creating result from dictionary."""

    @abstractmethod
    def test_result_nested_authors(self, result_data: Dict[str, Any]) -> None:
        """Test nested author objects."""

    @abstractmethod
    def test_result_empty_authors(self, result_data: Dict[str, Any]) -> None:
        """Test result with empty author list."""

    @abstractmethod
    def test_result_multiple_authors(self, result_data: Dict[str, Any]) -> None:
        """Test result with multiple authors."""

    @abstractmethod
    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test status code validation."""

    @abstractmethod
    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test count fields (result_count, total_count, first_position)."""

    @abstractmethod
    def test_result_author_type(self, result_data: Dict[str, Any]) -> None:
        """Test author field type is list."""

    @abstractmethod
    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class AuthorSearchResponseTestBase:
    """Abstract base class for author search response tests."""

    @pytest.fixture
    @abstractmethod
    def response_data(self) -> Dict[str, Any]:
        """Mock author search response data - must be implemented by subclasses."""

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
    def test_response_authors_property(self, response_data: Dict[str, Any]) -> None:
        """Test authors property accessor."""

    @abstractmethod
    def test_response_author_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test author_count property accessor."""

    @abstractmethod
    def test_response_total_authors_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test total_authors property accessor."""

    @abstractmethod
    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test status property accessor."""

    @abstractmethod
    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test consistency between properties and result fields."""
