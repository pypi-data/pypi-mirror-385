"""
Tests for ProductApiResult class.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.product import Product, ProductApiResult


class TestProductApiResult:
    """Test cases for ProductApiResult."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        """Mock ProductApiResult data from DMM API response."""

        return {
            "status": 200,
            "result_count": 1,
            "total_count": 1400,
            "first_position": 1,
            "items": [
                {
                    "service_code": "digital",
                    "service_name": "動画",
                    "floor_code": "videoa",
                    "floor_name": "ビデオ",
                    "category_name": "ビデオ (動画)",
                    "content_id": "mide00799",
                    "product_id": "mide00799",
                    "title": "友達の妹が常にノーブラぽろり！！可愛すぎるビンビン乳首をこねくりたい 七沢みあ",
                    "volume": "179",
                    "review": {"count": 91, "average": "4.84"},
                    "URL": "https://video.dmm.co.jp/av/content/?id=mide00799",
                    "affiliateURL": "https://al.fanza.co.jp/"
                    "?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
                    "%2Fav%2Fcontent%2F%3Fid%3Dmide00799&af_id=***REDACTED_AFF_ID***&ch=api",
                    "imageURL": {
                        "list": "https://pics.dmm.co.jp/digital/video/mide00799/mide00799pt.jpg",
                        "small": "https://pics.dmm.co.jp/digital/video/mide00799/mide00799ps.jpg",
                        "large": "https://pics.dmm.co.jp/digital/video/mide00799/mide00799pl.jpg",
                    },
                    "sampleImageURL": {
                        "sample_s": {
                            "image": [
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-1.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-2.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-3.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-4.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-5.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-6.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-7.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-8.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-9.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799-10.jpg",
                            ]
                        },
                        "sample_l": {
                            "image": [
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-1.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-2.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-3.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-4.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-5.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-6.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-7.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-8.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-9.jpg",
                                "https://pics.dmm.co.jp/digital/video/mide00799/mide00799jp-10.jpg",
                            ]
                        },
                    },
                    "sampleMovieURL": {
                        "size_476_306": "https://www.dmm.co.jp/litevideo/-/part/=/cid=mide00799/size=476_306/affi_id=***REDACTED_AFF_ID***/",
                        "size_560_360": "https://www.dmm.co.jp/litevideo/-/part/=/cid=mide00799/size=560_360/affi_id=***REDACTED_AFF_ID***/",
                        "size_644_414": "https://www.dmm.co.jp/litevideo/-/part/=/cid=mide00799/size=644_414/affi_id=***REDACTED_AFF_ID***/",
                        "size_720_480": "https://www.dmm.co.jp/litevideo/-/part/=/cid=mide00799/size=720_480/affi_id=***REDACTED_AFF_ID***/",
                        "pc_flag": 1,
                        "sp_flag": 1,
                    },
                    "prices": {
                        "price": "210~",
                        "list_price": "300~",
                        "deliveries": {
                            "delivery": [
                                {"type": "hd", "price": "686", "list_price": "980"},
                                {
                                    "type": "download",
                                    "price": "434",
                                    "list_price": "620",
                                },
                                {
                                    "type": "stream",
                                    "price": "210",
                                    "list_price": "300",
                                },
                                {
                                    "type": "iosdl",
                                    "price": "434",
                                    "list_price": "620",
                                },
                                {
                                    "type": "androiddl",
                                    "price": "434",
                                    "list_price": "620",
                                },
                            ]
                        },
                    },
                    "date": "2020-07-11 10:00:53",
                    "iteminfo": {
                        "genre": [
                            {"id": 6533, "name": "ハイビジョン"},
                            {"id": 6548, "name": "独占配信"},
                            {"id": 5023, "name": "顔射"},
                            {"id": 2005, "name": "貧乳・微乳"},
                            {"id": 102, "name": "美乳"},
                            {"id": 4010, "name": "その他フェチ"},
                            {"id": 1027, "name": "美少女"},
                            {"id": 6004, "name": "デジモ"},
                            {"id": 4025, "name": "単体作品"},
                        ],
                        "series": [
                            {
                                "id": 4594898,
                                "name": "友達の妹が常にノーブラぽろり！！可愛すぎるビンビン乳首をこねくりたい",
                            }
                        ],
                        "maker": [{"id": 1509, "name": "ムーディーズ"}],
                        "actress": [{"id": 1042129, "name": "七沢みあ", "ruby": "ななさわみあ"}],
                        "director": [{"id": 101796, "name": "五右衛門", "ruby": "ごえもん"}],
                        "label": [{"id": 4325, "name": "MOODYZ DIVA"}],
                    },
                    "campaign": [
                        {
                            "date_begin": "2025-10-20 10:00:00",
                            "date_end": "2025-10-22 09:59:59",
                            "title": "MOODYZキャンペーン30％OFF第4弾",
                        }
                    ],
                }
            ],
        }

    def test_result_basic_structure(self, result_data: Dict[str, Any]) -> None:
        """Test that ProductApiResult parses basic structure fields correctly."""

        result = ProductApiResult.from_dict(result_data)
        assert isinstance(result, ProductApiResult)
        assert result.status == 200
        assert result.result_count == 1
        assert result.total_count == 1400
        assert result.first_position == 1

    def test_result_items_list(self, result_data: Dict[str, Any]) -> None:
        """Test that items list contains Product instances."""

        result = ProductApiResult.from_dict(result_data)
        assert isinstance(result.items, list)
        assert len(result.items) == 1
        assert all(isinstance(item, Product) for item in result.items)

    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test that status code is parsed as integer."""

        result = ProductApiResult.from_dict(result_data)
        assert result.status == 200
        assert isinstance(result.status, int)

    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test that count fields are parsed correctly and logically consistent."""

        result = ProductApiResult.from_dict(result_data)
        assert result.result_count == 1
        assert result.total_count == 1400
        assert result.first_position == 1
        assert result.total_count > result.result_count

    def test_result_product_content(self, result_data: Dict[str, Any]) -> None:
        """Test that product items contain expected content data."""

        result = ProductApiResult.from_dict(result_data)
        product = result.items[0]
        assert product.content_id == "mide00799"
        assert product.service_code == "digital"
        assert product.floor_code == "videoa"
        assert "友達の妹" in product.title

    def test_result_empty_items(self) -> None:
        """Test that empty items list is handled correctly."""

        empty_data: Dict[str, Any] = {
            "status": 200,
            "result_count": 0,
            "total_count": 0,
            "first_position": 1,
            "items": [],
        }
        result = ProductApiResult.from_dict(empty_data)
        assert isinstance(result.items, list)
        assert len(result.items) == 0

    def test_result_default_values(self) -> None:
        """Test that default values are applied when data is missing."""

        minimal_data: Dict[str, Any] = {}
        result = ProductApiResult.from_dict(minimal_data)
        assert result.status == 200
        assert result.result_count == 0
        assert result.total_count == 0
        assert result.first_position == 1
        assert result.items == []

    def test_result_multiple_items(self) -> None:
        """Test that multiple product items are parsed correctly."""

        data = {
            "status": 200,
            "result_count": 2,
            "total_count": 1400,
            "first_position": 1,
            "items": [
                {
                    "service_code": "digital",
                    "service_name": "動画",
                    "floor_code": "videoa",
                    "floor_name": "ビデオ",
                    "category_name": "ビデオ (動画)",
                    "content_id": "mide00799",
                    "product_id": "mide00799",
                    "title": "友達の妹が常にノーブラぽろり！！可愛すぎるビンビン乳首をこねくりたい 七沢みあ",
                },
                {
                    "service_code": "digital",
                    "service_name": "動画",
                    "floor_code": "videoa",
                    "floor_name": "ビデオ",
                    "category_name": "ビデオ (動画)",
                    "content_id": "mide00800",
                    "product_id": "mide00800",
                    "title": "Another product",
                },
            ],
        }
        result = ProductApiResult.from_dict(data)
        assert len(result.items) == 2
        assert result.items[0].content_id == "mide00799"
        assert result.items[1].content_id == "mide00800"

    def test_result_product_parsing(self, result_data: Dict[str, Any]) -> None:
        """Test that nested product data is parsed correctly."""

        result = ProductApiResult.from_dict(result_data)
        product = result.items[0]
        assert product.review is not None
        assert product.review.count == 91
        assert product.review.average == 4.84
        assert product.image_url is not None
        assert product.sample_image_url is not None
        assert product.sample_movie_url is not None

    def test_result_type_consistency(self, result_data: Dict[str, Any]) -> None:
        """Test that all fields have consistent types."""

        result = ProductApiResult.from_dict(result_data)
        assert isinstance(result.status, int)
        assert isinstance(result.result_count, int)
        assert isinstance(result.total_count, int)
        assert isinstance(result.first_position, int)
        assert isinstance(result.items, list)
