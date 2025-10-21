"""
Tests for Ebook Comic products (service=ebook, floor=comic).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestEbookComicProduct(ProductTestBase):
    """Test cases for Ebook Comic products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """Ebook Comic product data from DMM API response."""

        return {
            "service_code": "ebook",
            "service_name": "FANZAブックス",
            "floor_code": "comic",
            "floor_name": "コミック",
            "category_name": "コミック (電子書籍)",
            "content_id": "b073bktcm07063",
            "product_id": "b073bktcm07063",
            "title": "同居する粘液",
            "volume": "293",
            "review": {"count": 44, "average": "4.80"},
            "URL": "https://book.dmm.co.jp/product/4003903/b073bktcm07063/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fbook.dmm.co.jp%2Fproduct%2F4003903%2Fb073bktcm07063%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://ebook-assets.dmm.co.jp/digital/e-book/b073bktcm07063/b073bktcm07063pt.jpg",
                "small": "https://ebook-assets.dmm.co.jp/digital/e-book/b073bktcm07063/b073bktcm07063ps.jpg",
                "large": "https://ebook-assets.dmm.co.jp/digital/e-book/b073bktcm07063/b073bktcm07063pl.jpg",
            },
            "tachiyomi": {
                "URL": "https://book.dmm.co.jp/tachiyomi/?cid=FRNfXRNVFW1RAQxaAwFVVQoRVVsADlQPUU5EDl0VClQMBllNB1o*UFcKWhRHVwVfCBxZW1kEVQ__&lin=1&sd=0",
                "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fbook.dmm.co.jp%2Ftachiyomi%2F%3Fcid%3DFRNfXRNVFW1RAQxaAwFVVQoRVVsADlQPUU5EDl0VClQMBllNB1o%2AUFcKWhRHVwVfCBxZW1kEVQ__%26lin%3D1%26sd%3D0&af_id=***REDACTED_AFF_ID***&ch=api",
            },
            "prices": {"price": "1760"},
            "date": "2025/10/09 00:00:05",
            "iteminfo": {
                "genre": [
                    {"id": 54, "name": "単行本"},
                    {"id": 568, "name": "ダーク系"},
                    {"id": 5071, "name": "ハーレム"},
                    {"id": 17, "name": "ファンタジー"},
                    {"id": 18, "name": "ホラー"},
                    {"id": 4013, "name": "レズビアン"},
                    {"id": 48, "name": "制服"},
                    {"id": 27, "name": "辱め"},
                    {"id": 59, "name": "ふたなり"},
                    {"id": 553, "name": "学園もの"},
                    {"id": 583, "name": "ラブ&H"},
                    {"id": 1033, "name": "お姉さん"},
                    {"id": 1085, "name": "変身ヒロイン"},
                    {"id": 2001, "name": "巨乳"},
                    {"id": 3008, "name": "水着"},
                    {"id": 3033, "name": "バニーガール"},
                    {"id": 3034, "name": "ゴスロリ"},
                    {"id": 4030, "name": "淫乱・ハード系"},
                    {"id": 4116, "name": "着エロ"},
                    {"id": 4141, "name": "女体化"},
                    {"id": 5019, "name": "パイズリ"},
                    {"id": 5022, "name": "3P・4P"},
                    {"id": 6661, "name": "先行販売"},
                    {"id": 7409, "name": "独占販売"},
                ],
                "series": [{"id": 4003903, "name": "同居する粘液"}],
                "manufacture": [{"id": 40291, "name": "キルタイムコミュニケーション"}],
                "author": [{"id": 243370, "name": "DATE"}],
            },
            "number": "2",
        }

    def test_product_basic_fields(self, product_data):
        """Test ebook comic product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "comic"
        assert product.floor_name == "コミック"
        assert product.category_name == "コミック (電子書籍)"

        assert product.content_id == "b073bktcm07063"
        assert product.product_id == "b073bktcm07063"
        assert product.title == "同居する粘液"
        assert product.volume == 293

    def test_product_sample_images(self, product_data):
        """Test that ebook comic products have no sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test ebook comic product's pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "1760"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 1760
        assert product.original_price is None

    def test_product_item_info_genres(self, product_data):
        """Test ebook comic product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "単行本" in genre_names
        assert "ダーク系" in genre_names
        assert "ハーレム" in genre_names
        assert "ファンタジー" in genre_names
        assert "ホラー" in genre_names
        assert "レズビアン" in genre_names
        assert "制服" in genre_names
        assert "辱め" in genre_names
        assert "ふたなり" in genre_names
        assert "学園もの" in genre_names
        assert "ラブ&H" in genre_names
        assert "お姉さん" in genre_names
        assert "変身ヒロイン" in genre_names
        assert "巨乳" in genre_names
        assert "水着" in genre_names
        assert "バニーガール" in genre_names
        assert "ゴスロリ" in genre_names
        assert "淫乱・ハード系" in genre_names
        assert "着エロ" in genre_names
        assert "女体化" in genre_names
        assert "パイズリ" in genre_names
        assert "3P・4P" in genre_names
        assert "先行販売" in genre_names
        assert "独占販売" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing with seconds."""

        product = Product.from_dict(product_data)

        assert product.date is None

    def test_product_image_urls(self, product_data):
        """Test ebook comic product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert (
            "ebook-assets.dmm.co.jp/digital/e-book/b073bktcm07063"
            in product.image_url.list
        )
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test ebook comic product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test ebook comic product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 0

    def test_product_item_info_manufactures(self, product_data):
        """Test ebook comic product manufactures."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 1
        if len(manufactures) > 0:
            manufacture = manufactures[0]
            assert manufacture.id == 40291
            assert manufacture.name == "キルタイムコミュニケーション"

    def test_product_to_dict(self, product_data):
        """Test converting ebook comic product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "ebook"
        assert result_dict["content_id"] == "b073bktcm07063"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw ebook comic API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "ebook"
        assert raw_data["content_id"] == "b073bktcm07063"

    def test_sample_images_large(self, product_data):
        """Test large sample images for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.number == 2
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.tachiyomi is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_item_info_categories(self, product_data):
        """Test item info categories for ebook comic products."""

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
        """Test convenience properties for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 44
        assert product.review_average == 4.8
        assert product.current_price == 1760
        assert product.original_price is None
        assert len(product.sample_images) == 0
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is None
        assert product.sample_movie_url is None
        assert product.tachiyomi is not None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for ebook comic products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "1760"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.prices.price_int == 1760

    def test_delivery_options(self, product_data):
        """Test delivery options for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 0

    def test_product_fields(self, product_data):
        """Test product fields for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "comic"
        assert product.floor_name == "コミック"
        assert product.category_name == "コミック (電子書籍)"
        assert product.content_id == "b073bktcm07063"
        assert product.product_id == "b073bktcm07063"
        assert product.title is not None
        assert product.volume == 293
        assert product.number == 2
        assert product.date is None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.jancode is None
        assert product.maker_product is None
        assert product.isbn is None
        assert product.stock is None
        assert product.raw_data is not None

    def test_product_review_data(self, product_data):
        """Test review data for ebook comic products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 44
        assert product.review.average == 4.8
        assert product.review_count == 44
        assert product.review_average == 4.8

    def test_ebook_specific_fields(self, product_data):
        """Test ebook specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "book.dmm.co.jp/product/" in product.url
        assert product.affiliate_url is not None
        assert "book.dmm.co.jp%2Fproduct%2F" in product.affiliate_url

        assert "ebook-assets.dmm.co.jp" in product.image_url.list

        assert product.tachiyomi is not None
        assert "book.dmm.co.jp/tachiyomi/" in product.tachiyomi.url

    def test_comic_content_characteristics(self, product_data):
        """Test comic content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "単行本" in genre_names
        assert "ダーク系" in genre_names
        assert "ファンタジー" in genre_names
        assert "ホラー" in genre_names
        assert "制服" in genre_names
        assert "学園もの" in genre_names
        assert "変身ヒロイン" in genre_names

        assert product.volume == 293
        assert product.number == 2

    def test_comic_pricing_model(self, product_data):
        """Test comic pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "1760"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 0
        assert product.current_price == 1760
        assert product.original_price is None

    def test_comic_series_info(self, product_data):
        """Test comic series information."""

        product = Product.from_dict(product_data)

        series = product.series
        assert len(series) == 1
        assert series[0].id == 4003903
        assert series[0].name == "同居する粘液"

    def test_comic_author_info(self, product_data):
        """Test comic author information."""

        product = Product.from_dict(product_data)

        authors = product.authors
        assert len(authors) == 1
        author = authors[0]
        assert author.id == 243370
        assert author.name == "DATE"

    def test_comic_category_structure(self, product_data):
        """Test comic category structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "ebook"
        assert product.service_name == "FANZAブックス"
        assert product.floor_code == "comic"
        assert product.floor_name == "コミック"
        assert product.category_name == "コミック (電子書籍)"

        assert len(product.directory) == 0

    def test_ebook_comic_features(self, product_data):
        """Test ebook comic specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.stock is None
        assert product.jancode is None

        assert "ebook-assets.dmm.co.jp" in product.image_url.list
        assert "book.dmm.co.jp/product/" in product.url

        assert product.tachiyomi is not None
        assert "book.dmm.co.jp/tachiyomi/" in product.tachiyomi.url

    def test_comic_genre_classification(self, product_data):
        """Test comic genre classification."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        publication_types = ["単行本"]
        for tag in publication_types:
            assert tag in genre_names

        content_themes = ["ダーク系", "ファンタジー", "ホラー"]
        for tag in content_themes:
            assert tag in genre_names

        distribution_tags = ["先行販売", "独占販売"]
        for tag in distribution_tags:
            assert tag in genre_names

    def test_comic_content_tags(self, product_data):
        """Test comic content tagging system."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        fantasy_elements = ["ファンタジー", "変身ヒロイン", "女体化"]
        for tag in fantasy_elements:
            assert tag in genre_names

        adult_content = ["ハーレム", "レズビアン", "辱め", "ふたなり"]
        for tag in adult_content:
            assert tag in genre_names

    def test_comic_image_structure(self, product_data):
        """Test comic image structure."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.small is not None
        assert product.image_url.large is not None
        assert product.image_url.list is not None

        assert product.sample_image_url is None
        assert len(product.sample_images_large) == 0
        assert len(product.sample_images) == 0

    def test_comic_volume_info(self, product_data):
        """Test comic volume information."""

        product = Product.from_dict(product_data)

        assert product.volume == 293
        assert isinstance(product.volume, int)
        assert product.number == 2

    def test_comic_publication_info(self, product_data):
        """Test comic publication information."""

        product = Product.from_dict(product_data)

        assert product.content_id.startswith("b")
        assert product.product_id.startswith("b")
        assert product.number == 2

        series = product.series
        assert len(series) == 1
        assert series[0].name == "同居する粘液"

        authors = product.authors
        assert len(authors) == 1
        assert authors[0].name == "DATE"

    def test_tachiyomi_features(self, product_data):
        """Test tachiyomi reading features."""

        product = Product.from_dict(product_data)

        assert product.tachiyomi is not None
        assert "book.dmm.co.jp/tachiyomi/" in product.tachiyomi.url
        assert "cid=" in product.tachiyomi.url
        assert product.tachiyomi.affiliate_url is not None

    def test_fanza_books_platform_features(self, product_data):
        """Test FANZA Books platform specific features."""

        product = Product.from_dict(product_data)

        assert product.service_name == "FANZAブックス"
        assert "book.dmm.co.jp" in product.url
        assert "ebook-assets.dmm.co.jp" in product.image_url.list

        assert product.tachiyomi is not None
        assert "book.dmm.co.jp/tachiyomi/" in product.tachiyomi.url

    def test_comic_manufacture_info(self, product_data):
        """Test comic manufacture information."""

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture")
        if product.item_info.manufacture:
            manufacture = product.item_info.manufacture[0]
            assert manufacture.id == 40291
            assert manufacture.name == "キルタイムコミュニケーション"

    def test_exclusive_distribution_features(self, product_data):
        """Test exclusive distribution characteristics."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "先行販売" in genre_names
        assert "独占販売" in genre_names

        assert product.service_name == "FANZAブックス"
        assert "book.dmm.co.jp" in product.url

    def test_digital_comic_classification(self, product_data):
        """Test digital comic classification system."""

        product = Product.from_dict(product_data)

        assert product.category_name == "コミック (電子書籍)"
        assert product.floor_name == "コミック"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "単行本" in genre_names

        assert product.tachiyomi is not None
        assert product.volume == 293
