"""
Test GenreSearchResponse with FANZA videoa floor data.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.commons import ApiRequest, RequestParameters
from py_dmmjp.genre import Genre, GenreSearchResponse, GenreSearchResult
from tests.genre_test_base import GenreSearchResponseTestBase


class TestGenreSearchResponseVideoA(GenreSearchResponseTestBase):
    """Test GenreSearchResponse with FANZA videoa floor data."""

    @pytest.fixture
    def response_data(self) -> Dict[str, Any]:
        return {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                    "floor_id": "43",
                    "hits": "5",
                }
            },
            "result": {
                "status": "200",
                "result_count": 5,
                "total_count": "341",
                "first_position": 1,
                "site_name": "FANZA（アダルト）",
                "site_code": "FANZA",
                "service_name": "動画",
                "service_code": "digital",
                "floor_id": "43",
                "floor_name": "ビデオ",
                "floor_code": "videoa",
                "genre": [
                    {
                        "genre_id": "6179",
                        "name": "4時間以上作品",
                        "ruby": "4じかんいじょうさくひん",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
                        "%2Fav%2Flist%2F%3Fgenre%3D6179%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                    },
                    {
                        "genre_id": "4118",
                        "name": "アイドル・芸能人",
                        "ruby": "あいどるげいのうじん",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
                        "%2Fav%2Flist%2F%3Fgenre%3D4118%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                    },
                    {
                        "genre_id": "4076",
                        "name": "アクション",
                        "ruby": "あくしょん",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
                        "%2Fav%2Flist%2F%3Fgenre%3D4076%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                    },
                ],
            },
        }

    def test_response_structure(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        assert isinstance(response, GenreSearchResponse)
        assert isinstance(response.request, ApiRequest)
        assert isinstance(response.result, GenreSearchResult)

    def test_response_from_dict(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        assert isinstance(response, GenreSearchResponse)
        assert response.result.floor_code == "videoa"
        assert response.result.service_code == "digital"

    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        assert response.request is not None
        assert isinstance(response.request, ApiRequest)
        assert isinstance(response.request.parameters, RequestParameters)
        assert response.request.parameters.api_id == "***REDACTED_APP_ID***"
        assert response.request.parameters.affiliate_id == "***REDACTED_AFF_ID***"

    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        assert response.result is not None
        assert isinstance(response.result, GenreSearchResult)
        assert response.result.status == 200
        assert response.result.floor_code == "videoa"

    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        raw = response.raw_response
        assert raw is not None
        assert isinstance(raw, dict)
        assert "request" in raw
        assert "result" in raw

    def test_response_genres_property(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        genres = response.genres
        assert isinstance(genres, list)
        assert len(genres) == 3
        assert all(isinstance(genre, Genre) for genre in genres)

    def test_response_genre_count_property(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        count = response.genre_count
        assert isinstance(count, int)
        assert count == 5

    def test_response_total_genres_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        total = response.total_genres
        assert isinstance(total, int)
        assert total == 341

    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        status = response.status
        assert isinstance(status, int)
        assert status == 200

    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        response = GenreSearchResponse.from_dict(response_data)

        assert response.genres == response.result.genres
        assert response.genre_count == response.result.result_count
        assert response.total_genres == response.result.total_count
        assert response.status == response.result.status
