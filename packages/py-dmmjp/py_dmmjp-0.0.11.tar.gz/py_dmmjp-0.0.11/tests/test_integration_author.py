"""
Integration tests for DMM author API functionality.
"""

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp import DMMClient
from py_dmmjp.author import Author
from py_dmmjp.exceptions import DMMAPIError


@pytest.mark.integration
class TestDMMClientWithAuthorIntegration:
    """Integration tests for DMM client with real API calls for authors."""

    def test_client_authentication(self, dmm_client: DMMClient) -> None:
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_authors_basic_request(self, dmm_client: DMMClient) -> None:
        """Test basic author retrieval from DMM."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)

        assert isinstance(authors, list)
        assert len(authors) > 0

        for author in authors:
            assert isinstance(author, Author)
            assert author.author_id is not None
            assert author.name is not None
            assert author.ruby is not None
            assert author.list_url is not None

    def test_get_authors_with_floor_id(self, dmm_client: DMMClient) -> None:
        """Test author retrieval with specific floor ID."""

        authors: List[Author] = dmm_client.get_authors(floor_id=94, hits=10)

        assert isinstance(authors, list)
        assert len(authors) > 0

        for author in authors:
            assert isinstance(author, Author)
            assert author.author_id is not None
            assert author.name is not None
            assert author.ruby is not None
            assert author.list_url is not None

    def test_get_authors_data_structure(self, dmm_client: DMMClient) -> None:
        """Test author data structure."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)

        for author in authors:
            assert isinstance(author.author_id, str)
            assert isinstance(author.name, str)
            assert isinstance(author.ruby, str)
            assert isinstance(author.list_url, str)
            assert len(author.author_id) > 0
            assert len(author.name) > 0

    def test_get_authors_with_hits_parameter(self, dmm_client: DMMClient) -> None:
        """Test author retrieval with hits parameter."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=3)

        assert isinstance(authors, list)
        assert len(authors) <= 3

        for author in authors:
            assert isinstance(author, Author)
            assert author.author_id is not None
            assert author.name is not None
            assert author.ruby is not None
            assert author.list_url is not None

    def test_get_authors_with_offset(self, dmm_client: DMMClient) -> None:
        """Test author retrieval with offset parameter."""

        first_page: List[Author] = dmm_client.get_authors(floor_id=27, hits=5, offset=1)
        second_page: List[Author] = dmm_client.get_authors(
            floor_id=27, hits=5, offset=6
        )
        total_authors: List[Author] = dmm_client.get_authors(
            floor_id=27, hits=10, offset=1
        )

        assert isinstance(first_page, list)
        assert isinstance(second_page, list)
        assert isinstance(total_authors, list)
        assert len(total_authors) == len(first_page) + len(second_page)

        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0].author_id != second_page[0].author_id

    def test_get_authors_with_initial_filter(self, dmm_client: DMMClient) -> None:
        """Test author retrieval with initial (phonetic) filter."""

        authors: List[Author] = dmm_client.get_authors(
            floor_id=27, initial="う", hits=10
        )

        assert isinstance(authors, list)
        assert len(authors) > 0

    def test_get_authors_dvd_floor(self, dmm_client: DMMClient) -> None:
        """Test author retrieval for DVD floor."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)

        assert isinstance(authors, list)
        assert len(authors) > 0

    def test_get_authors_figure_floor(self, dmm_client: DMMClient) -> None:
        """Test author retrieval for figure/goods floor."""

        authors: List[Author] = dmm_client.get_authors(floor_id=94, hits=5)

        assert isinstance(authors, list)
        assert len(authors) > 0

        for author in authors:
            assert isinstance(author, Author)
            assert author.author_id is not None
            assert author.name is not None
            assert author.ruby is not None

    def test_get_authors_book_floor(self, dmm_client: DMMClient) -> None:
        """Test author retrieval for book floor."""

        authors: List[Author] = dmm_client.get_authors(floor_id=27, hits=5)

        assert isinstance(authors, list)
        assert len(authors) > 0

        for author in authors:
            assert isinstance(author, Author)
            assert author.author_id is not None
            assert author.name is not None
            assert author.ruby is not None

    def test_get_authors_ruby_field(self, dmm_client: DMMClient) -> None:
        """Test author ruby (phonetic) field."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)

        for author in authors:
            assert isinstance(author.ruby, str)
            assert len(author.ruby) > 0

    def test_get_authors_multiple_calls_consistency(
        self, dmm_client: DMMClient
    ) -> None:
        """Test consistency of multiple author calls."""

        first_call: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)
        second_call: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)

        assert len(first_call) == len(second_call)

        for first_author, second_author in zip(first_call, second_call):
            assert first_author.author_id == second_author.author_id
            assert first_author.name == second_author.name
            assert first_author.ruby == second_author.ruby

    def test_get_authors_with_large_hits(self, dmm_client: DMMClient) -> None:
        """Test author retrieval with large hits parameter."""

        authors: List[Author] = dmm_client.get_authors(floor_id=27, hits=100)

        assert isinstance(authors, list)
        assert len(authors) > 0
        assert len(authors) <= 100

    def test_get_authors_different_floors(self, dmm_client: DMMClient) -> None:
        """Test author retrieval from different floors."""

        dvd_authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)
        figure_authors: List[Author] = dmm_client.get_authors(floor_id=94, hits=5)

        assert isinstance(dvd_authors, list)
        assert isinstance(figure_authors, list)
        assert len(dvd_authors) > 0
        assert len(figure_authors) > 0

    def test_get_authors_author_id_uniqueness(self, dmm_client: DMMClient) -> None:
        """Test that author IDs are unique within results."""

        authors: List[Author] = dmm_client.get_authors(floor_id=27, hits=20)

        author_ids = [author.author_id for author in authors]
        assert len(author_ids) == len(set(author_ids))

    def test_get_authors_data_completeness(self, dmm_client: DMMClient) -> None:
        """Test that all author fields are populated."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=5)

        for author in authors:
            assert author.author_id != ""
            assert author.name != ""
            assert author.ruby != ""

    def test_client_context_manager_authors(self, app_id: str, aff_id: str) -> None:
        """Test client as context manager with author retrieval."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            authors: List[Author] = client.get_authors(floor_id=74, hits=5)
            assert isinstance(authors, list)
            assert len(authors) > 0

    def test_get_authors_error_handling_invalid_floor(
        self, dmm_client: DMMClient
    ) -> None:
        """Test error handling with invalid floor ID."""

        with pytest.raises(DMMAPIError):
            dmm_client.get_authors(floor_id=0)

    def test_get_authors_pagination(self, dmm_client: DMMClient) -> None:
        """Test author pagination with offset."""

        page1: List[Author] = dmm_client.get_authors(floor_id=27, hits=10, offset=1)
        page2: List[Author] = dmm_client.get_authors(floor_id=27, hits=10, offset=11)

        assert isinstance(page1, list)
        assert isinstance(page2, list)

        if len(page1) > 0 and len(page2) > 0:
            page1_ids = {author.author_id for author in page1}
            page2_ids = {author.author_id for author in page2}
            assert page1_ids.isdisjoint(page2_ids)

    def test_get_authors_initial_filtering(self, dmm_client: DMMClient) -> None:
        """Test author filtering by initial phonetic character."""

        authors_u: List[Author] = dmm_client.get_authors(
            floor_id=27, initial="う", hits=5
        )
        authors_a: List[Author] = dmm_client.get_authors(
            floor_id=27, initial="あ", hits=5
        )

        assert isinstance(authors_u, list)
        assert isinstance(authors_a, list)

    def test_get_authors_another_name_field(self, dmm_client: DMMClient) -> None:
        """Test author another_name field handling."""

        authors: List[Author] = dmm_client.get_authors(floor_id=74, hits=20)

        assert isinstance(authors, list)
        for author in authors:
            assert isinstance(author.another_name, str)

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"authors": [], "total": 0}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_authors(floor_id=27)

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200, "author": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.AuthorSearchResponse.from_dict",
                side_effect=Exception("Unexpected parsing error"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_authors(floor_id=27)

                assert "Failed to get authors" in str(exc_info.value)
                assert "Unexpected parsing error" in str(exc_info.value)
