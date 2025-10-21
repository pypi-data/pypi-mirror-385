"""
Test cases for JSON parsing errors in DMMClient.
"""

# pylint: disable=protected-access

import unittest
from unittest.mock import MagicMock, patch

from py_dmmjp.client import DMMClient
from py_dmmjp.exceptions import DMMAPIError


class TestDMMClientJSONErrors(unittest.TestCase):
    """Test JSON parsing errors in DMMClient API methods."""

    def setUp(self):
        """Set up test fixtures."""

        self.client = DMMClient(api_key="test_key", affiliate_id="test_affiliate")

    def tearDown(self):
        """Clean up resources."""

        self.client.close()

    def test_invalid_json_on_get_products(self):
        """Test invalid JSON response on get_products raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Not valid JSON {{{{"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_products(site="FANZA")

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_invalid_json_on_get_actresses(self):
        """Test invalid JSON response on get_actresses raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON syntax"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_actresses(keyword="test")

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_invalid_json_on_get_floors(self):
        """Test invalid JSON response on get_floors raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{'invalid': 'json with single quotes'}"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_floors()

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_invalid_json_on_get_genres(self):
        """Test invalid JSON response on get_genres raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "[incomplete array"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_genres(floor_id=43)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_invalid_json_on_get_makers(self):
        """Test invalid JSON response on get_makers raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"unclosed": "object"'
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_makers(floor_id=43)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_invalid_json_on_get_series(self):
        """Test invalid JSON response on get_series raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "null,null,null"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_series(floor_id=27)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_invalid_json_on_get_authors(self):
        """Test invalid JSON response on get_authors raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "undefined"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_authors(floor_id=27)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_empty_response_text(self):
        """Test empty response text raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_products(site="FANZA")

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_malformed_unicode_in_json(self):
        """Test malformed Unicode in JSON raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"name": "\\uXXXX"}'
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_actresses()

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_json_with_trailing_comma(self):
        """Test JSON with trailing comma raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"status": 200,}}'
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_floors()

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_json_with_comments(self):
        """Test JSON with comments (invalid JSON) raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": /* comment */ {"status": 200}}'
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_genres(floor_id=43)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_exception_chaining_preserved(self):
        """Test that original ValueError is preserved in exception chain."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON"
        mock_response.raise_for_status = MagicMock()

        with patch.object(self.client._session, "get", return_value=mock_response):
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_products(site="FANZA")

            # Check that the original ValueError is preserved
            self.assertIsInstance(exc_info.exception.__cause__, ValueError)

    def test_json_with_null_bytes(self):
        """Test JSON with null bytes raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": "value\x00with null"}'
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_makers(floor_id=43)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_multiple_json_objects(self):
        """Test multiple JSON objects in response raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": "first"}{"result": "second"}'
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_series(floor_id=27)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_json_with_unescaped_control_characters(self):
        """Test JSON with unescaped control characters raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": "line1\nline2"}'  # Unescaped newline
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            self.client._session, "get", return_value=mock_response
        ) as mock_get:
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_authors(floor_id=27)

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )
            mock_get.assert_called_once()

    def test_json_error_on_get_product_by_cid(self):
        """Test invalid JSON on get_product_by_cid raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Not JSON"
        mock_response.raise_for_status = MagicMock()

        with patch.object(self.client._session, "get", return_value=mock_response):
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_product_by_cid(cid="test123", site="FANZA")

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )

    def test_json_error_on_get_product_by_product_id(self):
        """Test invalid JSON on get_product_by_product_id raises DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{invalid}"
        mock_response.raise_for_status = MagicMock()

        with patch.object(self.client._session, "get", return_value=mock_response):
            with self.assertRaises(DMMAPIError) as exc_info:
                self.client.get_product_by_product_id(
                    product_id="ABP-477", site="FANZA"
                )

            self.assertIn(
                "Error while formatting DMM Response", str(exc_info.exception)
            )


if __name__ == "__main__":
    unittest.main()
