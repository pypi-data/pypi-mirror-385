"""
Base classes for maker testing with abstract test methods.
"""

from abc import abstractmethod
from typing import Any, Dict

import pytest


class MakerTestBase:
    """Abstract base class for maker tests."""

    @pytest.fixture
    @abstractmethod
    def maker_data(self) -> Dict[str, Any]:
        """Mock maker data - must be implemented by subclasses."""

    @abstractmethod
    def test_maker_basic_fields(self, maker_data: Dict[str, Any]) -> None:
        """Test basic maker fields (maker_id, name, ruby, list_url)."""

    @abstractmethod
    def test_maker_from_dict(self, maker_data: Dict[str, Any]) -> None:
        """Test creating maker from dictionary."""

    @abstractmethod
    def test_maker_id_type(self, maker_data: Dict[str, Any]) -> None:
        """Test maker ID is string type."""

    @abstractmethod
    def test_maker_name_validation(self, maker_data: Dict[str, Any]) -> None:
        """Test maker name validation."""

    @abstractmethod
    def test_maker_ruby_validation(self, maker_data: Dict[str, Any]) -> None:
        """Test maker ruby (phonetic) validation."""

    @abstractmethod
    def test_maker_list_url_validation(self, maker_data: Dict[str, Any]) -> None:
        """Test maker list URL validation."""

    @abstractmethod
    def test_maker_empty_data_handling(self, maker_data: Dict[str, Any]) -> None:
        """Test handling of empty or missing data."""

    @abstractmethod
    def test_maker_default_values(self, maker_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class MakerSearchResultTestBase:
    """Abstract base class for maker search result tests."""

    @pytest.fixture
    @abstractmethod
    def result_data(self) -> Dict[str, Any]:
        """Mock maker search result data - must be implemented by subclasses."""

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
    def test_result_maker_list(self, result_data: Dict[str, Any]) -> None:
        """Test maker list parsing."""

    @abstractmethod
    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        """Test creating result from dictionary."""

    @abstractmethod
    def test_result_nested_makers(self, result_data: Dict[str, Any]) -> None:
        """Test nested maker objects."""

    @abstractmethod
    def test_result_empty_makers(self, result_data: Dict[str, Any]) -> None:
        """Test result with empty maker list."""

    @abstractmethod
    def test_result_multiple_makers(self, result_data: Dict[str, Any]) -> None:
        """Test result with multiple makers."""

    @abstractmethod
    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test status code validation."""

    @abstractmethod
    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test count fields (result_count, total_count, first_position)."""

    @abstractmethod
    def test_result_maker_type(self, result_data: Dict[str, Any]) -> None:
        """Test maker field type is list."""

    @abstractmethod
    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class MakerSearchResponseTestBase:
    """Abstract base class for maker search response tests."""

    @pytest.fixture
    @abstractmethod
    def response_data(self) -> Dict[str, Any]:
        """Mock maker search response data - must be implemented by subclasses."""

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
    def test_response_makers_property(self, response_data: Dict[str, Any]) -> None:
        """Test makers property accessor."""

    @abstractmethod
    def test_response_maker_count_property(self, response_data: Dict[str, Any]) -> None:
        """Test maker_count property accessor."""

    @abstractmethod
    def test_response_total_makers_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test total_makers property accessor."""

    @abstractmethod
    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test status property accessor."""

    @abstractmethod
    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test consistency between properties and result fields."""
