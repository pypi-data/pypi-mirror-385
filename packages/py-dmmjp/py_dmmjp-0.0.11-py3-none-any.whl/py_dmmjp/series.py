"""
Data models for the DMM Series Search API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from .commons import ApiRequest


class SeriesSearchParams(TypedDict, total=False):
    """Type definition for series search parameters."""

    initial: str
    hits: int
    offset: int


@dataclass
class Series:
    """Represents series information from the DMM Series Search API."""

    series_id: str
    "Series ID (e.g., '62226', '105331')"

    name: str
    "Series name (e.g., 'ARIA', 'おあいにくさま二ノ宮くん')"

    ruby: str
    "Series name phonetic reading (e.g., 'ありあ', 'おあいにくさまにのみやくん')"

    list_url: str
    "List page URL with affiliate ID"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Series":
        """Create Series from dictionary."""

        return cls(
            series_id=str(data.get("series_id", "")),
            name=data.get("name", ""),
            ruby=data.get("ruby", ""),
            list_url=data.get("list_url", ""),
        )


@dataclass
class SeriesSearchResult:
    """Represents the result section of the Series Search API response."""

    status: int
    "HTTP status code of the API response (e.g., 200, 404, 500)"

    result_count: int
    "Number of series returned in current response (e.g., 10, 100)"

    total_count: int
    "Total number of series matching the search criteria (e.g., 970, 1000)"

    first_position: int
    "Search start position in the overall result set (e.g., 1, 10)"

    site_name: str
    "Site name (e.g., 'DMM.com（一般）')"

    site_code: str
    "Site code (e.g., 'DMM.com')"

    service_name: str
    "Service name (e.g., '通販')"

    service_code: str
    "Service code (e.g., 'mono')"

    floor_id: str
    "Floor ID (e.g., '24', '27')"

    floor_name: str
    "Floor name (e.g., '本・コミック')"

    floor_code: str
    "Floor code (e.g., 'book')"

    series_list: List[Series] = field(default_factory=list)
    "List of series items returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeriesSearchResult":
        """Create SeriesSearchResult from dictionary."""

        series_data = data.get("series", [])
        series_list = [Series.from_dict(series) for series in series_data]

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
            series_list=series_list,
        )


@dataclass
class SeriesSearchResponse:
    """Represents the complete Series Search API response from DMM."""

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: SeriesSearchResult
    "Result data containing series and metadata"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeriesSearchResponse":
        """Create SeriesSearchResponse from the full API response dictionary."""

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=SeriesSearchResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""
        return self._raw_response

    @property
    def series(self) -> List[Series]:
        """Get all series from the response."""
        return self.result.series_list

    @property
    def series_count(self) -> int:
        """Get the number of series returned."""
        return self.result.result_count

    @property
    def total_series(self) -> int:
        """Get the total number of series available."""
        return self.result.total_count

    @property
    def status(self) -> int:
        """Get the API response status."""
        return self.result.status
