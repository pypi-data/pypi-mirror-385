"""
Test series data models with FANZA DVD floor data.
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from typing import Any, Dict

import pytest

from py_dmmjp.series import Series, SeriesSearchResponse, SeriesSearchResult

from .series_test_base import (
    SeriesSearchResponseTestBase,
    SeriesSearchResultTestBase,
    SeriesTestBase,
)


class TestSeriesDVD(SeriesTestBase):
    """Test series with FANZA DVD floor data."""

    @pytest.fixture
    def series_data(self) -> Dict[str, Any]:
        return {
            "series_id": "215651",
            "name": "100万の賞金を目指して街行く男子を逆ナンパしてSEXしちゃいました！！",
            "ruby": "100まんのしょうきんめざしてまちゆくだんしをぎゃくなんぱしてせっくすしちゃいました",
            "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D215651%2F&af_id=***REDACTED_AFF_ID***&ch=api",
        }

    def test_series_basic_fields(self, series_data: Dict[str, Any]) -> None:
        series = Series.from_dict(series_data)

        assert series.series_id == "215651"
        assert series.name == "100万の賞金を目指して街行く男子を逆ナンパしてSEXしちゃいました！！"
        assert series.ruby == "100まんのしょうきんめざしてまちゆくだんしをぎゃくなんぱしてせっくすしちゃいました"
        assert "fanza.co.jp" in series.list_url

    def test_series_from_dict(self, series_data: Dict[str, Any]) -> None:
        series = Series.from_dict(series_data)

        assert isinstance(series, Series)
        assert series.series_id == series_data["series_id"]
        assert series.name == series_data["name"]
        assert series.ruby == series_data["ruby"]
        assert series.list_url == series_data["list_url"]

    def test_series_id_type(self, series_data: Dict[str, Any]) -> None:
        series = Series.from_dict(series_data)

        assert isinstance(series.series_id, str)

    def test_series_name_validation(self, series_data: Dict[str, Any]) -> None:
        series = Series.from_dict(series_data)

        assert series.name is not None
        assert len(series.name) > 0
        assert isinstance(series.name, str)

    def test_series_ruby_validation(self, series_data: Dict[str, Any]) -> None:
        series = Series.from_dict(series_data)

        assert series.ruby is not None
        assert len(series.ruby) > 0
        assert isinstance(series.ruby, str)

    def test_series_list_url_validation(self, series_data: Dict[str, Any]) -> None:
        series = Series.from_dict(series_data)

        assert series.list_url is not None
        assert len(series.list_url) > 0
        assert isinstance(series.list_url, str)
        assert series.list_url.startswith("https://")

    def test_series_empty_data_handling(self, series_data: Dict[str, Any]) -> None:
        empty_data: Dict[str, Any] = {}
        series = Series.from_dict(empty_data)

        assert series.series_id == ""
        assert series.name == ""
        assert series.ruby == ""
        assert series.list_url == ""

    def test_series_default_values(self, series_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"series_id": "215651"}
        series = Series.from_dict(partial_data)

        assert series.series_id == "215651"
        assert series.name == ""
        assert series.ruby == ""
        assert series.list_url == ""


class TestSeriesSearchResultDVD(SeriesSearchResultTestBase):
    """Test series search result with FANZA DVD floor data."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        return {
            "status": "200",
            "result_count": 5,
            "total_count": "40808",
            "first_position": 1,
            "site_name": "FANZA（アダルト）",
            "site_code": "FANZA",
            "service_name": "通販",
            "service_code": "mono",
            "floor_id": "74",
            "floor_name": "DVD",
            "floor_code": "dvd",
            "series": [
                {
                    "series_id": "215651",
                    "name": "100万の賞金を目指して街行く男子を逆ナンパしてSEXしちゃいました！！",
                    "ruby": "100まんのしょうきんめざしてまちゆくだんしをぎゃくなんぱしてせっくすしちゃいました",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D215651%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "series_id": "216262",
                    "name": "10日間オナ禁＆ハメ禁で…足腰ガクブル超絶痙攣中出しトランスFUCK",
                    "ruby": "10かかんおなきんはめきんであしこしがくぶるちょうぜつけいれんなかだしとらんすふぁっく",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D216262%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "series_id": "215693",
                    "name": "10周年記念 看護師2作品同時収録",
                    "ruby": "10しゅうねんきねんかんごし2さくひんどうじしゅうろく",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D215693%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "series_id": "214747",
                    "name": "1人旅の温泉旅館でアダルトビデオの撮影にバッタリ遭遇！",
                    "ruby": "1りたびのおんせんりょかんであだるとびでおのさつえいにばったりそうぐう",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D214747%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
                {
                    "series_id": "4064794",
                    "name": "2泊3日の社員旅行中、居残りを命じられた僕は、憧れの受付嬢と二人きり…。",
                    "ruby": "2はく3かのしゃいんりょこうちゅういのこりをめいじられたぼくはあこがれのうけつけじょうとふたりきり",
                    "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D4064794%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                },
            ],
        }

    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert result.status == 200
        assert result.result_count == 5
        assert result.total_count == 40808
        assert result.first_position == 1

    def test_result_site_fields(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert result.site_name == "FANZA（アダルト）"
        assert result.site_code == "FANZA"

    def test_result_service_fields(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert result.service_name == "通販"
        assert result.service_code == "mono"

    def test_result_floor_fields(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert result.floor_id == "74"
        assert result.floor_name == "DVD"
        assert result.floor_code == "dvd"

    def test_result_series_list(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert isinstance(result.series_list, list)
        assert len(result.series_list) == 5

    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert isinstance(result, SeriesSearchResult)
        assert result.status == int(result_data["status"])
        assert result.result_count == result_data["result_count"]
        assert len(result.series_list) == len(result_data["series"])

    def test_result_nested_series(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        for series in result.series_list:
            assert isinstance(series, Series)
            assert series.series_id is not None
            assert series.name is not None
            assert series.ruby is not None
            assert series.list_url is not None

    def test_result_empty_series(self, result_data: Dict[str, Any]) -> None:
        empty_result_data: Dict[str, Any] = {
            "status": "200",
            "result_count": 0,
            "total_count": "0",
            "first_position": 1,
            "site_name": "Test",
            "site_code": "test",
            "service_name": "Test",
            "service_code": "test",
            "floor_id": "1",
            "floor_name": "Test",
            "floor_code": "test",
            "series": [],
        }
        result = SeriesSearchResult.from_dict(empty_result_data)

        assert isinstance(result.series_list, list)
        assert len(result.series_list) == 0

    def test_result_multiple_series(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert len(result.series_list) == 5
        assert result.series_list[0].series_id == "215651"
        assert result.series_list[1].series_id == "216262"
        assert result.series_list[2].series_id == "215693"
        assert result.series_list[3].series_id == "214747"
        assert result.series_list[4].series_id == "4064794"

    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert isinstance(result.status, int)
        assert result.status == 200

    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert isinstance(result.result_count, int)
        assert isinstance(result.total_count, int)
        assert isinstance(result.first_position, int)
        assert result.result_count == 5
        assert result.total_count == 40808
        assert result.first_position == 1

    def test_result_series_type(self, result_data: Dict[str, Any]) -> None:
        result = SeriesSearchResult.from_dict(result_data)

        assert isinstance(result.series_list, list)
        for series in result.series_list:
            assert isinstance(series, Series)

    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"status": "200"}
        result = SeriesSearchResult.from_dict(partial_data)

        assert result.status == 200
        assert result.result_count == 0
        assert result.total_count == 0
        assert result.first_position == 1
        assert isinstance(result.series_list, list)
        assert len(result.series_list) == 0


class TestSeriesSearchResponseDVD(SeriesSearchResponseTestBase):
    """Test series search response with FANZA DVD floor data."""

    @pytest.fixture
    def response_data(self) -> Dict[str, Any]:
        return {
            "request": {
                "parameters": {
                    "api_id": "test",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                    "floor_id": "74",
                    "hits": "5",
                }
            },
            "result": {
                "status": "200",
                "result_count": 5,
                "total_count": "40808",
                "first_position": 1,
                "site_name": "FANZA（アダルト）",
                "site_code": "FANZA",
                "service_name": "通販",
                "service_code": "mono",
                "floor_id": "74",
                "floor_name": "DVD",
                "floor_code": "dvd",
                "series": [
                    {
                        "series_id": "215651",
                        "name": "100万の賞金を目指して街行く男子を逆ナンパしてSEXしちゃいました！！",
                        "ruby": "100まんのしょうきんめざしてまちゆくだんしをぎゃくなんぱしてせっくすしちゃいました",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D215651%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                    },
                    {
                        "series_id": "216262",
                        "name": "10日間オナ禁＆ハメ禁で…足腰ガクブル超絶痙攣中出しトランスFUCK",
                        "ruby": "10かかんおなきんはめきんであしこしがくぶるちょうぜつけいれんなかだしとらんすふぁっく",
                        "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D216262%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                    },
                ],
            },
        }

    def test_response_structure(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert hasattr(response, "request")
        assert hasattr(response, "result")
        assert hasattr(response, "_raw_response")

    def test_response_from_dict(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert isinstance(response, SeriesSearchResponse)
        assert response.request is not None
        assert response.result is not None

    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert response.request is not None
        assert hasattr(response.request, "parameters")

    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert isinstance(response.result, SeriesSearchResult)
        assert response.result.status == 200
        assert len(response.result.series_list) == 2

    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert response.raw_response is not None
        assert isinstance(response.raw_response, dict)
        assert "request" in response.raw_response
        assert "result" in response.raw_response

    def test_response_series_property(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert isinstance(response.series, list)
        assert len(response.series) == 2
        for series in response.series:
            assert isinstance(series, Series)

    def test_response_series_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert isinstance(response.series_count, int)
        assert response.series_count == 5

    def test_response_total_series_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert isinstance(response.total_series, int)
        assert response.total_series == 40808

    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert isinstance(response.status, int)
        assert response.status == 200

    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        response = SeriesSearchResponse.from_dict(response_data)

        assert response.series == response.result.series_list
        assert response.series_count == response.result.result_count
        assert response.total_series == response.result.total_count
        assert response.status == response.result.status
