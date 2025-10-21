"""
Tests for Digital Video products (service=digital, floor=videoa).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDigitalVideoProduct(ProductTestBase):
    """Test cases for Digital Video products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Digital video product data from DMM API response."""

        return {
            "service_code": "digital",
            "service_name": "動画",
            "floor_code": "videoa",
            "floor_name": "ビデオ",
            "category_name": "ビデオ (動画)",
            "content_id": "sone00708",
            "product_id": "sone00708",
            "title": "村上悠華を【強力媚薬】でぶっ壊したい。この肉体がイキ跳ねて大痙攣するエビ反り超媚薬漬けアクメ",
            "volume": "120",
            "review": {"count": 14, "average": "5.00"},
            "URL": "https://video.dmm.co.jp/av/content/?id=sone00708",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Fcontent%2F%3Fid%3Dsone00708&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/video/sone00708/sone00708pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/video/sone00708/sone00708ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/video/sone00708/sone00708pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708-5.jpg",
                    ]
                },
                "sample_l": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708jp-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708jp-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708jp-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708jp-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/sone00708/sone00708jp-5.jpg",
                    ]
                },
            },
            "sampleMovieURL": {
                "size_476_306": "https://www.dmm.co.jp/litevideo/-/part/=/cid=sone00708/size=476_306/affi_id=***REDACTED_AFF_ID***/",
                "size_560_360": "https://www.dmm.co.jp/litevideo/-/part/=/cid=sone00708/size=560_360/affi_id=***REDACTED_AFF_ID***/",
                "size_644_414": "https://www.dmm.co.jp/litevideo/-/part/=/cid=sone00708/size=644_414/affi_id=***REDACTED_AFF_ID***/",
                "size_720_480": "https://www.dmm.co.jp/litevideo/-/part/=/cid=sone00708/size=720_480/affi_id=***REDACTED_AFF_ID***/",
                "pc_flag": 1,
                "sp_flag": 1,
            },
            "prices": {
                "price": "500~",
                "list_price": "500~",
                "deliveries": {
                    "delivery": [
                        {"type": "4k", "price": "2380", "list_price": "2380"},
                        {"type": "hd", "price": "1680", "list_price": "1680"},
                        {"type": "download", "price": "1180", "list_price": "1180"},
                        {"type": "stream", "price": "500", "list_price": "500"},
                        {"type": "iosdl", "price": "1180", "list_price": "1180"},
                        {"type": "androiddl", "price": "1180", "list_price": "1180"},
                    ]
                },
            },
            "date": "2025-06-06 00:00:32",
            "iteminfo": {
                "genre": [
                    {"id": 6533, "name": "ハイビジョン"},
                    {"id": 79015, "name": "4K"},
                    {"id": 6548, "name": "独占配信"},
                    {"id": 4030, "name": "淫乱・ハード系"},
                    {"id": 5022, "name": "3P・4P"},
                    {"id": 6968, "name": "アクメ・オーガズム"},
                ],
                "maker": [{"id": 3152, "name": "エスワン ナンバーワンスタイル"}],
                "actress": [{"id": 1085934, "name": "村上悠華", "ruby": "むらかみゆか"}],
                "director": [{"id": 101625, "name": "苺原", "ruby": "いちごはら"}],
                "label": [{"id": 3474, "name": "S1 NO.1 STYLE"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test digital video product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "videoa"
        assert product.floor_name == "ビデオ"
        assert product.category_name == "ビデオ (動画)"

        assert product.content_id == "sone00708"
        assert product.product_id == "sone00708"
        assert product.title == "村上悠華を【強力媚薬】でぶっ壊したい。この肉体がイキ跳ねて大痙攣するエビ反り超媚薬漬けアクメ"
        assert product.volume == 120

    def test_product_sample_images(self, product_data):
        """Test that digital products have both small and large sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 5
        assert "sone00708-1.jpg" in small_images[0]
        assert "sone00708-5.jpg" in small_images[4]

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 5
        assert "sone00708jp-1.jpg" in large_images[0]
        assert "sone00708jp-5.jpg" in large_images[4]

        assert len(product.sample_images) == 5
        assert len(product.sample_images_large) == 5

    def test_product_pricing_data(self, product_data):
        """Test digital product's complex pricing with multiple delivery options."""

        product = Product.from_dict(product_data)

        assert product.prices is not None

        assert product.prices.price == "500~"
        assert product.prices.list_price == "500~"

        deliveries = product.prices.deliveries
        assert len(deliveries) == 6

        delivery_types = {d.type: d.price for d in deliveries}
        assert delivery_types["4k"] == "2380"
        assert delivery_types["hd"] == "1680"
        assert delivery_types["download"] == "1180"
        assert delivery_types["stream"] == "500"
        assert delivery_types["iosdl"] == "1180"
        assert delivery_types["androiddl"] == "1180"

        assert product.current_price == 500
        assert product.original_price == 500

    def test_product_item_info_genres(self, product_data):
        """Test digital video product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "4K" in genre_names
        assert "独占配信" in genre_names
        assert "淫乱・ハード系" in genre_names
        assert "3P・4P" in genre_names
        assert "アクメ・オーガズム" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 6, 6, 0, 0, 32)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test digital product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/video/sone00708" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test digital video product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 1
        assert actresses[0].id == 1085934
        assert actresses[0].name == "村上悠華"
        assert actresses[0].ruby == "むらかみゆか"

    def test_product_item_info_makers(self, product_data):
        """Test digital video product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 3152
        assert makers[0].name == "エスワン ナンバーワンスタイル"

    def test_product_item_info_manufactures(self, product_data):
        """Test digital video product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting digital product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "digital"
        assert result_dict["content_id"] == "sone00708"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw digital API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "digital"
        assert raw_data["content_id"] == "sone00708"

    def test_sample_images_large(self, product_data):
        """Test large sample images for digital products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 5

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for digital products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is not None
        assert product.sample_movie_url.pc_flag == 1
        assert product.sample_movie_url.sp_flag == 1

    def test_optional_fields(self, product_data):
        """Test optional fields for digital products."""

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
        """Test item info categories for digital products."""

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
        """Test convenience properties for digital products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 14
        assert product.review_average == 5.0
        assert product.current_price == 500
        assert product.original_price == 500
        assert len(product.sample_images) == 5
        assert len(product.sample_images_large) == 5

    def test_nested_objects(self, product_data):
        """Test nested objects for digital products."""

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
        """Test directory structure for digital products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for digital products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "500~"
        assert product.prices.list_price == "500~"
        assert len(product.prices.deliveries) == 6
        assert product.prices.price_int == 500
        assert product.prices.list_price_int == 500

    def test_delivery_options(self, product_data):
        """Test delivery options for digital products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        delivery_types = {d.type for d in product.prices.deliveries}
        assert "4k" in delivery_types
        assert "hd" in delivery_types
        assert "download" in delivery_types
        assert "stream" in delivery_types
        assert "iosdl" in delivery_types
        assert "androiddl" in delivery_types

    def test_product_fields(self, product_data):
        """Test product fields for digital products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "videoa"
        assert product.floor_name == "ビデオ"
        assert product.category_name == "ビデオ (動画)"
        assert product.content_id == "sone00708"
        assert product.product_id == "sone00708"
        assert product.title is not None
        assert product.volume == 120
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
        """Test review data for digital products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 14
        assert product.review.average == 5.0
        assert product.review_count == 14
        assert product.review_average == 5.0
