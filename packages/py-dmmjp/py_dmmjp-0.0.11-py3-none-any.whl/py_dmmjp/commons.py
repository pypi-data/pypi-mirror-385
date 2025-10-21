"""
Common data models shared across different DMM API endpoints.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class RequestParameters:
    """
    Represents the readonly request parameters from the API response.
    """

    api_id: str
    "DMM API identifier for the request (e.g., 'your_api_id')"

    affiliate_id: str
    "Affiliate program identifier (e.g., 'affiliate_code-001')"

    _params: Dict[str, Any] = field(default_factory=dict)
    "Dictionary containing all request parameters"

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to parameters."""

        if key == "api_id":
            return self.api_id
        if key == "affiliate_id":
            return self.affiliate_id

        return self._params.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if a parameter exists."""

        if key in ("api_id", "affiliate_id"):
            return True

        return key in self._params

    def get(self, key: str, default: Any = None) -> Any:
        """Get parameter with optional default value."""

        if key == "api_id":
            return self.api_id

        if key == "affiliate_id":
            return self.affiliate_id

        return self._params.get(key, default)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RequestParameters":
        """Create RequestParameters from dictionary."""

        api_id = data.get("api_id", "")
        affiliate_id = data.get("affiliate_id", "")

        params = {k: v for k, v in data.items() if k not in ("api_id", "affiliate_id")}

        return cls(api_id=api_id, affiliate_id=affiliate_id, _params=params)


@dataclass
class ApiRequest:
    """Represents the request section of the API response."""

    parameters: RequestParameters
    "Request parameters used for the API call"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiRequest":
        """Create ApiRequest from dictionary."""

        return cls(parameters=RequestParameters.from_dict(data.get("parameters", {})))
