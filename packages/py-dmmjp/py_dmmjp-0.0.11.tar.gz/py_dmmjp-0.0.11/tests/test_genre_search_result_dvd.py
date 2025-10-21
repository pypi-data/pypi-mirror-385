"""
Test GenreSearchResult with FANZA DVD floor data.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.genre import Genre, GenreSearchResult
from tests.genre_test_base import GenreSearchResultTestBase


class TestGenreSearchResultDVD(GenreSearchResultTestBase):
    """Test GenreSearchResult with FANZA DVD floor data."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        return {
            "status": "200",
            "result_count": 5,
            "total_count": "452",
            "first_position": 1,
            "site_name": "FANZA（アダルト）",
            "site_code": "FANZA",
            "service_name": "通販",
            "service_code": "mono",
            "floor_id": "74",
            "floor_name": "DVD",
            "floor_code": "dvd",
            "genre": [
                {
                    "genre_id": "166",
                    "name": "10人新人女優デビュー祭",
                    "ruby": "10にんしんじんじょゆうでびゅーさい",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D166%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "genre_id": "6990",
                    "name": "1990年代（DOD）",
                    "ruby": "1990ねんだい",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D6990%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "genre_id": "6991",
                    "name": "2000年代（DOD）",
                    "ruby": "2000ねんだい",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D6991%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "genre_id": "6993",
                    "name": "2010年代後半（DOD）",
                    "ruby": "2010ねんだいこうはん",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D6993%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "genre_id": "6992",
                    "name": "2010年代前半（DOD）",
                    "ruby": "2010ねんだいぜんはん",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D6992%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
            ],
        }

    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.status == 200
        assert result.result_count == 5
        assert result.total_count == 452
        assert result.first_position == 1

    def test_result_site_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.site_name == "FANZA（アダルト）"
        assert result.site_code == "FANZA"

    def test_result_service_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.service_name == "通販"
        assert result.service_code == "mono"

    def test_result_floor_fields(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert result.floor_id == "74"
        assert result.floor_name == "DVD"
        assert result.floor_code == "dvd"

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
            "service_name": "通販",
            "service_code": "mono",
            "floor_id": "74",
            "floor_name": "DVD",
            "floor_code": "dvd",
            "genre": [],
        }
        result = GenreSearchResult.from_dict(empty_result_data)

        assert isinstance(result.genres, list)
        assert len(result.genres) == 0

    def test_result_multiple_genres(self, result_data: Dict[str, Any]) -> None:
        result = GenreSearchResult.from_dict(result_data)

        assert len(result.genres) == 5
        assert result.genres[0].genre_id == "166"
        assert result.genres[1].genre_id == "6990"
        assert result.genres[2].genre_id == "6991"
        assert result.genres[3].genre_id == "6993"
        assert result.genres[4].genre_id == "6992"

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
        assert result.total_count == 452
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
