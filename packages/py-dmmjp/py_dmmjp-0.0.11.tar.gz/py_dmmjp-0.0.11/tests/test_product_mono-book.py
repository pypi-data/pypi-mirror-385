"""
Tests for Mono Book products (service=mono, floor=book).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoBookProduct(ProductTestBase):
    """Test cases for Mono Book products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Mono Book product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "book",
            "floor_name": "ブック",
            "category_name": "ブック通販",
            "content_id": "275book97848671770752024",
            "product_id": "275book97848671770752024",
            "title": "佐野ゆま写真集 うわき。",
            "review": {"count": 8, "average": "5.00"},
            "URL": "https://www.dmm.co.jp/mono/book/-/detail/=/cid=275book97848671770752024/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fbook%2F-%2Fdetail%2F%3D%2Fcid%3D275book97848671770752024%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/mono/comic/275book97848671770752024/275book97848671770752024pt.jpg",
                "small": "https://pics.dmm.co.jp/mono/comic/275book97848671770752024/275book97848671770752024ps.jpg",
                "large": "https://pics.dmm.co.jp/mono/comic/275book97848671770752024/275book97848671770752024pl.jpg",
            },
            "prices": {"price": "4180"},
            "date": "2024-06-25 10:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 4098, "name": "セクシー"},
                    {"id": 3014, "name": "ランジェリー"},
                    {"id": 3008, "name": "水着"},
                    {"id": 2006, "name": "スレンダー"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 501, "name": "AV女優"},
                ],
                "maker": [{"id": 40272, "name": "ジーウォーク"}],
                "actress": [{"id": 1083818, "name": "佐野ゆま", "ruby": "さのゆま"}],
            },
            "isbn": "9784867177075",
            "stock": "stock",
            "directory": [{"id": 1404, "name": "写真集"}],
        }

    def test_product_basic_fields(self, product_data):
        """Test mono book product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "book"
        assert product.floor_name == "ブック"
        assert product.category_name == "ブック通販"

        assert product.content_id == "275book97848671770752024"
        assert product.product_id == "275book97848671770752024"
        assert product.title == "佐野ゆま写真集 うわき。"
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that mono book products do not have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test mono book product's physical product pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4180"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 4180
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test mono book product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "セクシー" in genre_names
        assert "ランジェリー" in genre_names
        assert "水着" in genre_names
        assert "スレンダー" in genre_names
        assert "巨乳" in genre_names
        assert "AV女優" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2024, 6, 25, 10, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test mono book product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "mono/comic/275book97848671770752024" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test mono book product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 1
        assert actresses[0].id == 1083818
        assert actresses[0].name == "佐野ゆま"
        assert actresses[0].ruby == "さのゆま"

    def test_product_item_info_makers(self, product_data):
        """Test mono book product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 40272
        assert makers[0].name == "ジーウォーク"

    def test_product_item_info_manufactures(self, product_data):
        """Test mono book product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting mono book product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "275book97848671770752024"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw mono book API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "275book97848671770752024"

    def test_sample_images_large(self, product_data):
        """Test large sample images for mono book products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for mono book products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for mono book products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn == "9784867177075"
        assert product.stock == "stock"
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for mono book products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.actresses) > 0
        assert len(product.directory) > 0

        assert len(product.labels) == 0
        assert len(product.directors) == 0
        assert len(product.series) == 0
        assert len(product.actors) == 0
        assert len(product.authors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for mono book products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 8
        assert product.review_average == 5.0
        assert product.current_price == 4180
        assert product.original_price is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for mono book products."""

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
        """Test directory structure for mono book products."""

        product = Product.from_dict(product_data)

        directories = product.directory
        assert len(directories) == 1

        dir_names = [d.name for d in directories]
        assert "写真集" in dir_names

        dir_ids = [d.id for d in directories]
        assert 1404 in dir_ids

    def test_pricing_structure(self, product_data):
        """Test pricing structure for mono book products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4180"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 4180
        assert product.prices.list_price_int is None

    def test_delivery_options(self, product_data):
        """Test delivery options for mono book products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for mono book products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "book"
        assert product.floor_name == "ブック"
        assert product.category_name == "ブック通販"
        assert product.content_id == "275book97848671770752024"
        assert product.product_id == "275book97848671770752024"
        assert product.title is not None
        assert product.volume is None
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn == "9784867177075"
        assert product.stock == "stock"
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for mono book products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 8
        assert product.review.average == 5.0
        assert product.review_count == 8
        assert product.review_average == 5.0

    def test_book_specific_fields(self, product_data):
        """Test book specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/mono/book/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmono%2Fbook%2F" in product.affiliate_url

        assert product.isbn == "9784867177075"
        assert product.stock == "stock"

        directories = product.directory
        assert len(directories) == 1
        assert directories[0].id == 1404
        assert directories[0].name == "写真集"

        actresses = product.actresses
        assert len(actresses) == 1
        assert actresses[0].id == 1083818
        assert actresses[0].name == "佐野ゆま"
        assert actresses[0].ruby == "さのゆま"

    def test_book_content_characteristics(self, product_data):
        """Test book content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "セクシー" in genre_names
        assert "ランジェリー" in genre_names
        assert "水着" in genre_names
        assert "スレンダー" in genre_names
        assert "巨乳" in genre_names
        assert "AV女優" in genre_names

        assert product.volume is None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None

        assert "写真集" in product.title

    def test_book_pricing_model(self, product_data):
        """Test book pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "4180"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 4180
        assert product.original_price is None

    def test_physical_book_attributes(self, product_data):
        """Test physical book specific attributes."""

        product = Product.from_dict(product_data)

        assert product.isbn is not None
        assert len(product.isbn) == 13
        assert product.isbn.isdigit()

        assert product.stock is not None
        assert product.stock == "stock"

        directories = product.directory
        assert len(directories) == 1
        directory = directories[0]
        assert directory.id == 1404
        assert directory.name == "写真集"

    def test_book_maker_info(self, product_data):
        """Test book maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 40272
        assert maker.name == "ジーウォーク"

    def test_book_actress_info(self, product_data):
        """Test book actress information."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 1

        actress = actresses[0]
        assert actress.id == 1083818
        assert actress.name == "佐野ゆま"
        assert actress.ruby == "さのゆま"

    def test_book_category_structure(self, product_data):
        """Test book category and directory structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "book"
        assert product.floor_name == "ブック"

        directories = product.directory
        assert len(directories) == 1

        directory = directories[0]
        assert directory.id == 1404
        assert directory.name == "写真集"

    def test_photobook_features(self, product_data):
        """Test photo book specific characteristics."""

        product = Product.from_dict(product_data)

        directories = product.directory
        directory_names = [d.name for d in directories]
        assert "写真集" in directory_names

        assert "写真集" in product.title
        assert product.title.endswith("うわき。")

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "セクシー" in genre_names
        assert "ランジェリー" in genre_names
        assert "水着" in genre_names

    def test_av_actress_photobook_features(self, product_data):
        """Test AV actress photo book classification."""

        product = Product.from_dict(product_data)

        assert product.category_name == "ブック通販"
        assert product.floor_name == "ブック"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "AV女優" in genre_names

        actresses = product.actresses
        assert len(actresses) == 1
        actress = actresses[0]
        assert actress.name == "佐野ゆま"

        assert "佐野ゆま" in product.title

    def test_isbn_validation(self, product_data):
        """Test ISBN format and validation."""

        product = Product.from_dict(product_data)

        isbn = product.isbn
        assert isbn is not None
        assert isbn == "9784867177075"
        assert len(isbn) == 13
        assert isbn.startswith("978")
        assert isbn.isdigit()
