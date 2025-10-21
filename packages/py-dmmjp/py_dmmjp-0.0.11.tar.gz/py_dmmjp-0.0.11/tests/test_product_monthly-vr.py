"""
Tests for Monthly VR products (service=monthly, floor=vr).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonthlyVRProduct(ProductTestBase):
    """Test cases for Monthly VR products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Monthly VR product data from DMM API response."""

        return {
            "service_code": "monthly",
            "service_name": "月額動画",
            "floor_code": "vr",
            "floor_name": "VRch",
            "category_name": "VRch (月額動画)",
            "content_id": "vrkm01415",
            "product_id": "vrkm01415",
            "title": "【VR】圧倒的美貌と性欲魔力に弄ばれる保護者不倫～息子の教師との踏み入れてはいけない関係～ 胡桃さくら",
            "volume": "80",
            "review": {"count": 19, "average": "5.00"},
            "URL": "https://www.dmm.co.jp/monthly/vr/-/detail/=/cid=vrkm01415/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fvr%2F-%2Fdetail%2F%3D%2Fcid%3Dvrkm01415%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-15.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-16.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415-17.jpg",
                    ]
                },
                "sample_l": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-15.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-16.jpg",
                        "https://pics.dmm.co.jp/digital/video/vrkm01415/vrkm01415jp-17.jpg",
                    ]
                },
            },
            "prices": {"price": "2800"},
            "date": "2025-09-16 10:00:06",
            "iteminfo": {
                "genre": [
                    {"id": 6925, "name": "ハイクオリティVR"},
                    {"id": 4025, "name": "単体作品"},
                    {"id": 6793, "name": "VR専用"},
                    {"id": 27, "name": "辱め"},
                    {"id": 1031, "name": "痴女"},
                    {"id": 5063, "name": "主観"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 5001, "name": "中出し"},
                ],
                "series": [
                    {
                        "id": 4296181,
                        "name": "圧倒的美貌と性欲魔力に弄ばれる保護者不倫",
                    }
                ],
                "maker": [{"id": 40071, "name": "ケイ・エム・プロデュース"}],
                "actress": [{"id": 1075066, "name": "胡桃さくら", "ruby": "くるみさくら"}],
                "director": [{"id": 114997, "name": "ウィルチンチン", "ruby": "うぃるちんちん"}],
                "label": [{"id": 25637, "name": "KMPVR"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test monthly VR product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "monthly"
        assert product.service_name == "月額動画"
        assert product.floor_code == "vr"
        assert product.floor_name == "VRch"
        assert product.category_name == "VRch (月額動画)"

        assert product.content_id == "vrkm01415"
        assert product.product_id == "vrkm01415"
        assert product.title == "【VR】圧倒的美貌と性欲魔力に弄ばれる保護者不倫～息子の教師との踏み入れてはいけない関係～ 胡桃さくら"
        assert product.volume == 80

    def test_product_sample_images(self, product_data):
        """Test that monthly VR products have extended sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 17
        assert "vrkm01415-1.jpg" in small_images[0]
        assert "vrkm01415-17.jpg" in small_images[16]

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 17
        assert "vrkm01415jp-1.jpg" in large_images[0]
        assert "vrkm01415jp-17.jpg" in large_images[16]

        assert len(product.sample_images) == 17
        assert len(product.sample_images_large) == 17

    def test_product_pricing_data(self, product_data):
        """Test monthly VR product's subscription pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "2800"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 2800
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test monthly VR product VR-specific genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイクオリティVR" in genre_names
        assert "VR専用" in genre_names
        assert "単体作品" in genre_names
        assert "主観" in genre_names
        assert "辱め" in genre_names
        assert "痴女" in genre_names
        assert "巨乳" in genre_names
        assert "中出し" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 9, 16, 10, 0, 6)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test monthly VR product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/video/vrkm01415" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test monthly VR product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 1
        assert actresses[0].id == 1075066
        assert actresses[0].name == "胡桃さくら"
        assert actresses[0].ruby == "くるみさくら"

    def test_product_item_info_makers(self, product_data):
        """Test monthly VR product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 40071
        assert makers[0].name == "ケイ・エム・プロデュース"

    def test_product_item_info_manufactures(self, product_data):
        "Test monthly vr product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting monthly VR product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "monthly"
        assert result_dict["content_id"] == "vrkm01415"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw monthly VR API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "monthly"
        assert raw_data["content_id"] == "vrkm01415"

    def test_sample_images_large(self, product_data):
        """Test large sample images for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 17

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for monthly VR products."""

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
        """Test item info categories for monthly VR products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.labels) > 0
        assert len(product.actresses) > 0
        assert len(product.directors) > 0
        assert len(product.series) > 0

        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 19
        assert product.review_average == 5.0
        assert product.current_price == 2800
        assert product.original_price is None
        assert len(product.sample_images) == 17
        assert len(product.sample_images_large) == 17

    def test_nested_objects(self, product_data):
        """Test nested objects for monthly VR products."""

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
        """Test directory structure for monthly VR products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "2800"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 2800
        assert product.prices.list_price_int is None

    def test_delivery_options(self, product_data):
        """Test delivery options for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "monthly"
        assert product.service_name == "月額動画"
        assert product.floor_code == "vr"
        assert product.floor_name == "VRch"
        assert product.category_name == "VRch (月額動画)"
        assert product.content_id == "vrkm01415"
        assert product.product_id == "vrkm01415"
        assert product.title is not None
        assert product.volume == 80
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
        """Test review data for monthly VR products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 19
        assert product.review.average == 5.0
        assert product.review_count == 19
        assert product.review_average == 5.0

    def test_vr_specific_fields(self, product_data):
        """Test VR subscription specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/monthly/vr/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmonthly%2Fvr%2F" in product.affiliate_url

        series = product.series
        assert len(series) == 1
        assert series[0].id == 4296181
        assert "圧倒的美貌と性欲魔力" in series[0].name

        directors = product.directors
        assert len(directors) == 1
        assert directors[0].id == 114997
        assert directors[0].name == "ウィルチンチン"
        assert directors[0].ruby == "うぃるちんちん"

        labels = product.labels
        assert len(labels) == 1
        assert labels[0].id == 25637
        assert labels[0].name == "KMPVR"

    def test_vr_content_characteristics(self, product_data):
        """Test VR-specific content features and quality."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイクオリティVR" in genre_names
        assert "VR専用" in genre_names
        assert "主観" in genre_names

        assert len(product.sample_images) == 17
        assert len(product.sample_images_large) == 17

        assert product.title.startswith("【VR】")
        assert product.volume == 80

    def test_vr_subscription_model(self, product_data):
        """Test VR subscription pricing and access model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "2800"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 2800
        assert product.original_price is None
