"""
Tests for maker data models using DVD floor (floor_id=74) data.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.maker import Maker, MakerSearchResponse, MakerSearchResult

from .maker_test_base import (
    MakerSearchResponseTestBase,
    MakerSearchResultTestBase,
    MakerTestBase,
)


class TestMakerDVD(MakerTestBase):
    """Test Maker class with DVD floor data."""

    @pytest.fixture
    def maker_data(self) -> Dict[str, Any]:
        return {
            "maker_id": "45614",
            "name": "108 gay studio",
            "ruby": "108げいすたじお",
            "list_url": "https://al.fanza.co.jp/?"
            "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D45614%2F&af_id=***REDACTED_AFF_ID***&ch=api",
        }

    def test_maker_basic_fields(self, maker_data: Dict[str, Any]) -> None:
        maker = Maker.from_dict(maker_data)
        assert maker.maker_id == "45614"
        assert maker.name == "108 gay studio"
        assert maker.ruby == "108げいすたじお"
        assert "maker%2Fid%3D45614" in maker.list_url

    def test_maker_from_dict(self, maker_data: Dict[str, Any]) -> None:
        maker = Maker.from_dict(maker_data)
        assert isinstance(maker, Maker)
        assert maker.maker_id == maker_data["maker_id"]

    def test_maker_id_type(self, maker_data: Dict[str, Any]) -> None:
        maker = Maker.from_dict(maker_data)
        assert isinstance(maker.maker_id, str)

    def test_maker_name_validation(self, maker_data: Dict[str, Any]) -> None:
        maker = Maker.from_dict(maker_data)
        assert maker.name == "108 gay studio"
        assert len(maker.name) > 0

    def test_maker_ruby_validation(self, maker_data: Dict[str, Any]) -> None:
        maker = Maker.from_dict(maker_data)
        assert maker.ruby == "108げいすたじお"
        assert len(maker.ruby) > 0

    def test_maker_list_url_validation(self, maker_data: Dict[str, Any]) -> None:
        maker = Maker.from_dict(maker_data)
        assert maker.list_url.startswith("https://")
        assert "af_id=" in maker.list_url

    def test_maker_empty_data_handling(self, maker_data: Dict[str, Any]) -> None:
        empty_data: Dict[str, Any] = {}
        maker = Maker.from_dict(empty_data)
        assert maker.maker_id == ""
        assert maker.name == ""

    def test_maker_default_values(self, maker_data: Dict[str, Any]) -> None:
        partial_data = {"maker_id": "45614"}
        maker = Maker.from_dict(partial_data)
        assert maker.maker_id == "45614"
        assert maker.name == ""


class TestMakerSearchResultDVD(MakerSearchResultTestBase):
    """Test MakerSearchResult class with DVD floor data."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        return {
            "status": "200",
            "result_count": 5,
            "total_count": "5550",
            "first_position": 1,
            "site_name": "FANZA（アダルト）",
            "site_code": "FANZA",
            "service_name": "通販",
            "service_code": "mono",
            "floor_id": "74",
            "floor_name": "DVD",
            "floor_code": "dvd",
            "maker": [
                {
                    "maker_id": "45614",
                    "name": "108 gay studio",
                    "ruby": "108げいすたじお",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D45614%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "maker_id": "5786",
                    "name": "1Z1",
                    "ruby": "1ぜっと1",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D5786%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "maker_id": "46167",
                    "name": "31co.",
                    "ruby": "31しーおーどっと",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D46167%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "maker_id": "4338",
                    "name": "3年2組",
                    "ruby": "3ねん2くみ",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D4338%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "maker_id": "45527",
                    "name": "4Beats",
                    "ruby": "4びーつ",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp"
                    "%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D45527%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
            ],
        }

    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert result.status == 200
        assert result.result_count == 5
        assert result.total_count == 5550
        assert result.first_position == 1

    def test_result_site_fields(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert result.site_name == "FANZA（アダルト）"
        assert result.site_code == "FANZA"

    def test_result_service_fields(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert result.service_name == "通販"
        assert result.service_code == "mono"

    def test_result_floor_fields(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert result.floor_id == "74"
        assert result.floor_name == "DVD"
        assert result.floor_code == "dvd"

    def test_result_maker_list(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert len(result.maker_list) == 5
        assert all(isinstance(maker, Maker) for maker in result.maker_list)

    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert isinstance(result, MakerSearchResult)
        assert result.floor_code == "dvd"

    def test_result_nested_makers(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        first_maker = result.maker_list[0]
        assert first_maker.maker_id == "45614"
        assert first_maker.name == "108 gay studio"

    def test_result_empty_makers(self, result_data: Dict[str, Any]) -> None:
        empty_data = result_data.copy()
        empty_data["maker"] = []
        result = MakerSearchResult.from_dict(empty_data)
        assert len(result.maker_list) == 0

    def test_result_multiple_makers(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert len(result.maker_list) == 5
        maker_ids = [maker.maker_id for maker in result.maker_list]
        assert "45614" in maker_ids
        assert "5786" in maker_ids

    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert result.status == 200

    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert result.result_count == 5
        assert result.total_count == 5550
        assert result.first_position == 1

    def test_result_maker_type(self, result_data: Dict[str, Any]) -> None:
        result = MakerSearchResult.from_dict(result_data)
        assert isinstance(result.maker_list, list)

    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        minimal_data: Dict[str, Any] = {}
        result = MakerSearchResult.from_dict(minimal_data)
        assert result.status == 200
        assert result.result_count == 0


class TestMakerSearchResponseDVD(MakerSearchResponseTestBase):
    """Test MakerSearchResponse class with DVD floor data."""

    @pytest.fixture
    def response_data(self) -> Dict[str, Any]:
        return {
            "request": {
                "parameters": {
                    "api_id": "my_api_id",
                    "affiliate_id": "my_affiliate_id",
                    "floor_id": "74",
                    "hits": "5",
                }
            },
            "result": {
                "status": "200",
                "result_count": 5,
                "total_count": "5550",
                "first_position": 1,
                "site_name": "FANZA（アダルト）",
                "site_code": "FANZA",
                "service_name": "通販",
                "service_code": "mono",
                "floor_id": "74",
                "floor_name": "DVD",
                "floor_code": "dvd",
                "maker": [
                    {
                        "maker_id": "45614",
                        "name": "108 gay studio",
                        "ruby": "108げいすたじお",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2F"
                        "www.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D45614%2F&af_id=my_affiliate_id&ch=api",
                    },
                    {
                        "maker_id": "5786",
                        "name": "1Z1",
                        "ruby": "1ぜっと1",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2F"
                        "www.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dmaker%2Fid%3D5786%2F&af_id=my_affiliate_id&ch=api",
                    },
                ],
            },
        }

    def test_response_structure(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert hasattr(response, "request")
        assert hasattr(response, "result")

    def test_response_from_dict(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert isinstance(response, MakerSearchResponse)

    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert response.request is not None
        assert hasattr(response.request, "parameters")

    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert isinstance(response.result, MakerSearchResult)
        assert response.result.floor_code == "dvd"

    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert response.raw_response is not None
        assert "request" in response.raw_response

    def test_response_makers_property(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert len(response.makers) == 2
        assert all(isinstance(maker, Maker) for maker in response.makers)

    def test_response_maker_count_property(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert response.maker_count == 5

    def test_response_total_makers_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert response.total_makers == 5550

    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert response.status == 200

    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        response = MakerSearchResponse.from_dict(response_data)
        assert response.maker_count == response.result.result_count
        assert response.total_makers == response.result.total_count
        assert response.status == response.result.status
