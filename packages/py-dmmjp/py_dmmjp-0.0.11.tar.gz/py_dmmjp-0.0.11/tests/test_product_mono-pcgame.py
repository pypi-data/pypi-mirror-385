"""
Tests for Mono PC Game products (service=mono, floor=pcgame).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestMonoPCGameProduct(ProductTestBase):
    """Test cases for Mono PC Game products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Mono PC Game product data from DMM API response."""

        return {
            "service_code": "mono",
            "service_name": "通販",
            "floor_code": "pcgame",
            "floor_name": "PCゲーム",
            "category_name": "アダルトPCゲーム通販",
            "content_id": "1915anm446",
            "product_id": "1915anm446",
            "title": "【完全受注生産】ANIM.teamMM 寝取ラレ寝取ラセ欲ばりセット～人気の若妻からオギャれるママまでネットリ堪能できちゃう厳選5本パック～",
            "review": {"count": 6, "average": "5.00"},
            "URL": "https://www.dmm.co.jp/mono/pcgame/-/detail/=/cid=1915anm446/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fpcgame%2F-%2Fdetail%2F%3D%2Fcid%3D1915anm446%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/mono/game/1915anm446/1915anm446pt.jpg",
                "small": "https://pics.dmm.co.jp/mono/game/1915anm446/1915anm446ps.jpg",
                "large": "https://pics.dmm.co.jp/mono/game/1915anm446/1915anm446pl.jpg",
            },
            "prices": {"price": "11220", "list_price": "13200"},
            "date": "2019-12-27 10:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 30092, "name": "寝取り・寝取られ"},
                    {"id": 30036, "name": "花嫁・若妻"},
                    {"id": 30154, "name": "セット商品"},
                    {"id": 30144, "name": "イチオシ作品"},
                ],
                "maker": [{"id": 31475, "name": "ANIM.teamMM"}],
                "author": [
                    {"id": 239162, "name": "リャオ", "ruby": "りゃお"},
                    {"id": 245591, "name": "うん=食太郎", "ruby": "うんたべたろう"},
                ],
            },
            "jancode": "4530758190198",
            "maker_product": "ANM-446",
            "stock": "empty",
            "directory": [{"id": 1401, "name": "その他"}],
        }

    def test_product_basic_fields(self, product_data):
        """Test mono pcgame product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "pcgame"
        assert product.floor_name == "PCゲーム"
        assert product.category_name == "アダルトPCゲーム通販"

        assert product.content_id == "1915anm446"
        assert product.product_id == "1915anm446"
        assert (
            product.title
            == "【完全受注生産】ANIM.teamMM 寝取ラレ寝取ラセ欲ばりセット～人気の若妻からオギャれるママまでネットリ堪能できちゃう厳選5本パック～"
        )
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that mono pcgame products do not have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test mono pcgame product's physical product pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "11220"
        assert product.prices.list_price == "13200"
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 11220
        assert product.original_price == 13200

    def test_product_item_info_genres(self, product_data):
        """Test mono pcgame product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "寝取り・寝取られ" in genre_names
        assert "花嫁・若妻" in genre_names
        assert "セット商品" in genre_names
        assert "イチオシ作品" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2019, 12, 27, 10, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test mono pcgame product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "mono/game/1915anm446" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test mono pcgame product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test mono pcgame product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 31475
        assert makers[0].name == "ANIM.teamMM"

    def test_product_item_info_manufactures(self, product_data):
        "Test mono pcgame product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting mono pcgame product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "mono"
        assert result_dict["content_id"] == "1915anm446"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw mono pcgame API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "mono"
        assert raw_data["content_id"] == "1915anm446"

    def test_sample_images_large(self, product_data):
        """Test large sample images for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.number is None
        assert product.jancode == "4530758190198"
        assert product.maker_product == "ANM-446"
        assert product.isbn is None
        assert product.stock == "empty"
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.authors) > 0
        assert len(product.directory) > 0

        assert len(product.labels) == 0
        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.series) == 0
        assert len(product.actors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 6
        assert product.review_average == 5.0
        assert product.current_price == 11220
        assert product.original_price == 13200
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for mono pcgame products."""

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
        """Test directory structure for mono pcgame products."""

        product = Product.from_dict(product_data)

        directories = product.directory
        assert len(directories) == 1

        dir_names = [d.name for d in directories]
        assert "その他" in dir_names

        dir_ids = [d.id for d in directories]
        assert 1401 in dir_ids

    def test_pricing_structure(self, product_data):
        """Test pricing structure for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "11220"
        assert product.prices.list_price == "13200"
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 11220
        assert product.prices.list_price_int == 13200

    def test_delivery_options(self, product_data):
        """Test delivery options for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "pcgame"
        assert product.floor_name == "PCゲーム"
        assert product.category_name == "アダルトPCゲーム通販"
        assert product.content_id == "1915anm446"
        assert product.product_id == "1915anm446"
        assert product.title is not None
        assert product.volume is None
        assert product.number is None
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode == "4530758190198"
        assert product.maker_product == "ANM-446"
        assert product.isbn is None
        assert product.stock == "empty"
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for mono pcgame products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 6
        assert product.review.average == 5.0
        assert product.review_count == 6
        assert product.review_average == 5.0

    def test_pcgame_specific_fields(self, product_data):
        """Test PC game specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "/mono/pcgame/" in product.url
        assert product.affiliate_url is not None
        assert "%2Fmono%2Fpcgame%2F" in product.affiliate_url

        assert product.jancode == "4530758190198"
        assert product.maker_product == "ANM-446"
        assert product.stock == "empty"

        directories = product.directory
        assert len(directories) == 1
        assert directories[0].id == 1401
        assert directories[0].name == "その他"

        authors = product.authors
        assert len(authors) == 2
        assert authors[0].id == 239162
        assert authors[0].name == "リャオ"
        assert authors[0].ruby == "りゃお"

    def test_pcgame_content_characteristics(self, product_data):
        """Test PC game content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "寝取り・寝取られ" in genre_names
        assert "花嫁・若妻" in genre_names
        assert "セット商品" in genre_names
        assert "イチオシ作品" in genre_names

        assert product.volume is None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None

        assert product.title.startswith("【完全受注生産】")
        assert "5本パック" in product.title

    def test_pcgame_pricing_model(self, product_data):
        """Test PC game pricing and discount model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "11220"
        assert product.prices.list_price == "13200"
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 11220
        assert product.original_price == 13200

        discount_amount = product.original_price - product.current_price
        assert discount_amount == 1980
        discount_percentage = (discount_amount / product.original_price) * 100
        assert abs(discount_percentage - 15.0) < 0.1

    def test_physical_pcgame_attributes(self, product_data):
        """Test physical PC game specific attributes."""

        product = Product.from_dict(product_data)

        assert product.jancode is not None
        assert len(product.jancode) == 13
        assert product.jancode.isdigit()

        assert product.maker_product is not None
        assert product.maker_product == "ANM-446"

        assert product.stock is not None
        assert product.stock == "empty"

        directories = product.directory
        assert len(directories) == 1
        for directory in directories:
            assert directory.id is not None
            assert directory.name is not None

    def test_pcgame_maker_info(self, product_data):
        """Test PC game maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 31475
        assert maker.name == "ANIM.teamMM"

    def test_pcgame_author_info(self, product_data):
        """Test PC game author information."""

        product = Product.from_dict(product_data)

        authors = product.authors
        assert len(authors) == 2

        author1 = authors[0]
        assert author1.id == 239162
        assert author1.name == "リャオ"
        assert author1.ruby == "りゃお"

        author2 = authors[1]
        assert author2.id == 245591
        assert author2.name == "うん=食太郎"
        assert author2.ruby == "うんたべたろう"

    def test_pcgame_category_structure(self, product_data):
        """Test PC game category and directory structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "pcgame"
        assert product.floor_name == "PCゲーム"

        directories = product.directory
        assert len(directories) == 1

        directory = directories[0]
        assert directory.id == 1401
        assert directory.name == "その他"

    def test_pcgame_set_product_features(self, product_data):
        """Test PC game set product characteristics."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "セット商品" in genre_names
        assert "イチオシ作品" in genre_names

        assert "5本パック" in product.title
        assert "【完全受注生産】" in product.title

        assert product.stock == "empty"

    def test_pcgame_adult_content_features(self, product_data):
        """Test adult PC game content classification."""

        product = Product.from_dict(product_data)

        assert product.category_name == "アダルトPCゲーム通販"
        assert product.floor_name == "PCゲーム"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "寝取り・寝取られ" in genre_names
        assert "花嫁・若妻" in genre_names

        authors = product.authors
        assert len(authors) == 2
