"""
Test genre data models with FANZA videoa floor data.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.genre import Genre
from tests.genre_test_base import GenreTestBase


class TestGenreVideoA(GenreTestBase):
    """Test genre with FANZA videoa floor data."""

    @pytest.fixture
    def genre_data(self) -> Dict[str, Any]:
        return {
            "genre_id": "6179",
            "name": "4時間以上作品",
            "ruby": "4じかんいじょうさくひん",
            "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp"
            "%2Fav%2Flist%2F%3Fgenre%3D6179%2F&af_id=***REDACTED_AFF_ID***&ch=api",
        }

    def test_genre_basic_fields(self, genre_data: Dict[str, Any]) -> None:
        genre = Genre.from_dict(genre_data)

        assert genre.genre_id == "6179"
        assert genre.name == "4時間以上作品"
        assert genre.ruby == "4じかんいじょうさくひん"
        assert "fanza.co.jp" in genre.list_url

    def test_genre_from_dict(self, genre_data: Dict[str, Any]) -> None:
        genre = Genre.from_dict(genre_data)

        assert isinstance(genre, Genre)
        assert genre.genre_id == genre_data["genre_id"]
        assert genre.name == genre_data["name"]
        assert genre.ruby == genre_data["ruby"]
        assert genre.list_url == genre_data["list_url"]

    def test_genre_id_type(self, genre_data: Dict[str, Any]) -> None:
        genre = Genre.from_dict(genre_data)

        assert isinstance(genre.genre_id, str)

    def test_genre_name_validation(self, genre_data: Dict[str, Any]) -> None:
        genre = Genre.from_dict(genre_data)

        assert genre.name is not None
        assert len(genre.name) > 0
        assert isinstance(genre.name, str)

    def test_genre_ruby_validation(self, genre_data: Dict[str, Any]) -> None:
        genre = Genre.from_dict(genre_data)

        assert genre.ruby is not None
        assert len(genre.ruby) > 0
        assert isinstance(genre.ruby, str)

    def test_genre_list_url_validation(self, genre_data: Dict[str, Any]) -> None:
        genre = Genre.from_dict(genre_data)

        assert genre.list_url is not None
        assert len(genre.list_url) > 0
        assert isinstance(genre.list_url, str)
        assert genre.list_url.startswith("https://")

    def test_genre_empty_data_handling(self, genre_data: Dict[str, Any]) -> None:
        empty_data: Dict[str, Any] = {}
        genre = Genre.from_dict(empty_data)

        assert genre.genre_id == ""
        assert genre.name == ""
        assert genre.ruby == ""
        assert genre.list_url == ""

    def test_genre_default_values(self, genre_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"genre_id": "6179"}
        genre = Genre.from_dict(partial_data)

        assert genre.genre_id == "6179"
        assert genre.name == ""
        assert genre.ruby == ""
        assert genre.list_url == ""
