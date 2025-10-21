"""
Tests for CD products (service=mono, floor=cd).
"""

# pylint: disable=R0904

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoCDProduct(ProductTestBase):
    """Test cases for CD products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """CD product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "cd",
            "floor_name": "CD",
            "category_name": "CD通販",
            "content_id": "cd_258empc5158",
            "product_id": "cd_258empc5158",
            "title": "【予約特典付き】ミュージカル『刀剣乱舞』 ～陸奥一蓮～ （初回限定盤B）/刀剣男士 formation of 陸奥一蓮",
            "URL": "https://www.dmm.com/mono/cd/-/detail/=/cid=cd_258empc5158/",
            "affiliateURL": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com"
            "%2Fmono%2Fcd%2F-%2Fdetail%2F%3D%2Fcid%3Dcd_258empc5158%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.com/mono/cd/anime_game/cd_258empc5158/cd_258empc5158pt.jpg",
                "small": "https://pics.dmm.com/mono/cd/anime_game/cd_258empc5158/cd_258empc5158ps.jpg",
                "large": "https://pics.dmm.com/mono/cd/anime_game/cd_258empc5158/cd_258empc5158pl.jpg",
            },
            "prices": {"price": "4950"},
            "date": "2025-12-10 10:00:00",
            "iteminfo": {
                "genre": [{"id": 79022, "name": "刀剣乱舞"}],
                "series": [{"id": 65820, "name": "ミュージカル『刀剣乱舞』"}],
                "maker": [{"id": 81607, "name": "ユークリッド・エージェンシー"}],
                "artist": [
                    {
                        "id": 219614,
                        "name": "刀剣男士 formation of 陸奥一蓮",
                        "ruby": "とうけんだんしふぉーめーしょんおぶみちのおくひとつはちす",
                    }
                ],
            },
            "jancode": "4571603151292",
            "stock": "reserve_empty",
            "cdinfo": {"kind": "シングル"},
            "directory": [
                {"id": 776, "name": "アニメ・ゲーム"},
                {"id": 796, "name": "2.5次元"},
                {"id": 824, "name": "その他"},
            ],
        }

    def test_product_basic_fields(self, product_data):
        """Test CD product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "cd"
        assert product.floor_name == "CD"
        assert product.category_name == "CD通販"

        assert product.content_id == "cd_258empc5158"
        assert product.product_id == "cd_258empc5158"
        assert (
            product.title
            == "【予約特典付き】ミュージカル『刀剣乱舞』 ～陸奥一蓮～ （初回限定盤B）/刀剣男士 formation of 陸奥一蓮"
        )
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that CD products have no sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test CD product's pricing structure."""

        product = Product.from_dict(product_data)

        assert product.prices is not None

        assert product.prices.price == "4950"
        assert product.prices.list_price is None

        assert product.prices.deliveries is None or len(product.prices.deliveries) == 0

        assert product.current_price == 4950
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test CD product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        assert len(genres) == 1
        assert genres[0].id == 79022
        assert genres[0].name == "刀剣乱舞"

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 12, 10, 10, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test CD product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "mono/cd/anime_game/cd_258empc5158" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test CD product actresses (should be empty for CD)."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test CD product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 81607
        assert makers[0].name == "ユークリッド・エージェンシー"

    def test_product_item_info_manufactures(self, product_data):
        """Test CD product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting CD product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "cd_258empc5158"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw CD API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "cd_258empc5158"

    def test_sample_images_large(self, product_data):
        """Test large sample images for CD products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for CD products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for CD products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode == "4571603151292"
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock == "reserve_empty"
        assert product.tachiyomi is None
        assert product.cdinfo is not None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for CD products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.series) > 0
        assert len(product.artists) > 0

        assert len(product.actresses) == 0
        assert len(product.actors) == 0
        assert len(product.directors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0
        assert len(product.labels) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for CD products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 0
        assert product.review_average is None
        assert product.current_price == 4950
        assert product.original_price is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for CD products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is None
        assert product.item_info is not None
        assert product.cdinfo is not None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for CD products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 3
        assert product.directory[0].id == 776
        assert product.directory[0].name == "アニメ・ゲーム"
        assert product.directory[1].id == 796
        assert product.directory[1].name == "2.5次元"
        assert product.directory[2].id == 824
        assert product.directory[2].name == "その他"

    def test_pricing_structure(self, product_data):
        """Test pricing structure for CD products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4950"
        assert product.prices.list_price is None
        assert product.prices.deliveries is None or len(product.prices.deliveries) == 0
        assert product.prices.price_int == 4950
        assert product.prices.list_price_int is None

    def test_delivery_options(self, product_data):
        """Test delivery options for CD products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.deliveries is None or len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for CD products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "cd"
        assert product.floor_name == "CD"
        assert product.category_name == "CD通販"
        assert product.content_id == "cd_258empc5158"
        assert product.product_id == "cd_258empc5158"
        assert product.title is not None
        assert product.volume is None
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode == "4571603151292"
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock == "reserve_empty"
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for CD products."""

        product = Product.from_dict(product_data)

        assert product.review is None
        assert product.review_count == 0
        assert product.review_average is None

    def test_cd_specific_fields(self, product_data):
        """Test CD-specific fields and characteristics."""

        product = Product.from_dict(product_data)

        assert product.cdinfo is not None
        assert product.cdinfo.kind == "シングル"

        artists = product.artists
        assert len(artists) == 1
        assert artists[0].id == 219614
        assert artists[0].name == "刀剣男士 formation of 陸奥一蓮"
        assert artists[0].ruby == "とうけんだんしふぉーめーしょんおぶみちのおくひとつはちす"

        series = product.series
        assert len(series) == 1
        assert series[0].id == 65820
        assert series[0].name == "ミュージカル『刀剣乱舞』"

        assert product.url is not None
        assert "/mono/cd/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmono%2Fcd%2F" in product.affiliate_url

    def test_cd_stock_status(self, product_data):
        """Test CD stock status."""

        product = Product.from_dict(product_data)

        assert product.stock == "reserve_empty"
        assert product.jancode == "4571603151292"

    def test_cd_directory_categories(self, product_data):
        """Test CD directory categories."""

        product = Product.from_dict(product_data)

        directory_names = [d.name for d in product.directory]
        assert "アニメ・ゲーム" in directory_names
        assert "2.5次元" in directory_names
        assert "その他" in directory_names

        directory_ids = [d.id for d in product.directory]
        assert 776 in directory_ids
        assert 796 in directory_ids
        assert 824 in directory_ids

    def test_cd_artist_information(self, product_data):
        """Test CD artist information parsing."""

        product = Product.from_dict(product_data)

        assert len(product.artists) == 1
        artist = product.artists[0]
        assert artist.id == 219614
        assert "刀剣男士" in artist.name
        assert artist.ruby is not None
        assert len(artist.ruby) > 0

    def test_cd_no_video_content(self, product_data):
        """Test that CD products have no video-related content."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_cd_pricing_no_deliveries(self, product_data):
        """Test that CD products have simple pricing without delivery options."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4950"
        assert product.prices.list_price is None
        assert product.prices.deliveries is None or len(product.prices.deliveries) == 0
        assert product.current_price == 4950
        assert product.original_price is None
