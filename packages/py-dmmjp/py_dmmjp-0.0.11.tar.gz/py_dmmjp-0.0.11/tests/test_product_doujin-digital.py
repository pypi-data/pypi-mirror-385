"""
Tests for Doujin Digital products (service=doujin, floor=digital_doujin).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDoujinDigitalProduct(ProductTestBase):
    """Test cases for Doujin Digital products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Doujin Digital product data from DMM API response."""

        return {
            "service_code": "doujin",
            "service_name": "同人",
            "floor_code": "digital_doujin",
            "floor_name": "同人",
            "category_name": "同人 (同人)",
            "content_id": "d_643155",
            "product_id": "d_643155",
            "title": "となりの席の友達と一緒にオナニーする話",
            "volume": "78",
            "review": {"count": 20, "average": "5.00"},
            "URL": "https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_643155/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_643155%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155pt.jpg",
                "large": "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155pl.jpg",
            },
            "sampleImageURL": {
                "sample_l": {
                    "image": [
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-001.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-002.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-003.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-004.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-005.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-006.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-007.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-008.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-009.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_643155/d_643155jp-010.jpg",
                    ]
                }
            },
            "prices": {
                "price": "880",
                "list_price": "880",
                "deliveries": {
                    "delivery": [
                        {"type": "download", "price": "880", "list_price": "880"}
                    ]
                },
            },
            "date": "2025-10-10 00:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 48, "name": "制服"},
                    {"id": 55, "name": "処女"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 5001, "name": "中出し"},
                    {"id": 5002, "name": "フェラ"},
                    {"id": 5003, "name": "ぶっかけ"},
                    {"id": 5008, "name": "オナニー"},
                    {"id": 5009, "name": "ごっくん"},
                    {"id": 153003, "name": "おっぱい"},
                    {"id": 156021, "name": "専売"},
                    {"id": 156022, "name": "男性向け"},
                    {"id": 156023, "name": "成人向け"},
                    {"id": 160044, "name": "汁/液大量"},
                ],
                "maker": [{"id": 203156, "name": "フグタ家"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test doujin digital product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin"
        assert product.floor_name == "同人"
        assert product.category_name == "同人 (同人)"

        assert product.content_id == "d_643155"
        assert product.product_id == "d_643155"
        assert product.title == "となりの席の友達と一緒にオナニーする話"
        assert product.volume == 78

    def test_product_sample_images(self, product_data):
        """Test that doujin digital products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 10
        assert "d_643155jp-001.jpg" in large_images[0]
        assert "d_643155jp-010.jpg" in large_images[9]

        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 10

    def test_product_pricing_data(self, product_data):
        """Test doujin digital product's download pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "880"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 880
        assert product.original_price == 880

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "880"
        assert delivery.list_price == "880"

    def test_product_item_info_genres(self, product_data):
        """Test doujin digital product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "制服" in genre_names
        assert "処女" in genre_names
        assert "巨乳" in genre_names
        assert "中出し" in genre_names
        assert "フェラ" in genre_names
        assert "ぶっかけ" in genre_names
        assert "オナニー" in genre_names
        assert "ごっくん" in genre_names
        assert "おっぱい" in genre_names
        assert "専売" in genre_names
        assert "男性向け" in genre_names
        assert "成人向け" in genre_names
        assert "汁/液大量" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 10, 10, 0, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test doujin digital product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "doujin-assets.dmm.co.jp/digital/comic/d_643155" in product.image_url.list
        )
        assert product.image_url.small is None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test doujin digital product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test doujin digital product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 203156
        assert makers[0].name == "フグタ家"

    def test_product_item_info_manufactures(self, product_data):
        """Test doujin digital product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting doujin digital product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "doujin"
        assert result_dict["content_id"] == "d_643155"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw doujin digital API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "doujin"
        assert raw_data["content_id"] == "d_643155"

    def test_sample_images_large(self, product_data):
        """Test large sample images for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 10

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for doujin digital products."""

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
        """Test item info categories for doujin digital products."""

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
        """Test convenience properties for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 20
        assert product.review_average == 5.0
        assert product.current_price == 880
        assert product.original_price == 880
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 10

    def test_nested_objects(self, product_data):
        """Test nested objects for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for doujin digital products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "880"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.prices.price_int == 880
        assert product.prices.list_price_int == 880

    def test_delivery_options(self, product_data):
        """Test delivery options for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 1

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "880"

    def test_product_fields(self, product_data):
        """Test product fields for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin"
        assert product.floor_name == "同人"
        assert product.category_name == "同人 (同人)"
        assert product.content_id == "d_643155"
        assert product.product_id == "d_643155"
        assert product.title is not None
        assert product.volume == 78
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
        """Test review data for doujin digital products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 20
        assert product.review.average == 5.0
        assert product.review_count == 20
        assert product.review_average == 5.0

    def test_doujin_specific_fields(self, product_data):
        """Test doujin specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/dc/doujin/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fdc%2Fdoujin%2F" in product.affiliate_url

        assert "doujin-assets.dmm.co.jp" in product.image_url.list

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 203156
        assert makers[0].name == "フグタ家"

    def test_doujin_content_characteristics(self, product_data):
        """Test doujin content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "制服" in genre_names
        assert "処女" in genre_names
        assert "巨乳" in genre_names
        assert "オナニー" in genre_names
        assert "専売" in genre_names
        assert "男性向け" in genre_names
        assert "成人向け" in genre_names

        assert product.volume == 78
        assert len(product.sample_images_large) == 10

    def test_doujin_pricing_model(self, product_data):
        """Test doujin download pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "880"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 880
        assert product.original_price == 880

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "880"
        assert delivery.list_price == "880"

    def test_doujin_maker_info(self, product_data):
        """Test doujin maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 203156
        assert maker.name == "フグタ家"

    def test_doujin_category_structure(self, product_data):
        """Test doujin category structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin"
        assert product.floor_name == "同人"
        assert product.category_name == "同人 (同人)"

        assert len(product.directory) == 0

    def test_digital_doujin_features(self, product_data):
        """Test digital doujin specific characteristics."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "専売" in genre_names

        assert product.stock is None
        assert product.jancode is None

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"

        assert "doujin-assets.dmm.co.jp" in product.image_url.list

    def test_adult_doujin_classification(self, product_data):
        """Test adult doujin classification."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "男性向け" in genre_names
        assert "成人向け" in genre_names

        assert len(product.sample_images_large) == 10
        assert product.volume == 78

    def test_doujin_content_tags(self, product_data):
        """Test doujin content tagging system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "制服" in genre_names
        assert "処女" in genre_names
        assert "巨乳" in genre_names
        assert "中出し" in genre_names
        assert "フェラ" in genre_names
        assert "ぶっかけ" in genre_names
        assert "オナニー" in genre_names
        assert "ごっくん" in genre_names
        assert "おっぱい" in genre_names
        assert "汁/液大量" in genre_names

    def test_doujin_image_structure(self, product_data):
        """Test doujin image structure."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.small is None
        assert product.image_url.large is not None

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 10
        assert len(product.sample_images) == 0

        for i, image_url in enumerate(product.sample_images_large, 1):
            assert f"d_643155jp-{i:03d}.jpg" in image_url

    def test_doujin_volume_info(self, product_data):
        """Test doujin volume information."""

        product = Product.from_dict(product_data)

        assert product.volume == 78
        assert isinstance(product.volume, int)

    def test_doujin_exclusive_content(self, product_data):
        """Test doujin exclusive content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "専売" in genre_names

        assert product.content_id.startswith("d_")
        assert product.product_id.startswith("d_")
