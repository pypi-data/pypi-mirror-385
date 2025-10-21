"""
Data models for the DMM Genre Search API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from .commons import ApiRequest


class GenreSearchParams(TypedDict, total=False):
    """Type definition for genre search parameters."""

    initial: str
    hits: int
    offset: int


@dataclass
class Genre:
    """Represents genre information from the DMM Genre Search API."""

    genre_id: str
    "Genre ID (e.g., '2001', '73115')"

    name: str
    "Genre name (e.g., '巨乳', 'キャラクター')"

    ruby: str
    "Genre name phonetic reading (e.g., 'きょにゅう', 'きゃらくたー')"

    list_url: str
    "List page URL with affiliate ID"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Genre":
        """Create Genre from dictionary."""

        return cls(
            genre_id=str(data.get("genre_id", "")),
            name=data.get("name", ""),
            ruby=data.get("ruby", ""),
            list_url=data.get("list_url", ""),
        )


@dataclass
class GenreSearchResult:
    """Represents the result section of the Genre Search API response."""

    status: int
    "HTTP status code of the API response (e.g., 200, 404, 500)"

    result_count: int
    "Number of genres returned in current response (e.g., 10, 100)"

    total_count: int
    "Total number of genres matching the search criteria (e.g., 1000)"

    first_position: int
    "Search start position in the overall result set (e.g., 1, 10)"

    site_name: str
    "Site name (e.g., 'FANZA（アダルト）', 'DMM.com（一般）')"

    site_code: str
    "Site code (e.g., 'FANZA', 'DMM.com')"

    service_name: str
    "Service name (e.g., '動画', '通販')"

    service_code: str
    "Service code (e.g., 'digital', 'mono')"

    floor_id: str
    "Floor ID (e.g., '40', '25')"

    floor_name: str
    "Floor name (e.g., 'ビデオ', 'DVD・Blu-ray')"

    floor_code: str
    "Floor code (e.g., 'videoa', 'dvd')"

    genres: List[Genre] = field(default_factory=list)
    "List of genre items returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenreSearchResult":
        """Create GenreSearchResult from dictionary."""

        genres_data = data.get("genre", [])
        genres = [Genre.from_dict(genre) for genre in genres_data]

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
            genres=genres,
        )


@dataclass
class GenreSearchResponse:
    """Represents the complete Genre Search API response from DMM."""

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: GenreSearchResult
    "Result data containing genres and metadata"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenreSearchResponse":
        """Create GenreSearchResponse from the full API response dictionary."""

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=GenreSearchResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""
        return self._raw_response

    @property
    def genres(self) -> List[Genre]:
        """Get all genres from the response."""
        return self.result.genres

    @property
    def genre_count(self) -> int:
        """Get the number of genres returned."""
        return self.result.result_count

    @property
    def total_genres(self) -> int:
        """Get the total number of genres available."""
        return self.result.total_count

    @property
    def status(self) -> int:
        """Get the API response status."""
        return self.result.status
