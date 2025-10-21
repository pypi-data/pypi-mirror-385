"""
Tests for Mono Figure products (service=mono, floor=figure).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoFigureProduct(ProductTestBase):
    """Test cases for Mono Figure products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Mono Figure product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "figure",
            "floor_name": "フィギュア・グッズ",
            "category_name": "フィギュア・グッズ通販",
            "content_id": "fig_2510021531441",
            "product_id": "fig_2510021531441",
            "title": "氷見山珖",
            "URL": "https://www.dmm.co.jp/mono/figure/-/detail/=/cid=fig_2510021531441/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Ffigure%2F-%2Fdetail%2F%3D%2Fcid%3Dfig_2510021531441%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/mono/figure/fig_2510021531441/fig_2510021531441pt.jpg",
                "small": "https://pics.dmm.co.jp/mono/figure/fig_2510021531441/fig_2510021531441ps.jpg",
                "large": "https://pics.dmm.co.jp/mono/figure/fig_2510021531441/fig_2510021531441pl.jpg",
            },
            "prices": {"list_price": "29700"},
            "date": "2026-05-31 10:00:00",
            "iteminfo": {
                "genre": [{"id": 300243, "name": "フィギュア"}],
                "maker": [{"id": 24308, "name": "ロケットボーイ"}],
            },
            "jancode": "4573343560761",
            "stock": "reserve",
            "directory": [
                {"id": 1154, "name": "フィギュア"},
                {"id": 1157, "name": "キャラクターフィギュア_スケール"},
            ],
        }

    def test_product_basic_fields(self, product_data):
        """Test mono figure product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "figure"
        assert product.floor_name == "フィギュア・グッズ"
        assert product.category_name == "フィギュア・グッズ通販"

        assert product.content_id == "fig_2510021531441"
        assert product.product_id == "fig_2510021531441"
        assert product.title == "氷見山珖"
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that mono figure products do not have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test mono figure product's physical product pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price is None
        assert product.prices.list_price == "29700"
        assert len(product.prices.deliveries) == 0
        assert product.current_price is None
        assert product.original_price == 29700

    def test_product_item_info_genres(self, product_data):
        """Test mono figure product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "フィギュア" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2026, 5, 31, 10, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test mono figure product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "mono/figure/fig_2510021531441" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test mono figure product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test mono figure product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 24308
        assert makers[0].name == "ロケットボーイ"

    def test_product_item_info_manufactures(self, product_data):
        "Test mono figure product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting mono figure product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "fig_2510021531441"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw mono figure API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "fig_2510021531441"

    def test_sample_images_large(self, product_data):
        """Test large sample images for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode == "4573343560761"
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock == "reserve"
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for mono figure products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.directory) > 0

        assert len(product.labels) == 0
        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.series) == 0
        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 0
        assert product.current_price is None
        assert product.original_price == 29700
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.review_average is None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for mono figure products."""

        product = Product.from_dict(product_data)

        directories = product.directory
        assert len(directories) == 2

        dir_names = [d.name for d in directories]
        assert "フィギュア" in dir_names
        assert "キャラクターフィギュア_スケール" in dir_names

        dir_ids = [d.id for d in directories]
        assert 1154 in dir_ids
        assert 1157 in dir_ids

    def test_pricing_structure(self, product_data):
        """Test pricing structure for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price is None
        assert product.prices.list_price == "29700"
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int is None
        assert product.prices.list_price_int == 29700

    def test_delivery_options(self, product_data):
        """Test delivery options for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "figure"
        assert product.floor_name == "フィギュア・グッズ"
        assert product.category_name == "フィギュア・グッズ通販"
        assert product.content_id == "fig_2510021531441"
        assert product.product_id == "fig_2510021531441"
        assert product.title is not None
        assert product.volume is None
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode == "4573343560761"
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock == "reserve"
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for mono figure products."""

        product = Product.from_dict(product_data)

        assert product.review is None
        assert product.review_count == 0
        assert product.review_average is None

    def test_figure_specific_fields(self, product_data):
        """Test figure specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/mono/figure/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmono%2Ffigure%2F" in product.affiliate_url

        assert product.jancode == "4573343560761"
        assert product.stock == "reserve"

        directories = product.directory
        assert len(directories) == 2
        assert directories[0].id == 1154
        assert directories[0].name == "フィギュア"
        assert directories[1].id == 1157
        assert directories[1].name == "キャラクターフィギュア_スケール"

    def test_figure_content_characteristics(self, product_data):
        """Test figure content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "フィギュア" in genre_names

        assert product.volume is None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None

    def test_figure_pricing_model(self, product_data):
        """Test figure pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price is None
        assert product.prices.list_price == "29700"
        assert len(product.prices.deliveries) == 0
        assert product.current_price is None
        assert product.original_price == 29700

    def test_physical_figure_attributes(self, product_data):
        """Test physical figure specific attributes."""

        product = Product.from_dict(product_data)

        assert product.jancode is not None
        assert len(product.jancode) == 13
        assert product.jancode.isdigit()

        assert product.stock is not None
        assert product.stock == "reserve"

        directories = product.directory
        assert len(directories) == 2
        for directory in directories:
            assert directory.id is not None
            assert directory.name is not None

    def test_figure_maker_info(self, product_data):
        """Test figure maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 24308
        assert maker.name == "ロケットボーイ"

    def test_figure_category_structure(self, product_data):
        """Test figure category and directory structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "figure"
        assert product.floor_name == "フィギュア・グッズ"

        directories = product.directory
        assert len(directories) == 2

        category_mapping = {
            1154: "フィギュア",
            1157: "キャラクターフィギュア_スケール",
        }

        for directory in directories:
            assert directory.id in category_mapping
            assert directory.name == category_mapping[directory.id]

    def test_preorder_figure_features(self, product_data):
        """Test pre-order figure characteristics."""

        product = Product.from_dict(product_data)

        assert product.stock == "reserve"

        release_date = product.date
        assert release_date is not None
        assert release_date.year == 2026
        assert release_date.month == 5
        assert release_date.day == 31

    def test_scale_figure_classification(self, product_data):
        """Test scale figure classification."""

        product = Product.from_dict(product_data)

        assert product.category_name == "フィギュア・グッズ通販"
        assert product.floor_name == "フィギュア・グッズ"

        directories = product.directory
        directory_names = [d.name for d in directories]
        assert "フィギュア" in directory_names
        assert "キャラクターフィギュア_スケール" in directory_names

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "フィギュア" in genre_names

    def test_collectible_figure_attributes(self, product_data):
        """Test collectible figure specific attributes."""

        product = Product.from_dict(product_data)

        assert product.jancode is not None
        assert product.jancode.startswith("45")

        assert product.current_price is None
        assert product.original_price == 29700

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].name == "ロケットボーイ"

        assert product.stock == "reserve"

    def test_character_figure_features(self, product_data):
        """Test character figure specific features."""

        product = Product.from_dict(product_data)

        directories = product.directory
        character_figure_dir = None
        for directory in directories:
            if "キャラクターフィギュア" in directory.name:
                character_figure_dir = directory
                break

        assert character_figure_dir is not None
        assert character_figure_dir.id == 1157
        assert "スケール" in character_figure_dir.name

        assert product.title == "氷見山珖"
