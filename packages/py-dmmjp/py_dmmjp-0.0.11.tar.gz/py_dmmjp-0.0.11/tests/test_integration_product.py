"""
Integration tests for DMM client with real API requests for product-related functionality.
"""

# pylint: disable=redefined-outer-name,import-outside-toplevel,too-many-statements,too-many-public-methods


from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp.client import DMMClient
from py_dmmjp.exceptions import DMMAPIError
from py_dmmjp.product import Product


@pytest.mark.integration
class TestDMMClientWithProductIntegration:
    """Integration tests for DMM client with real API calls for products."""

    def test_client_authentication(self, dmm_client):
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_products_basic_request(self, dmm_client):
        """Test basic product retrieval from FANZA."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=5
        )

        assert isinstance(products, list)
        assert len(products) <= 5

        for product in products:
            assert isinstance(product, Product)
            assert product.service_code == "digital"
            assert product.floor_code == "videoa"
            assert product.title is not None
            assert product.content_id is not None

    def test_get_products_with_keyword_search(self, dmm_client):
        """Test product search with keyword."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", keyword="S1", hits=3
        )

        assert isinstance(products, list)
        assert len(products) <= 3

        for product in products:
            assert isinstance(product, Product)
            assert product.service_code == "digital"

    def test_get_products_dmm_com_site(self, dmm_client):
        """Test product retrieval from DMM.com (general content)."""

        products = dmm_client.get_products(
            site="DMM.com", service="mono", floor="book", hits=3
        )

        assert isinstance(products, list)
        assert len(products) <= 3

        for product in products:
            assert isinstance(product, Product)
            assert product.service_code == "mono"
            assert product.floor_code == "book"

    def test_get_products_with_sorting(self, dmm_client):
        """Test product retrieval with different sort options."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", sort="date", hits=3
        )

        assert isinstance(products, list)
        assert len(products) <= 3

        for product in products:
            assert isinstance(product, Product)
            assert product.date is not None

    def test_get_products_ebook_service(self, dmm_client):
        """Test ebook product retrieval."""

        products = dmm_client.get_products(
            site="FANZA", service="ebook", floor="comic", hits=3
        )

        assert isinstance(products, list)
        assert len(products) <= 3

        for product in products:
            assert isinstance(product, Product)
            assert product.service_code == "ebook"
            assert product.floor_code == "comic"

    def test_product_data_completeness(self, dmm_client):
        """Test that product data contains expected fields."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        assert product.service_code is not None
        assert product.service_name is not None
        assert product.floor_code is not None
        assert product.floor_name is not None
        assert product.category_name is not None
        assert product.content_id is not None
        assert product.product_id is not None
        assert product.title is not None
        assert product.url is not None
        assert product.affiliate_url is not None
        assert product.image_url is not None
        assert product.prices is not None

    def test_product_item_info_data(self, dmm_client):
        """Test that product item info contains valid data."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        assert product.item_info is not None
        assert isinstance(product.genres, list)
        assert isinstance(product.actresses, list)
        assert isinstance(product.makers, list)
        assert isinstance(product.series, list)

    def test_product_pricing_data(self, dmm_client):
        """Test product pricing information."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        assert product.prices is not None
        assert product.current_price is not None
        assert isinstance(product.current_price, int)
        assert product.current_price > 0

    def test_product_image_urls(self, dmm_client):
        """Test product image URL data."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert product.image_url.list.startswith("http")

    def test_product_review_data(self, dmm_client):
        """Test product review information."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", sort="review", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        if product.review is not None:
            assert product.review_count >= 0
            assert product.review_average is None or product.review_average >= 0

    def test_product_sample_data(self, dmm_client):
        """Test product sample images and videos."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        assert isinstance(product.sample_images, list)
        assert isinstance(product.sample_images_large, list)

    def test_error_handling_invalid_service(self, dmm_client):
        """Test error handling with invalid service."""

        with pytest.raises(DMMAPIError) as exc_info:
            dmm_client.get_products(
                site="FANZA", service="invalid_service", floor="videoa", hits=1
            )

        # Verify that the error contains information about the invalid service
        assert "400" in str(exc_info.value)
        assert "BAD REQUEST" in str(exc_info.value) or "Invalid Request Error" in str(
            exc_info.value
        )

    def test_empty_results_valid_request(self, dmm_client):
        """Test handling of valid requests that return no results."""

        # Use a very specific keyword that's unlikely to match any products
        products = dmm_client.get_products(
            site="FANZA",
            service="digital",
            floor="videoa",
            keyword="xyznomatchkeyword12345",
            hits=1,
        )

        assert isinstance(products, list)
        assert len(products) == 0

    def test_error_handling_invalid_floor(self, dmm_client):
        """Test error handling with invalid floor for a valid service."""

        with pytest.raises(DMMAPIError) as exc_info:
            dmm_client.get_products(
                site="FANZA", service="digital", floor="invalid_floor", hits=1
            )

        assert "400" in str(exc_info.value)

    def test_error_handling_invalid_site(self, dmm_client):
        """Test error handling with invalid site parameter."""

        with pytest.raises(DMMAPIError) as exc_info:
            dmm_client.get_products(
                site="INVALID_SITE", service="digital", floor="videoa", hits=1
            )

        assert "400" in str(exc_info.value)

    def test_pagination_with_offset(self, dmm_client):
        """Test pagination using offset parameter."""

        first_page = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=2, offset=1
        )

        second_page = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=2, offset=3
        )

        assert len(first_page) <= 2
        assert len(second_page) <= 2

        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0].content_id != second_page[0].content_id

    def test_client_context_manager(self, app_id, aff_id):
        """Test client as context manager."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            products = client.get_products(
                site="FANZA", service="digital", floor="videoa", hits=1
            )

            assert isinstance(products, list)

    def test_raw_data_access(self, dmm_client):
        """Test access to raw API response data."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        assert product.raw_data is not None
        assert isinstance(product.raw_data, dict)
        assert "service_code" in product.raw_data
        assert "content_id" in product.raw_data

    def test_product_to_dict_conversion(self, dmm_client):
        """Test product to dictionary conversion."""

        products = dmm_client.get_products(
            site="FANZA", service="digital", floor="videoa", hits=1
        )

        assert len(products) >= 1
        product = products[0]

        product_dict = product.to_dict()

        assert isinstance(product_dict, dict)
        assert product_dict["service_code"] == product.service_code
        assert product_dict["content_id"] == product.content_id
        assert product_dict["title"] == product.title

    def test_product_with_fanza_cid(self, dmm_client):
        """Test retrieving a single product by content ID (CID)."""

        cid = "mird00127"
        product = dmm_client.get_product_by_cid(cid, site="FANZA")

        assert product is not None
        assert isinstance(product, Product)

        assert product.service_code == "digital"
        assert product.service_name == "動画"
        assert product.floor_code == "videoa"
        assert product.floor_name == "ビデオ"
        assert product.category_name == "ビデオ (動画)"
        assert product.content_id == cid
        assert product.product_id == cid
        assert product.title is not None
        assert "国民的アイドルM-girls" in product.title
        assert product.volume == 237

        assert product.review is not None
        assert product.review.count == 10
        assert product.review.average == 3.4
        assert product.review_count == 10
        assert product.review_average == 3.4

        assert product.url is not None
        assert product.affiliate_url is not None
        assert "mird00127" in product.url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert product.image_url.small is not None
        assert product.image_url.large is not None
        assert "mird00127pt.jpg" in product.image_url.list

        assert product.sample_image_url is not None
        assert len(product.sample_images) == 10
        assert len(product.sample_images_large) == 10
        assert all("mird00127-" in img for img in product.sample_images)
        assert all("mird00127jp-" in img for img in product.sample_images_large)

        assert product.sample_movie_url is not None
        assert product.sample_movie_url.size_476_306 is not None
        assert product.sample_movie_url.size_560_360 is not None
        assert product.sample_movie_url.size_644_414 is not None
        assert product.sample_movie_url.size_720_480 is not None
        assert product.sample_movie_url.pc_flag == 1
        assert product.sample_movie_url.sp_flag == 1

        assert product.prices is not None
        assert product.prices.price == "300~"
        assert product.prices.list_price == "300~"
        assert len(product.prices.deliveries) == 5
        assert product.current_price == 300
        assert product.original_price == 300

        delivery_types = [d.type for d in product.prices.deliveries]
        assert "stream" in delivery_types
        assert "download" in delivery_types
        assert "hd" in delivery_types
        assert "iosdl" in delivery_types
        assert "androiddl" in delivery_types

        assert product.date is not None
        assert product.date.year == 2013
        assert product.date.month == 11
        assert product.date.day == 28

        assert product.item_info is not None
        assert len(product.genres) == 8
        assert len(product.series) == 1
        assert len(product.makers) == 1
        assert len(product.actresses) == 9
        assert len(product.directors) == 1
        assert len(product.labels) == 1

        genre_names = [g.name for g in product.genres]
        assert "アイドル・芸能人" in genre_names
        assert "乱交" in genre_names
        assert "美少女" in genre_names

        assert product.series[0].name == "国民的アイドルM-girls"
        assert product.makers[0].name == "ムーディーズ"
        assert product.directors[0].name == "ZAMPA"
        assert product.labels[0].name == "MOODYZ REAL"

        actress_names = [a.name for a in product.actresses]
        assert "乙葉ななせ" in actress_names
        assert "鈴村みゆう" in actress_names

        assert product.raw_data is not None
        assert isinstance(product.raw_data, dict)
        assert product.raw_data["content_id"] == cid

    def test_product_with_mono_cid(self, dmm_client):
        """Test retrieving a single product by content ID (CID) from MONO service."""

        cid = "118abp477"
        product = dmm_client.get_product_by_cid(cid, site="FANZA")

        assert product is not None
        assert isinstance(product, Product)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "dvd"
        assert product.floor_name == "DVD"
        assert product.category_name == "DVD通販"
        assert product.content_id == cid
        assert product.product_id == cid
        assert product.title == "エンドレスセックス AIKA"
        assert product.volume == 140

        assert product.review is not None
        assert product.review.count == 32
        assert product.review.average == 4.41
        assert product.review_count == 32
        assert product.review_average == 4.41

        assert product.url is not None
        assert product.affiliate_url is not None
        assert "118abp477" in product.url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "118abp477pt.jpg" in product.image_url.list

        assert product.sample_image_url is not None
        assert len(product.sample_images) == 13
        assert all("118abp477-" in img for img in product.sample_images)

        assert product.prices is not None
        assert product.prices.price == "2589"
        assert product.prices.list_price == "3278"
        assert product.current_price == 2589
        assert product.original_price == 3278

        assert product.date is not None
        assert product.date.year == 2016
        assert product.date.month == 5
        assert product.date.day == 10

        assert product.item_info is not None
        assert len(product.genres) == 7
        assert len(product.series) == 1
        assert len(product.makers) == 1
        assert len(product.actresses) == 1
        assert len(product.directors) == 1
        assert len(product.labels) == 1

        genre_names = [g.name for g in product.genres]
        assert "ギャル" in genre_names
        assert "ぶっかけ" in genre_names
        assert "乱交" in genre_names

        assert product.series[0].name == "エンドレスセックス"
        assert product.makers[0].name == "プレステージ"
        assert product.actresses[0].name == "AIKA"
        assert product.directors[0].name == "マンハッタン木村"
        assert product.labels[0].name == "ABSOLUTELY PERFECT"

        assert product.jancode == "4571471003921"
        assert product.maker_product == "ABP-477"
        assert product.stock == "empty"

        assert len(product.directory) == 1
        assert product.directory[0].name == "DVD"

        assert product.raw_data is not None
        assert product.raw_data["content_id"] == cid

    def test_product_with_pcgame_cid(self, dmm_client):
        """Test retrieving a single product by content ID (CID) from PC Game service."""

        cid = "sisp_0049pack"
        product = dmm_client.get_product_by_cid(cid, site="FANZA")

        assert product is not None
        assert isinstance(product, Product)

        assert product.service_code == "pcgame"
        assert product.service_name == "アダルトPCゲーム"
        assert product.floor_code == "digital_pcgame"
        assert product.floor_name == "アダルトPCゲーム"
        assert product.category_name == "アダルトPCゲーム"
        assert product.content_id == cid
        assert product.product_id == cid
        assert product.title is not None
        assert "ANIM.teamMM" in product.title
        assert "寝取ラレ寝取ラセ欲ばりセット" in product.title

        assert product.review is not None
        assert product.review.count == 6
        assert product.review.average == 5.0
        assert product.review_count == 6
        assert product.review_average == 5.0

        assert product.url is not None
        assert product.affiliate_url is not None
        assert "sisp_0049pack" in product.url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert "sisp_0049packpt.jpg" in product.image_url.list

        assert product.sample_image_url is not None
        assert len(product.sample_images) == 24
        assert all("sisp_0049packjs-" in img for img in product.sample_images)

        assert product.prices is not None
        assert product.prices.price == "9480"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 9480
        assert product.prices.deliveries[0].type == "download"
        assert product.prices.deliveries[0].price == "9480"

        assert product.date is not None
        assert product.date.year == 2019
        assert product.date.month == 12
        assert product.date.day == 27

        assert product.item_info is not None
        assert len(product.genres) >= 0
        assert len(product.makers) >= 0
        assert len(product.authors) >= 0

        genre_names = [g.name for g in product.genres]
        assert "お母さん" in genre_names
        assert "人妻" in genre_names
        assert "巨乳" in genre_names
        assert "寝取られ（NTR）" in genre_names
        assert "セット商品" in genre_names

        assert product.makers[0].name == "Anim"

        author_names = [a.name for a in product.authors]
        assert "うん=食太郎" in author_names
        assert "リャオ" in author_names

        assert product.raw_data is not None
        assert product.raw_data["content_id"] == cid

    def test_product_with_doujin_cid(self, dmm_client):
        """Test retrieving a single product by content ID (CID) from Doujin service."""

        cid = "d_668247"
        product = dmm_client.get_product_by_cid(cid, site="FANZA")

        assert product is not None
        assert isinstance(product, Product)

        assert product.service_code == "doujin"
        assert product.service_name == "同人"
        assert product.floor_code == "digital_doujin_tl"
        assert product.floor_name == "らぶカル（TL）"
        assert product.category_name == "TL (電子書籍)"
        assert product.content_id == cid
        assert product.product_id == cid
        assert product.title is not None
        assert "狼に衣" in product.title
        assert "ドジなふりした幼馴染の執着体格差えっちに抗えない" in product.title
        assert product.volume == 69

        assert product.review is not None
        assert product.review.count == 1
        assert product.review.average == 5.0
        assert product.review_count == 1
        assert product.review_average == 5.0

        assert product.url is not None
        assert product.affiliate_url is not None
        assert "d_668247" in product.url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert product.image_url.large is not None
        assert "d_668247pt.jpg" in product.image_url.list
        assert "d_668247pl.jpg" in product.image_url.large

        assert product.sample_image_url is not None
        assert len(product.sample_images_large) == 10
        assert all("d_668247jp-" in img for img in product.sample_images_large)

        assert product.prices is not None
        assert product.prices.price == "616"
        assert product.prices.list_price == "880"
        assert len(product.prices.deliveries) == 1
        assert product.current_price == 616
        assert product.original_price == 880
        assert product.prices.deliveries[0].type == "download"
        assert product.prices.deliveries[0].price == "616"
        assert product.prices.deliveries[0].list_price == "880"

        assert product.date is not None
        assert product.date.year == 2025
        assert product.date.month == 10
        assert product.date.day == 1

        assert product.item_info is not None
        assert len(product.genres) == 8
        assert len(product.makers) == 1

        genre_names = [g.name for g in product.genres]
        assert "幼なじみ" in genre_names
        assert "中出し" in genre_names
        assert "おっぱい" in genre_names
        assert "女性向け" in genre_names
        assert "成人向け" in genre_names
        assert "執着攻め" in genre_names
        assert "種付けプレス" in genre_names
        assert "体格差" in genre_names

        assert product.makers[0].name == "準社員井上"

        assert hasattr(product, "campaign") and len(product.campaign) == 1
        assert product.campaign[0].title == "30%OFF"

        assert product.raw_data is not None
        assert product.raw_data["content_id"] == cid

    def test_product_with_nonexistent_cid(self, dmm_client):
        """Test retrieving a product with non-existent CID returns None."""

        nonexistent_cid = "nonexistent12345"
        product = dmm_client.get_product_by_cid(nonexistent_cid, site="FANZA")

        assert product is None

    def test_product_with_invalid_site(self, dmm_client):
        """Test retrieving a product with invalid site"""

        cid = "mird00127"

        with pytest.raises(DMMAPIError) as exc_info:
            dmm_client.get_product_by_cid(cid, site="INVALID_SITE")

        assert "400" in str(exc_info.value)
        assert "BAD REQUEST" in str(exc_info.value) or "Invalid Request Error" in str(
            exc_info.value
        )

    def test_product_by_product_id(self, dmm_client):
        """Test retrieving a single product by its product ID (maker_product)."""

        product_id = "PPPE-064"
        product = dmm_client.get_product_by_product_id(product_id, site="FANZA")

        assert product is not None
        assert isinstance(product, Product)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "dvd"
        assert product.floor_name == "DVD"
        assert product.category_name == "DVD通販"
        assert product.content_id == "pppe064"
        assert product.product_id == "pppe064"
        assert product.title is not None
        assert "あいつが母と結婚した理由は私でした" in product.title
        assert "夕美しおん" in product.title
        assert product.volume == 120

        assert product.review is not None
        assert product.review.count == 8
        assert product.review.average == 3.38
        assert product.review_count == 8
        assert product.review_average == 3.38

        assert product.url is not None
        assert product.affiliate_url is not None
        assert "pppe064" in product.url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert product.image_url.small is not None
        assert product.image_url.large is not None
        assert "pppe064pt.jpg" in product.image_url.list

        assert product.sample_image_url is not None
        assert len(product.sample_images) == 12
        assert all("pppe00064-" in img for img in product.sample_images)

        assert product.prices is not None
        assert product.prices.price == "2622"
        assert product.prices.list_price == "3278"
        assert product.current_price == 2622
        assert product.original_price == 3278

        assert product.date is not None
        assert product.date.year == 2022
        assert product.date.month == 8
        assert product.date.day == 16

        assert product.item_info is not None
        assert len(product.genres) == 7
        assert len(product.series) == 1
        assert len(product.makers) == 1
        assert len(product.actresses) == 1
        assert len(product.labels) == 1

        genre_names = [g.name for g in product.genres]
        assert "中出し" in genre_names
        assert "フェラ" in genre_names
        assert "巨乳" in genre_names
        assert "潮吹き" in genre_names
        assert "パイズリ" in genre_names
        assert "単体作品" in genre_names

        assert product.series[0].name == "妻が帰省した一週間早熟な巨乳連れ子を絶倫チ○ポでピストン調教"
        assert product.makers[0].name == "OPPAI"
        assert product.actresses[0].name == "夕美しおん"
        assert product.actresses[0].ruby == "ゆうみしおん"
        assert product.labels[0].name == "OPPAI"

        assert product.jancode == "4549831864413"
        assert product.maker_product == "PPPE-064"
        assert product.stock == "empty"

        assert len(product.directory) == 1
        assert product.directory[0].name == "DVD"

        assert product.raw_data is not None
        assert product.raw_data["content_id"] == "pppe064"

    def test_product_by_product_id_with_nonexistent(
        self, dmm_client: DMMClient
    ) -> None:
        """Test retrieving a product with non-existent product ID returns None."""

        nonexistent_product_id = "NONEXISTENT-999"
        product = dmm_client.get_product_by_product_id(
            nonexistent_product_id,
            site="FANZA",
        )

        assert product is None

    def test_product_by_product_id_with_empty_maker_product(
        self, dmm_client: DMMClient
    ) -> None:
        """Test retrieving a product with empty maker_product returns None."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
{
  "request": {
    "parameters": {
      "api_id": "my_app_id",
      "affiliate_id": "my_affiliate_id",
      "site": "FANZA",
      "keyword": "MIDE",
      "hits": "1"
    }
  },
  "result": {
    "status": 200,
    "result_count": 1,
    "total_count": 5477,
    "first_position": 1,
    "items": [
      {
        "service_code": "digital",
        "service_name": "動画",
        "floor_code": "videoa",
        "floor_name": "ビデオ",
        "category_name": "ビデオ (動画)",
        "content_id": "mide00872",
        "product_id": "mide00872",
        "title": "妻が帰省した3日間発育しきって喰い頃な巨乳連れ子を一生分ヤリ貯めした。 水卜さくら",
        "volume": "118",
        "review": {
          "count": 83,
          "average": "4.69"
        },
        "URL": "https://video.dmm.co.jp/av/content/?id=mide00872",
        "sampleImageURL": {
          "sample_s": {
            "image": [
              "https://pics.dmm.co.jp/digital/video/mide00872/mide00872-1.jpg",
              "https://pics.dmm.co.jp/digital/video/mide00872/mide00872-2.jpg"
            ]
          },
          "sample_l": {
            "image": [
              "https://pics.dmm.co.jp/digital/video/mide00872/mide00872jp-1.jpg",
              "https://pics.dmm.co.jp/digital/video/mide00872/mide00872jp-2.jpg"
            ]
          }
        }
      }
    ]
  }
}
        """

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            product = dmm_client.get_product_by_product_id(
                "MIDE-872",
                site="FANZA",
            )

        assert product is None

    def test_product_by_product_id_with_predicate(self, dmm_client: DMMClient) -> None:
        """Test retrieving a single product by product ID with a predicate function."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
{
  "request": {
    "parameters": {
      "api_id": "my_app_id",
      "affiliate_id": "my_affiliate_id",
      "site": "FANZA",
      "keyword": "KEED-077"
    }
  },
  "result": {
    "status": 200,
    "result_count": 1,
    "total_count": 1,
    "first_position": 1,
    "items": [
      {
        "service_code": "mono",
        "service_name": "通販",
        "floor_code": "dvd",
        "floor_name": "DVD",
        "category_name": "DVD通販",
        "content_id": "h_086keed77",
        "product_id": "h_086keed77",
        "title": "娘が不在中、娘の彼氏に無理やり中出しされ発情した彼女の母親 君島みお",
        "volume": "90",
        "review": {
          "count": 4,
          "average": "3.75"
        },
        "URL": "https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=h_086keed77/",
        "sampleImageURL": {
          "sample_s": {
            "image": [
              "https://pics.dmm.co.jp/digital/video/h_086keed77/h_086keed77-1.jpg"
            ]
          }
        },
        "jancode": "4573228571981",
        "maker_product": "KEED-77",
        "stock": "empty"
      }
    ]
  }
}
"""

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            product = dmm_client.get_product_by_product_id(
                "KEED-077",
                site="FANZA",
            )

        assert product is not None
        assert isinstance(product, Product)
        assert product.maker_product == "KEED-77"

    def test_product_by_product_id_with_no_dash(self, dmm_client: DMMClient) -> None:
        """Test retrieving products by product ID with no dash."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
{
  "request": {
    "parameters": {
      "api_id": "my_app_id",
      "affiliate_id": "my_affiliate_id",
      "site": "FANZA",
      "keyword": "SNIS"
    }
  },
  "result": {
    "status": 200,
    "result_count": 2,
    "total_count": 2,
    "first_position": 2,
    "items": [
      {
        "service_code": "mono",
        "service_name": "通販",
        "floor_code": "dvd",
        "floor_name": "DVD",
        "category_name": "DVD通販",
        "content_id": "snis777",
        "product_id": "snis777",
        "title": "Some Other Product",
        "jancode": "4573228571981",
        "maker_product": "snis777",
        "stock": "empty"
      },
      {
        "service_code": "mono",
        "service_name": "通販",
        "floor_code": "dvd",
        "floor_name": "DVD",
        "category_name": "DVD通販",
        "content_id": "snis777dd",
        "product_id": "snis777dd",
        "title": "Some Other Product",
        "jancode": "4573228571981",
        "maker_product": "snis-00777",
        "stock": "empty"
      }
    ]
  }
}
"""

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            product = dmm_client.get_product_by_product_id(
                "SNIS-777",
                site="FANZA",
            )

        assert product is None

    def test_product_by_product_id_with_zero_padding(self, dmm_client):
        """Test retrieving a single product by product ID that requires zero padding."""

        product_id = "KEED-077"
        product = dmm_client.get_product_by_product_id(product_id, site="FANZA")

        assert product is not None
        assert isinstance(product, Product)

        assert product.service_code == "mono"
        assert product.service_name == "通販"
        assert product.floor_code == "dvd"
        assert product.floor_name == "DVD"
        assert product.category_name == "DVD通販"
        assert product.content_id == "h_086keed77"
        assert product.product_id == "h_086keed77"
        assert product.title is not None
        assert "娘が不在中、娘の彼氏に無理やり中出しされ発情した彼女の母親" in product.title
        assert "君島みお" in product.title
        assert product.volume == 90

        assert product.review is not None
        assert product.review.count == 4
        assert product.review.average == 3.75
        assert product.review_count == 4
        assert product.review_average == 3.75

        assert product.url is not None
        assert product.affiliate_url is not None
        assert "h_086keed77" in product.url

        assert product.image_url is not None
        assert product.image_url.list is not None
        assert product.image_url.small is not None
        assert product.image_url.large is not None
        assert "h_086keed77pt.jpg" in product.image_url.list

        assert product.sample_image_url is not None
        assert len(product.sample_images) == 10
        assert all("h_086keed77-" in img for img in product.sample_images)

        assert product.prices is not None
        assert product.prices.price == "2967"
        assert product.prices.list_price == "4180"
        assert product.current_price == 2967
        assert product.original_price == 4180

        assert product.date is not None
        assert product.date.year == 2022
        assert product.date.month == 9
        assert product.date.day == 29

        assert product.item_info is not None
        assert len(product.genres) == 6
        assert len(product.series) == 1
        assert len(product.makers) == 1
        assert len(product.actresses) == 1
        assert len(product.directors) == 1
        assert len(product.labels) == 1

        genre_names = [g.name for g in product.genres]
        assert "寝取り・寝取られ・NTR" in genre_names
        assert "人妻・主婦" in genre_names
        assert "熟女" in genre_names
        assert "中出し" in genre_names
        assert "単体作品" in genre_names

        assert product.series[0].name == "娘が不在中、娘の彼氏に無理やり中出しされ発情した彼女の母親"
        assert product.makers[0].name == "センタービレッジ"
        assert product.actresses[0].name == "君島みお"
        assert product.actresses[0].ruby == "きみじまみお"
        assert product.directors[0].name == "湊谷"
        assert product.directors[0].ruby == "みなとや"
        assert product.labels[0].name == "花園（センタービレッジ）"

        assert product.jancode == "4573228571981"
        assert product.maker_product == "KEED-77"
        assert product.stock == "empty"

        assert len(product.directory) == 1
        assert product.directory[0].name == "DVD"

        assert product.raw_data is not None
        assert product.raw_data["content_id"] == "h_086keed77"

    def test_product_by_product_id_nonexistent(self, dmm_client):
        """Test retrieving a product with non-existent product ID returns None."""

        nonexistent_product_id = "NONEXISTENT-999"
        product = dmm_client.get_product_by_product_id(
            nonexistent_product_id, site="FANZA"
        )

        assert product is None

    def test_product_by_product_id_invalid_site(self, dmm_client):
        """Test retrieving a product by product ID with invalid site."""

        product_id = "PPPE-064"

        with pytest.raises(DMMAPIError) as exc_info:
            dmm_client.get_product_by_product_id(product_id, site="INVALID_SITE")

        assert "400" in str(exc_info.value)
        assert "BAD REQUEST" in str(exc_info.value) or "Invalid Request Error" in str(
            exc_info.value
        )

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": 200, "data": []}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_products(site="FANZA", service="digital", floor="videoa")

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200, "items": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.DMMClient._make_request",
                side_effect=ValueError("Unexpected error"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_products(
                        site="FANZA", service="digital", floor="videoa"
                    )

                assert "Failed to get products" in str(exc_info.value)
                assert "Unexpected error" in str(exc_info.value)
