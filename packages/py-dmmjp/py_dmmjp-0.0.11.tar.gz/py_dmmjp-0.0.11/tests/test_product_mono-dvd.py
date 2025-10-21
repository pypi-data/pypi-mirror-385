"""
Tests for DVD products (service=mono, floor=dvd).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoDVDProduct(ProductTestBase):
    """Test cases for DVD products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """DVD product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "dvd",
            "floor_name": "DVD",
            "category_name": "DVD通販",
            "content_id": "tkmird261",
            "product_id": "tkmird261",
            "title": "【FANZA限定】爆乳保育士がむぎゅむぎゅ圧迫お遊戯会 授乳手コキハーレム保育園 水原みその 小梅えな 羽月乃蒼 小坂ひまり 生写真2枚付き",
            "volume": "160",
            "review": {"count": 7, "average": 5.00},
            "URL": "https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=tkmird261/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
            + "%2Fmono%2Fdvd%2F-%2Fdetail%2F%3D%2Fcid%3Dtkmird261%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/mono/movie/adult/tkmird261/tkmird261pt.jpg",
                "small": "https://pics.dmm.co.jp/mono/movie/adult/tkmird261/tkmird261ps.jpg",
                "large": "https://pics.dmm.co.jp/mono/movie/adult/tkmird261/tkmird261pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/mird00261/mird00261-9.jpg",
                    ]
                }
            },
            "prices": {"price": "4028", "list_price": "4598"},
            "date": "2025-08-20 00:00:01",
            "iteminfo": {
                "genre": [
                    {"id": 5004, "name": "手コキ"},
                    {"id": 5019, "name": "パイズリ"},
                    {"id": 4009, "name": "巨乳フェチ"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 6561, "name": "特典付き・セット商品"},
                    {"id": 5071, "name": "ハーレム"},
                    {"id": 6102, "name": "サンプル動画"},
                ],
                "maker": [{"id": 1509, "name": "ムーディーズ"}],
                "actress": [
                    {"id": 1071048, "name": "水原みその", "ruby": "みずはらみその"},
                    {"id": 1053857, "name": "小梅えな", "ruby": "こうめえな"},
                    {"id": 1084337, "name": "羽月乃蒼", "ruby": "はるなのあ"},
                    {"id": 1091790, "name": "小坂ひまり", "ruby": "こさかひまり"},
                ],
                "director": [{"id": 108180, "name": "ZAMPA", "ruby": "ざんぱ"}],
                "label": [{"id": 3397, "name": "MOODYZ REAL"}],
            },
            "maker_product": "TKMIRD-261",
            "stock": "stock",
            "directory": [{"id": 764, "name": "DVD"}],
        }

    def test_product_basic_fields(self, product_data):
        """Test creating DVD Product from dictionary data."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "dvd"
        assert product.floor_name == "DVD"
        assert product.category_name == "DVD通販"
        assert product.content_id == "tkmird261"
        assert product.product_id == "tkmird261"
        assert (
            product.title
            == "【FANZA限定】爆乳保育士がむぎゅむぎゅ圧迫お遊戯会 授乳手コキハーレム保育園 水原みその 小梅えな 羽月乃蒼 小坂ひまり 生写真2枚付き"
        )
        assert product.volume == 160
        assert product.maker_product == "TKMIRD-261"
        assert product.stock == "stock"

    def test_product_date_parsing(self, product_data):
        """Test date parsing in DVD Product."""

        product = Product.from_dict(product_data)
        expected_date = datetime(2025, 8, 20, 0, 0, 1)
        assert product.date == expected_date

    def test_product_review_data(self, product_data):
        """Test DVD review data parsing."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 7
        assert product.review.average == 5.00

        assert product.review_count == 7
        assert product.review_average == 5.0

    def test_product_pricing_data(self, product_data):
        """Test DVD pricing data parsing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4028"
        assert product.prices.list_price == "4598"

        assert product.current_price == 4028
        assert product.original_price == 4598

    def test_product_image_urls(self, product_data):
        """Test DVD image URL parsing."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert (
            product.image_url.list
            == "https://pics.dmm.co.jp/mono/movie/adult/tkmird261/tkmird261pt.jpg"
        )
        assert (
            product.image_url.small
            == "https://pics.dmm.co.jp/mono/movie/adult/tkmird261/tkmird261ps.jpg"
        )
        assert (
            product.image_url.large
            == "https://pics.dmm.co.jp/mono/movie/adult/tkmird261/tkmird261pl.jpg"
        )

    def test_product_sample_images(self, product_data):
        """Test DVD sample image parsing."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_image_url.sample_s.image) == 9

        sample_images = product.sample_image_url.sample_s.image
        assert "mird00261-1.jpg" in sample_images[0]
        assert "mird00261-9.jpg" in sample_images[-1]

        sample_urls = product.sample_images
        assert len(sample_urls) == 9

    def test_product_item_info_genres(self, product_data):
        """Test DVD genre information parsing."""

        product = Product.from_dict(product_data)

        genres = product.genres
        assert len(genres) == 7
        assert genres[0].id == 5004
        assert genres[0].name == "手コキ"
        assert genres[1].id == 5019
        assert genres[1].name == "パイズリ"

    def test_product_item_info_actresses(self, product_data):
        """Test DVD actress information parsing."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 4
        assert actresses[0].id == 1071048
        assert actresses[0].name == "水原みその"
        assert actresses[0].ruby == "みずはらみその"

    def test_product_item_info_makers(self, product_data):
        """Test DVD maker information parsing."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 1509
        assert makers[0].name == "ムーディーズ"

    def test_product_item_info_manufactures(self, product_data):
        "Test mono dvd product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting DVD Product back to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "tkmird261"
        assert result_dict["title"] == product.title
        assert result_dict["volume"] == 160
        assert result_dict["date"] == "2025/08/20 00:00"

    def test_product_raw_data_access(self, product_data):
        """Test access to raw DVD API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "tkmird261"

    def test_sample_images_large(self, product_data):
        """Test large sample images for DVD products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for DVD products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for DVD products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode is None
        assert product.isbn is None
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for DVD products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.actresses) > 0
        assert len(product.makers) > 0
        assert len(product.directors) > 0
        assert len(product.labels) > 0

        assert len(product.actors) == 0
        assert len(product.series) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for DVD products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 7
        assert product.review_average == 5.0
        assert product.current_price == 4028
        assert product.original_price == 4598
        assert len(product.sample_images) == 9
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for DVD products."""

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
        """Test directory structure for DVD products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 1
        assert product.directory[0].id == 764
        assert product.directory[0].name == "DVD"

    def test_pricing_structure(self, product_data):
        """Test pricing structure for DVD products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4028"
        assert product.prices.list_price == "4598"
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 4028
        assert product.prices.list_price_int == 4598

    def test_delivery_options(self, product_data):
        """Test delivery options for DVD products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for DVD products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "dvd"
        assert product.floor_name == "DVD"
        assert product.category_name == "DVD通販"
        assert product.content_id == "tkmird261"
        assert product.product_id == "tkmird261"
        assert product.title is not None
        assert product.volume == 160
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product == "TKMIRD-261"
        assert product.isbn is None
        assert product.stock == "stock"
        assert product.raw_data is not None
