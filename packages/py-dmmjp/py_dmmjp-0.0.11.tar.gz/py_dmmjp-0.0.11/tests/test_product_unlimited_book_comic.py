"""
Tests for Unlimited Book Comic products (service=unlimited_book, floor=unlimited_comic).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestUnlimitedBookComicProduct(ProductTestBase):
    """Test cases for Unlimited Book Comic products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Unlimited Book Comic product data from DMM API response."""

        return {
            "service_code": "unlimited_book",
            "service_name": "FANZAブックス読み放題",
            "floor_code": "unlimited_comic",
            "floor_name": "FANZAブックス読み放題",
            "category_name": "FANZAブックス読み放題",
            "content_id": "b253atato02161",
            "product_id": "b253atato02161st",
            "title": "貼ったらヤレちゃう！？えろシール（単話）",
            "review": {"count": 5, "average": "5.00"},
            "URL": "https://unlimited.book.dmm.co.jp/products/b253atato02161/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Funlimited.book.dmm.co.jp%2Fproducts%2Fb253atato02161%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://ebook-assets.dmm.co.jp/digital/e-book/b253atato02161/b253atato02161pt.jpg",
                "small": "https://ebook-assets.dmm.co.jp/digital/e-book/b253atato02161/b253atato02161ps.jpg",
                "large": "https://ebook-assets.dmm.co.jp/digital/e-book/b253atato02161/b253atato02161pl.jpg",
            },
            "prices": {"price": "1480"},
            "date": "2024-02-01 00:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 1, "name": "フルカラー"},
                    {"id": 55, "name": "処女"},
                    {"id": 1018, "name": "女子校生"},
                    {"id": 4014, "name": "童貞"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 553, "name": "学園もの"},
                    {"id": 1016, "name": "女教師"},
                    {"id": 25, "name": "拘束"},
                    {"id": 1034, "name": "ギャル"},
                    {"id": 5022, "name": "3P・4P"},
                ],
                "series": [{"id": 504686, "name": "貼ったらヤレちゃう！？えろシール（単話）"}],
                "manufacture": [{"id": 301707, "name": "大洋図書"}],
                "author": [{"id": 243015, "name": "丸居まる"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test unlimited book comic product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "unlimited_book"
        assert product.service_name == "FANZAブックス読み放題"
        assert product.floor_code == "unlimited_comic"
        assert product.floor_name == "FANZAブックス読み放題"
        assert product.category_name == "FANZAブックス読み放題"

        assert product.content_id == "b253atato02161"
        assert product.product_id == "b253atato02161st"
        assert product.title == "貼ったらヤレちゃう！？えろシール（単話）"
        assert product.volume is None

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2024, 2, 1, 0, 0, 0)
        assert product.date == expected_date

    def test_product_review_data(self, product_data):
        """Test review data for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 5
        assert product.review.average == 5.0
        assert product.review_count == 5
        assert product.review_average == 5.0

    def test_product_pricing_data(self, product_data):
        """Test unlimited book comic product's pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "1480"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 1480
        assert product.original_price is None

    def test_product_image_urls(self, product_data):
        """Test unlimited book comic product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "ebook-assets.dmm.co.jp/digital/e-book/b253atato02161"
            in product.image_url.list
        )
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_sample_images(self, product_data):
        """Test that unlimited book comic products have no sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_item_info_genres(self, product_data):
        """Test unlimited book comic product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "フルカラー" in genre_names
        assert "処女" in genre_names
        assert "女子校生" in genre_names
        assert "童貞" in genre_names
        assert "巨乳" in genre_names
        assert "学園もの" in genre_names
        assert "女教師" in genre_names
        assert "拘束" in genre_names
        assert "ギャル" in genre_names
        assert "3P・4P" in genre_names

    def test_product_item_info_actresses(self, product_data):
        """Test unlimited book comic products have no actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test unlimited book comic products have no makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 0

    def test_product_item_info_manufactures(self, product_data):
        """Test unlimited book comic product manufactures."""

        product = Product.from_dict(product_data)

        manufactures = product.manufactures
        assert len(manufactures) == 1
        assert manufactures[0].name == "大洋図書"

    def test_product_to_dict(self, product_data):
        """Test converting unlimited book comic product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "unlimited_book"
        assert result_dict["content_id"] == "b253atato02161"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw unlimited book comic API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "unlimited_book"
        assert raw_data["content_id"] == "b253atato02161"

    def test_sample_images_large(self, product_data):
        """Test large sample images for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for unlimited book comic products."""

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
        """Test convenience properties for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 5
        assert product.review_average == 5.0
        assert product.current_price == 1480
        assert product.original_price is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "1480"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 1480

    def test_delivery_options(self, product_data):
        """Test delivery options for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for unlimited book comic products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "unlimited_book"
        assert product.service_name == "FANZAブックス読み放題"
        assert product.floor_code == "unlimited_comic"
        assert product.floor_name == "FANZAブックス読み放題"
        assert product.category_name == "FANZAブックス読み放題"
        assert product.content_id == "b253atato02161"
        assert product.product_id == "b253atato02161st"
        assert product.title is not None
        assert product.volume is None
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.raw_data is not None
