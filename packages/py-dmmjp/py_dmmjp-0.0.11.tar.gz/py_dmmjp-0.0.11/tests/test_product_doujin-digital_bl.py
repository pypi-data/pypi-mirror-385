"""
Tests for Doujin Digital BL products (service=doujin, floor=digital_doujin_bl).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDoujinDigitalBLProduct(ProductTestBase):
    """Test cases for Doujin Digital BL products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Doujin Digital BL product data from DMM API response."""

        return {
            "service_code": "doujin",
            "service_name": "同人",
            "floor_code": "digital_doujin_bl",
            "floor_name": "らぶカル（BL）",
            "category_name": "らぶカル（BL）",
            "content_id": "d_659526",
            "product_id": "d_659526",
            "title": "梱包男子  闇オークションの裏側",
            "volume": "39",
            "URL": "https://lovecul.dmm.co.jp/bl/-/detail/=/cid=d_659526/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Flovecul.dmm.co.jp%2Fbl%2F-%2Fdetail%2F%3D%2Fcid%3Dd_659526%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526pt.jpg",
                "large": "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526pl.jpg",
            },
            "sampleImageURL": {
                "sample_l": {
                    "image": [
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-001.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-002.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-003.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-004.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-005.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-006.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-007.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_659526/d_659526jp-008.jpg",
                    ]
                }
            },
            "prices": {
                "price": "550",
                "list_price": "550",
                "deliveries": {
                    "delivery": [
                        {"type": "download", "price": "550", "list_price": "550"}
                    ]
                },
            },
            "date": "2025-09-02 00:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 25, "name": "拘束"},
                    {"id": 28, "name": "羞恥"},
                    {"id": 156006, "name": "女性向け"},
                    {"id": 156023, "name": "成人向け"},
                    {"id": 160067, "name": "尿道"},
                ],
                "maker": [{"id": 73816, "name": "なついろ乙女"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test doujin digital BL product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_bl"
        assert product.floor_name == "らぶカル（BL）"
        assert product.category_name == "らぶカル（BL）"

        assert product.content_id == "d_659526"
        assert product.product_id == "d_659526"
        assert product.title == "梱包男子  闇オークションの裏側"
        assert product.volume == 39

    def test_product_sample_images(self, product_data):
        """Test that doujin digital BL products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 8
        assert "d_659526jp-001.jpg" in large_images[0]
        assert "d_659526jp-008.jpg" in large_images[7]

        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 8

    def test_product_pricing_data(self, product_data):
        """Test doujin digital BL product's download pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "550"
        assert product.prices.list_price == "550"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 550
        assert product.original_price == 550

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "550"
        assert delivery.list_price == "550"

    def test_product_item_info_genres(self, product_data):
        """Test doujin digital BL product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "拘束" in genre_names
        assert "羞恥" in genre_names
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names
        assert "尿道" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 9, 2, 0, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test doujin digital BL product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "doujin-assets.dmm.co.jp/digital/comic/d_659526" in product.image_url.list
        )
        assert product.image_url.small is None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test doujin digital BL product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test doujin digital BL product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 73816
        assert makers[0].name == "なついろ乙女"

    def test_product_item_info_manufactures(self, product_data):
        """Test doujin digital BL product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting doujin digital BL product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "doujin"
        assert result_dict["content_id"] == "d_659526"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw doujin digital BL API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "doujin"
        assert raw_data["content_id"] == "d_659526"

    def test_sample_images_large(self, product_data):
        """Test large sample images for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 8

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for doujin digital BL products."""

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
        """Test item info categories for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0

        assert len(product.labels) == 0
        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.series) == 0
        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0
        assert len(product.directory) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.review_average is None
        assert product.review_count == 0
        assert product.current_price == 550
        assert product.original_price == 550
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 8

    def test_nested_objects(self, product_data):
        """Test nested objects for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "550"
        assert product.prices.list_price == "550"
        assert len(product.prices.deliveries) == 1
        assert product.prices.price_int == 550
        assert product.prices.list_price_int == 550

    def test_delivery_options(self, product_data):
        """Test delivery options for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 1

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "550"

    def test_product_fields(self, product_data):
        """Test product fields for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_bl"
        assert product.floor_name == "らぶカル（BL）"
        assert product.category_name == "らぶカル（BL）"
        assert product.content_id == "d_659526"
        assert product.product_id == "d_659526"
        assert product.title is not None
        assert product.volume == 39
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for doujin digital BL products."""

        product = Product.from_dict(product_data)

        assert product.review is None
        assert product.review_average is None
        assert product.review_count == 0

    def test_bl_specific_fields(self, product_data):
        """Test BL specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "lovecul.dmm.co.jp/bl/" in product.url
        assert product.affiliate_url is not None
        assert "lovecul.dmm.co.jp%2Fbl%2F" in product.affiliate_url

        assert "doujin-assets.dmm.co.jp" in product.image_url.list

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 73816
        assert makers[0].name == "なついろ乙女"

    def test_bl_content_characteristics(self, product_data):
        """Test BL content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "拘束" in genre_names
        assert "羞恥" in genre_names
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names
        assert "尿道" in genre_names

        assert product.volume == 39
        assert len(product.sample_images_large) == 8

    def test_bl_pricing_model(self, product_data):
        """Test BL download pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "550"
        assert product.prices.list_price == "550"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 550
        assert product.original_price == 550

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "550"
        assert delivery.list_price == "550"

    def test_bl_maker_info(self, product_data):
        """Test BL maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 73816
        assert maker.name == "なついろ乙女"

    def test_bl_category_structure(self, product_data):
        """Test BL category structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_bl"
        assert product.floor_name == "らぶカル（BL）"
        assert product.category_name == "らぶカル（BL）"

        assert len(product.directory) == 0

    def test_digital_bl_features(self, product_data):
        """Test digital BL specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.stock is None
        assert product.jancode is None

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"

        assert "doujin-assets.dmm.co.jp" in product.image_url.list
        assert "lovecul.dmm.co.jp/bl/" in product.url

    def test_bl_classification(self, product_data):
        """Test BL classification."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names

        assert len(product.sample_images_large) == 8
        assert product.volume == 39
        assert product.floor_name == "らぶカル（BL）"

    def test_bl_content_tags(self, product_data):
        """Test BL content tagging system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "拘束" in genre_names
        assert "羞恥" in genre_names
        assert "尿道" in genre_names

    def test_bl_image_structure(self, product_data):
        """Test BL image structure."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.small is None
        assert product.image_url.large is not None

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 8
        assert len(product.sample_images) == 0

        for i, image_url in enumerate(product.sample_images_large, 1):
            assert f"d_659526jp-{i:03d}.jpg" in image_url

    def test_bl_volume_info(self, product_data):
        """Test BL volume information."""

        product = Product.from_dict(product_data)

        assert product.volume == 39
        assert isinstance(product.volume, int)

    def test_bl_exclusive_content(self, product_data):
        """Test BL exclusive content features."""

        product = Product.from_dict(product_data)

        assert product.content_id.startswith("d_")
        assert product.product_id.startswith("d_")

        assert "lovecul.dmm.co.jp" in product.url
        assert product.floor_name == "らぶカル（BL）"

    def test_lovecul_platform_features(self, product_data):
        """Test Love Culture platform specific features."""

        product = Product.from_dict(product_data)

        assert "lovecul.dmm.co.jp" in product.url
        assert "lovecul.dmm.co.jp%2Fbl%2F" in product.affiliate_url
        assert product.floor_name == "らぶカル（BL）"
        assert product.category_name == "らぶカル（BL）"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "女性向け" in genre_names

    def test_bl_genre_classification(self, product_data):
        """Test BL genre classification system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        adult_content_tags = ["拘束", "羞恥", "尿道"]
        for tag in adult_content_tags:
            assert tag in genre_names

        target_audience_tags = ["女性向け", "成人向け"]
        for tag in target_audience_tags:
            assert tag in genre_names
