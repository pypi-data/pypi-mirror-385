"""
Tests for Ebook TL products (service=ebook, floor=tl).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestEbookTLProduct(ProductTestBase):
    """Test cases for Ebook TL products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Ebook TL product data from DMM API response."""

        return {
            "service_code": "ebook",
            "service_name": "FANZAブックス",
            "floor_code": "tl",
            "floor_name": "TL",
            "category_name": "TL (電子書籍)",
            "content_id": "b351ammrc11056",
            "product_id": "b351ammrc11056",
            "title": "強精入院～退院するまで100人のナースに射精管理されてます～（単話）",
            "volume": "30",
            "review": {"count": 1, "average": "3.00"},
            "URL": "https://book.dmm.co.jp/product/6211277/b351ammrc11056/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fbook.dmm.co.jp%2Fproduct%2F6211277%2Fb351ammrc11056%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://ebook-assets.dmm.co.jp/digital/e-book/b351ammrc11056/b351ammrc11056pt.jpg",
                "small": "https://ebook-assets.dmm.co.jp/digital/e-book/b351ammrc11056/b351ammrc11056ps.jpg",
                "large": "https://ebook-assets.dmm.co.jp/digital/e-book/b351ammrc11056/b351ammrc11056pl.jpg",
            },
            "tachiyomi": {
                "URL": "https://book.dmm.co.jp/tachiyomi/?cid=FRNfXRNVFW1RAQxaAANXVgwIRFUBCFQMVE5EDl0VClQMBllNB1o*UFcKWhRHVwVfCBxZW1kEVQ__&lin=1&sd=0",
                "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fbook.dmm.co.jp%2Ftachiyomi%2F%3Fcid%3DFRNfXRNVFW1RAQxaAANXVgwIRFUBCFQMVE5EDl0VClQMBllNB1o%2AUFcKWhRHVwVfCBxZW1kEVQ__%26lin%3D1%26sd%3D0&af_id=***REDACTED_AFF_ID***&ch=api",
            },
            "prices": {"price": "275"},
            "date": "2025-10-03 00:00:04",
            "iteminfo": {
                "genre": [
                    {"id": 1, "name": "フルカラー"},
                    {"id": 53, "name": "単話"},
                    {"id": 1013, "name": "看護婦・ナース"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 2007, "name": "ぽっちゃり"},
                ],
                "series": [
                    {
                        "id": 6211277,
                        "name": "強精入院～退院するまで100人のナースに射精管理されてます～",
                    }
                ],
                "manufacture": [{"id": 65347, "name": "モバイルメディアリサーチ"}],
                "author": [{"id": 322650, "name": "七草天音"}],
            },
            "number": "3",
        }

    def test_product_basic_fields(self, product_data):
        """Test ebook TL product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "tl"
        assert product.floor_name == "TL"
        assert product.category_name == "TL (電子書籍)"

        assert product.content_id == "b351ammrc11056"
        assert product.product_id == "b351ammrc11056"
        assert product.title == "強精入院～退院するまで100人のナースに射精管理されてます～（単話）"
        assert product.volume == 30

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 10, 3, 0, 0, 4)
        assert product.date == expected_date

    def test_product_review_data(self, product_data):
        """Test review data for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 1
        assert product.review.average == 3.0
        assert product.review_count == 1
        assert product.review_average == 3.0

    def test_product_pricing_data(self, product_data):
        """Test ebook TL product's pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "275"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 275
        assert product.original_price is None

    def test_product_image_urls(self, product_data):
        """Test ebook TL product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "ebook-assets.dmm.co.jp/digital/e-book/b351ammrc11056"
            in product.image_url.list
        )
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_sample_images(self, product_data):
        """Test that ebook TL products have no sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_item_info_genres(self, product_data):
        """Test ebook TL product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "フルカラー" in genre_names
        assert "単話" in genre_names
        assert "看護婦・ナース" in genre_names
        assert "巨乳" in genre_names
        assert "ぽっちゃり" in genre_names

    def test_product_item_info_actresses(self, product_data):
        """Test ebook TL products have no actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test ebook TL products have no makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 0

    def test_product_item_info_manufactures(self, product_data):
        """Test ebook TL product manufactures."""

        product = Product.from_dict(product_data)

        manufactures = product.manufactures
        assert len(manufactures) == 1
        assert manufactures[0].name == "モバイルメディアリサーチ"

    def test_product_to_dict(self, product_data):
        """Test converting ebook TL product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "ebook"
        assert result_dict["content_id"] == "b351ammrc11056"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw ebook TL API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "ebook"
        assert raw_data["content_id"] == "b351ammrc11056"

    def test_sample_images_large(self, product_data):
        """Test large sample images for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.number == 3
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.tachiyomi is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for ebook TL products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) == 0
        assert len(product.labels) == 0
        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.series) > 0
        assert len(product.actors) == 0
        assert len(product.authors) > 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0
        assert len(product.directory) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 1
        assert product.review_average == 3.0
        assert product.current_price == 275
        assert product.original_price is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert product.tachiyomi is not None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for ebook TL products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "275"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 275

    def test_delivery_options(self, product_data):
        """Test delivery options for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for ebook TL products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "tl"
        assert product.floor_name == "TL"
        assert product.category_name == "TL (電子書籍)"
        assert product.content_id == "b351ammrc11056"
        assert product.product_id == "b351ammrc11056"
        assert product.title is not None
        assert product.volume == 30
        assert product.number == 3
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.raw_data is not None
