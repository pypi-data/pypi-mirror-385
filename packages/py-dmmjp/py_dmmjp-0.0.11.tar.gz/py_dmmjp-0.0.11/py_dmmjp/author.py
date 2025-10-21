"""
Data models for the DMM Author Search API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from .commons import ApiRequest


class AuthorSearchParams(TypedDict, total=False):
    """Type definition for author search parameters."""

    initial: str
    hits: int
    offset: int


@dataclass
class Author:
    """Represents author information from the DMM Author Search API."""

    author_id: str
    "Author ID (e.g., '21414', '182179')"

    name: str
    "Author name (e.g., 'ヴィクトル・ユゴー', 'ウィクセル')"

    ruby: str
    "Author name phonetic reading (e.g., 'う゛ぃくとるゆごー', 'うぃくせる')"

    list_url: str
    "List page URL with affiliate ID"

    another_name: str
    "Author alias/another name (e.g., 'ヴィクトル・ユーゴー/ヴィクトル=ユーゴー')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Author":
        """Create Author from dictionary."""

        return cls(
            author_id=str(data.get("author_id", "")),
            name=data.get("name", ""),
            ruby=data.get("ruby", ""),
            list_url=data.get("list_url", ""),
            another_name=data.get("another_name", ""),
        )


@dataclass
class AuthorSearchResult:
    """Represents the result section of the Author Search API response."""

    status: int
    "HTTP status code of the API response (e.g., 200, 404, 500)"

    result_count: int
    "Number of authors returned in current response (e.g., 10, 100)"

    total_count: int
    "Total number of authors matching the search criteria (e.g., 2311, 1000)"

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

    author_list: List[Author] = field(default_factory=list)
    "List of author items returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorSearchResult":
        """Create AuthorSearchResult from dictionary."""

        author_data = data.get("author", [])
        author_list = [Author.from_dict(author) for author in author_data]

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
            author_list=author_list,
        )


@dataclass
class AuthorSearchResponse:
    """Represents the complete Author Search API response from DMM."""

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: AuthorSearchResult
    "Result data containing authors and metadata"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorSearchResponse":
        """Create AuthorSearchResponse from the full API response dictionary."""

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=AuthorSearchResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""
        return self._raw_response

    @property
    def authors(self) -> List[Author]:
        """Get all authors from the response."""
        return self.result.author_list

    @property
    def author_count(self) -> int:
        """Get the number of authors returned."""
        return self.result.result_count

    @property
    def total_authors(self) -> int:
        """Get the total number of authors available."""
        return self.result.total_count

    @property
    def status(self) -> int:
        """Get the API response status."""
        return self.result.status
