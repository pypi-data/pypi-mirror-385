"""
Test for actress search functionality with missing fields.
"""

# pylint: disable=duplicate-code,too-many-public-methods,line-too-long
# mypy: disable-error-code="no-untyped-def"

from typing import Any, Dict

import pytest

from py_dmmjp.actress import (
    Actress,
    ActressImageURL,
    ActressListURL,
    ActressSearchResponse,
    ActressSearchResult,
)
from tests.actress_test_base import (
    ActressSearchResponseTestBase,
    ActressSearchResultTestBase,
    ActressTestBase,
)


class TestActressWithMissingFields(ActressTestBase):
    """Test implementation for actress functionality with missing fields."""

    @pytest.fixture
    def actress_data(self) -> Dict[str, Any]:
        """Mock actress data for testing - actress item with some missing fields."""

        return {
            "id": "1018785",
            "name": "吉川あいみ",
            "ruby": "よしかわあいみ",
            "bust": "95",
            "cup": "H",
            "waist": "58",
            "hip": "85",
            "height": "152",
            "birthday": None,
            "blood_type": None,
            "hobby": None,
            "prefectures": "神奈川県",
            "imageURL": {
                "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/yosikawa_aimi.jpg",
                "large": "http://pics.dmm.co.jp/mono/actjpgs/yosikawa_aimi.jpg",
            },
            "listURL": {
                "digital": "https://al.fanza.co.jp/?"
                "lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                "monthly": "https://al.fanza.co.jp/?"
                "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                "mono": "https://al.fanza.co.jp/?"
                "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
            },
        }

    def test_actress_basic_fields(self, actress_data: Dict[str, Any]) -> None:
        """Test basic actress fields (id, name, ruby)."""

        actress = Actress.from_dict(actress_data)

        assert actress.id == 1018785
        assert actress.name == "吉川あいみ"
        assert actress.ruby == "よしかわあいみ"

    def test_actress_measurements(self, actress_data: Dict[str, Any]) -> None:
        """Test measurement fields (bust, waist, hip, height, cup)."""

        actress = Actress.from_dict(actress_data)

        assert actress.bust == 95
        assert actress.waist == 58
        assert actress.hip == 85
        assert actress.height == 152
        assert actress.cup == "H"

    def test_actress_personal_info(self, actress_data: Dict[str, Any]) -> None:
        """Test personal information (birthday, blood_type, hobby, prefectures)."""

        actress = Actress.from_dict(actress_data)

        assert actress.birthday is None
        assert actress.blood_type is None
        assert actress.hobby is None
        assert actress.prefectures == "神奈川県"

    def test_actress_image_urls(self, actress_data: Dict[str, Any]) -> None:
        """Test image URL parsing (small and large images)."""

        actress = Actress.from_dict(actress_data)

        assert actress.image_url is not None
        assert (
            actress.image_url.small
            == "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/yosikawa_aimi.jpg"
        )
        assert (
            actress.image_url.large
            == "http://pics.dmm.co.jp/mono/actjpgs/yosikawa_aimi.jpg"
        )

    def test_actress_list_urls(self, actress_data: Dict[str, Any]) -> None:
        """Test list URL parsing (digital, monthly, mono)."""

        actress = Actress.from_dict(actress_data)

        assert actress.list_url is not None
        assert "video.dmm.co.jp" in actress.list_url.digital
        assert "actress%3D1018785" in actress.list_url.digital
        assert "monthly" in actress.list_url.monthly
        assert "mono" in actress.list_url.mono

    def test_actress_from_dict(self, actress_data: Dict[str, Any]) -> None:
        """Test creating actress from dictionary."""

        actress = Actress.from_dict(actress_data)

        assert isinstance(actress, Actress)
        assert actress.id == 1018785

    def test_actress_safe_int_conversion(self, actress_data: Dict[str, Any]) -> None:
        """Test safe integer conversion for measurements."""

        actress = Actress.from_dict(actress_data)

        assert actress.bust == 95
        assert actress.waist == 58
        assert actress.hip == 85
        assert actress.height == 152

    def test_actress_optional_fields(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of optional/null fields."""

        actress = Actress.from_dict(actress_data)

        assert actress.birthday is None
        assert actress.blood_type is None
        assert actress.hobby is None
        assert actress.prefectures is not None

    def test_actress_nested_objects(self, actress_data: Dict[str, Any]) -> None:
        """Test nested objects (image_url, list_url)."""

        actress = Actress.from_dict(actress_data)

        assert isinstance(actress.image_url, ActressImageURL)
        assert isinstance(actress.list_url, ActressListURL)

    def test_actress_image_url_from_dict(self, actress_data: Dict[str, Any]) -> None:
        """Test ActressImageURL creation from dictionary."""

        image_data = actress_data["imageURL"]
        image_url = ActressImageURL.from_dict(image_data)

        assert isinstance(image_url, ActressImageURL)
        assert "yosikawa_aimi.jpg" in image_url.small
        assert "yosikawa_aimi.jpg" in image_url.large

    def test_actress_list_url_from_dict(self, actress_data: Dict[str, Any]) -> None:
        """Test ActressListURL creation from dictionary."""

        list_data = actress_data["listURL"]
        list_url = ActressListURL.from_dict(list_data)

        assert isinstance(list_url, ActressListURL)
        assert "fanza.co.jp" in list_url.digital
        assert "fanza.co.jp" in list_url.monthly
        assert "fanza.co.jp" in list_url.mono

    def test_actress_empty_data_handling(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of empty or missing data."""

        empty_data = {"id": "1", "name": "Test"}
        actress = Actress.from_dict(empty_data)

        assert actress.id == 1
        assert actress.name == "Test"
        assert actress.image_url is None
        assert actress.list_url is None

    def test_actress_string_measurements(self, actress_data: Dict[str, Any]) -> None:
        """Test conversion of string measurements to integers."""

        test_data = {"id": "1", "name": "Test", "bust": "90", "height": "165"}
        actress = Actress.from_dict(test_data)

        assert actress.bust == 90
        assert actress.height == 165

    def test_actress_invalid_data_handling(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of invalid data types."""

        test_data = {
            "id": "1",
            "name": "Test",
            "bust": "invalid",
            "height": "not_a_number",
        }
        actress = Actress.from_dict(test_data)

        assert actress.bust is None
        assert actress.height is None

    def test_actress_birthday_format(self, actress_data: Dict[str, Any]) -> None:
        """Test birthday format handling."""

        actress = Actress.from_dict(actress_data)

        assert actress.birthday is None

        test_data = {"id": "1", "name": "Test", "birthday": "1990-01-01"}
        actress = Actress.from_dict(test_data)
        assert actress.birthday == "1990-01-01"

    def test_actress_cup_size_validation(self, actress_data: Dict[str, Any]) -> None:
        """Test cup size field validation."""

        actress = Actress.from_dict(actress_data)

        assert actress.cup == "H"

        test_data = {"id": "1", "name": "Test", "cup": "C"}
        actress = Actress.from_dict(test_data)
        assert actress.cup == "C"

    def test_actress_prefecture_data(self, actress_data: Dict[str, Any]) -> None:
        """Test prefecture/birthplace data."""

        actress = Actress.from_dict(actress_data)

        assert actress.prefectures == "神奈川県"

        test_data = {"id": "1", "name": "Test", "prefectures": "東京都"}
        actress = Actress.from_dict(test_data)
        assert actress.prefectures == "東京都"

    def test_actress_hobby_data(self, actress_data: Dict[str, Any]) -> None:
        """Test hobby/interests data."""

        actress = Actress.from_dict(actress_data)

        assert actress.hobby is None

        test_data = {"id": "1", "name": "Test", "hobby": "読書、映画鑑賞"}
        actress = Actress.from_dict(test_data)
        assert actress.hobby == "読書、映画鑑賞"

    def test_actress_blood_type_data(self, actress_data: Dict[str, Any]) -> None:
        """Test blood type data."""

        actress = Actress.from_dict(actress_data)

        assert actress.blood_type is None

        test_data = {"id": "1", "name": "Test", "blood_type": "B"}
        actress = Actress.from_dict(test_data)
        assert actress.blood_type == "B"

    def test_actress_url_formatting(self, actress_data: Dict[str, Any]) -> None:
        """Test URL formatting in image and list URLs."""

        actress = Actress.from_dict(actress_data)

        assert actress.image_url.small.startswith("http://")
        assert actress.list_url.digital.startswith("https://")

    def test_actress_mixed_data_validation(self, actress_data: Dict[str, Any]) -> None:
        """Test validation of actress data with mixed populated and null fields."""

        actress = Actress.from_dict(actress_data)

        assert actress.id == 1018785
        assert actress.name == "吉川あいみ"
        assert actress.ruby == "よしかわあいみ"

        assert actress.bust == 95
        assert actress.cup == "H"
        assert actress.waist == 58
        assert actress.hip == 85
        assert actress.height == 152

        assert actress.birthday is None
        assert actress.blood_type is None
        assert actress.hobby is None
        assert actress.prefectures == "神奈川県"

        assert actress.image_url is not None
        assert actress.list_url is not None

    def test_actress_null_field_handling(self, actress_data: Dict[str, Any]) -> None:
        """Test that null fields are properly handled without errors."""

        actress = Actress.from_dict(actress_data)

        assert actress.birthday is None
        assert actress.blood_type is None
        assert actress.hobby is None

    def test_actress_partial_personal_info(self, actress_data: Dict[str, Any]) -> None:
        """Test handling of partially populated personal information."""

        actress = Actress.from_dict(actress_data)

        assert actress.prefectures is not None
        assert actress.birthday is None
        assert actress.blood_type is None
        assert actress.hobby is None


class TestActressSearchResultMissingFields(ActressSearchResultTestBase):
    """Test implementation for actress search result with missing fields."""

    @pytest.fixture
    def result_data(self) -> Dict[str, Any]:
        """Mock actress search result data."""

        return {
            "status": "200",
            "result_count": 1,
            "total_count": "1",
            "first_position": 1,
            "actress": [
                {
                    "id": "1018785",
                    "name": "吉川あいみ",
                    "ruby": "よしかわあいみ",
                    "bust": "95",
                    "cup": "H",
                    "waist": "58",
                    "hip": "85",
                    "height": "152",
                    "birthday": None,
                    "blood_type": None,
                    "hobby": None,
                    "prefectures": "神奈川県",
                    "imageURL": {
                        "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/yosikawa_aimi.jpg",
                        "large": "http://pics.dmm.co.jp/mono/actjpgs/yosikawa_aimi.jpg",
                    },
                    "listURL": {
                        "digital": "https://al.fanza.co.jp/?"
                        "lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                        "monthly": "https://al.fanza.co.jp/?"
                        "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                        "mono": "https://al.fanza.co.jp/?"
                        "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                    },
                }
            ],
        }

    def test_result_basic_fields(self, result_data: Dict[str, Any]) -> None:
        """Test basic result fields (status, counts, positions)."""

        result = ActressSearchResult.from_dict(result_data)

        assert result.status == 200
        assert result.result_count == 1
        assert result.total_count == 1
        assert result.first_position == 1

    def test_result_from_dict(self, result_data: Dict[str, Any]) -> None:
        """Test creating result from dictionary."""

        result = ActressSearchResult.from_dict(result_data)

        assert isinstance(result, ActressSearchResult)
        assert result.status == 200

    def test_result_actress_list(self, result_data: Dict[str, Any]) -> None:
        """Test actress list parsing."""

        result = ActressSearchResult.from_dict(result_data)

        assert len(result.actresses) == 1
        assert result.actresses[0].id == 1018785

    def test_result_nested_actresses(self, result_data: Dict[str, Any]) -> None:
        """Test nested actress objects."""

        result = ActressSearchResult.from_dict(result_data)

        assert isinstance(result.actresses[0], Actress)
        assert result.actresses[0].name == "吉川あいみ"

    def test_result_empty_actresses(self, result_data: Dict[str, Any]) -> None:
        """Test result with empty actress list."""

        empty_data = {
            "status": "200",
            "result_count": 0,
            "total_count": "0",
            "first_position": 1,
            "actress": [],
        }
        result = ActressSearchResult.from_dict(empty_data)

        assert len(result.actresses) == 0
        assert result.result_count == 0

    def test_result_multiple_actresses(self, result_data: Dict[str, Any]) -> None:
        """Test result with multiple actresses."""

        result = ActressSearchResult.from_dict(result_data)

        assert result.result_count == 1
        assert len(result.actresses) == 1

    def test_result_status_code(self, result_data: Dict[str, Any]) -> None:
        """Test status code validation."""

        result = ActressSearchResult.from_dict(result_data)

        assert result.status == 200
        assert isinstance(result.status, int)

    def test_result_count_fields(self, result_data: Dict[str, Any]) -> None:
        """Test count fields (result_count, total_count, first_position)."""

        result = ActressSearchResult.from_dict(result_data)

        assert result.result_count == 1
        assert result.total_count == 1
        assert result.first_position == 1

    def test_result_actress_type(self, result_data: Dict[str, Any]) -> None:
        """Test actress field type is list."""

        result = ActressSearchResult.from_dict(result_data)

        assert isinstance(result.actresses, list)

    def test_result_default_values(self, result_data: Dict[str, Any]) -> None:
        """Test default values for missing fields."""

        minimal_data = {"status": "200"}
        result = ActressSearchResult.from_dict(minimal_data)

        assert result.status == 200
        assert result.result_count == 0
        assert result.total_count == 0
        assert result.first_position == 1


class TestActressSearchResponseMissingFields(ActressSearchResponseTestBase):
    """Test implementation for actress search response with missing fields."""

    @pytest.fixture
    def response_data(self) -> Dict[str, Any]:
        """Mock actress search response data."""

        return {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                    "actress_id": "1018785",
                }
            },
            "result": {
                "status": "200",
                "result_count": 1,
                "total_count": "1",
                "first_position": 1,
                "actress": [
                    {
                        "id": "1018785",
                        "name": "吉川あいみ",
                        "ruby": "よしかわあいみ",
                        "bust": "95",
                        "cup": "H",
                        "waist": "58",
                        "hip": "85",
                        "height": "152",
                        "birthday": None,
                        "blood_type": None,
                        "hobby": None,
                        "prefectures": "神奈川県",
                        "imageURL": {
                            "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/yosikawa_aimi.jpg",
                            "large": "http://pics.dmm.co.jp/mono/actjpgs/yosikawa_aimi.jpg",
                        },
                        "listURL": {
                            "digital": "https://al.fanza.co.jp/?"
                            "lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                            "monthly": "https://al.fanza.co.jp/?"
                            "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                            "mono": "https://al.fanza.co.jp/?"
                            "lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1018785%2F&af_id=***REDACTED_AFF_ID***&ch=api",
                        },
                    }
                ],
            },
        }

    def test_response_structure(self, response_data: Dict[str, Any]) -> None:
        """Test response structure (request, result)."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.request is not None
        assert response.result is not None

    def test_response_from_dict(self, response_data: Dict[str, Any]) -> None:
        """Test creating response from dictionary."""

        response = ActressSearchResponse.from_dict(response_data)

        assert isinstance(response, ActressSearchResponse)

    def test_response_request_object(self, response_data: Dict[str, Any]) -> None:
        """Test request object in response."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.request is not None
        assert hasattr(response.request, "parameters")

    def test_response_result_object(self, response_data: Dict[str, Any]) -> None:
        """Test result object in response."""

        response = ActressSearchResponse.from_dict(response_data)

        assert isinstance(response.result, ActressSearchResult)
        assert response.result.status == 200

    def test_response_raw_response_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test raw_response property access."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.raw_response is not None
        assert "request" in response.raw_response
        assert "result" in response.raw_response

    def test_response_actresses_property(self, response_data: Dict[str, Any]) -> None:
        """Test actresses property accessor."""

        response = ActressSearchResponse.from_dict(response_data)

        assert len(response.actresses) == 1
        assert response.actresses[0].name == "吉川あいみ"

    def test_response_actress_count_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test actress_count property accessor."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.actress_count == 1

    def test_response_total_actresses_property(
        self, response_data: Dict[str, Any]
    ) -> None:
        """Test total_actresses property accessor."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.total_actresses == 1

    def test_response_status_property(self, response_data: Dict[str, Any]) -> None:
        """Test status property accessor."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.status == 200

    def test_response_property_consistency(self, response_data: Dict[str, Any]) -> None:
        """Test consistency between properties and result fields."""

        response = ActressSearchResponse.from_dict(response_data)

        assert response.actress_count == response.result.result_count
        assert response.total_actresses == response.result.total_count
        assert response.status == response.result.status
        assert response.actresses == response.result.actresses
