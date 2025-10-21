"""
Base class for actress testing with abstract test methods.
"""

# pylint: disable=too-many-public-methods

from abc import abstractmethod
from typing import Any, Dict

import pytest


class ActressTestBase:
    """Abstract base class for actress tests."""

    @pytest.fixture
    @abstractmethod
    def actress_data(self) -> Dict[str, Any]:
        """Mock actress data - must be implemented by subclasses."""

    @abstractmethod
    def test_actress_basic_fields(self, actress_data: Dict[str, Any]) -> None:
        """Test basic actress fields (id, name, ruby)."""

    @abstractmethod
    def test_actress_measurements(self, actress_data: Dict[str, Any]) -> None:
        """Test measurement fields (bust, waist, hip, height, cup)."""

    @abstractmethod
    def test_actress_personal_info(self, actress_data: Dict[str, Any]) -> None:
        """Test personal information (birthday, blood_type, hobby, prefectures)."""

    @abstractmethod
    def test_actress_image_urls(self, actress_data: Dict[str, Any]) -> None:
        """Test image URL parsing (small and large images)."""

    @abstractmethod
    def test_actress_list_urls(self, actress_data: Dict[str, Any]) -> None:
        """Test list URL parsing (digital, monthly, mono)."""

    @abstractmethod
    def test_actress_from_dict(self, actress_data: Dict[str, Any]) -> None:
        """Test creating actress from dictionary."""

    @abstractmethod
    def test_actress_safe_int_conversion(self, actress_data: Dict[str, Any]) -> None:
        """Test safe integer conversion for measurements."""

    @abstractmethod
    def test_actress_optional_fields(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of optional/null fields."""

    @abstractmethod
    def test_actress_nested_objects(self, actress_data: Dict[str, Any]) -> None:
        """Test nested objects (image_url, list_url)."""

    @abstractmethod
    def test_actress_image_url_from_dict(self, actress_data: Dict[str, Any]) -> None:
        """Test ActressImageURL creation from dictionary."""

    @abstractmethod
    def test_actress_list_url_from_dict(self, actress_data: Dict[str, Any]) -> None:
        """Test ActressListURL creation from dictionary."""

    @abstractmethod
    def test_actress_empty_data_handling(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of empty or missing data."""

    @abstractmethod
    def test_actress_string_measurements(self, actress_data: Dict[str, Any]) -> None:
        """Test conversion of string measurements to integers."""

    @abstractmethod
    def test_actress_invalid_data_handling(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of invalid data types."""

    @abstractmethod
    def test_actress_birthday_format(self, actress_data: Dict[str, Any]) -> None:
        """Test birthday format handling."""

    @abstractmethod
    def test_actress_cup_size_validation(self, actress_data: Dict[str, Any]) -> None:
        """Test cup size field validation."""

    @abstractmethod
    def test_actress_prefecture_data(self, actress_data: Dict[str, Any]) -> None:
        """Test prefecture/birthplace data."""

    @abstractmethod
    def test_actress_hobby_data(self, actress_data: Dict[str, Any]) -> None:
        """Test hobby/interests data."""

    @abstractmethod
    def test_actress_blood_type_data(self, actress_data: Dict[str, Any]) -> None:
        """Test blood type data."""

    @abstractmethod
    def test_actress_url_formatting(self, actress_data: Dict[str, Any]) -> None:
        """Test URL formatting in image and list URLs."""


class ActressSearchResultTestBase:
    """Abstract base class for actress search result tests."""

    @pytest.fixture
    @abstractmethod
    def result_data(self) -> Dict[str, Any]:
        """Mock actress search result data - must be implemented by subclasses."""

    @abstractmethod
    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        """Test basic result fields (status, counts, positions)."""

    @abstractmethod
    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        """Test creating result from dictionary."""

    @abstractmethod
    def test_result_actress_list(self, result_data: Dict[str, Any]) -> None:
        """Test actress list parsing."""

    @abstractmethod
    def test_result_nested_actresses(self, result_data: Dict[str, Any]) -> None:
        """Test nested actress objects."""

    @abstractmethod
    def test_result_empty_actresses(self, result_data: Dict[str, Any]) -> None:
        """Test result with empty actress list."""

    @abstractmethod
    def test_result_multiple_actresses(self, result_data: Dict[str, Any]) -> None:
        """Test result with multiple actresses."""

    @abstractmethod
    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test status code validation."""

    @abstractmethod
    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test count fields (result_count, total_count, first_position)."""

    @abstractmethod
    def test_result_actress_type(self, result_data: Dict[str, Any]) -> None:
        """Test actress field type is list."""

    @abstractmethod
    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""


class ActressSearchResponseTestBase:
    """Abstract base class for actress search response tests."""

    @pytest.fixture
    @abstractmethod
    def response_data(self) -> Dict[str, Any]:
        """Mock actress search response data - must be implemented by subclasses."""

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
    def test_response_actresses_property(self, response_data: Dict[str, Any]) -> None:
        """Test actresses property accessor."""

    @abstractmethod
    def test_response_actress_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test actress_count property accessor."""

    @abstractmethod
    def test_response_total_actresses_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test total_actresses property accessor."""

    @abstractmethod
    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test status property accessor."""

    @abstractmethod
    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test consistency between properties and result fields."""
