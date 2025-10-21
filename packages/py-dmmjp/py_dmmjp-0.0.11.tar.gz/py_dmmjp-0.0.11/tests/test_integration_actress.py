"""Integration tests for DMM actress API functionality."""

# pylint: disable=redefined-outer-name,import-outside-toplevel,too-many-statements,too-many-public-methods
# mypy: disable-error-code=attr-defined

import datetime
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp import DMMAPIError, DMMClient
from py_dmmjp.actress import Actress


@pytest.mark.integration
class TestDMMClientWithActressIntegration:
    """Integration tests for DMM client with real API calls for actresses."""

    def test_client_authentication(self, dmm_client: DMMClient) -> None:
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_actresses_basic_request(self, dmm_client: DMMClient) -> None:
        """Test basic actress retrieval from DMM."""

        actresses: List[Actress] = dmm_client.get_actresses(hits=5)

        assert isinstance(actresses, list)
        assert len(actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.id is not None
            assert actress.name is not None

    def test_get_actresses_with_keyword_search(self, dmm_client: DMMClient) -> None:
        """Test actress search with keyword."""

        actresses: List[Actress] = dmm_client.get_actresses(keyword="あさみ", hits=3)

        assert isinstance(actresses, list)
        assert len(actresses) <= 3

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.ruby is not None

            assert "あさみ" in actress.name or "あさみ" in actress.ruby

    def test_get_actresses_with_initial_filter(self, dmm_client: DMMClient) -> None:
        """Test actress search with initial character filter."""

        actresses: List[Actress] = dmm_client.get_actresses(initial="はる", hits=5)

        assert isinstance(actresses, list)
        assert len(actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None

            assert actress.ruby.startswith("はる")

    def test_get_actresses_with_measurements_filter(
        self, dmm_client: DMMClient
    ) -> None:
        """Test actress search with bust measurement filters."""

        actresses: List[Actress] = dmm_client.get_actresses(
            gte_bust=85, lte_bust=95, hits=5
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.bust is not None

            assert 85 <= actress.bust <= 95

    def test_get_actresses_with_height_filter(self, dmm_client: DMMClient) -> None:
        """Test actress search with height filters."""

        actresses: List[Actress] = dmm_client.get_actresses(
            gte_height=155, lte_height=165, hits=5
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.height is not None
            assert 155 <= actress.height <= 165

    def test_get_actresses_with_sorting_by_name(self, dmm_client: DMMClient) -> None:
        """Test actress retrieval with different sort options."""

        actresses: List[Actress] = dmm_client.get_actresses(
            initial="ともだ", sort="name", hits=9
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 9

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.ruby is not None

            assert actress.ruby.startswith("ともだ")

        reversed_actresses: List[Actress] = dmm_client.get_actresses(
            initial="ともだ", sort="-name", hits=9
        )

        assert isinstance(reversed_actresses, list)
        assert len(reversed_actresses) <= 9

        for actress in reversed_actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.ruby is not None

        assert list(reversed(actresses)) == reversed_actresses

    def test_get_actresses_with_sorting_by_bust_measurements(
        self, dmm_client: DMMClient
    ) -> None:
        """Test actress sorting by measurements."""

        actresses: List[Actress] = dmm_client.get_actresses(
            initial="みかみ", sort="bust", hits=9
        )
        reversed_actresses: List[Actress] = dmm_client.get_actresses(
            initial="みかみ", sort="-bust", hits=9
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 9
        assert isinstance(reversed_actresses, list)
        assert len(reversed_actresses) <= 9

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.bust is not None

        assert all(
            actresses[i].bust <= actresses[i + 1].bust
            for i in range(len(actresses) - 1)
        )

        assert all(
            reversed_actresses[i].bust >= reversed_actresses[i + 1].bust
            for i in range(len(reversed_actresses) - 1)
        )

    def test_get_actresses_with_sorting_by_waist_measurements(
        self, dmm_client: DMMClient
    ) -> None:
        """Test actress sorting by measurements."""

        actresses: List[Actress] = dmm_client.get_actresses(
            initial="みかみ", sort="waist", hits=9
        )
        reversed_actresses: List[Actress] = dmm_client.get_actresses(
            initial="みかみ", sort="-waist", hits=9
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 9
        assert isinstance(reversed_actresses, list)
        assert len(reversed_actresses) <= 9

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.waist is not None

        assert all(
            actresses[i].waist <= actresses[i + 1].waist
            for i in range(len(actresses) - 1)
        )

        assert all(
            reversed_actresses[i].waist >= reversed_actresses[i + 1].waist
            for i in range(len(reversed_actresses) - 1)
        )

    def test_get_actresses_with_sorting_by_height_measurements(
        self, dmm_client: DMMClient
    ) -> None:
        """Test actress sorting by measurements."""

        actresses: List[Actress] = dmm_client.get_actresses(sort="height", hits=5)
        reversed_actresses: List[Actress] = dmm_client.get_actresses(
            sort="-height", hits=5
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 5
        assert isinstance(reversed_actresses, list)
        assert len(reversed_actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.height is not None

        assert all(
            actresses[i].height <= actresses[i + 1].height
            for i in range(len(actresses) - 1)
        )

        assert all(
            reversed_actresses[i].height >= reversed_actresses[i + 1].height
            for i in range(len(reversed_actresses) - 1)
        )

    def test_get_actresses_with_sorting_by_birthday(
        self, dmm_client: DMMClient
    ) -> None:
        """Test actress sorting by measurements."""

        actresses: List[Actress] = dmm_client.get_actresses(sort="birthday", hits=5)
        reversed_actresses: List[Actress] = dmm_client.get_actresses(
            sort="-birthday", hits=5
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 5
        assert isinstance(reversed_actresses, list)
        assert len(reversed_actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.birthday is not None
            assert isinstance(actress.birthday, str)

        assert all(
            datetime.datetime.strptime(actresses[i].birthday, "%Y-%m-%d")
            <= datetime.datetime.strptime(actresses[i + 1].birthday, "%Y-%m-%d")
            for i in range(len(actresses) - 1)
        )

        assert all(
            datetime.datetime.strptime(reversed_actresses[i].birthday, "%Y-%m-%d")
            >= datetime.datetime.strptime(
                reversed_actresses[i + 1].birthday, "%Y-%m-%d"
            )
            for i in range(len(reversed_actresses) - 1)
        )

    def test_get_actresses_with_sorting_by_id(self, dmm_client: DMMClient) -> None:
        """Test actress sorting by measurements."""

        actresses: List[Actress] = dmm_client.get_actresses(sort="id", hits=5)
        reversed_actresses: List[Actress] = dmm_client.get_actresses(sort="-id", hits=5)

        assert isinstance(actresses, list)
        assert len(actresses) <= 5
        assert isinstance(reversed_actresses, list)
        assert len(reversed_actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            assert actress.name is not None
            assert actress.id is not None

        assert all(
            actresses[i].id <= actresses[i + 1].id for i in range(len(actresses) - 1)
        )

        assert all(
            reversed_actresses[i].id >= reversed_actresses[i + 1].id
            for i in range(len(reversed_actresses) - 1)
        )

    def test_get_actresses_by_id(self, dmm_client: DMMClient) -> None:
        """Test retrieving specific actress by ID."""

        actresses: List[Actress] = dmm_client.get_actresses(actress_id=8053)

        assert isinstance(actresses, list)
        assert len(actresses) == 1

        actress: Actress = actresses[0]
        assert isinstance(actress, Actress)
        assert actress.id == 8053

    def test_actress_data_completeness(self, dmm_client: DMMClient) -> None:
        """Test that actress data contains expected fields."""

        actresses: List[Actress] = dmm_client.get_actresses(actress_id=1017139)
        assert len(actresses) == 1

        actress: Actress = actresses[0]
        assert actress.id == 1017139
        assert actress.name == "蓮実クレア"
        assert actress.ruby == "はすみくれあ"
        assert actress.bust == 86
        assert actress.cup == "F"
        assert actress.waist == 57
        assert actress.hip == 87
        assert actress.height == 158
        assert actress.birthday == "1991-12-03"
        assert actress.blood_type == "A"
        assert actress.hobby == "ベリーダンス"
        assert actress.prefectures == "神奈川県"

        assert actress.image_url is not None
        assert (
            actress.image_url.small
            == "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/hasumi_kurea.jpg"
        )
        assert (
            actress.image_url.large
            == "http://pics.dmm.co.jp/mono/actjpgs/hasumi_kurea.jpg"
        )

        assert actress.list_url is not None

    def test_actress_measurements_data(self, dmm_client: DMMClient) -> None:
        """Test actress measurement data types."""

        actresses: List[Actress] = dmm_client.get_actresses(hits=10)

        assert len(actresses) >= 1

        for actress in actresses:
            if actress.bust is not None:
                assert isinstance(actress.bust, int)
            if actress.waist is not None:
                assert isinstance(actress.waist, int)
            if actress.hip is not None:
                assert isinstance(actress.hip, int)
            if actress.height is not None:
                assert isinstance(actress.height, int)

    def test_actress_image_urls(self, dmm_client: DMMClient) -> None:
        """Test actress image URL data."""

        actresses: List[Actress] = dmm_client.get_actresses(hits=5)

        assert len(actresses) >= 1

        for actress in actresses:
            if actress.image_url is not None:
                assert (
                    actress.image_url.small is None
                    or actress.image_url.small.startswith("http")
                )
                assert (
                    actress.image_url.large is None
                    or actress.image_url.large.startswith("http")
                )

    def test_actress_list_urls(self, dmm_client: DMMClient) -> None:
        """Test actress content list URLs."""

        actresses: List[Actress] = dmm_client.get_actresses(hits=5)

        assert len(actresses) >= 1

        for actress in actresses:
            if actress.list_url is not None:
                if actress.list_url.digital is not None:
                    assert actress.list_url.digital.startswith("http")
                if actress.list_url.monthly is not None:
                    assert actress.list_url.monthly.startswith("http")
                if actress.list_url.mono is not None:
                    assert actress.list_url.mono.startswith("http")

    def test_empty_results_valid_request(self, dmm_client: DMMClient) -> None:
        """Test handling of valid requests that return no results."""

        actresses: List[Actress] = dmm_client.get_actresses(
            keyword="xyznomatchkeyword12345", hits=1
        )

        assert isinstance(actresses, list)
        assert len(actresses) == 0

    def test_pagination_with_offset(self, dmm_client: DMMClient) -> None:
        """Test pagination using offset parameter."""

        first_page: List[Actress] = dmm_client.get_actresses(hits=2, offset=1)
        second_page: List[Actress] = dmm_client.get_actresses(hits=2, offset=3)
        total_page = dmm_client.get_actresses(hits=4)

        assert len(first_page) <= 2
        assert len(second_page) <= 2
        assert len(total_page) <= 4

        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0].id != second_page[0].id

        assert list(first_page + second_page) == total_page

    def test_client_context_manager_actresses(self, app_id: str, aff_id: str) -> None:
        """Test client as context manager with actress search."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            actresses: List[Actress] = client.get_actresses(hits=1)
            assert isinstance(actresses, list)

    def test_actress_birthday_filter(self, dmm_client: DMMClient) -> None:
        """Test actress search with birthday filters."""

        actresses: List[Actress] = dmm_client.get_actresses(
            gte_birthday="1990-01-01", lte_birthday="1995-12-31", hits=5
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            if actress.birthday is not None:
                assert "1990" <= actress.birthday[:4] <= "1995"

    def test_actress_waist_hip_filters(self, dmm_client: DMMClient) -> None:
        """Test actress search with waist and hip measurement filters."""

        actresses: List[Actress] = dmm_client.get_actresses(
            gte_waist=55, lte_waist=65, gte_hip=80, lte_hip=90, hits=5
        )

        assert isinstance(actresses, list)
        assert len(actresses) <= 5

        for actress in actresses:
            assert isinstance(actress, Actress)
            if actress.waist is not None:
                assert 55 <= actress.waist <= 65
            if actress.hip is not None:
                assert 80 <= actress.hip <= 90

    def test_get_actresses_with_exceeding_offsets(self, dmm_client: DMMClient) -> None:
        """Test that providing exceeding offset"""

        actresses = dmm_client.get_actresses(offset=1000000, hits=5)
        assert isinstance(actresses, list)
        assert len(actresses) == 0

    def test_get_actresses_with_invalid_hits(self, dmm_client: DMMClient) -> None:
        """Test that providing invalid hits raises ValueError."""

        with pytest.raises(DMMAPIError):
            dmm_client.get_actresses(hits=0)

        with pytest.raises(DMMAPIError):
            dmm_client.get_actresses(hits=101)

    def test_get_actresses_with_invalid_sort(self, dmm_client: DMMClient) -> None:
        """Test that providing invalid sort raises ValueError."""

        with pytest.raises(DMMAPIError):
            dmm_client.get_actresses(sort="invalid_sort_option", hits=5)

    def test_get_actresses_with_invalid_birthday_filter(
        self, dmm_client: DMMClient
    ) -> None:
        """Test that providing invalid birthday filter raises ValueError."""

        with pytest.raises(DMMAPIError) as dmm_error:
            dmm_client.get_actresses(gte_birthday="something", hits=5)

            assert dmm_error.value.status_code == 400
            assert (
                dmm_error.value.message
                == "The gte_birthday field is not in the correct format."
            )

        with pytest.raises(DMMAPIError) as dmm_error:
            dmm_client.get_actresses(lte_birthday="invalid_format", hits=5)
            assert dmm_error.value.status_code == 400
            assert (
                dmm_error.value.message
                == "The lte_birthday field is not in the correct format."
            )

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": 200, "data": []}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_actresses(keyword="test")

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200, "actresses": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.ActressSearchResponse.from_dict",
                side_effect=KeyError("Missing key"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_actresses(keyword="test")

                assert "Failed to get actresses" in str(exc_info.value)
                assert "Missing key" in str(exc_info.value)
