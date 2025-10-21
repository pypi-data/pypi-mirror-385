"""
Tests for ProductApiResponse class.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.commons import ApiRequest
from py_dmmjp.product import Product, ProductApiResponse, ProductApiResult


class TestProductApiResponse:
    """Test cases for ProductApiResponse."""

    @pytest.fixture
    def response_data(self) -> Dict[str, Any]:
        """Mock ProductApiResponse data from DMM API response."""

        return {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                    "site": "FANZA",
                    "keyword": "mide",
                    "service": "digital",
                    "floor": "videoa",
                    "hits": "1",
                }
            },
            "result": {
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
                                    {
                                        "type": "hd",
                                        "price": "686",
                                        "list_price": "980",
                                    },
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
                            "actress": [
                                {
                                    "id": 1042129,
                                    "name": "七沢みあ",
                                    "ruby": "ななさわみあ",
                                }
                            ],
                            "director": [
                                {"id": 101796, "name": "五右衛門", "ruby": "ごえもん"}
                            ],
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
            },
        }

    def test_response_basic_structure(self, response_data: Dict[str, Any]) -> None:
        """Test that ProductApiResponse parses basic structure with request and result."""

        response = ProductApiResponse.from_dict(response_data)
        assert isinstance(response, ProductApiResponse)
        assert isinstance(response.request, ApiRequest)
        assert isinstance(response.result, ProductApiResult)

    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        """Test that request object contains correct parameters."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.request is not None
        assert response.request.parameters is not None
        assert response.request.parameters.api_id == "***REDACTED_APP_ID***"
        assert response.request.parameters.affiliate_id == "***REDACTED_AFF_ID***"
        assert response.request.parameters["site"] == "FANZA"
        assert response.request.parameters["keyword"] == "mide"

    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        """Test that result object contains correct status and count fields."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.result is not None
        assert response.result.status == 200
        assert response.result.result_count == 1
        assert response.result.total_count == 1400
        assert len(response.result.items) == 1

    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test that raw_response property provides access to original data."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.raw_response is not None
        assert isinstance(response.raw_response, dict)
        assert "request" in response.raw_response
        assert "result" in response.raw_response

    def test_response_products_property(self, response_data: Dict[str, Any]) -> None:
        """Test that products property returns list of Product instances."""

        response = ProductApiResponse.from_dict(response_data)
        products = response.products
        assert isinstance(products, list)
        assert len(products) == 1
        assert all(isinstance(p, Product) for p in products)
        assert products[0].content_id == "mide00799"

    def test_response_product_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test that product_count property matches result.result_count."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.product_count == 1
        assert response.product_count == response.result.result_count

    def test_response_total_products_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test that total_products property matches result.total_count."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.total_products == 1400
        assert response.total_products == response.result.total_count

    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test that status property matches result.status."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.status == 200
        assert response.status == response.result.status

    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test that convenience properties are consistent with result fields."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.products == response.result.items
        assert response.product_count == response.result.result_count
        assert response.total_products == response.result.total_count
        assert response.status == response.result.status

    def test_response_from_dict_creates_deep_copy(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test that raw_response is a deep copy of original data."""

        response = ProductApiResponse.from_dict(response_data)
        assert response.raw_response is not response_data
        response.raw_response["modified"] = True
        assert "modified" not in response_data

    def test_response_private_raw_response_not_in_repr(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test that private _raw_response field is excluded from repr."""

        response = ProductApiResponse.from_dict(response_data)
        repr_str = repr(response)
        assert "_raw_response" not in repr_str

    def test_response_empty_result(self) -> None:
        """Test that empty result with no products is handled correctly."""

        empty_data = {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                }
            },
            "result": {
                "status": 200,
                "result_count": 0,
                "total_count": 0,
                "first_position": 1,
                "items": [],
            },
        }
        response = ProductApiResponse.from_dict(empty_data)
        assert response.products == []
        assert response.product_count == 0
        assert response.total_products == 0

    def test_response_with_missing_request(self) -> None:
        """Test that missing request section is handled with defaults."""

        data = {
            "result": {
                "status": 200,
                "result_count": 0,
                "total_count": 0,
                "first_position": 1,
                "items": [],
            }
        }
        response = ProductApiResponse.from_dict(data)
        assert isinstance(response.request, ApiRequest)

    def test_response_with_missing_result(self) -> None:
        """Test that missing result section is handled with defaults."""

        data = {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                }
            }
        }
        response = ProductApiResponse.from_dict(data)
        assert isinstance(response.result, ProductApiResult)
        assert response.result.status == 200
        assert response.result.items == []

    def test_response_nested_product_data(self, response_data: Dict[str, Any]) -> None:
        """Test that nested product data within result is accessible."""

        response = ProductApiResponse.from_dict(response_data)
        product = response.products[0]
        assert product.title == "友達の妹が常にノーブラぽろり！！可愛すぎるビンビン乳首をこねくりたい 七沢みあ"
        assert product.service_code == "digital"
        assert product.floor_code == "videoa"
        assert product.review is not None
        assert product.review.count == 91

    def test_response_request_parameters_access(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test that request parameters can be accessed via dict-style interface."""

        response = ProductApiResponse.from_dict(response_data)
        params = response.request.parameters
        assert params["service"] == "digital"
        assert params["floor"] == "videoa"
        assert params["hits"] == "1"
        assert params["keyword"] == "mide"
