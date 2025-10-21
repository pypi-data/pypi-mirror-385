"""
Test GenreSearchResult with FANZA videoa floor data.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.genre import Genre, GenreSearchResult
from tests.genre_test_base import GenreSearchResultTestBase


class TestGenreSearchResultVideoA(GenreSearchResultTestBase):
    """Test GenreSearchResult with FANZA videoa floor data."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        return {
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
                {
                    "genre_id": "514",
                    "name": "アクション・格闘",
                    "ruby": "あくしょんかくとう",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
                    "%2Fav%2Flist%2F%3Fgenre%3D514%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "genre_id": "6968",
                    "name": "アクメ・オーガズム",
                    "ruby": "あくめおーがずむ",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
                    "%2Fav%2Flist%2F%3Fgenre%3D6968%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
            ],
        }

    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.status == 200
        assert result.result_count == 5
        assert result.total_count == 341
        assert result.first_position == 1

    def test_result_site_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.site_name == "FANZA（アダルト）"
        assert result.site_code == "FANZA"

    def test_result_service_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.service_name == "動画"
        assert result.service_code == "digital"

    def test_result_floor_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.floor_id == "43"
        assert result.floor_name == "ビデオ"
        assert result.floor_code == "videoa"

    def test_result_genre_list(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert isinstance(result.genres, list)
        assert len(result.genres) == 5

    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert isinstance(result, GenreSearchResult)
        assert result.status == 200
        assert result.site_code == result_data["site_code"]
        assert result.floor_code == result_data["floor_code"]

    def test_result_nested_genres(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        for genre in result.genres:
            assert isinstance(genre, Genre)
            assert genre.genre_id is not None
            assert genre.name is not None
            assert genre.ruby is not None
            assert genre.list_url is not None

    def test_result_empty_genres(self, result_data: Dict[str, Any]) -> None:
        empty_result_data: Dict[str, Any] = {
            "status": "200",
            "result_count": 0,
            "total_count": "0",
            "first_position": 1,
            "site_name": "FANZA（アダルト）",
            "site_code": "FANZA",
            "service_name": "動画",
            "service_code": "digital",
            "floor_id": "43",
            "floor_name": "ビデオ",
            "floor_code": "videoa",
            "genre": [],
        }
        result = GenreSearchResult.from_dict(empty_result_data)

        assert isinstance(result.genres, list)
        assert len(result.genres) == 0

    def test_result_multiple_genres(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert len(result.genres) == 5
        assert result.genres[0].genre_id == "6179"
        assert result.genres[1].genre_id == "4118"
        assert result.genres[2].genre_id == "4076"
        assert result.genres[3].genre_id == "514"
        assert result.genres[4].genre_id == "6968"

    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert isinstance(result.status, int)
        assert result.status == 200

    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert isinstance(result.result_count, int)
        assert isinstance(result.total_count, int)
        assert isinstance(result.first_position, int)
        assert result.result_count == 5
        assert result.total_count == 341
        assert result.first_position == 1

    def test_result_genre_type(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert isinstance(result.genres, list)
        for genre in result.genres:
            assert isinstance(genre, Genre)

    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"status": "200"}
        result = GenreSearchResult.from_dict(partial_data)

        assert result.status == 200
        assert result.result_count == 0
        assert result.total_count == 0
        assert result.first_position == 1
        assert result.site_name == ""
        assert result.site_code == ""
        assert result.service_name == ""
        assert result.service_code == ""
        assert result.floor_id == ""
        assert result.floor_name == ""
        assert result.floor_code == ""
        assert isinstance(result.genres, list)
        assert len(result.genres) == 0
