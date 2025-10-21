"""
Tests for Digital Anime products (service=digital, floor=anime).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestDigitalAnimeProduct(ProductTestBase):
    """Test cases for Digital Anime products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Digital anime product data from DMM API response."""

        return {
            "service_code": "digital",
            "service_name": "動画",
            "floor_code": "anime",
            "floor_name": "アニメ動画",
            "category_name": "アニメ動画 (動画)",
            "content_id": "h_1379jdxa57770",
            "product_id": "h_1379jdxa57770",
            "title": "バブルdeハウスde○○○ THE ANIMATION",
            "volume": "31",
            "review": {"count": 7, "average": "5.00"},
            "URL": "https://video.dmm.co.jp/anime/content/?id=h_1379jdxa57770",
            "affiliateURL": "https://al.fanza.co.jp/?"
            + "lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fanime%2Fcontent%2F%3Fid%3Dh_1379jdxa57770&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-15.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-16.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-17.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-18.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-19.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770-20.jpg",
                    ]
                },
                "sample_l": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-15.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-16.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-17.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-18.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-19.jpg",
                        "https://pics.dmm.co.jp/digital/video/h_1379jdxa57770/h_1379jdxa57770jp-20.jpg",
                    ]
                },
            },
            "sampleMovieURL": {
                "size_476_306": "https://www.dmm.co.jp/litevideo/-/part/=/cid=h_1379jdxa57770/size=476_306/affi_id=***REDACTED_AFF_ID***/",
                "size_560_360": "https://www.dmm.co.jp/litevideo/-/part/=/cid=h_1379jdxa57770/size=560_360/affi_id=***REDACTED_AFF_ID***/",
                "size_644_414": "https://www.dmm.co.jp/litevideo/-/part/=/cid=h_1379jdxa57770/size=644_414/affi_id=***REDACTED_AFF_ID***/",
                "size_720_480": "https://www.dmm.co.jp/litevideo/-/part/=/cid=h_1379jdxa57770/size=720_480/affi_id=***REDACTED_AFF_ID***/",
                "pc_flag": 1,
                "sp_flag": 1,
            },
            "prices": {
                "price": "4950~",
                "list_price": "4950~",
                "deliveries": {
                    "delivery": [
                        {"type": "hd", "price": "5830", "list_price": "5830"},
                        {"type": "download", "price": "4950", "list_price": "4950"},
                        {"type": "stream", "price": "4950", "list_price": "4950"},
                        {"type": "iosdl", "price": "4950", "list_price": "4950"},
                        {"type": "androiddl", "price": "4950", "list_price": "4950"},
                    ]
                },
            },
            "date": "2025-01-24 10:00:04",
            "iteminfo": {
                "genre": [
                    {"id": 6153, "name": "ハイビジョン"},
                    {"id": 5041, "name": "中出し"},
                    {"id": 6139, "name": "ラブコメ"},
                    {"id": 2017, "name": "巨乳"},
                    {"id": 1059, "name": "女子大生"},
                    {"id": 6203, "name": "お風呂"},
                ],
                "series": [{"id": 4589261, "name": "バブルdeハウスde○○○"}],
                "maker": [{"id": 45018, "name": "ピンクパイナップル"}],
                "label": [{"id": 102, "name": "Pink Pineapple"}],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test digital anime product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "anime"
        assert product.floor_name == "アニメ動画"
        assert product.category_name == "アニメ動画 (動画)"

        assert product.content_id == "h_1379jdxa57770"
        assert product.product_id == "h_1379jdxa57770"
        assert product.title == "バブルdeハウスde○○○ THE ANIMATION"
        assert product.volume == 31

    def test_product_sample_images(self, product_data):
        """Test that digital anime products have both small and large sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 20
        assert "h_1379jdxa57770-1.jpg" in small_images[0]
        assert "h_1379jdxa57770-20.jpg" in small_images[19]

        large_images = product.sample_image_url.sample_l.image
        assert len(large_images) == 20
        assert "h_1379jdxa57770jp-1.jpg" in large_images[0]
        assert "h_1379jdxa57770jp-20.jpg" in large_images[19]

        assert len(product.sample_images) == 20
        assert len(product.sample_images_large) == 20

    def test_product_pricing_data(self, product_data):
        """Test digital anime product's pricing with multiple delivery options."""

        product = Product.from_dict(product_data)

        assert product.prices is not None

        assert product.prices.price == "4950~"
        assert product.prices.list_price == "4950~"

        deliveries = product.prices.deliveries
        assert len(deliveries) == 5

        delivery_types = {d.type: d.price for d in deliveries}
        assert delivery_types["hd"] == "5830"
        assert delivery_types["download"] == "4950"
        assert delivery_types["stream"] == "4950"
        assert delivery_types["iosdl"] == "4950"
        assert delivery_types["androiddl"] == "4950"

        assert product.current_price == 4950
        assert product.original_price == 4950

    def test_product_item_info_genres(self, product_data):
        """Test digital anime product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "ハイビジョン" in genre_names
        assert "中出し" in genre_names
        assert "ラブコメ" in genre_names
        assert "巨乳" in genre_names
        assert "女子大生" in genre_names
        assert "お風呂" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 1, 24, 10, 0, 4)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test digital anime product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/video/h_1379jdxa57770" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test digital anime product actresses (should be empty for anime)."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test digital anime product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 45018
        assert makers[0].name == "ピンクパイナップル"

    def test_product_item_info_manufactures(self, product_data):
        """Test digital anime product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting digital anime product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "digital"
        assert result_dict["content_id"] == "h_1379jdxa57770"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw digital anime API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "digital"
        assert raw_data["content_id"] == "h_1379jdxa57770"

    def test_sample_images_large(self, product_data):
        """Test large sample images for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 20

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is not None
        assert product.sample_movie_url.pc_flag == 1
        assert product.sample_movie_url.sp_flag == 1

    def test_optional_fields(self, product_data):
        """Test optional fields for digital anime products."""

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
        """Test item info categories for digital anime products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.labels) > 0
        assert len(product.series) > 0

        assert len(product.actresses) == 0
        assert len(product.actors) == 0
        assert len(product.directors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 7
        assert product.review_average == 5.0
        assert product.current_price == 4950
        assert product.original_price == 4950
        assert len(product.sample_images) == 20
        assert len(product.sample_images_large) == 20

    def test_nested_objects(self, product_data):
        """Test nested objects for digital anime products."""

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
        """Test directory structure for digital anime products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4950~"
        assert product.prices.list_price == "4950~"
        assert len(product.prices.deliveries) == 5
        assert product.prices.price_int == 4950
        assert product.prices.list_price_int == 4950

    def test_delivery_options(self, product_data):
        """Test delivery options for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        delivery_types = {d.type for d in product.prices.deliveries}
        assert "hd" in delivery_types
        assert "download" in delivery_types
        assert "stream" in delivery_types
        assert "iosdl" in delivery_types
        assert "androiddl" in delivery_types

    def test_product_fields(self, product_data):
        """Test product fields for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "anime"
        assert product.floor_name == "アニメ動画"
        assert product.category_name == "アニメ動画 (動画)"
        assert product.content_id == "h_1379jdxa57770"
        assert product.product_id == "h_1379jdxa57770"
        assert product.title is not None
        assert product.volume == 31
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
        """Test review data for digital anime products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 7
        assert product.review.average == 5.0
        assert product.review_count == 7
        assert product.review_average == 5.0

    def test_anime_specific_fields(self, product_data):
        """Test anime-specific fields and characteristics."""

        product = Product.from_dict(product_data)

        series = product.series
        assert len(series) == 1
        assert series[0].id == 4589261
        assert series[0].name == "バブルdeハウスde○○○"

        labels = product.labels
        assert len(labels) == 1
        assert labels[0].id == 102
        assert labels[0].name == "Pink Pineapple"

        assert product.url is not None
        assert "/anime/content/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fanime%2Fcontent%2F" in product.affiliate_url

    def test_sample_images_count(self, product_data):
        """Test that anime products have more sample images than typical video products."""

        product = Product.from_dict(product_data)

        assert len(product.sample_images) == 20
        assert len(product.sample_images_large) == 20

        for i, image_url in enumerate(product.sample_images, 1):
            assert f"h_1379jdxa57770-{i}.jpg" in image_url

        for i, image_url in enumerate(product.sample_images_large, 1):
            assert f"h_1379jdxa57770jp-{i}.jpg" in image_url
