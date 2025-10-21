"""
Integration tests for DMM genre API functionality.
"""

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp import DMMClient
from py_dmmjp.exceptions import DMMAPIError
from py_dmmjp.genre import Genre


@pytest.mark.integration
class TestDMMClientWithGenreIntegration:
    """Integration tests for DMM client with real API calls for genres."""

    def test_client_authentication(self, dmm_client: DMMClient) -> None:
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_genres_basic_request(self, dmm_client: DMMClient) -> None:
        """Test basic genre retrieval from DMM."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        assert isinstance(genres, list)
        assert len(genres) > 0

        for genre in genres:
            assert isinstance(genre, Genre)
            assert genre.genre_id is not None
            assert genre.name is not None
            assert genre.ruby is not None
            assert genre.list_url is not None

    def test_get_genres_with_floor_id(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval with specific floor ID."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=74, hits=10)

        assert isinstance(genres, list)
        assert len(genres) > 0

        for genre in genres:
            assert isinstance(genre, Genre)
            assert genre.genre_id is not None
            assert genre.name is not None
            assert genre.ruby is not None
            assert genre.list_url is not None

    def test_get_genres_data_structure(self, dmm_client: DMMClient) -> None:
        """Test genre data structure."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        for genre in genres:
            assert isinstance(genre.genre_id, str)
            assert isinstance(genre.name, str)
            assert isinstance(genre.ruby, str)
            assert isinstance(genre.list_url, str)
            assert len(genre.genre_id) > 0
            assert len(genre.name) > 0

    def test_get_genres_with_hits_parameter(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval with hits parameter."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=3)

        assert isinstance(genres, list)
        assert len(genres) <= 3

        for genre in genres:
            assert isinstance(genre, Genre)
            assert genre.genre_id is not None
            assert genre.name is not None
            assert genre.ruby is not None
            assert genre.list_url is not None

    def test_get_genres_with_offset(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval with offset parameter."""

        first_page: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5, offset=1)
        second_page: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5, offset=6)
        total_genres: List[Genre] = dmm_client.get_genres(
            floor_id=43, hits=10, offset=1
        )

        assert isinstance(first_page, list)
        assert isinstance(second_page, list)
        assert isinstance(total_genres, list)
        # in case second page has less items
        assert len(total_genres) == len(first_page) + len(second_page)

        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0].genre_id != second_page[0].genre_id

    def test_get_genres_with_initial_filter(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval with initial (50-sound) filter."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, initial="あ", hits=10)

        assert isinstance(genres, list)
        assert len(genres) > 0

    def test_get_genres_videoa_floor(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval for videoa floor."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        assert isinstance(genres, list)
        assert len(genres) > 0

        for genre in genres:
            assert "fanza.co.jp" in genre.list_url or "dmm.co.jp" in genre.list_url

    def test_get_genres_dvd_floor(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval for DVD floor."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=74, hits=5)

        assert isinstance(genres, list)
        assert len(genres) > 0

        for genre in genres:
            assert isinstance(genre, Genre)
            assert genre.genre_id is not None
            assert genre.name is not None
            assert genre.ruby is not None

    def test_get_genres_ebook_floor(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval for ebook floor."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=19, hits=5)

        assert isinstance(genres, list)
        assert len(genres) > 0

        for genre in genres:
            assert isinstance(genre, Genre)
            assert genre.genre_id is not None
            assert genre.name is not None
            assert genre.ruby is not None

    def test_get_genres_list_url_format(self, dmm_client: DMMClient) -> None:
        """Test genre list URL format."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        for genre in genres:
            assert genre.list_url.startswith("https://")
            assert "af_id=" in genre.list_url
            assert "ch=api" in genre.list_url

    def test_get_genres_ruby_field(self, dmm_client: DMMClient) -> None:
        """Test genre ruby (phonetic) field."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        for genre in genres:
            assert isinstance(genre.ruby, str)
            assert len(genre.ruby) > 0

    def test_get_genres_multiple_calls_consistency(self, dmm_client: DMMClient) -> None:
        """Test consistency of multiple genre calls."""

        first_call: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)
        second_call: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        assert len(first_call) == len(second_call)

        for first_genre, second_genre in zip(first_call, second_call):
            assert first_genre.genre_id == second_genre.genre_id
            assert first_genre.name == second_genre.name
            assert first_genre.ruby == second_genre.ruby

    def test_get_genres_with_large_hits(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval with large hits parameter."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=100)

        assert isinstance(genres, list)
        assert len(genres) > 0
        assert len(genres) <= 100

    def test_get_genres_different_floors(self, dmm_client: DMMClient) -> None:
        """Test genre retrieval from different floors."""

        videoa_genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)
        dvd_genres: List[Genre] = dmm_client.get_genres(floor_id=74, hits=5)

        assert isinstance(videoa_genres, list)
        assert isinstance(dvd_genres, list)
        assert len(videoa_genres) > 0
        assert len(dvd_genres) > 0

    def test_get_genres_genre_id_uniqueness(self, dmm_client: DMMClient) -> None:
        """Test that genre IDs are unique within results."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=20)

        genre_ids = [g.genre_id for g in genres]
        assert len(genre_ids) == len(set(genre_ids))

    def test_get_genres_data_completeness(self, dmm_client: DMMClient) -> None:
        """Test that all genre fields are populated."""

        genres: List[Genre] = dmm_client.get_genres(floor_id=43, hits=5)

        for genre in genres:
            assert genre.genre_id != ""
            assert genre.name != ""
            assert genre.ruby != ""
            assert genre.list_url != ""

    def test_client_context_manager_genres(self, app_id: str, aff_id: str) -> None:
        """Test client as context manager with genre retrieval."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            genres: List[Genre] = client.get_genres(floor_id=43, hits=5)
            assert isinstance(genres, list)
            assert len(genres) > 0

    def test_get_genres_error_handling_invalid_floor(
        self, dmm_client: DMMClient
    ) -> None:
        """Test error handling with invalid floor ID."""

        with pytest.raises(DMMAPIError):
            dmm_client.get_genres(floor_id=0)

    def test_get_genres_pagination(self, dmm_client: DMMClient) -> None:
        """Test genre pagination with offset."""

        page1: List[Genre] = dmm_client.get_genres(floor_id=43, hits=10, offset=1)
        page2: List[Genre] = dmm_client.get_genres(floor_id=43, hits=10, offset=11)

        assert isinstance(page1, list)
        assert isinstance(page2, list)

        if len(page1) > 0 and len(page2) > 0:
            page1_ids = {g.genre_id for g in page1}
            page2_ids = {g.genre_id for g in page2}
            assert page1_ids.isdisjoint(page2_ids)

    def test_get_genres_initial_filtering(self, dmm_client: DMMClient) -> None:
        """Test genre filtering by initial character."""

        genres_a: List[Genre] = dmm_client.get_genres(floor_id=43, initial="あ", hits=5)
        genres_ka: List[Genre] = dmm_client.get_genres(floor_id=43, initial="か", hits=5)

        assert isinstance(genres_a, list)
        assert isinstance(genres_ka, list)

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"genres": [], "count": 0}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_genres(floor_id=43)

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200, "genre": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.GenreSearchResponse.from_dict",
                side_effect=TypeError("Type mismatch"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_genres(floor_id=43)

                assert "Failed to get genres" in str(exc_info.value)
                assert "Type mismatch" in str(exc_info.value)
