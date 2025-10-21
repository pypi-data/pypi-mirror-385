"""
Base classes for series testing with abstract test methods.
"""

from abc import abstractmethod
from typing import Any, Dict

import pytest


class SeriesTestBase:
    """Abstract base class for series tests."""

    @pytest.fixture
    @abstractmethod
    def series_data(self) -> Dict[str, Any]:
        """Mock series data - must be implemented by subclasses."""

    @abstractmethod
    def test_series_basic_fields(self, series_data: Dict[str, Any]) -> None:
        """Test basic series fields (series_id, name, ruby, list_url)."""

    @abstractmethod
    def test_series_from_dict(self, series_data: Dict[str, Any]) -> None:
        """Test creating series from dictionary."""

    @abstractmethod
    def test_series_id_type(self, series_data: Dict[str, Any]) -> None:
        """Test series ID is string type."""

    @abstractmethod
    def test_series_name_validation(self, series_data: Dict[str, Any]) -> None:
        """Test series name validation."""

    @abstractmethod
    def test_series_ruby_validation(self, series_data: Dict[str, Any]) -> None:
        """Test series ruby (phonetic) validation."""

    @abstractmethod
    def test_series_list_url_validation(self, series_data: Dict[str, Any]) -> None:
        """Test series list URL validation."""

    @abstractmethod
    def test_series_empty_data_handling(self, series_data: Dict[str, Any]) -> None:
        """Test handling of empty or missing data."""

    @abstractmethod
    def test_series_default_values(self, series_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class SeriesSearchResultTestBase:
    """Abstract base class for series search result tests."""

    @pytest.fixture
    @abstractmethod
    def result_data(self) -> Dict[str, Any]:
        """Mock series search result data - must be implemented by subclasses."""

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
    def test_result_series_list(self, result_data: Dict[str, Any]) -> None:
        """Test series list parsing."""

    @abstractmethod
    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        """Test creating result from dictionary."""

    @abstractmethod
    def test_result_nested_series(self, result_data: Dict[str, Any]) -> None:
        """Test nested series objects."""

    @abstractmethod
    def test_result_empty_series(self, result_data: Dict[str, Any]) -> None:
        """Test result with empty series list."""

    @abstractmethod
    def test_result_multiple_series(self, result_data: Dict[str, Any]) -> None:
        """Test result with multiple series."""

    @abstractmethod
    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test status code validation."""

    @abstractmethod
    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test count fields (result_count, total_count, first_position)."""

    @abstractmethod
    def test_result_series_type(self, result_data: Dict[str, Any]) -> None:
        """Test series field type is list."""

    @abstractmethod
    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class SeriesSearchResponseTestBase:
    """Abstract base class for series search response tests."""

    @pytest.fixture
    @abstractmethod
    def response_data(self) -> Dict[str, Any]:
        """Mock series search response data - must be implemented by subclasses."""

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
    def test_response_series_property(self, response_data: Dict[str, Any]) -> None:
        """Test series property accessor."""

    @abstractmethod
    def test_response_series_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test series_count property accessor."""

    @abstractmethod
    def test_response_total_series_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test total_series property accessor."""

    @abstractmethod
    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test status property accessor."""

    @abstractmethod
    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test consistency between properties and result fields."""
