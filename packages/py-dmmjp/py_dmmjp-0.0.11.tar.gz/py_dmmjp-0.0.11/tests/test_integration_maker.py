"""
Integration tests for DMM maker API functionality.
"""

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp import DMMClient
from py_dmmjp.exceptions import DMMAPIError
from py_dmmjp.maker import Maker


@pytest.mark.integration
class TestDMMClientWithMakerIntegration:
    """Integration tests for DMM client with real API calls for makers."""

    def test_client_authentication(self, dmm_client: DMMClient) -> None:
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_makers_basic_request(self, dmm_client: DMMClient) -> None:
        """Test basic maker retrieval from DMM."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        assert isinstance(makers, list)
        assert len(makers) > 0

        for maker in makers:
            assert isinstance(maker, Maker)
            assert maker.maker_id is not None
            assert maker.name is not None
            assert maker.ruby is not None
            assert maker.list_url is not None

    def test_get_makers_with_floor_id(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval with specific floor ID."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=74, hits=10)

        assert isinstance(makers, list)
        assert len(makers) > 0

        for maker in makers:
            assert isinstance(maker, Maker)
            assert maker.maker_id is not None
            assert maker.name is not None
            assert maker.ruby is not None
            assert maker.list_url is not None

    def test_get_makers_data_structure(self, dmm_client: DMMClient) -> None:
        """Test maker data structure."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        for maker in makers:
            assert isinstance(maker.maker_id, str)
            assert isinstance(maker.name, str)
            assert isinstance(maker.ruby, str)
            assert isinstance(maker.list_url, str)
            assert len(maker.maker_id) > 0
            assert len(maker.name) > 0

    def test_get_makers_with_hits_parameter(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval with hits parameter."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=3)

        assert isinstance(makers, list)
        assert len(makers) <= 3

        for maker in makers:
            assert isinstance(maker, Maker)
            assert maker.maker_id is not None
            assert maker.name is not None
            assert maker.ruby is not None
            assert maker.list_url is not None

    def test_get_makers_with_offset(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval with offset parameter."""

        first_page: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5, offset=1)
        second_page: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5, offset=6)
        total_makers: List[Maker] = dmm_client.get_makers(
            floor_id=43, hits=10, offset=1
        )

        assert isinstance(first_page, list)
        assert isinstance(second_page, list)
        assert isinstance(total_makers, list)
        assert len(total_makers) == len(first_page) + len(second_page)

        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0].maker_id != second_page[0].maker_id

    def test_get_makers_with_initial_filter(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval with initial (50-sound) filter."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, initial="あ", hits=10)

        assert isinstance(makers, list)
        assert len(makers) > 0

    def test_get_makers_videoa_floor(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval for videoa floor."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        assert isinstance(makers, list)
        assert len(makers) > 0

        for maker in makers:
            assert "fanza.co.jp" in maker.list_url or "dmm.co.jp" in maker.list_url

    def test_get_makers_dvd_floor(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval for DVD floor."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=74, hits=5)

        assert isinstance(makers, list)
        assert len(makers) > 0

        for maker in makers:
            assert isinstance(maker, Maker)
            assert maker.maker_id is not None
            assert maker.name is not None
            assert maker.ruby is not None

    def test_get_makers_book_floor(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval for book floor."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=27, hits=5)

        assert isinstance(makers, list)
        assert len(makers) > 0

        for maker in makers:
            assert isinstance(maker, Maker)
            assert maker.maker_id is not None
            assert maker.name is not None
            assert maker.ruby is not None

    def test_get_makers_list_url_format(self, dmm_client: DMMClient) -> None:
        """Test maker list URL format."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        for maker in makers:
            assert maker.list_url.startswith("https://")
            assert "af_id=" in maker.list_url
            assert "ch=api" in maker.list_url

    def test_get_makers_ruby_field(self, dmm_client: DMMClient) -> None:
        """Test maker ruby (phonetic) field."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        for maker in makers:
            assert isinstance(maker.ruby, str)
            assert len(maker.ruby) > 0

    def test_get_makers_multiple_calls_consistency(self, dmm_client: DMMClient) -> None:
        """Test consistency of multiple maker calls."""

        first_call: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)
        second_call: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        assert len(first_call) == len(second_call)

        for first_maker, second_maker in zip(first_call, second_call):
            assert first_maker.maker_id == second_maker.maker_id
            assert first_maker.name == second_maker.name
            assert first_maker.ruby == second_maker.ruby

    def test_get_makers_with_large_hits(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval with large hits parameter."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=100)

        assert isinstance(makers, list)
        assert len(makers) > 0
        assert len(makers) <= 100

    def test_get_makers_different_floors(self, dmm_client: DMMClient) -> None:
        """Test maker retrieval from different floors."""

        videoa_makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)
        dvd_makers: List[Maker] = dmm_client.get_makers(floor_id=74, hits=5)

        assert isinstance(videoa_makers, list)
        assert isinstance(dvd_makers, list)
        assert len(videoa_makers) > 0
        assert len(dvd_makers) > 0

    def test_get_makers_maker_id_uniqueness(self, dmm_client: DMMClient) -> None:
        """Test that maker IDs are unique within results."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=20)

        maker_ids = [maker.maker_id for maker in makers]
        assert len(maker_ids) == len(set(maker_ids))

    def test_get_makers_data_completeness(self, dmm_client: DMMClient) -> None:
        """Test that all maker fields are populated."""

        makers: List[Maker] = dmm_client.get_makers(floor_id=43, hits=5)

        for maker in makers:
            assert maker.maker_id != ""
            assert maker.name != ""
            assert maker.ruby != ""
            assert maker.list_url != ""

    def test_client_context_manager_makers(self, app_id: str, aff_id: str) -> None:
        """Test client as context manager with maker retrieval."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            makers: List[Maker] = client.get_makers(floor_id=43, hits=5)
            assert isinstance(makers, list)
            assert len(makers) > 0

    def test_get_makers_error_handling_invalid_floor(
        self, dmm_client: DMMClient
    ) -> None:
        """Test error handling with invalid floor ID."""

        with pytest.raises(DMMAPIError):
            dmm_client.get_makers(floor_id=0)

    def test_get_makers_pagination(self, dmm_client: DMMClient) -> None:
        """Test maker pagination with offset."""

        page1: List[Maker] = dmm_client.get_makers(floor_id=43, hits=10, offset=1)
        page2: List[Maker] = dmm_client.get_makers(floor_id=43, hits=10, offset=11)

        assert isinstance(page1, list)
        assert isinstance(page2, list)

        if len(page1) > 0 and len(page2) > 0:
            page1_ids = {maker.maker_id for maker in page1}
            page2_ids = {maker.maker_id for maker in page2}
            assert page1_ids.isdisjoint(page2_ids)

    def test_get_makers_initial_filtering(self, dmm_client: DMMClient) -> None:
        """Test maker filtering by initial character."""

        makers_a: List[Maker] = dmm_client.get_makers(floor_id=43, initial="あ", hits=5)
        makers_m: List[Maker] = dmm_client.get_makers(floor_id=43, initial="む", hits=5)

        assert isinstance(makers_a, list)
        assert isinstance(makers_m, list)

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"makers": [], "total": 0}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_makers(floor_id=43)

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200, "maker": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.MakerSearchResponse.from_dict",
                side_effect=RuntimeError("Processing error"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_makers(floor_id=43)

                assert "Failed to get makers" in str(exc_info.value)
                assert "Processing error" in str(exc_info.value)
