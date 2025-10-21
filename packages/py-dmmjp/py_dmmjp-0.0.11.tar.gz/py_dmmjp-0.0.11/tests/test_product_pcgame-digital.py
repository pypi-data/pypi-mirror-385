"""
Tests for PC Game Digital products (service=pcgame, floor=digital_pcgame).
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from datetime import datetime
from typing import Any, Dict

import pytest

from py_dmmjp.product import Product

from .product_test_base import ProductTestBase


class TestPCGameDigitalProduct(ProductTestBase):
    """Test cases for PC Game Digital products."""

    @pytest.fixture
    def product_data(self) -> Dict[str, Any]:
        """PC Game Digital product data from DMM API response."""

        return {
            "service_code": "pcgame",
            "service_name": "アダルトPCゲーム",
            "floor_code": "digital_pcgame",
            "floor_name": "アダルトPCゲーム",
            "category_name": "アダルトPCゲーム",
            "content_id": "yuzu_0012",
            "product_id": "yuzu_0012",
            "title": "ライムライト・レモネードジャム",
            "review": {"count": 91, "average": "4.84"},
            "URL": "https://dlsoft.dmm.co.jp/detail/yuzu_0012/",
            "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fdlsoft.dmm.co.jp%2Fdetail%2Fyuzu_0012%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            "imageURL": {
                "list": "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012pt.jpg",
                "small": "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012ps.jpg",
                "large": "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012pl.jpg",
            },
            "sampleImageURL": {
                "sample_s": {
                    "image": [
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-001.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-002.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-003.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-004.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-005.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-006.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-007.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-008.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-009.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-010.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-011.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-012.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-013.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-014.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-015.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-016.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-017.jpg",
                        "https://pics.dmm.co.jp/digital/pcgame/yuzu_0012/yuzu_0012js-018.jpg",
                    ]
                }
            },
            "prices": {
                "price": "8470",
                "deliveries": {
                    "delivery": [
                        {"type": "download", "price": "8470", "list_price": ""}
                    ]
                },
            },
            "date": "2025-09-26 00:00:00",
            "iteminfo": {
                "genre": [
                    {"id": 7018, "name": "女子校生"},
                    {"id": 7301, "name": "制服"},
                    {"id": 7405, "name": "デモ・体験版あり"},
                    {"id": 7486, "name": "DL版独占販売"},
                    {"id": 7721, "name": "ブラウザ対応"},
                    {"id": 301085, "name": "CGがいい"},
                    {"id": 301088, "name": "キャラクターがいい"},
                    {"id": 301098, "name": "音楽がいい"},
                    {"id": 307544, "name": "Windows11対応作品"},
                    {"id": 308891, "name": "2025/9/26 配信開始作品"},
                    {
                        "id": 7470,
                        "name": "ハロウィン先取りエロゲフェス☆ 最大16%ポイント還元キャンペーン　第1弾",
                    },
                    {
                        "id": 300064,
                        "name": "【プレミアム新規登録された方へ】FANZA GAMES（アダルトPCゲーム）で使える最大90％OFFクーポン対象",
                    },
                ],
                "series": [{"id": 4594520, "name": "ライムライト・レモネードジャム"}],
                "maker": [{"id": 30727, "name": "ゆずソフト"}],
                "author": [
                    {"id": 239231, "name": "むりりん", "ruby": "むりりん"},
                    {"id": 239232, "name": "こぶいち", "ruby": "こぶいち"},
                    {"id": 365208, "name": "ほかん", "ruby": "ほかん"},
                    {"id": 248182, "name": "羽純りお", "ruby": "はづみりお"},
                ],
            },
        }

    def test_product_basic_fields(self, product_data):
        """Test pcgame digital product basic fields."""

        product = Product.from_dict(product_data)

        assert product.service_code == "pcgame"
        assert product.service_name == "アダルトPCゲーム"
        assert product.floor_code == "digital_pcgame"
        assert product.floor_name == "アダルトPCゲーム"
        assert product.category_name == "アダルトPCゲーム"

        assert product.content_id == "yuzu_0012"
        assert product.product_id == "yuzu_0012"
        assert product.title == "ライムライト・レモネードジャム"
        assert product.volume is None

    def test_product_sample_images(self, product_data):
        """Test that pcgame digital products have sample images."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None

        small_images = product.sample_image_url.sample_s.image
        assert len(small_images) == 18
        assert "yuzu_0012js-001.jpg" in small_images[0]
        assert "yuzu_0012js-018.jpg" in small_images[17]

        assert len(product.sample_images) == 18
        assert len(product.sample_images_large) == 0

    def test_product_pricing_data(self, product_data):
        """Test pcgame digital product's download pricing."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "8470"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 8470
        assert product.original_price is None

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "8470"
        assert delivery.list_price == ""

    def test_product_item_info_genres(self, product_data):
        """Test pcgame digital product genres."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "女子校生" in genre_names
        assert "制服" in genre_names
        assert "デモ・体験版あり" in genre_names
        assert "DL版独占販売" in genre_names
        assert "ブラウザ対応" in genre_names
        assert "CGがいい" in genre_names
        assert "キャラクターがいい" in genre_names
        assert "音楽がいい" in genre_names
        assert "Windows11対応作品" in genre_names

    def test_product_date_parsing(self, product_data):
        """Test date parsing without seconds."""

        product = Product.from_dict(product_data)

        expected_date = datetime(2025, 9, 26, 0, 0, 0)
        assert product.date == expected_date

    def test_product_image_urls(self, product_data):
        """Test pcgame digital product image URLs."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "digital/pcgame/yuzu_0012" in product.image_url.list
        assert product.image_url.small is not None
        assert product.image_url.large is not None

    def test_product_item_info_actresses(self, product_data):
        """Test pcgame digital product actresses."""

        product = Product.from_dict(product_data)

        actresses = product.actresses
        assert len(actresses) == 0

    def test_product_item_info_makers(self, product_data):
        """Test pcgame digital product makers."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        assert makers[0].id == 30727
        assert makers[0].name == "ゆずソフト"

    def test_product_item_info_manufactures(self, product_data):
        "Test pcgame digital product manufactures."

        product = Product.from_dict(product_data)

        assert hasattr(product.item_info, "manufacture") if product.item_info else True
        manufactures = (
            getattr(product.item_info, "manufacture", []) if product.item_info else []
        )
        assert len(manufactures) == 0

    def test_product_to_dict(self, product_data):
        """Test converting pcgame digital product to dictionary."""

        product = Product.from_dict(product_data)
        result_dict = product.to_dict()

        assert result_dict["service_code"] == "pcgame"
        assert result_dict["content_id"] == "yuzu_0012"
        assert result_dict["title"] == product.title

    def test_product_raw_data_access(self, product_data):
        """Test access to raw pcgame digital API data."""

        product = Product.from_dict(product_data)

        raw_data = product.raw_data
        assert raw_data is not None
        assert raw_data["service_code"] == "pcgame"
        assert raw_data["content_id"] == "yuzu_0012"

    def test_sample_images_large(self, product_data):
        """Test large sample images for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 0

    def test_sample_movie_url(self, product_data):
        """Test sample movie URLs for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.sample_movie_url is None

    def test_optional_fields(self, product_data):
        """Test optional fields for pcgame digital products."""

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
        """Test item info categories for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert len(product.genres) > 0
        assert len(product.makers) > 0
        assert len(product.authors) > 0
        assert len(product.series) > 0

        assert len(product.labels) == 0
        assert len(product.actresses) == 0
        assert len(product.directors) == 0
        assert len(product.actors) == 0
        assert len(product.types) == 0
        assert len(product.colors) == 0
        assert len(product.sizes) == 0
        assert len(product.directory) == 0

    def test_convenience_properties(self, product_data):
        """Test convenience properties for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.review_count == 91
        assert product.review_average == 4.84
        assert product.current_price == 8470
        assert product.original_price is None
        assert len(product.sample_images) == 18
        assert len(product.sample_images_large) == 0

    def test_nested_objects(self, product_data):
        """Test nested objects for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is None
        assert product.tachiyomi is None
        assert product.prices is not None
        assert product.review is not None
        assert product.item_info is not None
        assert product.cdinfo is None
        assert product.campaign is None

    def test_directory_structure(self, product_data):
        """Test directory structure for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert len(product.directory) == 0

    def test_pricing_structure(self, product_data):
        """Test pricing structure for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "8470"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 1
        assert product.prices.price_int == 8470
        assert product.prices.list_price_int is None

    def test_delivery_options(self, product_data):
        """Test delivery options for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert len(product.prices.deliveries) == 1

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "8470"

    def test_product_fields(self, product_data):
        """Test product fields for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.service_code == "pcgame"
        assert product.service_name == "アダルトPCゲーム"
        assert product.floor_code == "digital_pcgame"
        assert product.floor_name == "アダルトPCゲーム"
        assert product.category_name == "アダルトPCゲーム"
        assert product.content_id == "yuzu_0012"
        assert product.product_id == "yuzu_0012"
        assert product.title is not None
        assert product.volume is None
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
        """Test review data for pcgame digital products."""

        product = Product.from_dict(product_data)

        assert product.review is not None
        assert product.review.count == 91
        assert product.review.average == 4.84
        assert product.review_count == 91
        assert product.review_average == 4.84

    def test_digital_pcgame_specific_fields(self, product_data):
        """Test digital PC game specific characteristics."""

        product = Product.from_dict(product_data)

        assert product.url is not None
        assert "dlsoft.dmm.co.jp" in product.url
        assert product.affiliate_url is not None
        assert "dlsoft.dmm.co.jp" in product.affiliate_url

        series = product.series
        assert len(series) == 1
        assert series[0].id == 4594520
        assert series[0].name == "ライムライト・レモネードジャム"

        authors = product.authors
        assert len(authors) == 4
        assert authors[0].id == 239231
        assert authors[0].name == "むりりん"
        assert authors[0].ruby == "むりりん"

    def test_digital_pcgame_content_characteristics(self, product_data):
        """Test digital PC game content features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]

        assert "女子校生" in genre_names
        assert "制服" in genre_names
        assert "デモ・体験版あり" in genre_names
        assert "DL版独占販売" in genre_names
        assert "ブラウザ対応" in genre_names
        assert "Windows11対応作品" in genre_names

        assert len(product.sample_images) == 18
        assert product.sample_movie_url is None

    def test_digital_pcgame_pricing_model(self, product_data):
        """Test digital PC game download pricing model."""

        product = Product.from_dict(product_data)

        assert product.prices is not None
        assert product.prices.price == "8470"
        assert product.prices.list_price is None
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 8470
        assert product.original_price is None

        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"
        assert delivery.price == "8470"
        assert delivery.list_price == ""

    def test_digital_pcgame_maker_info(self, product_data):
        """Test digital PC game maker information."""

        product = Product.from_dict(product_data)

        makers = product.makers
        assert len(makers) == 1
        maker = makers[0]
        assert maker.id == 30727
        assert maker.name == "ゆずソフト"

    def test_digital_pcgame_author_info(self, product_data):
        """Test digital PC game author information."""

        product = Product.from_dict(product_data)

        authors = product.authors
        assert len(authors) == 4

        author1 = authors[0]
        assert author1.id == 239231
        assert author1.name == "むりりん"
        assert author1.ruby == "むりりん"

        author2 = authors[1]
        assert author2.id == 239232
        assert author2.name == "こぶいち"
        assert author2.ruby == "こぶいち"

        author3 = authors[2]
        assert author3.id == 365208
        assert author3.name == "ほかん"
        assert author3.ruby == "ほかん"

        author4 = authors[3]
        assert author4.id == 248182
        assert author4.name == "羽純りお"
        assert author4.ruby == "はづみりお"

    def test_digital_pcgame_category_structure(self, product_data):
        """Test digital PC game category structure."""

        product = Product.from_dict(product_data)

        assert product.service_code == "pcgame"
        assert product.service_name == "アダルトPCゲーム"
        assert product.floor_code == "digital_pcgame"
        assert product.floor_name == "アダルトPCゲーム"
        assert product.category_name == "アダルトPCゲーム"

        assert len(product.directory) == 0

    def test_digital_download_features(self, product_data):
        """Test digital download specific characteristics."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "DL版独占販売" in genre_names

        assert product.stock is None
        assert product.jancode is None

        assert product.prices is not None
        delivery = product.prices.deliveries[0]
        assert delivery.type == "download"

    def test_adult_pcgame_classification(self, product_data):
        """Test adult PC game classification."""

        product = Product.from_dict(product_data)

        assert product.category_name == "アダルトPCゲーム"
        assert product.floor_name == "アダルトPCゲーム"
        assert product.service_name == "アダルトPCゲーム"

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "女子校生" in genre_names
        assert "制服" in genre_names

        assert len(product.sample_images) == 18

    def test_game_technical_features(self, product_data):
        """Test game technical compatibility features."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "Windows11対応作品" in genre_names
        assert "ブラウザ対応" in genre_names
        assert "デモ・体験版あり" in genre_names

    def test_game_quality_ratings(self, product_data):
        """Test game quality and content ratings."""

        product = Product.from_dict(product_data)

        genres = product.genres
        genre_names = [g.name for g in genres]
        assert "CGがいい" in genre_names
        assert "キャラクターがいい" in genre_names
        assert "音楽がいい" in genre_names

        assert product.review_count == 91
        assert product.review_average == 4.84
