"""
Test author data models with FANZA figure/goods floor data.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.author import Author, AuthorSearchResponse, AuthorSearchResult

from .author_test_base import (
    AuthorSearchResponseTestBase,
    AuthorSearchResultTestBase,
    AuthorTestBase,
)


class TestAuthorFigure(AuthorTestBase):
    """Test author with FANZA figure/goods floor data."""

    @pytest.fixture
    def author_data(self) -> Dict[str, Any]:
        return {
            "author_id": "259140",
            "name": "愛上陸",
            "ruby": "あいうえおか",
            "list_url": "https://al.dmm.com/?"
            "lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Ffigure%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D259140%2F&af_id=***REDACTED_AFF_ID***&ch=api",
        }

    def test_author_basic_fields(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert author.author_id == "259140"
        assert author.name == "愛上陸"
        assert author.ruby == "あいうえおか"
        assert "dmm.com" in author.list_url

    def test_author_from_dict(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert isinstance(author, Author)
        assert author.author_id == author_data["author_id"]
        assert author.name == author_data["name"]
        assert author.ruby == author_data["ruby"]
        assert author.list_url == author_data["list_url"]

    def test_author_id_type(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert isinstance(author.author_id, str)

    def test_author_name_validation(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert author.name is not None
        assert len(author.name) > 0
        assert isinstance(author.name, str)

    def test_author_ruby_validation(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert author.ruby is not None
        assert len(author.ruby) > 0
        assert isinstance(author.ruby, str)

    def test_author_list_url_validation(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert author.list_url is not None
        assert len(author.list_url) > 0
        assert isinstance(author.list_url, str)
        assert author.list_url.startswith("https://")

    def test_author_another_name_field(self, author_data: Dict[str, Any]) -> None:
        author = Author.from_dict(author_data)

        assert isinstance(author.another_name, str)

        author_with_alias = Author.from_dict(
            {
                "author_id": "332206",
                "name": "INAZUMA.",
                "ruby": "いなずま",
                "another_name": "稲妻",
            }
        )
        assert author_with_alias.another_name == "稲妻"

    def test_author_empty_data_handling(self, author_data: Dict[str, Any]) -> None:
        empty_data: Dict[str, Any] = {}
        author = Author.from_dict(empty_data)

        assert author.author_id == ""
        assert author.name == ""
        assert author.ruby == ""
        assert author.list_url == ""
        assert author.another_name == ""

    def test_author_default_values(self, author_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"author_id": "259140"}
        author = Author.from_dict(partial_data)

        assert author.author_id == "259140"
        assert author.name == ""
        assert author.ruby == ""
        assert author.list_url == ""
        assert author.another_name == ""


class TestAuthorSearchResultFigure(AuthorSearchResultTestBase):
    """Test author search result with FANZA figure/goods floor data."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        return {
            "status": "200",
            "result_count": 10,
            "total_count": "111",
            "first_position": 1,
            "site_name": "FANZA（アダルト）",
            "site_code": "FANZA",
            "service_name": "通販",
            "service_code": "mono",
            "floor_id": "94",
            "floor_name": "フィギュア・グッズ",
            "floor_code": "figure",
            "author": [
                {
                    "author_id": "259140",
                    "name": "愛上陸",
                    "ruby": "あいうえおか",
                },
                {
                    "author_id": "237059",
                    "name": "葵渚",
                    "ruby": "あおいなぎさ",
                },
                {
                    "author_id": "252434",
                    "name": "あかつき聖",
                    "ruby": "あかつきひじり",
                },
                {
                    "author_id": "332083",
                    "name": "アゴビッチ姉さん",
                    "ruby": "あごびっちねえさん",
                },
                {
                    "author_id": "50017",
                    "name": "あずまゆき",
                    "ruby": "あずまゆき",
                },
                {
                    "author_id": "26924",
                    "name": "綾瀬はづき",
                    "ruby": "あやせはづき",
                },
                {
                    "author_id": "253547",
                    "name": "あるぷ",
                    "ruby": "あるぷ",
                },
                {
                    "author_id": "332206",
                    "name": "INAZUMA.",
                    "ruby": "いなずま",
                },
                {
                    "author_id": "244277",
                    "name": "犬江しんすけ",
                    "ruby": "いぬえしんすけ",
                },
                {
                    "author_id": "255723",
                    "name": "印度カリー",
                    "ruby": "いんどかりー",
                },
            ],
        }

    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert result.status == 200
        assert result.result_count == 10
        assert result.total_count == 111
        assert result.first_position == 1

    def test_result_site_fields(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert result.site_name == "FANZA（アダルト）"
        assert result.site_code == "FANZA"

    def test_result_service_fields(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert result.service_name == "通販"
        assert result.service_code == "mono"

    def test_result_floor_fields(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert result.floor_id == "94"
        assert result.floor_name == "フィギュア・グッズ"
        assert result.floor_code == "figure"

    def test_result_author_list(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert isinstance(result.author_list, list)
        assert len(result.author_list) == 10

    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert isinstance(result, AuthorSearchResult)
        assert result.status == int(result_data["status"])
        assert result.result_count == result_data["result_count"]
        assert len(result.author_list) == len(result_data["author"])

    def test_result_nested_authors(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        for author in result.author_list:
            assert isinstance(author, Author)
            assert author.author_id is not None
            assert author.name is not None
            assert author.ruby is not None

    def test_result_empty_authors(self, result_data: Dict[str, Any]) -> None:
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
            "author": [],
        }
        result = AuthorSearchResult.from_dict(empty_result_data)

        assert isinstance(result.author_list, list)
        assert len(result.author_list) == 0

    def test_result_multiple_authors(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert len(result.author_list) == 10
        assert result.author_list[0].author_id == "259140"
        assert result.author_list[1].author_id == "237059"
        assert result.author_list[2].author_id == "252434"
        assert result.author_list[3].author_id == "332083"

    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert isinstance(result.status, int)
        assert result.status == 200

    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert isinstance(result.result_count, int)
        assert isinstance(result.total_count, int)
        assert isinstance(result.first_position, int)
        assert result.result_count == 10
        assert result.total_count == 111
        assert result.first_position == 1

    def test_result_author_type(self, result_data: Dict[str, Any]) -> None:
        result = AuthorSearchResult.from_dict(result_data)

        assert isinstance(result.author_list, list)
        for author in result.author_list:
            assert isinstance(author, Author)

    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"status": "200"}
        result = AuthorSearchResult.from_dict(partial_data)

        assert result.status == 200
        assert result.result_count == 0
        assert result.total_count == 0
        assert result.first_position == 1
        assert isinstance(result.author_list, list)
        assert len(result.author_list) == 0


class TestAuthorSearchResponseFigure(AuthorSearchResponseTestBase):
    """Test author search response with FANZA figure/goods floor data."""

    @pytest.fixture
    def response_data(self) -> Dict[str, Any]:
        return {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                    "floor_id": "94",
                    "hits": "10",
                }
            },
            "result": {
                "status": "200",
                "result_count": 10,
                "total_count": "111",
                "first_position": 1,
                "site_name": "FANZA（アダルト）",
                "site_code": "FANZA",
                "service_name": "通販",
                "service_code": "mono",
                "floor_id": "94",
                "floor_name": "フィギュア・グッズ",
                "floor_code": "figure",
                "author": [
                    {
                        "author_id": "259140",
                        "name": "愛上陸",
                        "ruby": "あいうえおか",
                    },
                    {
                        "author_id": "237059",
                        "name": "葵渚",
                        "ruby": "あおいなぎさ",
                    },
                ],
            },
        }

    def test_response_structure(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert hasattr(response, "request")
        assert hasattr(response, "result")
        assert hasattr(response, "_raw_response")

    def test_response_from_dict(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert isinstance(response, AuthorSearchResponse)
        assert response.request is not None
        assert response.result is not None

    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert response.request is not None
        assert hasattr(response.request, "parameters")

    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert isinstance(response.result, AuthorSearchResult)
        assert response.result.status == 200
        assert len(response.result.author_list) == 2

    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert response.raw_response is not None
        assert isinstance(response.raw_response, dict)
        assert "request" in response.raw_response
        assert "result" in response.raw_response

    def test_response_authors_property(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert isinstance(response.authors, list)
        assert len(response.authors) == 2
        for author in response.authors:
            assert isinstance(author, Author)

    def test_response_author_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert isinstance(response.author_count, int)
        assert response.author_count == 10

    def test_response_total_authors_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert isinstance(response.total_authors, int)
        assert response.total_authors == 111

    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert isinstance(response.status, int)
        assert response.status == 200

    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        response = AuthorSearchResponse.from_dict(response_data)

        assert response.authors == response.result.author_list
        assert response.author_count == response.result.result_count
        assert response.total_authors == response.result.total_count
        assert response.status == response.result.status
