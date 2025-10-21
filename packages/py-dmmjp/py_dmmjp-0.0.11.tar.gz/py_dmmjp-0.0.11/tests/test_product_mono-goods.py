"""
Tests for Mono Goods products (service=mono, floor=goods).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoGoodsProduct(ProductTestBase):
    """Test cases for Mono Goods products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Mono Goods product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "goods",
            "floor_name": "大人のおもちゃ",
            "category_name": "大人のおもちゃ通販",
            "content_id": "lotion0727",
            "product_id": "lo0744",
            "title": "おなつゆ トイズハート",
            "review": {"count": 189, "average": "4.54"},
            "URL": "https://www.dmm.co.jp/mono/goods/-/detail/=/cid=lotion0727/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fgoods%2F-%2Fdetail%2F%3D%2Fcid%3Dlotion0727%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/mono/goods/lo0744/lo0744pt.jpg",
                "small": "https://pics.dmm.co.jp/mono/goods/lo0744/lo0744ps.jpg",
                "large": "https://pics.dmm.co.jp/mono/goods/lo0744/lo0744pl.jpg",
            },
            "prices": {"price": "605", "list_price": "1210"},
            "date": "2011-07-15 10:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 10095, "name": "1000円以下"},
                    {"id": 10226, "name": "セール開催中"},
                ],
                "maker": [{"id": 10007, "name": "トイズハート"}],
            },
            "jancode": "4526374159008",
            "stock": "stock",
            "directory": [
                {"id": 852, "name": "ローション"},
                {"id": 17634, "name": "オナホ用"},
                {"id": 17657, "name": "200ml以上"},
            ],
        }

    def test_product_basic_fields(self, product_data):
        """Test mono goods product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "goods"
        assert product.floor_name == "大人のおもちゃ"
        assert product.category_name == "大人のおもちゃ通販"

        assert product.content_id == "lotion0727"
        assert product.product_id == "lo0744"
        assert product.title == "おなつゆ トイズハート"
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that mono goods products do not have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test mono goods product's physical product pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "605"
        assert product.prices.list_price == "1210"
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 605
        assert product.original_price == 1210

    def test_product_item_info_genres(self, product_data):
        """Test mono goods product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "1000円以下" in genre_names
        assert "セール開催中" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2011, 7, 15, 10, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test mono goods product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "mono/goods/lo0744" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test mono goods product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test mono goods product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 10007
        assert makers[0].name == "トイズハート"

    def test_product_item_info_manufactures(self, product_data):
        "Test mono goods product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting mono goods product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "lotion0727"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw mono goods API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "lotion0727"

    def test_sample_images_large(self, product_data):
        """Test large sample images for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode == "4526374159008"
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock == "stock"
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for mono goods products."""

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
        """Test convenience properties for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 189
        assert product.review_average == 4.54
        assert product.current_price == 605
        assert product.original_price == 1210
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for mono goods products."""

        product = Product.from_dict(product_data)

        directories = product.directory
        assert len(directories) == 3

        dir_names = [d.name for d in directories]
        assert "ローション" in dir_names
        assert "オナホ用" in dir_names
        assert "200ml以上" in dir_names

        dir_ids = [d.id for d in directories]
        assert 852 in dir_ids
        assert 17634 in dir_ids
        assert 17657 in dir_ids

    def test_pricing_structure(self, product_data):
        """Test pricing structure for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "605"
        assert product.prices.list_price == "1210"
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 605
        assert product.prices.list_price_int == 1210

    def test_delivery_options(self, product_data):
        """Test delivery options for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "goods"
        assert product.floor_name == "大人のおもちゃ"
        assert product.category_name == "大人のおもちゃ通販"
        assert product.content_id == "lotion0727"
        assert product.product_id == "lo0744"
        assert product.title is not None
        assert product.volume is None
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode == "4526374159008"
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock == "stock"
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for mono goods products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 189
        assert product.review.average == 4.54
        assert product.review_count == 189
        assert product.review_average == 4.54

    def test_goods_specific_fields(self, product_data):
        """Test physical goods specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/mono/goods/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmono%2Fgoods%2F" in product.affiliate_url

        assert product.jancode == "4526374159008"
        assert product.stock == "stock"

        directories = product.directory
        assert len(directories) == 3
        assert directories[0].id == 852
        assert directories[0].name == "ローション"

    def test_goods_content_characteristics(self, product_data):
        """Test physical goods content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "1000円以下" in genre_names
        assert "セール開催中" in genre_names

        assert product.volume is None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None

    def test_goods_pricing_model(self, product_data):
        """Test physical goods pricing and discount model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "605"
        assert product.prices.list_price == "1210"
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 605
        assert product.original_price == 1210

        discount_amount = product.original_price - product.current_price
        assert discount_amount == 605
        discount_percentage = (discount_amount / product.original_price) * 100
        assert abs(discount_percentage - 50.0) < 0.1

    def test_physical_product_attributes(self, product_data):
        """Test physical product specific attributes."""

        product = Product.from_dict(product_data)

        assert product.jancode is not None
        assert len(product.jancode) == 13
        assert product.jancode.isdigit()

        assert product.stock is not None
        assert product.stock == "stock"

        directories = product.directory
        assert len(directories) == 3
        for directory in directories:
            assert directory.id is not None
            assert directory.name is not None

    def test_goods_maker_info(self, product_data):
        """Test goods maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 10007
        assert maker.name == "トイズハート"

    def test_goods_category_structure(self, product_data):
        """Test goods category and directory structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "goods"
        assert product.floor_name == "大人のおもちゃ"

        directories = product.directory
        assert len(directories) == 3

        category_mapping = {852: "ローション", 17634: "オナホ用", 17657: "200ml以上"}

        for directory in directories:
            assert directory.id in category_mapping
            assert directory.name == category_mapping[directory.id]
