"""
Data models for the DMM Floor List API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .commons import ApiRequest


@dataclass
class Floor:
    """
    Represents a floor within a service in the DMM Floor List API.

    Attributes:
        id: Floor ID (e.g., '6')
        name: Floor name (e.g., '映画・ドラマ')
        code: Floor code (e.g., 'cinema')
    """

    id: str
    "Floor ID (e.g., '6')"

    name: str
    "Floor name (e.g., '映画・ドラマ')"

    code: str
    "Floor code (e.g., 'cinema')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Floor":
        """Create Floor from dictionary."""

        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            code=data.get("code", ""),
        )


@dataclass
class Service:
    """
    Represents a service within a site in the DMM Floor List API.

    Attributes:
        name: Service name (e.g., '動画')
        code: Service code (e.g., 'digital')
        floors: List of Floor objects for this service
    """

    name: str
    "Service name (e.g., '動画')"

    code: str
    "Service code (e.g., 'digital')"

    floors: List[Floor] = field(default_factory=list)
    "List of Floor objects for this service"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Service":
        """Create Service from dictionary."""

        floors_data = data.get("floor", [])
        floors = (
            [Floor.from_dict(f) for f in floors_data]
            if isinstance(floors_data, list)
            else []
        )
        return cls(
            name=data.get("name", ""),
            code=data.get("code", ""),
            floors=floors,
        )


@dataclass
class Site:
    """
    Represents a site in the DMM Floor List API.

    Attributes:
        name: Site name (e.g., 'DMM.com（一般）')
        code: Site code (e.g., 'DMM.com')
        services: List of Service objects for this site
    """

    name: str
    "Site name (e.g., 'DMM.com（一般）')"

    code: str
    "Site code (e.g., 'DMM.com')"

    services: List[Service] = field(default_factory=list)
    "List of Service objects for this site"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Site":
        """Create Site from dictionary."""

        services_data = data.get("service", [])
        services = (
            [Service.from_dict(s) for s in services_data]
            if isinstance(services_data, list)
            else []
        )
        return cls(
            name=data.get("name", ""),
            code=data.get("code", ""),
            services=services,
        )


@dataclass
class FloorListResult:
    """
    Represents the result section of the Floor List API response.

    Attributes:
        sites: List of Site objects returned by the API
    """

    sites: List[Site] = field(default_factory=list)
    "List of Site objects returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FloorListResult":
        """Create FloorListResult from dictionary."""

        sites_data = data.get("site", [])
        sites = (
            [Site.from_dict(s) for s in sites_data]
            if isinstance(sites_data, list)
            else []
        )
        return cls(sites=sites)


@dataclass
class FloorListResponse:
    """
    Represents the complete Floor List API response from DMM.

    Attributes:
        request: Request information including parameters used for the API call
        result: Result data containing sites, services, and floors
        _raw_response: Complete raw API response data (internal use, not displayed)
    """

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: FloorListResult
    "Result data containing sites, services, and floors"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FloorListResponse":
        """Create FloorListResponse from the full API response dictionary."""

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=FloorListResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""

        return self._raw_response

    @property
    def sites(self) -> List[Site]:
        """Get all sites from the response."""

        return self.result.sites
