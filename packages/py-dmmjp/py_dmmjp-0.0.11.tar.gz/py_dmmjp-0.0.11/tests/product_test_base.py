"""
Base class for product testing with abstract test methods.
"""

from abc import abstractmethod
from typing import Any, Dict

import pytest


class ProductTestBase:
    """Abstract base class for product tests."""

    @pytest.fixture
    @abstractmethod
    def product_data(self) -> Dict[str, Any]:
        """Mock product data - must be implemented by subclasses."""

    @abstractmethod
    def test_product_basic_fields(self, product_data: Dict[str, Any]) -> None:
        """Test basic product fields."""

    @abstractmethod
    def test_product_date_parsing(self, product_data: Dict[str, Any]) -> None:
        """Test date parsing."""

    @abstractmethod
    def test_product_review_data(self, product_data: Dict[str, Any]) -> None:
        """Test review data parsing."""

    @abstractmethod
    def test_product_pricing_data(self, product_data: Dict[str, Any]) -> None:
        """Test pricing data parsing."""

    @abstractmethod
    def test_product_image_urls(self, product_data: Dict[str, Any]) -> None:
        """Test image URL parsing."""

    @abstractmethod
    def test_product_sample_images(self, product_data: Dict[str, Any]) -> None:
        """Test sample image parsing."""

    @abstractmethod
    def test_product_item_info_genres(self, product_data: Dict[str, Any]) -> None:
        """Test genre information parsing."""

    @abstractmethod
    def test_product_item_info_actresses(self, product_data: Dict[str, Any]) -> None:
        """Test actress information parsing."""

    @abstractmethod
    def test_product_item_info_makers(self, product_data: Dict[str, Any]) -> None:
        """Test maker information parsing."""

    @abstractmethod
    def test_product_item_info_manufactures(self, product_data: Dict[str, Any]) -> None:
        """Test manufacture information parsing."""

    @abstractmethod
    def test_product_to_dict(self, product_data: Dict[str, Any]) -> None:
        """Test converting product back to dictionary."""

    @abstractmethod
    def test_product_raw_data_access(self, product_data: Dict[str, Any]) -> None:
        """Test access to raw API data."""

    @abstractmethod
    def test_sample_images_large(self, product_data: Dict[str, Any]) -> None:
        """Test large sample images."""

    @abstractmethod
    def test_sample_movie_url(self, product_data: Dict[str, Any]) -> None:
        """Test sample movie URLs."""

    @abstractmethod
    def test_optional_fields(self, product_data: Dict[str, Any]) -> None:
        """Test optional fields."""

    @abstractmethod
    def test_item_info_categories(self, product_data: Dict[str, Any]) -> None:
        """Test item info categories."""

    @abstractmethod
    def test_convenience_properties(self, product_data: Dict[str, Any]) -> None:
        """Test convenience properties."""

    @abstractmethod
    def test_nested_objects(self, product_data: Dict[str, Any]) -> None:
        """Test nested objects."""

    @abstractmethod
    def test_directory_structure(self, product_data: Dict[str, Any]) -> None:
        """Test directory structure."""

    @abstractmethod
    def test_pricing_structure(self, product_data: Dict[str, Any]) -> None:
        """Test pricing structure."""

    @abstractmethod
    def test_delivery_options(self, product_data: Dict[str, Any]) -> None:
        """Test delivery options."""

    @abstractmethod
    def test_product_fields(self, product_data: Dict[str, Any]) -> None:
        """Test all product fields."""
