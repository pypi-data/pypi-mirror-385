"""
Test cases for RequestParameters class in commons module.
"""

# pylint: disable=W0212,R0904

import unittest
from typing import Any, Dict

from py_dmmjp.commons import RequestParameters


class TestRequestParameters(unittest.TestCase):
    """Test RequestParameters class."""

    def test_basic_parameters_only_api_and_affiliate(self):
        """Test RequestParameters with only api_id and affiliate_id."""

        data = {
            "api_id": "***REDACTED_APP_ID***",
            "affiliate_id": "***REDACTED_AFF_ID***",
        }

        params = RequestParameters.from_dict(data)

        assert params.api_id == "***REDACTED_APP_ID***"
        assert params.affiliate_id == "***REDACTED_AFF_ID***"
        assert params._params == {}

    def test_complex_parameters_with_extra_fields(self):
        """Test RequestParameters with additional parameters."""

        data = {
            "api_id": "***REDACTED_APP_ID***",
            "affiliate_id": "***REDACTED_AFF_ID***",
            "site": "FANZA",
            "service": "mono",
            "floor": "dvd",
            "article": ["actress"],
            "article_id": ["1017139"],
            "hits": "1",
            "offset": "6",
        }

        params = RequestParameters.from_dict(data)

        assert params.api_id == "***REDACTED_APP_ID***"
        assert params.affiliate_id == "***REDACTED_AFF_ID***"
        assert params._params["site"] == "FANZA"
        assert params._params["service"] == "mono"
        assert params._params["floor"] == "dvd"
        assert params._params["article"] == ["actress"]
        assert params._params["article_id"] == ["1017139"]
        assert params._params["hits"] == "1"
        assert params._params["offset"] == "6"

    def test_dict_style_access_api_id(self):
        """Test dictionary-style access for api_id."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params["api_id"] == "test_api_key"

    def test_dict_style_access_affiliate_id(self):
        """Test dictionary-style access for affiliate_id."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params["affiliate_id"] == "test_affiliate"

    def test_dict_style_access_extra_params(self):
        """Test dictionary-style access for extra parameters."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "site": "FANZA",
            "hits": "10",
        }

        params = RequestParameters.from_dict(data)

        assert params["site"] == "FANZA"
        assert params["hits"] == "10"

    def test_dict_style_access_nonexistent_key(self):
        """Test dictionary-style access for non-existent key returns None."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params["nonexistent"] is None

    def test_contains_api_id(self):
        """Test __contains__ for api_id."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert "api_id" in params

    def test_contains_affiliate_id(self):
        """Test __contains__ for affiliate_id."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert "affiliate_id" in params

    def test_contains_extra_param(self):
        """Test __contains__ for extra parameters."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "site": "FANZA",
        }

        params = RequestParameters.from_dict(data)

        assert "site" in params

    def test_contains_nonexistent_key(self):
        """Test __contains__ for non-existent key."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert "nonexistent" not in params

    def test_get_method_api_id(self):
        """Test get method for api_id."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params.get("api_id") == "test_api_key"

    def test_get_method_affiliate_id(self):
        """Test get method for affiliate_id."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params.get("affiliate_id") == "test_affiliate"

    def test_get_method_extra_param(self):
        """Test get method for extra parameters."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "floor": "dvd",
        }

        params = RequestParameters.from_dict(data)

        assert params.get("floor") == "dvd"

    def test_get_method_with_default(self):
        """Test get method with default value."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params.get("nonexistent", "default_value") == "default_value"

    def test_get_method_without_default(self):
        """Test get method without default value returns None."""

        data = {"api_id": "test_api_key", "affiliate_id": "test_affiliate"}

        params = RequestParameters.from_dict(data)

        assert params.get("nonexistent") is None

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dictionary."""

        data: Dict[str, Any] = {}
        params = RequestParameters.from_dict(data)

        assert params.api_id == ""
        assert params.affiliate_id == ""
        assert params._params == {}

    def test_from_dict_with_missing_api_id(self):
        """Test from_dict with missing api_id."""

        data = {"affiliate_id": "test_affiliate", "site": "FANZA"}

        params = RequestParameters.from_dict(data)

        assert params.api_id == ""
        assert params.affiliate_id == "test_affiliate"
        assert params._params["site"] == "FANZA"

    def test_from_dict_with_missing_affiliate_id(self):
        """Test from_dict with missing affiliate_id."""

        data = {"api_id": "test_api_key", "service": "digital"}

        params = RequestParameters.from_dict(data)

        assert params.api_id == "test_api_key"
        assert params.affiliate_id == ""
        assert params._params["service"] == "digital"

    def test_parameters_with_array_values(self):
        """Test parameters with array values."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "article": ["actress", "genre"],
            "article_id": ["1001", "2002", "3003"],
        }

        params = RequestParameters.from_dict(data)

        assert params._params["article"] == ["actress", "genre"]
        assert params._params["article_id"] == ["1001", "2002", "3003"]
        assert len(params._params["article_id"]) == 3

    def test_parameters_with_numeric_string_values(self):
        """Test parameters with numeric string values."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "hits": "100",
            "offset": "50",
            "floor_id": "43",
        }

        params = RequestParameters.from_dict(data)

        assert params._params["hits"] == "100"
        assert params._params["offset"] == "50"
        assert params._params["floor_id"] == "43"

    def test_parameters_isolation(self):
        """Test that _params doesn't include api_id and affiliate_id."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "site": "FANZA",
            "service": "digital",
        }

        params = RequestParameters.from_dict(data)

        assert "api_id" not in params._params
        assert "affiliate_id" not in params._params
        assert "site" in params._params
        assert "service" in params._params

    def test_direct_instantiation(self):
        """Test direct instantiation of RequestParameters."""

        params = RequestParameters(
            api_id="direct_api", affiliate_id="direct_aff", _params={"key": "value"}
        )

        assert params.api_id == "direct_api"
        assert params.affiliate_id == "direct_aff"
        assert params._params["key"] == "value"

    def test_direct_instantiation_without_params(self):
        """Test direct instantiation without _params."""

        params = RequestParameters(api_id="direct_api", affiliate_id="direct_aff")

        assert params.api_id == "direct_api"
        assert params.affiliate_id == "direct_aff"
        assert params._params == {}

    def test_multiple_parameter_types(self):
        """Test parameters with various data types."""

        data = {
            "api_id": "test_api_key",
            "affiliate_id": "test_affiliate",
            "string_param": "text",
            "list_param": ["item1", "item2"],
            "numeric_string": "123",
            "boolean_string": "true",
        }

        params = RequestParameters.from_dict(data)

        assert params._params["string_param"] == "text"
        assert params._params["list_param"] == ["item1", "item2"]
        assert params._params["numeric_string"] == "123"
        assert params._params["boolean_string"] == "true"

    def test_real_floor_api_response(self):
        """Test with real Floor API request parameters."""

        data = {
            "api_id": "***REDACTED_APP_ID***",
            "affiliate_id": "***REDACTED_AFF_ID***",
        }

        params = RequestParameters.from_dict(data)

        assert params.api_id == "***REDACTED_APP_ID***"
        assert params.affiliate_id == "***REDACTED_AFF_ID***"
        assert len(params._params) == 0

    def test_real_product_api_response(self):
        """Test with real Product API request parameters."""

        data = {
            "api_id": "***REDACTED_APP_ID***",
            "affiliate_id": "***REDACTED_AFF_ID***",
            "site": "FANZA",
            "service": "mono",
            "floor": "dvd",
            "article": ["actress"],
            "article_id": ["1017139"],
            "hits": "1",
            "offset": "6",
        }

        params = RequestParameters.from_dict(data)

        assert params.api_id == "***REDACTED_APP_ID***"
        assert params.affiliate_id == "***REDACTED_AFF_ID***"
        assert params["site"] == "FANZA"
        assert params["service"] == "mono"
        assert params["floor"] == "dvd"
        assert params["article"] == ["actress"]
        assert params["article_id"] == ["1017139"]
        assert params["hits"] == "1"
        assert params["offset"] == "6"

    def test_get_all_parameters_via_dict_access(self):
        """Test accessing all parameters including api_id and affiliate_id."""

        data = {
            "api_id": "key123",
            "affiliate_id": "aff456",
            "param1": "value1",
            "param2": "value2",
        }

        params = RequestParameters.from_dict(data)

        assert params["api_id"] == "key123"
        assert params["affiliate_id"] == "aff456"
        assert params["param1"] == "value1"
        assert params["param2"] == "value2"

    def test_contains_with_multiple_params(self):
        """Test __contains__ with multiple parameters."""

        data = {
            "api_id": "key",
            "affiliate_id": "aff",
            "site": "FANZA",
            "service": "digital",
            "floor": "videoa",
        }

        params = RequestParameters.from_dict(data)

        assert "api_id" in params
        assert "affiliate_id" in params
        assert "site" in params
        assert "service" in params
        assert "floor" in params
        assert "nonexistent" not in params


if __name__ == "__main__":
    unittest.main()
