"""
Tests for Digital Amateur/VideoC products (service=digital, floor=videoc).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDigitalAmateurProduct(ProductTestBase):
    """Test cases for Digital Amateur/VideoC products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Digital amateur product data from DMM API response."""

        return {
            "service_code": "digital",
            "service_name": "動画",
            "floor_code": "videoc",
            "floor_name": "素人",
            "category_name": "素人 (動画)",
            "content_id": "stbs001",
            "product_id": "stbs001",
            "title": "りくさん（仮）",
            "volume": "1:29:00",
            "review": {"count": 27, "average": "5.00"},
            "URL": "https://video.dmm.co.jp/amateur/content/?id=stbs001",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Famateur%2Fcontent%2F%3Fid%3Dstbs001&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jm.jpg",
                "small": "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jm.jpg",
                "large": "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jp.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001js-001.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001js-002.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001js-003.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001js-004.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001js-005.jpg",
                    ]
                },
                "sample_l": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jp-001.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jp-002.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jp-003.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jp-004.jpg",
                        "https://pics.dmm.co.jp/digital/amateur/stbs001/stbs001jp-005.jpg",
                    ]
                },
            },
            "sampleMovieURL": {
                "size_476_306": "https://www.dmm.co.jp/litevideo/-/part/=/cid=stbs001/size=476_306/affi_id=***REDACTED_AFF_ID***/",
                "size_560_360": "https://www.dmm.co.jp/litevideo/-/part/=/cid=stbs001/size=560_360/affi_id=***REDACTED_AFF_ID***/",
                "size_644_414": "https://www.dmm.co.jp/litevideo/-/part/=/cid=stbs001/size=644_414/affi_id=***REDACTED_AFF_ID***/",
                "size_720_480": "https://www.dmm.co.jp/litevideo/-/part/=/cid=stbs001/size=720_480/affi_id=***REDACTED_AFF_ID***/",
                "pc_flag": 1,
                "sp_flag": 1,
            },
            "prices": {
                "price": "175~",
                "list_price": "250~",
                "deliveries": {
                    "delivery": [
                        {"type": "hd", "price": "1036", "list_price": "1480"},
                        {"type": "download", "price": "686", "list_price": "980"},
                        {"type": "stream", "price": "175", "list_price": "250"},
                        {"type": "iosdl", "price": "686", "list_price": "980"},
                        {"type": "androiddl", "price": "686", "list_price": "980"},
                    ]
                },
            },
            "date": "2022-10-12 10:00:02",
            "iteminfo": {
                "genre": [
                    {"id": 6533, "name": "ハイビジョン"},
                    {"id": 8511, "name": "スレンダー"},
                    {"id": 8513, "name": "色白"},
                    {"id": 8509, "name": "美乳"},
                    {"id": 6548, "name": "独占配信"},
                    {"id": 6002, "name": "ハメ撮り"},
                    {"id": 1039, "name": "人妻・主婦"},
                ],
                "maker": [{"id": 302366, "name": "セックスサセテナブルズ"}],
                "label": [{"id": 2064634, "name": "セックスサセテナブルズ"}],
            },
            "campaign": [
                {
                    "date_begin": "2025-10-14 00:00:00",
                    "date_end": "2025-10-16 23:59:59",
                    "title": "売れ筋！素人30％OFF第2弾",
                }
            ],
        }

    def test_product_basic_fields(self, product_data):
        """Test digital amateur product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "videoc"
        assert product.floor_name == "素人"
        assert product.category_name == "素人 (動画)"

        assert product.content_id == "stbs001"
        assert product.product_id == "stbs001"
        assert product.title == "りくさん（仮）"

    def test_product_sample_images(self, product_data):
        """Test that digital amateur products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 5
        assert "stbs001js-001.jpg" in small_images[0]
        assert "stbs001js-005.jpg" in small_images[4]

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 5
        assert "stbs001jp-001.jpg" in large_images[0]
        assert "stbs001jp-005.jpg" in large_images[4]

        assert len(product.sample_images) == 5
        assert len(product.sample_images_large) == 5

    def test_product_pricing_data(self, product_data):
        """Test digital amateur product's pricing with multiple delivery options."""

        product = Product.from_dict(product_data)

        assert product.prices is not None

        assert product.prices.price == "175~"
        assert product.prices.list_price == "250~"

        deliveries = product.prices.deliveries
        assert len(deliveries) == 5

        delivery_types = {d.type: d.price for d in deliveries}
        assert delivery_types["hd"] == "1036"
        assert delivery_types["download"] == "686"
        assert delivery_types["stream"] == "175"
        assert delivery_types["iosdl"] == "686"
        assert delivery_types["androiddl"] == "686"

        assert product.current_price == 175
        assert product.original_price == 250

    def test_product_item_info_genres(self, product_data):
        """Test digital amateur product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "スレンダー" in genre_names
        assert "色白" in genre_names
        assert "美乳" in genre_names
        assert "独占配信" in genre_names
        assert "ハメ撮り" in genre_names
        assert "人妻・主婦" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2022, 10, 12, 10, 0, 2)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test digital amateur product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/amateur/stbs001" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test digital amateur product actresses (should be empty for amateur)."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test digital amateur product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 302366
        assert makers[0].name == "セックスサセテナブルズ"

    def test_product_item_info_manufactures(self, product_data):
        """Test digital amateur product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting digital amateur product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "digital"
        assert result_dict["content_id"] == "stbs001"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw digital amateur API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "digital"
        assert raw_data["content_id"] == "stbs001"

    def test_sample_images_large(self, product_data):
        """Test large sample images for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 5

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is not None
        assert product.sample_movie_url.pc_flag == 1
        assert product.sample_movie_url.sp_flag == 1

    def test_optional_fields(self, product_data):
        """Test optional fields for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.tachiyomi is None
        assert product.cdinfo is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for digital amateur products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.labels) > 0

        assert len(product.actresses) == 0
        assert len(product.actors) == 0
        assert len(product.directors) == 0
        assert len(product.series) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 27
        assert product.review_average == 5.0
        assert product.current_price == 175
        assert product.original_price == 250
        assert len(product.sample_images) == 5
        assert len(product.sample_images_large) == 5

    def test_nested_objects(self, product_data):
        """Test nested objects for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is not None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is not None

    def test_directory_structure(self, product_data):
        """Test directory structure for digital amateur products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "175~"
        assert product.prices.list_price == "250~"
        assert len(product.prices.deliveries) == 5
        assert product.prices.price_int == 175
        assert product.prices.list_price_int == 250

    def test_delivery_options(self, product_data):
        """Test delivery options for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        delivery_types = {d.type for d in product.prices.deliveries}
        assert "hd" in delivery_types
        assert "download" in delivery_types
        assert "stream" in delivery_types
        assert "iosdl" in delivery_types
        assert "androiddl" in delivery_types

    def test_product_fields(self, product_data):
        """Test product fields for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "videoc"
        assert product.floor_name == "素人"
        assert product.category_name == "素人 (動画)"
        assert product.content_id == "stbs001"
        assert product.product_id == "stbs001"
        assert product.volume == "1:29:00"
        assert product.title is not None
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
        """Test review data for digital amateur products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 27
        assert product.review.average == 5.0
        assert product.review_count == 27
        assert product.review_average == 5.0

    def test_amateur_specific_fields(self, product_data):
        """Test amateur-specific fields and characteristics."""

        product = Product.from_dict(product_data)

        labels = product.labels
        assert len(labels) == 1
        assert labels[0].id == 2064634
        assert labels[0].name == "セックスサセテナブルズ"

        assert product.url is not None
        assert "/amateur/content/" in product.url
        assert product.affiliate_url is not None
        assert "%2Famateur%2Fcontent%2F" in product.affiliate_url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "amateur" in product.image_url.list
        assert "jm.jpg" in product.image_url.list

    def test_campaign_information(self, product_data):
        """Test campaign information for amateur products."""

        product = Product.from_dict(product_data)

        assert product.campaign is not None
        assert len(product.campaign) == 1

        campaign = product.campaign[0]
        assert campaign.title == "売れ筋！素人30％OFF第2弾"
        assert campaign.date_begin == "2025-10-14 00:00:00"
        assert campaign.date_end == "2025-10-16 23:59:59"

    def test_volume_time_format(self, product_data):
        """Test that volume in time format is handled correctly."""

        product = Product.from_dict(product_data)

        assert product.volume == "1:29:00"
        assert product.raw_data is not None
        assert product.raw_data["volume"] == "1:29:00"

    def test_amateur_genres(self, product_data):
        """Test amateur-specific genre characteristics."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハメ撮り" in genre_names

        body_type_genres = ["スレンダー", "色白", "美乳"]
        assert any(genre in genre_names for genre in body_type_genres)

    def test_pricing_discounts(self, product_data):
        """Test pricing shows discount from list price."""

        product = Product.from_dict(product_data)

        assert product.prices is not None

        current = product.current_price
        original = product.original_price

        assert current is not None
        assert original is not None
        assert current < original

        discount_percent = ((original - current) / original) * 100
        assert discount_percent > 0
