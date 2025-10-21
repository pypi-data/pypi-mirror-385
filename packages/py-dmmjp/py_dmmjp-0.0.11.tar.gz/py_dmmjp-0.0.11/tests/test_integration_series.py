"""
Integration tests for DMM series API functionality.
"""

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp import DMMClient
from py_dmmjp.exceptions import DMMAPIError
from py_dmmjp.series import Series


@pytest.mark.integration
class TestDMMClientWithSeriesIntegration:
    """Integration tests for DMM client with real API calls for series."""

    def test_client_authentication(self, dmm_client: DMMClient) -> None:
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_series_basic_request(self, dmm_client: DMMClient) -> None:
        """Test basic series retrieval from DMM."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        assert isinstance(series, list)
        assert len(series) > 0

        for s in series:
            assert isinstance(s, Series)
            assert s.series_id is not None
            assert s.name is not None
            assert s.ruby is not None
            assert s.list_url is not None

    def test_get_series_with_floor_id(self, dmm_client: DMMClient) -> None:
        """Test series retrieval with specific floor ID."""

        series: List[Series] = dmm_client.get_series(floor_id=74, hits=10)

        assert isinstance(series, list)
        assert len(series) > 0

        for s in series:
            assert isinstance(s, Series)
            assert s.series_id is not None
            assert s.name is not None
            assert s.ruby is not None
            assert s.list_url is not None

    def test_get_series_data_structure(self, dmm_client: DMMClient) -> None:
        """Test series data structure."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        for s in series:
            assert isinstance(s.series_id, str)
            assert isinstance(s.name, str)
            assert isinstance(s.ruby, str)
            assert isinstance(s.list_url, str)
            assert len(s.series_id) > 0
            assert len(s.name) > 0

    def test_get_series_with_hits_parameter(self, dmm_client: DMMClient) -> None:
        """Test series retrieval with hits parameter."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=3)

        assert isinstance(series, list)
        assert len(series) <= 3

        for s in series:
            assert isinstance(s, Series)
            assert s.series_id is not None
            assert s.name is not None
            assert s.ruby is not None
            assert s.list_url is not None

    def test_get_series_with_offset(self, dmm_client: DMMClient) -> None:
        """Test series retrieval with offset parameter."""

        first_page: List[Series] = dmm_client.get_series(floor_id=43, hits=5, offset=1)
        second_page: List[Series] = dmm_client.get_series(floor_id=43, hits=5, offset=6)
        total_series: List[Series] = dmm_client.get_series(
            floor_id=43, hits=10, offset=1
        )

        assert isinstance(first_page, list)
        assert isinstance(second_page, list)
        assert isinstance(total_series, list)
        assert len(total_series) == len(first_page) + len(second_page)

        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0].series_id != second_page[0].series_id

    def test_get_series_with_initial_filter(self, dmm_client: DMMClient) -> None:
        """Test series retrieval with initial (50-sound) filter."""

        series: List[Series] = dmm_client.get_series(floor_id=43, initial="お", hits=10)

        assert isinstance(series, list)
        assert len(series) > 0

    def test_get_series_videoa_floor(self, dmm_client: DMMClient) -> None:
        """Test series retrieval for videoa floor."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        assert isinstance(series, list)
        assert len(series) > 0

        for s in series:
            assert "fanza.co.jp" in s.list_url or "dmm.co.jp" in s.list_url

    def test_get_series_dvd_floor(self, dmm_client: DMMClient) -> None:
        """Test series retrieval for DVD floor."""

        series: List[Series] = dmm_client.get_series(floor_id=74, hits=5)

        assert isinstance(series, list)
        assert len(series) > 0

        for s in series:
            assert isinstance(s, Series)
            assert s.series_id is not None
            assert s.name is not None
            assert s.ruby is not None

    def test_get_series_book_floor(self, dmm_client: DMMClient) -> None:
        """Test series retrieval for book floor."""

        series: List[Series] = dmm_client.get_series(floor_id=27, hits=5)

        assert isinstance(series, list)
        assert len(series) > 0

        for s in series:
            assert isinstance(s, Series)
            assert s.series_id is not None
            assert s.name is not None
            assert s.ruby is not None

    def test_get_series_list_url_format(self, dmm_client: DMMClient) -> None:
        """Test series list URL format."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        for s in series:
            assert s.list_url.startswith("https://")
            assert "af_id=" in s.list_url
            assert "ch=api" in s.list_url

    def test_get_series_ruby_field(self, dmm_client: DMMClient) -> None:
        """Test series ruby (phonetic) field."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        for s in series:
            assert isinstance(s.ruby, str)
            assert len(s.ruby) > 0

    def test_get_series_multiple_calls_consistency(self, dmm_client: DMMClient) -> None:
        """Test consistency of multiple series calls."""

        first_call: List[Series] = dmm_client.get_series(floor_id=43, hits=5)
        second_call: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        assert len(first_call) == len(second_call)

        for first_s, second_s in zip(first_call, second_call):
            assert first_s.series_id == second_s.series_id
            assert first_s.name == second_s.name
            assert first_s.ruby == second_s.ruby

    def test_get_series_with_large_hits(self, dmm_client: DMMClient) -> None:
        """Test series retrieval with large hits parameter."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=100)

        assert isinstance(series, list)
        assert len(series) > 0
        assert len(series) <= 100

    def test_get_series_different_floors(self, dmm_client: DMMClient) -> None:
        """Test series retrieval from different floors."""

        videoa_series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)
        dvd_series: List[Series] = dmm_client.get_series(floor_id=74, hits=5)

        assert isinstance(videoa_series, list)
        assert isinstance(dvd_series, list)
        assert len(videoa_series) > 0
        assert len(dvd_series) > 0

    def test_get_series_series_id_uniqueness(self, dmm_client: DMMClient) -> None:
        """Test that series IDs are unique within results."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=20)

        series_ids = [s.series_id for s in series]
        assert len(series_ids) == len(set(series_ids))

    def test_get_series_data_completeness(self, dmm_client: DMMClient) -> None:
        """Test that all series fields are populated."""

        series: List[Series] = dmm_client.get_series(floor_id=43, hits=5)

        for s in series:
            assert s.series_id != ""
            assert s.name != ""
            assert s.ruby != ""
            assert s.list_url != ""

    def test_client_context_manager_series(self, app_id: str, aff_id: str) -> None:
        """Test client as context manager with series retrieval."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            series: List[Series] = client.get_series(floor_id=43, hits=5)
            assert isinstance(series, list)
            assert len(series) > 0

    def test_get_series_error_handling_invalid_floor(
        self, dmm_client: DMMClient
    ) -> None:
        """Test error handling with invalid floor ID."""

        with pytest.raises(DMMAPIError):
            dmm_client.get_series(floor_id=0)

    def test_get_series_pagination(self, dmm_client: DMMClient) -> None:
        """Test series pagination with offset."""

        page1: List[Series] = dmm_client.get_series(floor_id=43, hits=10, offset=1)
        page2: List[Series] = dmm_client.get_series(floor_id=43, hits=10, offset=11)

        assert isinstance(page1, list)
        assert isinstance(page2, list)

        if len(page1) > 0 and len(page2) > 0:
            page1_ids = {s.series_id for s in page1}
            page2_ids = {s.series_id for s in page2}
            assert page1_ids.isdisjoint(page2_ids)

    def test_get_series_initial_filtering(self, dmm_client: DMMClient) -> None:
        """Test series filtering by initial character."""

        series_o: List[Series] = dmm_client.get_series(floor_id=43, initial="お", hits=5)
        series_a: List[Series] = dmm_client.get_series(floor_id=43, initial="あ", hits=5)

        assert isinstance(series_o, list)
        assert isinstance(series_a, list)

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"series": [], "count": 0}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_series(floor_id=27)

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200, "series": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.SeriesSearchResponse.from_dict",
                side_effect=IndexError("Index out of range"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_series(floor_id=27)

                assert "Failed to get series" in str(exc_info.value)
                assert "Index out of range" in str(exc_info.value)
