"""
Tests for Doujin Digital TL products (service=doujin, floor=digital_doujin_tl).
"""

# pylint: disable=duplicate-code, too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDoujinDigitalTLProduct(ProductTestBase):
    """Test cases for Doujin Digital TL products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Doujin Digital TL product data from DMM API response."""

        return {
            "service_code": "doujin",
            "service_name": "同人",
            "floor_code": "digital_doujin_tl",
            "floor_name": "らぶカル（TL）",
            "category_name": "TL (電子書籍)",
            "content_id": "d_668247",
            "product_id": "d_668247",
            "title": "狼に衣 ～ドジなふりした幼馴染の執着体格差えっちに抗えない～",
            "volume": "69",
            "review": {"count": 1, "average": "5.00"},
            "URL": "https://lovecul.dmm.co.jp/tl/-/detail/=/cid=d_668247/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Flovecul.dmm.co.jp%2Ftl%2F-%2Fdetail%2F%3D%2Fcid%3Dd_668247%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247pt.jpg",
                "large": "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247pl.jpg",
            },
            "sampleImageURL": {
                "sample_l": {
                    "image": [
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-001.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-002.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-003.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-004.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-005.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-006.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-007.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-008.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-009.jpg",
                        "https://doujin-assets.dmm.co.jp/digital/comic/d_668247/d_668247jp-010.jpg",
                    ]
                }
            },
            "prices": {
                "price": "616",
                "list_price": "880",
                "deliveries": {
                    "delivery": [
                        {"type": "download", "price": "616", "list_price": "880"}
                    ]
                },
            },
            "date": "2025-10-01 00:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 1083, "name": "幼なじみ"},
                    {"id": 5001, "name": "中出し"},
                    {"id": 153003, "name": "おっぱい"},
                    {"id": 156006, "name": "女性向け"},
                    {"id": 156023, "name": "成人向け"},
                    {"id": 160109, "name": "執着攻め"},
                    {"id": 160161, "name": "種付けプレス"},
                    {"id": 160213, "name": "体格差"},
                ],
                "maker": [{"id": 75116, "name": "準社員井上"}],
            },
            "campaign": [
                {
                    "date_begin": "2025-10-01T00:00:00Z",
                    "date_end": "",
                    "title": "30%OFF",
                }
            ],
        }

    def test_product_basic_fields(self, product_data):
        """Test doujin digital TL product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_tl"
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"

        assert product.content_id == "d_668247"
        assert product.product_id == "d_668247"
        assert product.title == "狼に衣 ～ドジなふりした幼馴染の執着体格差えっちに抗えない～"
        assert product.volume == 69

    def test_product_sample_images(self, product_data):
        """Test that doujin digital TL products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 10
        assert "d_668247jp-001.jpg" in large_images[0]
        assert "d_668247jp-010.jpg" in large_images[9]

        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 10

    def test_product_pricing_data(self, product_data):
        """Test doujin digital TL product's discount pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "616"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 616
        assert product.original_price == 880

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "616"
        assert delivery.list_price == "880"

    def test_product_item_info_genres(self, product_data):
        """Test doujin digital TL product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "幼なじみ" in genre_names
        assert "中出し" in genre_names
        assert "おっぱい" in genre_names
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names
        assert "執着攻め" in genre_names
        assert "種付けプレス" in genre_names
        assert "体格差" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 10, 1, 0, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test doujin digital TL product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "doujin-assets.dmm.co.jp/digital/comic/d_668247" in product.image_url.list
        )
        assert product.image_url.small is None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test doujin digital TL product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test doujin digital TL product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 75116
        assert makers[0].name == "準社員井上"

    def test_product_item_info_manufactures(self, product_data):
        """Test doujin digital TL product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting doujin digital TL product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "doujin"
        assert result_dict["content_id"] == "d_668247"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw doujin digital TL API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "doujin"
        assert raw_data["content_id"] == "d_668247"

    def test_sample_images_large(self, product_data):
        """Test large sample images for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 10

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is not None

    def test_item_info_categories(self, product_data):
        """Test item info categories for doujin digital TL products."""

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
        """Test convenience properties for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 1
        assert product.review_average == 5.0
        assert product.current_price == 616
        assert product.original_price == 880
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 10

    def test_nested_objects(self, product_data):
        """Test nested objects for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is not None

    def test_directory_structure(self, product_data):
        """Test directory structure for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "616"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.prices.price_int == 616
        assert product.prices.list_price_int == 880

    def test_delivery_options(self, product_data):
        """Test delivery options for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 1

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "616"

    def test_product_fields(self, product_data):
        """Test product fields for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_tl"
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"
        assert product.content_id == "d_668247"
        assert product.product_id == "d_668247"
        assert product.title is not None
        assert product.volume == 69
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
        """Test review data for doujin digital TL products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 1
        assert product.review.average == 5.0
        assert product.review_count == 1
        assert product.review_average == 5.0

    def test_tl_specific_fields(self, product_data):
        """Test TL specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "lovecul.dmm.co.jp/tl/" in product.url
        assert product.affiliate_url is not None
        assert "lovecul.dmm.co.jp%2Ftl%2F" in product.affiliate_url

        assert "doujin-assets.dmm.co.jp" in product.image_url.list

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 75116
        assert makers[0].name == "準社員井上"

    def test_tl_content_characteristics(self, product_data):
        """Test TL content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "幼なじみ" in genre_names
        assert "中出し" in genre_names
        assert "おっぱい" in genre_names
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names
        assert "執着攻め" in genre_names
        assert "種付けプレス" in genre_names
        assert "体格差" in genre_names

        assert product.volume == 69
        assert len(product.sample_images_large) == 10

    def test_tl_pricing_model(self, product_data):
        """Test TL discount pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "616"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 616
        assert product.original_price == 880

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "616"
        assert delivery.list_price == "880"

    def test_tl_maker_info(self, product_data):
        """Test TL maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 75116
        assert maker.name == "準社員井上"

    def test_tl_category_structure(self, product_data):
        """Test TL category structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_tl"
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"

        assert len(product.directory) == 0

    def test_digital_tl_features(self, product_data):
        """Test digital TL specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.stock is None
        assert product.jancode is None

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"

        assert "doujin-assets.dmm.co.jp" in product.image_url.list
        assert "lovecul.dmm.co.jp/tl/" in product.url

    def test_tl_classification(self, product_data):
        """Test TL classification."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names

        assert len(product.sample_images_large) == 10
        assert product.volume == 69
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"

    def test_tl_content_tags(self, product_data):
        """Test TL content tagging system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "幼なじみ" in genre_names
        assert "執着攻め" in genre_names
        assert "種付けプレス" in genre_names
        assert "体格差" in genre_names

    def test_tl_image_structure(self, product_data):
        """Test TL image structure."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.small is None
        assert product.image_url.large is not None

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 10
        assert len(product.sample_images) == 0

        for i, image_url in enumerate(product.sample_images_large, 1):
            assert f"d_668247jp-{i:03d}.jpg" in image_url

    def test_tl_volume_info(self, product_data):
        """Test TL volume information."""

        product = Product.from_dict(product_data)

        assert product.volume == 69
        assert isinstance(product.volume, int)

    def test_tl_exclusive_content(self, product_data):
        """Test TL exclusive content features."""

        product = Product.from_dict(product_data)

        assert product.content_id.startswith("d_")
        assert product.product_id.startswith("d_")

        assert "lovecul.dmm.co.jp" in product.url
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"

    def test_lovecul_tl_platform_features(self, product_data):
        """Test Love Culture TL platform specific features."""

        product = Product.from_dict(product_data)

        assert "lovecul.dmm.co.jp" in product.url
        assert "lovecul.dmm.co.jp%2Ftl%2F" in product.affiliate_url
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "女性向け" in genre_names

    def test_tl_campaign_data(self, product_data):
        """Test TL campaign information."""

        product = Product.from_dict(product_data)

        assert product.campaign is not None
        assert len(product.campaign) == 1
        campaign = product.campaign[0]
        assert campaign.title == "30%OFF"
        assert campaign.date_begin == "2025-10-01T00:00:00Z"
        assert campaign.date_end == ""

    def test_tl_romance_genres(self, product_data):
        """Test TL romance-specific genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        romance_tags = ["幼なじみ", "執着攻め", "体格差"]
        for tag in romance_tags:
            assert tag in genre_names

        adult_tags = ["中出し", "種付けプレス", "おっぱい"]
        for tag in adult_tags:
            assert tag in genre_names

    def test_tl_discount_pricing(self, product_data):
        """Test TL discount pricing features."""

        product = Product.from_dict(product_data)

        assert product.current_price == 616
        assert product.original_price == 880
        discount_rate = (880 - 616) / 880
        assert abs(discount_rate - 0.3) < 0.01

        assert product.campaign is not None
        assert product.campaign[0].title == "30%OFF"

    def test_tl_genre_classification(self, product_data):
        """Test TL genre classification system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        target_audience_tags = ["女性向け", "成人向け"]
        for tag in target_audience_tags:
            assert tag in genre_names

        romance_scenario_tags = ["幼なじみ", "執着攻め", "体格差", "種付けプレス"]
        for tag in romance_scenario_tags:
            assert tag in genre_names
