"""
Tests for Mono Anime products (service=mono, floor=anime).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoAnimeProduct(ProductTestBase):
    """Test cases for Mono Anime products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Mono Anime product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "anime",
            "floor_name": "アニメ",
            "category_name": "アニメ通販",
            "content_id": "196glod0339t",
            "product_id": "196glod0339t",
            "title": "【FANZA限定】OVAシスターブリーダー #2 セル版 オリジナルB2タペストリー付",
            "volume": "20",
            "review": {"count": 1, "average": "3.00"},
            "URL": "https://www.dmm.co.jp/mono/anime/-/detail/=/cid=196glod0339t/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fanime%2F-%2Fdetail%2F%3D%2Fcid%3D196glod0339t%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/mono/movie/adult/196glod0339t/196glod0339tpt.jpg",
                "small": "https://pics.dmm.co.jp/mono/movie/adult/196glod0339t/196glod0339tps.jpg",
                "large": "https://pics.dmm.co.jp/mono/movie/adult/196glod0339t/196glod0339tpl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-1.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-2.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-3.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-4.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-5.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-6.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-7.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-8.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-9.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-10.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-11.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-12.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-13.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-14.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-15.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-16.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-17.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-18.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-19.jpg",
                        "https://pics.dmm.co.jp/digital/video/196glod0339/196glod0339-20.jpg",
                    ]
                }
            },
            "date": "2025-09-26 00:00:01",
            "iteminfo": {
                "genre": [
                    {"id": 6180, "name": "特典付き・セット商品"},
                    {"id": 6102, "name": "サンプル動画"},
                    {"id": 4109, "name": "姉・妹"},
                    {"id": 2017, "name": "巨乳"},
                    {"id": 4066, "name": "学園もの"},
                    {"id": 5041, "name": "中出し"},
                ],
                "series": [{"id": 4593786, "name": "OVAシスターブリーダーシリーズ"}],
                "maker": [{"id": 45012, "name": "ルネピクチャーズ"}],
                "label": [{"id": 24860, "name": "ばにぃうぉ〜か〜"}],
            },
            "maker_product": "GLOD-0339T",
            "stock": "stock",
            "directory": [{"id": 1391, "name": "DVD"}],
        }

    def test_product_basic_fields(self, product_data):
        """Test mono anime product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "anime"
        assert product.floor_name == "アニメ"
        assert product.category_name == "アニメ通販"

        assert product.content_id == "196glod0339t"
        assert product.product_id == "196glod0339t"
        assert product.title == "【FANZA限定】OVAシスターブリーダー #2 セル版 オリジナルB2タペストリー付"
        assert product.volume == 20

    def test_product_sample_images(self, product_data):
        """Test that mono anime products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 20
        assert "196glod0339-1.jpg" in small_images[0]
        assert "196glod0339-20.jpg" in small_images[19]

        assert len(product.sample_images) == 20
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test mono anime product's physical product pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is None

    def test_product_item_info_genres(self, product_data):
        """Test mono anime product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "特典付き・セット商品" in genre_names
        assert "サンプル動画" in genre_names
        assert "姉・妹" in genre_names
        assert "巨乳" in genre_names
        assert "学園もの" in genre_names
        assert "中出し" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 9, 26, 0, 0, 1)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test mono anime product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "mono/movie/adult/196glod0339t" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test mono anime product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test mono anime product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 45012
        assert makers[0].name == "ルネピクチャーズ"

    def test_product_item_info_manufactures(self, product_data):
        """Test mono anime product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting mono anime product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "196glod0339t"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw mono anime API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "196glod0339t"

    def test_sample_images_large(self, product_data):
        """Test large sample images for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode is None
        assert product.maker_product == "GLOD-0339T"
        assert product.isbn is None
        assert product.stock == "stock"
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for mono anime products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.labels) > 0
        assert len(product.series) > 0
        assert len(product.directory) > 0

        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 1
        assert product.review_average == 3.0
        assert product.current_price is None
        assert product.original_price is None
        assert len(product.sample_images) == 20
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for mono anime products."""

        product = Product.from_dict(product_data)

        directories = product.directory
        assert len(directories) == 1

        dir_names = [d.name for d in directories]
        assert "DVD" in dir_names

        dir_ids = [d.id for d in directories]
        assert 1391 in dir_ids

    def test_pricing_structure(self, product_data):
        """Test pricing structure for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.prices is None

    def test_delivery_options(self, product_data):
        """Test delivery options for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.prices is None

    def test_product_fields(self, product_data):
        """Test product fields for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "anime"
        assert product.floor_name == "アニメ"
        assert product.category_name == "アニメ通販"
        assert product.content_id == "196glod0339t"
        assert product.product_id == "196glod0339t"
        assert product.title is not None
        assert product.volume == 20
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product == "GLOD-0339T"
        assert product.isbn is None
        assert product.stock == "stock"
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for mono anime products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 1
        assert product.review.average == 3.0
        assert product.review_count == 1
        assert product.review_average == 3.0

    def test_anime_specific_fields(self, product_data):
        """Test anime specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/mono/anime/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmono%2Fanime%2F" in product.affiliate_url

        assert product.maker_product == "GLOD-0339T"
        assert product.stock == "stock"

        directories = product.directory
        assert len(directories) == 1
        assert directories[0].id == 1391
        assert directories[0].name == "DVD"

        series = product.series
        assert len(series) == 1
        assert series[0].id == 4593786
        assert series[0].name == "OVAシスターブリーダーシリーズ"

    def test_anime_content_characteristics(self, product_data):
        """Test anime content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "特典付き・セット商品" in genre_names
        assert "サンプル動画" in genre_names
        assert "学園もの" in genre_names
        assert "姉・妹" in genre_names

        assert product.volume == 20
        assert len(product.sample_images) == 20
        assert product.sample_movie_url is None

        assert product.title.startswith("【FANZA限定】")
        assert "OVA" in product.title
        assert "セル版" in product.title

    def test_anime_pricing_model(self, product_data):
        """Test anime pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is None
        assert product.current_price is None
        assert product.original_price is None

    def test_physical_anime_attributes(self, product_data):
        """Test physical anime product specific attributes."""

        product = Product.from_dict(product_data)

        assert product.maker_product is not None
        assert product.maker_product == "GLOD-0339T"

        assert product.stock is not None
        assert product.stock == "stock"

        directories = product.directory
        assert len(directories) == 1
        directory = directories[0]
        assert directory.id == 1391
        assert directory.name == "DVD"

    def test_anime_maker_info(self, product_data):
        """Test anime maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 45012
        assert maker.name == "ルネピクチャーズ"

        labels = product.labels
        assert len(labels) == 1
        label = labels[0]
        assert label.id == 24860
        assert label.name == "ばにぃうぉ〜か〜"

    def test_anime_series_structure(self, product_data):
        """Test anime series structure."""

        product = Product.from_dict(product_data)

        series = product.series
        assert len(series) == 1

        series_item = series[0]
        assert series_item.id == 4593786
        assert series_item.name == "OVAシスターブリーダーシリーズ"

    def test_anime_sample_content(self, product_data):
        """Test anime sample content availability."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 20

        for i, image_url in enumerate(small_images, 1):
            assert f"196glod0339-{i}.jpg" in image_url

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "サンプル動画" in genre_names
