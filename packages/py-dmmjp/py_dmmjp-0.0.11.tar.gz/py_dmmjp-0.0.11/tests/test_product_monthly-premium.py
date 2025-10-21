"""
Tests for Monthly Premium products (service=monthly, floor=premium).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonthlyPremiumProduct(ProductTestBase):
    """Test cases for Monthly Premium products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Monthly premium product data from DMM API response."""

        return {
            "service_code": "monthly",
            "service_name": "月額動画",
            "floor_code": "premium",
            "floor_name": "見放題ch デラックス",
            "category_name": "見放題ch デラックス (月額動画)",
            "content_id": "juq00978",
            "product_id": "juq00978",
            "title": "息子の友人ともう5年間、セフレ関係を続けています―。 年下の子と不埒な火遊び…中出し情事に溺れる私。 大島優香",
            "volume": "124",
            "review": {"count": 36, "average": "5.00"},
            "URL": "https://www.dmm.co.jp/monthly/premium/-/detail/=/cid=juq00978/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Fdetail%2F%3D%2Fcid%3Djuq00978%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/video/juq00978/juq00978pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/video/juq00978/juq00978ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/video/juq00978/juq00978pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978-10.jpg",
                    ]
                },
                "sample_l": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/juq00978/juq00978jp-10.jpg",
                    ]
                },
            },
            "sampleMovieURL": {
                "size_476_306": "https://www.dmm.co.jp/litevideo/-/part/=/cid=juq00978/size=476_306/affi_id=***REDACTED_AFF_ID***/",
                "size_560_360": "https://www.dmm.co.jp/litevideo/-/part/=/cid=juq00978/size=560_360/affi_id=***REDACTED_AFF_ID***/",
                "size_644_414": "https://www.dmm.co.jp/litevideo/-/part/=/cid=juq00978/size=644_414/affi_id=***REDACTED_AFF_ID***/",
                "size_720_480": "https://www.dmm.co.jp/litevideo/-/part/=/cid=juq00978/size=720_480/affi_id=***REDACTED_AFF_ID***/",
                "pc_flag": 1,
                "sp_flag": 1,
            },
            "prices": {"price": "8980"},
            "date": "2025-06-24 10:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 6533, "name": "ハイビジョン"},
                    {"id": 6548, "name": "独占配信"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 1014, "name": "熟女"},
                    {"id": 1069, "name": "不倫"},
                    {"id": 1039, "name": "人妻・主婦"},
                    {"id": 5001, "name": "中出し"},
                    {"id": 4025, "name": "単体作品"},
                ],
                "series": [
                    {
                        "id": 4304515,
                        "name": "息子の友人ともう5年間、セフレ関係を続けています─。",
                    }
                ],
                "maker": [{"id": 2661, "name": "マドンナ"}],
                "actress": [{"id": 1028857, "name": "大島優香", "ruby": "おおしまゆうか"}],
                "director": [{"id": 1443, "name": "朝霧浄", "ruby": "あさぎりじょう"}],
                "label": [{"id": 2931, "name": "Madonna"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test monthly premium product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "monthly"
        assert product.service_name == "月額動画"
        assert product.floor_code == "premium"
        assert product.floor_name == "見放題ch デラックス"
        assert product.category_name == "見放題ch デラックス (月額動画)"

        assert product.content_id == "juq00978"
        assert product.product_id == "juq00978"
        assert (
            product.title == "息子の友人ともう5年間、セフレ関係を続けています―。 年下の子と不埒な火遊び…中出し情事に溺れる私。 大島優香"
        )
        assert product.volume == 124

    def test_product_sample_images(self, product_data):
        """Test that monthly premium products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 10
        assert "juq00978-1.jpg" in small_images[0]
        assert "juq00978-10.jpg" in small_images[9]

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 10
        assert "juq00978jp-1.jpg" in large_images[0]
        assert "juq00978jp-10.jpg" in large_images[9]

        assert len(product.sample_images) == 10
        assert len(product.sample_images_large) == 10

    def test_product_pricing_data(self, product_data):
        """Test monthly premium product's flat pricing structure."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "8980"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 8980
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test monthly premium product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "独占配信" in genre_names
        assert "巨乳" in genre_names
        assert "熟女" in genre_names
        assert "不倫" in genre_names
        assert "人妻・主婦" in genre_names
        assert "中出し" in genre_names
        assert "単体作品" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 6, 24, 10, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test monthly premium product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/video/juq00978" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test monthly premium product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 1
        assert actresses[0].id == 1028857
        assert actresses[0].name == "大島優香"
        assert actresses[0].ruby == "おおしまゆうか"

    def test_product_item_info_makers(self, product_data):
        """Test monthly premium product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 2661
        assert makers[0].name == "マドンナ"

    def test_product_item_info_manufactures(self, product_data):
        "Test monthly premium product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting monthly premium product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "monthly"
        assert result_dict["content_id"] == "juq00978"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw monthly premium API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "monthly"
        assert raw_data["content_id"] == "juq00978"

    def test_sample_images_large(self, product_data):
        """Test large sample images for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 10

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is not None
        assert product.sample_movie_url.pc_flag == 1
        assert product.sample_movie_url.sp_flag == 1

    def test_optional_fields(self, product_data):
        """Test optional fields for monthly premium products."""

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
        """Test item info categories for monthly premium products."""

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
        """Test convenience properties for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 36
        assert product.review_average == 5.0
        assert product.current_price == 8980
        assert product.original_price is None
        assert len(product.sample_images) == 10
        assert len(product.sample_images_large) == 10

    def test_nested_objects(self, product_data):
        """Test nested objects for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is not None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for monthly premium products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "8980"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 8980
        assert product.prices.list_price_int is None

    def test_delivery_options(self, product_data):
        """Test delivery options for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "monthly"
        assert product.service_name == "月額動画"
        assert product.floor_code == "premium"
        assert product.floor_name == "見放題ch デラックス"
        assert product.category_name == "見放題ch デラックス (月額動画)"
        assert product.content_id == "juq00978"
        assert product.product_id == "juq00978"
        assert product.title is not None
        assert product.volume == 124
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
        """Test review data for monthly premium products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 36
        assert product.review.average == 5.0
        assert product.review_count == 36
        assert product.review_average == 5.0

    def test_monthly_specific_fields(self, product_data):
        """Test monthly subscription specific fields."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/monthly/premium/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmonthly%2Fpremium%2F" in product.affiliate_url

        series = product.series
        assert len(series) == 1
        assert series[0].id == 4304515
        assert "息子の友人ともう5年間" in series[0].name

        directors = product.directors
        assert len(directors) == 1
        assert directors[0].id == 1443
        assert directors[0].name == "朝霧浄"
        assert directors[0].ruby == "あさぎりじょう"

        labels = product.labels
        assert len(labels) == 1
        assert labels[0].id == 2931
        assert labels[0].name == "Madonna"

    def test_subscription_pricing_model(self, product_data):
        """Test subscription-based pricing characteristics."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price is not None
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0

        assert product.current_price == 8980
        assert product.original_price is None

    def test_premium_content_characteristics(self, product_data):
        """Test premium subscription content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "独占配信" in genre_names
        assert "単体作品" in genre_names

        assert len(product.sample_images) == 10
        assert len(product.sample_images_large) == 10

        assert product.volume == 124
        assert product.review_count > 0
        assert product.review_average == 5.0
