"""
Tests for Ebook Novel products (service=ebook, floor=novel).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestEbookNovelProduct(ProductTestBase):
    """Test cases for Ebook Novel products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Ebook Novel product data from DMM API response."""

        return {
            "service_code": "ebook",
            "service_name": "FANZAブックス",
            "floor_code": "novel",
            "floor_name": "美少女ノベル・官能小説",
            "category_name": "美少女ノベル・官能小説 (電子書籍)",
            "content_id": "s741asnxe00009",
            "product_id": "s741asnxe00009",
            "title": "ゴエティア・ショック",
            "review": {"count": 7, "average": "2.86"},
            "URL": "https://book.dmm.co.jp/product/6220320/s741asnxe00009/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fbook.dmm.co.jp%2Fproduct%2F6220320%2Fs741asnxe00009%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://ebook-assets.dmm.co.jp/digital/e-book/s741asnxe00009/s741asnxe00009pt.jpg",
                "small": "https://ebook-assets.dmm.co.jp/digital/e-book/s741asnxe00009/s741asnxe00009ps.jpg",
                "large": "https://ebook-assets.dmm.co.jp/digital/e-book/s741asnxe00009/s741asnxe00009pl.jpg",
            },
            "prices": {"price": "2420"},
            "date": "2025-10-10 00:00:02",
            "iteminfo": {
                "genre": [
                    {"id": 27, "name": "辱め"},
                    {"id": 55, "name": "処女"},
                    {"id": 102, "name": "美乳"},
                    {"id": 1027, "name": "美少女"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 4075, "name": "SF"},
                    {"id": 4098, "name": "セクシー"},
                    {"id": 6661, "name": "先行販売"},
                    {"id": 7409, "name": "独占販売"},
                ],
                "series": [{"id": 6220320, "name": "ゴエティア・ショック"}],
                "manufacture": [{"id": 311187, "name": "MM社"}],
                "author": [
                    {"id": 392929, "name": "読図健人"},
                    {"id": 250826, "name": "大熊猫介"},
                ],
            },
            "number": "2",
        }

    def test_product_basic_fields(self, product_data):
        """Test ebook novel product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "novel"
        assert product.floor_name == "美少女ノベル・官能小説"
        assert product.category_name == "美少女ノベル・官能小説 (電子書籍)"

        assert product.content_id == "s741asnxe00009"
        assert product.product_id == "s741asnxe00009"
        assert product.title == "ゴエティア・ショック"
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that ebook novel products have no sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test ebook novel product's pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "2420"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 2420
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test ebook novel product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "辱め" in genre_names
        assert "処女" in genre_names
        assert "美乳" in genre_names
        assert "美少女" in genre_names
        assert "巨乳" in genre_names
        assert "SF" in genre_names
        assert "セクシー" in genre_names
        assert "先行販売" in genre_names
        assert "独占販売" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 10, 10, 0, 0, 2)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test ebook novel product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "ebook-assets.dmm.co.jp/digital/e-book/s741asnxe00009"
            in product.image_url.list
        )
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test ebook novel product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test ebook novel product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 0

    def test_product_item_info_manufactures(self, product_data):
        """Test ebook novel product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 1
        if len(manufactures) > 0:
            manufacture = manufactures[0]
            assert manufacture.id == 311187
            assert manufacture.name == "MM社"

    def test_product_to_dict(self, product_data):
        """Test converting ebook novel product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "ebook"
        assert result_dict["content_id"] == "s741asnxe00009"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw ebook novel API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "ebook"
        assert raw_data["content_id"] == "s741asnxe00009"

    def test_sample_images_large(self, product_data):
        """Test large sample images for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.number == 2
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.tachiyomi is None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for ebook novel products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) == 0

        assert len(product.labels) == 0
        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.series) > 0
        assert len(product.actors) == 0
        assert len(product.authors) > 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0
        assert len(product.directory) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 7
        assert product.review_average == 2.86
        assert product.current_price == 2420
        assert product.original_price is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for ebook novel products."""

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
        """Test directory structure for ebook novel products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "2420"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 2420

    def test_delivery_options(self, product_data):
        """Test delivery options for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "novel"
        assert product.floor_name == "美少女ノベル・官能小説"
        assert product.category_name == "美少女ノベル・官能小説 (電子書籍)"
        assert product.content_id == "s741asnxe00009"
        assert product.product_id == "s741asnxe00009"
        assert product.title is not None
        assert product.volume is None
        assert product.number == 2
        assert product.date is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for ebook novel products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 7
        assert product.review.average == 2.86
        assert product.review_count == 7
        assert product.review_average == 2.86

    def test_novel_specific_fields(self, product_data):
        """Test novel specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "book.dmm.co.jp/product/" in product.url
        assert product.affiliate_url is not None
        assert "book.dmm.co.jp%2Fproduct%2F" in product.affiliate_url

        assert "ebook-assets.dmm.co.jp" in product.image_url.list

    def test_novel_content_characteristics(self, product_data):
        """Test novel content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "美少女" in genre_names
        assert "SF" in genre_names
        assert "セクシー" in genre_names
        assert "辱め" in genre_names
        assert "処女" in genre_names

        assert product.number == 2

    def test_novel_pricing_model(self, product_data):
        """Test novel pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "2420"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 2420
        assert product.original_price is None

    def test_novel_series_info(self, product_data):
        """Test novel series information."""

        product = Product.from_dict(product_data)

        series = product.series
        assert len(series) == 1
        assert series[0].id == 6220320
        assert series[0].name == "ゴエティア・ショック"

    def test_novel_author_info(self, product_data):
        """Test novel author information."""

        product = Product.from_dict(product_data)

        authors = product.authors
        assert len(authors) == 2
        author_names = [a.name for a in authors]
        assert "読図健人" in author_names
        assert "大熊猫介" in author_names

    def test_novel_category_structure(self, product_data):
        """Test novel category structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "novel"
        assert product.floor_name == "美少女ノベル・官能小説"
        assert product.category_name == "美少女ノベル・官能小説 (電子書籍)"

        assert len(product.directory) == 0

    def test_ebook_novel_features(self, product_data):
        """Test ebook novel specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.stock is None
        assert product.jancode is None

        assert "ebook-assets.dmm.co.jp" in product.image_url.list
        assert "book.dmm.co.jp/product/" in product.url

        assert product.tachiyomi is None

    def test_novel_genre_classification(self, product_data):
        """Test novel genre classification."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        content_themes = ["SF", "美少女", "セクシー"]
        for tag in content_themes:
            assert tag in genre_names

        adult_content = ["辱め", "処女", "美乳", "巨乳"]
        for tag in adult_content:
            assert tag in genre_names

        distribution_tags = ["先行販売", "独占販売"]
        for tag in distribution_tags:
            assert tag in genre_names

    def test_novel_content_tags(self, product_data):
        """Test novel content tagging system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        story_elements = ["SF", "美少女"]
        for tag in story_elements:
            assert tag in genre_names

        mature_themes = ["辱め", "処女", "セクシー"]
        for tag in mature_themes:
            assert tag in genre_names

    def test_novel_image_structure(self, product_data):
        """Test novel image structure."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.small is not None
        assert product.image_url.large is not None
        assert product.image_url.list is not None

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0
        assert len(product.sample_images) == 0

    def test_novel_volume_info(self, product_data):
        """Test novel volume information."""

        product = Product.from_dict(product_data)

        assert product.volume is None
        assert product.number == 2

    def test_novel_publication_info(self, product_data):
        """Test novel publication information."""

        product = Product.from_dict(product_data)

        assert product.content_id.startswith("s")
        assert product.product_id.startswith("s")
        assert product.number == 2

        series = product.series
        assert len(series) == 1
        assert series[0].name == "ゴエティア・ショック"

        authors = product.authors
        assert len(authors) == 2

    def test_fanza_books_novel_platform(self, product_data):
        """Test FANZA Books novel platform specific features."""

        product = Product.from_dict(product_data)

        assert product.service_name == "FANZAブックス"
        assert "book.dmm.co.jp" in product.url
        assert "ebook-assets.dmm.co.jp" in product.image_url.list

        assert product.floor_name == "美少女ノベル・官能小説"
        assert product.category_name == "美少女ノベル・官能小説 (電子書籍)"

    def test_novel_manufacture_info(self, product_data):
        """Test novel manufacture information."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 1
        if len(manufactures) > 0:
            manufacture = manufactures[0]
            assert manufacture.id == 311187
            assert manufacture.name == "MM社"

    def test_exclusive_distribution_novel(self, product_data):
        """Test exclusive distribution characteristics for novels."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "先行販売" in genre_names
        assert "独占販売" in genre_names

        assert product.service_name == "FANZAブックス"
        assert "book.dmm.co.jp" in product.url

    def test_digital_novel_classification(self, product_data):
        """Test digital novel classification system."""

        product = Product.from_dict(product_data)

        assert product.category_name == "美少女ノベル・官能小説 (電子書籍)"
        assert product.floor_name == "美少女ノベル・官能小説"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "美少女" in genre_names
        assert "SF" in genre_names

        assert product.volume is None
        assert product.number == 2

    def test_novel_sf_genre_features(self, product_data):
        """Test SF novel specific features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "SF" in genre_names
        assert "美少女" in genre_names
        assert "セクシー" in genre_names

        assert product.title == "ゴエティア・ショック"
        assert len(product.authors) == 2

    def test_novel_multi_author_structure(self, product_data):
        """Test novel multi-author structure."""

        product = Product.from_dict(product_data)

        authors = product.authors
        assert len(authors) == 2

        author_ids = [a.id for a in authors]
        assert 392929 in author_ids
        assert 250826 in author_ids

        author_names = [a.name for a in authors]
        assert "読図健人" in author_names
        assert "大熊猫介" in author_names
