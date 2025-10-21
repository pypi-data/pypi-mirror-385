"""
Tests for Digital Nikkatsu products (service=digital, floor=nikkatsu).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDigitalNikkatsuProduct(ProductTestBase):
    """Test cases for Digital Nikkatsu products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Digital Nikkatsu product data from DMM API response."""

        return {
            "service_code": "digital",
            "service_name": "動画",
            "floor_code": "nikkatsu",
            "floor_name": "成人映画",
            "category_name": "成人映画 (動画)",
            "content_id": "174okura405",
            "product_id": "174okura00405",
            "title": "美人家庭教師/ふくよかな谷間",
            "volume": "59",
            "review": {"count": 5, "average": "4.00"},
            "URL": "https://video.dmm.co.jp/cinema/content/?id=174okura405",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fcinema%2Fcontent%2F%3Fid%3D174okura405&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/174okura00405/174okura00405-5.jpg",
                    ]
                }
            },
            "prices": {
                "price": "530~",
                "list_price": "530~",
                "deliveries": {
                    "delivery": [
                        {"type": "stream", "price": "530", "list_price": "530"},
                        {"type": "download", "price": "1020", "list_price": "1020"},
                    ]
                },
            },
            "date": "2005-03-18 09:59:34",
            "iteminfo": {
                "genre": [
                    {"id": 4103, "name": "成人映画"},
                    {"id": 1022, "name": "家庭教師"},
                    {"id": 1019, "name": "女子大生"},
                ],
                "maker": [{"id": 40187, "name": "大蔵映画"}],
                "actress": [
                    {"id": 472, "name": "加藤由香", "ruby": "かとうゆか"},
                    {"id": 2268, "name": "中里優奈", "ruby": "なかざとゆうな"},
                ],
                "director": [{"id": 71987, "name": "小川欽也", "ruby": "おがわきんや"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test digital nikkatsu product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "nikkatsu"
        assert product.floor_name == "成人映画"
        assert product.category_name == "成人映画 (動画)"

        assert product.content_id == "174okura405"
        assert product.product_id == "174okura00405"
        assert product.title == "美人家庭教師/ふくよかな谷間"
        assert product.volume == 59

    def test_product_sample_images(self, product_data):
        """Test digital nikkatsu product sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images) > 0
        assert len(product.sample_images_large) == 0
        assert "174okura00405-1.jpg" in product.sample_images[0]

    def test_product_pricing_data(self, product_data):
        """Test digital nikkatsu product's pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "530~"
        assert product.prices.list_price == "530~"
        assert len(product.prices.deliveries) == 2
        assert product.current_price == 530
        assert product.original_price == 530

    def test_product_item_info_genres(self, product_data):
        """Test digital nikkatsu product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "成人映画" in genre_names
        assert "家庭教師" in genre_names
        assert "女子大生" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2005, 3, 18, 9, 59, 34)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test digital nikkatsu product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "pics.dmm.co.jp/digital/video/174okura00405" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test digital nikkatsu product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 2
        assert actresses[0].name == "加藤由香"
        assert actresses[0].ruby == "かとうゆか"
        assert actresses[1].name == "中里優奈"

    def test_product_item_info_makers(self, product_data):
        """Test digital nikkatsu product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].name == "大蔵映画"

    def test_product_item_info_manufactures(self, product_data):
        """Test digital nikkatsu product manufactures."""

        product = Product.from_dict(product_data)

        manufactures = product.manufactures
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting digital nikkatsu product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "digital"
        assert result_dict["content_id"] == "174okura405"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw digital nikkatsu API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "digital"
        assert raw_data["content_id"] == "174okura405"

    def test_sample_images_large(self, product_data):
        """Test large sample images for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for digital nikkatsu products."""

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
        """Test item info categories for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.labels) == 0
        assert len(product.actresses) > 0
        assert len(product.directors) > 0
        assert len(product.series) == 0
        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0
        assert len(product.directory) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 5
        assert product.review_average == 4.0
        assert product.current_price == 530
        assert product.original_price == 530
        assert len(product.sample_images) > 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for digital nikkatsu products."""

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
        """Test directory structure for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "530~"
        assert product.prices.list_price == "530~"
        assert len(product.prices.deliveries) == 2
        assert product.prices.price_int == 530

    def test_delivery_options(self, product_data):
        """Test delivery options for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 2

        delivery_types = [d.type for d in product.prices.deliveries]
        assert "stream" in delivery_types
        assert "download" in delivery_types

    def test_product_fields(self, product_data):
        """Test product fields for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "nikkatsu"
        assert product.floor_name == "成人映画"
        assert product.category_name == "成人映画 (動画)"
        assert product.content_id == "174okura405"
        assert product.product_id == "174okura00405"
        assert product.title is not None
        assert product.volume == 59
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
        """Test review data for digital nikkatsu products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 5
        assert product.review.average == 4.0
        assert product.review_count == 5
        assert product.review_average == 4.0
