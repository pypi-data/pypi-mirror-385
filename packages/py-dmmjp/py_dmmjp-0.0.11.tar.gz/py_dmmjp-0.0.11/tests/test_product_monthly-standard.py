"""
Tests for Monthly Standard products (service=monthly, floor=standard).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonthlyStandardProduct(ProductTestBase):
    """Test cases for Monthly Standard products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Monthly Standard product data from DMM API response."""

        return {
            "service_code": "monthly",
            "service_name": "月額動画",
            "floor_code": "standard",
            "floor_name": "見放題ch",
            "category_name": "見放題ch (月額動画)",
            "content_id": "huntc00132",
            "product_id": "huntc00132",
            "title": "親友に隠れて何度もNTR！飲み会の後、終電を逃して家に泊めた親友の彼女NTR盗撮！酔った勢いとノリでエッチまでしたら体の相性抜群で…",
            "volume": "239",
            "review": {"count": 18, "average": "4.61"},
            "URL": "https://www.dmm.co.jp/monthly/standard/-/detail/=/cid=huntc00132/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fstandard%2F-%2Fdetail%2F%3D%2Fcid%3Dhuntc00132%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132-15.jpg",
                    ]
                },
                "sample_l": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/huntc00132/huntc00132jp-15.jpg",
                    ]
                },
            },
            "sampleMovieURL": {
                "size_476_306": "https://www.dmm.co.jp/litevideo/-/part/=/cid=huntc00132/size=476_306/affi_id=***REDACTED_AFF_ID***/",
                "size_560_360": "https://www.dmm.co.jp/litevideo/-/part/=/cid=huntc00132/size=560_360/affi_id=***REDACTED_AFF_ID***/",
                "size_644_414": "https://www.dmm.co.jp/litevideo/-/part/=/cid=huntc00132/size=644_414/affi_id=***REDACTED_AFF_ID***/",
                "size_720_480": "https://www.dmm.co.jp/litevideo/-/part/=/cid=huntc00132/size=720_480/affi_id=***REDACTED_AFF_ID***/",
                "pc_flag": 1,
                "sp_flag": 1,
            },
            "prices": {"price": "3980"},
            "date": "2025-10-08 10:00:42",
            "iteminfo": {
                "genre": [
                    {"id": 6533, "name": "ハイビジョン"},
                    {"id": 6548, "name": "独占配信"},
                    {"id": 5001, "name": "中出し"},
                    {"id": 4111, "name": "寝取り・寝取られ・NTR"},
                    {"id": 6957, "name": "飲み会・合コン"},
                    {"id": 4030, "name": "淫乱・ハード系"},
                    {"id": 5002, "name": "フェラ"},
                ],
                "maker": [{"id": 45287, "name": "Hunter"}],
                "director": [{"id": 103965, "name": "川尻", "ruby": "かわじり"}],
                "label": [{"id": 25990, "name": "HHHグループ"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test monthly standard product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "monthly"
        assert product.service_name == "月額動画"
        assert product.floor_code == "standard"
        assert product.floor_name == "見放題ch"
        assert product.category_name == "見放題ch (月額動画)"

        assert product.content_id == "huntc00132"
        assert product.product_id == "huntc00132"
        assert (
            product.title
            == "親友に隠れて何度もNTR！飲み会の後、終電を逃して家に泊めた親友の彼女NTR盗撮！酔った勢いとノリでエッチまでしたら体の相性抜群で…"
        )
        assert product.volume == 239

    def test_product_sample_images(self, product_data):
        """Test that monthly standard products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 15
        assert "huntc00132-1.jpg" in small_images[0]
        assert "huntc00132-15.jpg" in small_images[14]

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 15
        assert "huntc00132jp-1.jpg" in large_images[0]
        assert "huntc00132jp-15.jpg" in large_images[14]

        assert len(product.sample_images) == 15
        assert len(product.sample_images_large) == 15

    def test_product_pricing_data(self, product_data):
        """Test monthly standard product's subscription pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "3980"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 3980
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test monthly standard product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "独占配信" in genre_names
        assert "中出し" in genre_names
        assert "寝取り・寝取られ・NTR" in genre_names
        assert "飲み会・合コン" in genre_names
        assert "淫乱・ハード系" in genre_names
        assert "フェラ" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 10, 8, 10, 0, 42)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test monthly standard product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/video/huntc00132" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test monthly standard product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test monthly standard product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 45287
        assert makers[0].name == "Hunter"

    def test_product_item_info_manufactures(self, product_data):
        "Test monthly standard product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting monthly standard product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "monthly"
        assert result_dict["content_id"] == "huntc00132"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw monthly standard API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "monthly"
        assert raw_data["content_id"] == "huntc00132"

    def test_sample_images_large(self, product_data):
        """Test large sample images for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 15

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is not None
        assert product.sample_movie_url.size_476_306 is not None
        assert product.sample_movie_url.size_560_360 is not None
        assert product.sample_movie_url.size_644_414 is not None
        assert product.sample_movie_url.size_720_480 is not None
        assert product.sample_movie_url.pc_flag == 1
        assert product.sample_movie_url.sp_flag == 1

    def test_optional_fields(self, product_data):
        """Test optional fields for monthly standard products."""

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
        """Test item info categories for monthly standard products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.labels) > 0
        assert len(product.directors) > 0

        assert len(product.actresses) == 0
        assert len(product.series) == 0
        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 18
        assert product.review_average == 4.61
        assert product.current_price == 3980
        assert product.original_price is None
        assert len(product.sample_images) == 15
        assert len(product.sample_images_large) == 15

    def test_nested_objects(self, product_data):
        """Test nested objects for monthly standard products."""

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
        """Test directory structure for monthly standard products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "3980"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 3980
        assert product.prices.list_price_int is None

    def test_delivery_options(self, product_data):
        """Test delivery options for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "monthly"
        assert product.service_name == "月額動画"
        assert product.floor_code == "standard"
        assert product.floor_name == "見放題ch"
        assert product.category_name == "見放題ch (月額動画)"
        assert product.content_id == "huntc00132"
        assert product.product_id == "huntc00132"
        assert product.title is not None
        assert product.volume == 239
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
        """Test review data for monthly standard products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 18
        assert product.review.average == 4.61
        assert product.review_count == 18
        assert product.review_average == 4.61

    def test_standard_specific_fields(self, product_data):
        """Test standard subscription specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/monthly/standard/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmonthly%2Fstandard%2F" in product.affiliate_url

        directors = product.directors
        assert len(directors) == 1
        assert directors[0].id == 103965
        assert directors[0].name == "川尻"
        assert directors[0].ruby == "かわじり"

        labels = product.labels
        assert len(labels) == 1
        assert labels[0].id == 25990
        assert labels[0].name == "HHHグループ"

        assert product.sample_movie_url is not None

    def test_standard_content_characteristics(self, product_data):
        """Test standard subscription content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "独占配信" in genre_names
        assert "寝取り・寝取られ・NTR" in genre_names
        assert "飲み会・合コン" in genre_names

        assert len(product.sample_images) == 15
        assert len(product.sample_images_large) == 15

        assert product.volume == 239

    def test_standard_subscription_model(self, product_data):
        """Test standard subscription pricing and access model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "3980"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 3980
        assert product.original_price is None

        assert product.sample_movie_url is not None
        movie_url = product.sample_movie_url
        assert movie_url.size_476_306 is not None
        assert movie_url.size_560_360 is not None
        assert movie_url.size_644_414 is not None
        assert movie_url.size_720_480 is not None
