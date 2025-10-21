"""
Data models for the DMM Maker Search API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from .commons import ApiRequest


class MakerSearchParams(TypedDict, total=False):
    """Type definition for maker search parameters."""

    initial: str
    hits: int
    offset: int


@dataclass
class Maker:
    """Represents maker information from the DMM Maker Search API."""

    maker_id: str
    "Maker ID (e.g., '1509', '45556')"

    name: str
    "Maker name (e.g., 'ムーディーズ', 'アタッカーズ')"

    ruby: str
    "Maker name phonetic reading (e.g., 'むーでぃーず', 'あたっかーず')"

    list_url: str
    "List page URL with affiliate ID"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Maker":
        """Create Maker from dictionary."""

        return cls(
            maker_id=str(data.get("maker_id", "")),
            name=data.get("name", ""),
            ruby=data.get("ruby", ""),
            list_url=data.get("list_url", ""),
        )


@dataclass
class MakerSearchResult:
    """Represents the result section of the Maker Search API response."""

    status: int
    "HTTP status code of the API response (e.g., 200, 404, 500)"

    result_count: int
    "Number of makers returned in current response (e.g., 10, 100)"

    total_count: int
    "Total number of makers matching the search criteria (e.g., 4739, 1000)"

    first_position: int
    "Search start position in the overall result set (e.g., 1, 10)"

    site_name: str
    "Site name (e.g., 'FANZA（アダルト）')"

    site_code: str
    "Site code (e.g., 'FANZA')"

    service_name: str
    "Service name (e.g., '動画')"

    service_code: str
    "Service code (e.g., 'digital')"

    floor_id: str
    "Floor ID (e.g., '40', '43')"

    floor_name: str
    "Floor name (e.g., 'ビデオ')"

    floor_code: str
    "Floor code (e.g., 'videoa')"

    maker_list: List[Maker] = field(default_factory=list)
    "List of maker items returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MakerSearchResult":
        """Create MakerSearchResult from dictionary."""

        maker_data = data.get("maker", [])
        maker_list = [Maker.from_dict(maker) for maker in maker_data]

        return cls(
            status=int(data.get("status", 200)),
            result_count=int(data.get("result_count", 0)),
            total_count=int(data.get("total_count", 0)),
            first_position=int(data.get("first_position", 1)),
            site_name=data.get("site_name", ""),
            site_code=data.get("site_code", ""),
            service_name=data.get("service_name", ""),
            service_code=data.get("service_code", ""),
            floor_id=str(data.get("floor_id", "")),
            floor_name=data.get("floor_name", ""),
            floor_code=data.get("floor_code", ""),
            maker_list=maker_list,
        )


@dataclass
class MakerSearchResponse:
    """Represents the complete Maker Search API response from DMM."""

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: MakerSearchResult
    "Result data containing makers and metadata"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MakerSearchResponse":
        """Create MakerSearchResponse from the full API response dictionary."""

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=MakerSearchResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""
        return self._raw_response

    @property
    def makers(self) -> List[Maker]:
        """Get all makers from the response."""
        return self.result.maker_list

    @property
    def maker_count(self) -> int:
        """Get the number of makers returned."""
        return self.result.result_count

    @property
    def total_makers(self) -> int:
        """Get the total number of makers available."""
        return self.result.total_count

    @property
    def status(self) -> int:
        """Get the API response status."""
        return self.result.status
