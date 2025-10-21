"""
Data models for the DMM Actress Search API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from .commons import ApiRequest


class ActressSearchParams(TypedDict, total=False):
    """Type definition for actress search parameters."""

    initial: str
    actress_id: int
    keyword: str
    gte_bust: int
    lte_bust: int
    gte_waist: int
    lte_waist: int
    gte_hip: int
    lte_hip: int
    gte_height: int
    lte_height: int
    gte_birthday: str
    lte_birthday: str
    hits: int
    offset: int
    sort: str


@dataclass
class ActressImageURL:
    """Represents actress image URLs in different sizes."""

    small: Optional[str] = None
    "Small actress image URL (e.g., http://pics.dmm.co.jp/mono/actjpgs/thumbnail/asami_yuma.jpg)"

    large: Optional[str] = None
    "Large actress image URL (e.g., http://pics.dmm.co.jp/mono/actjpgs/asami_yuma.jpg)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActressImageURL":
        """Create ActressImageURL from dictionary."""

        return cls(small=data.get("small"), large=data.get("large"))


@dataclass
class ActressListURL:
    """Represents actress content list URLs with affiliate tracking."""

    digital: Optional[str] = None
    "Digital video list URL"

    monthly: Optional[str] = None
    "Monthly unlimited subscription URL"

    mono: Optional[str] = None
    "DVD mail order list URL"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActressListURL":
        """Create ActressListURL from dictionary."""

        return cls(
            digital=data.get("digital"),
            monthly=data.get("monthly"),
            mono=data.get("mono"),
        )


@dataclass
class Actress:
    """Represents actress information from the DMM Actress Search API."""

    id: int
    "Actress ID (e.g., 15365, 1058259)"

    name: str
    "Actress name in Japanese (e.g., '麻美ゆま', '市川花音')"

    ruby: Optional[str] = None
    "Actress name phonetic reading (e.g., 'あさみゆま', 'いちかわかのん')"

    bust: Optional[int] = None
    "Bust measurement in cm (e.g., 96, 80)"

    cup: Optional[str] = None
    "Cup size (e.g., 'H', 'B', 'C')"

    waist: Optional[int] = None
    "Waist measurement in cm (e.g., 58, 55)"

    hip: Optional[int] = None
    "Hip measurement in cm (e.g., 88, 82)"

    height: Optional[int] = None
    "Height in cm (e.g., 158, 141)"

    birthday: Optional[str] = None
    "Birthday in YYYY-MM-DD format (e.g., '1987-03-24', '1991-05-30')"

    blood_type: Optional[str] = None
    "Blood type (e.g., 'AB', 'O')"

    hobby: Optional[str] = None
    "Hobbies and interests (e.g., '香水集め、英会話、ピアノ', 'コスプレ、サバイバルゲーム')"

    prefectures: Optional[str] = None
    "Birthplace prefecture (e.g., '東京都', '北海道')"

    image_url: Optional[ActressImageURL] = None
    "Actress image URLs in different sizes"

    list_url: Optional[ActressListURL] = None
    "Content list URLs with affiliate tracking"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Actress":
        """Create Actress from dictionary."""

        # Convert string measurements to integers where possible
        def safe_int(value: Any) -> Optional[int]:
            if value is None or value == "":
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        image_url = (
            ActressImageURL.from_dict(data.get("imageURL", {}))
            if data.get("imageURL")
            else None
        )

        list_url = (
            ActressListURL.from_dict(data.get("listURL", {}))
            if data.get("listURL")
            else None
        )

        return cls(
            id=int(data.get("id", 0)),
            name=data.get("name", ""),
            ruby=data.get("ruby"),
            bust=safe_int(data.get("bust")),
            cup=data.get("cup"),
            waist=safe_int(data.get("waist")),
            hip=safe_int(data.get("hip")),
            height=safe_int(data.get("height")),
            birthday=data.get("birthday"),
            blood_type=data.get("blood_type"),
            hobby=data.get("hobby"),
            prefectures=data.get("prefectures"),
            image_url=image_url,
            list_url=list_url,
        )


@dataclass
class ActressSearchResult:
    """Represents the result section of the Actress Search API response."""

    status: int
    "HTTP status code of the API response (e.g., 200, 404, 500)"

    result_count: int
    "Number of actresses returned in current response (e.g., 10, 20)"

    total_count: int
    "Total number of actresses matching the search criteria (e.g., 64964)"

    first_position: int
    "Position of first item in the overall result set (e.g., 1, 21, 41)"

    actresses: List[Actress] = field(default_factory=list)
    "List of actress items returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActressSearchResult":
        """Create ActressSearchResult from dictionary."""

        actresses_data = data.get("actress", [])
        actresses = [Actress.from_dict(actress) for actress in actresses_data]

        return cls(
            status=int(data.get("status", 200)),
            result_count=int(data.get("result_count", 0)),
            total_count=int(data.get("total_count", 0)),
            first_position=int(data.get("first_position", 1)),
            actresses=actresses,
        )


@dataclass
class ActressSearchResponse:
    """Represents the complete Actress Search API response from DMM."""

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: ActressSearchResult
    "Result data containing actresses and metadata"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActressSearchResponse":
        """Create ActressSearchResponse from the full API response dictionary."""

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=ActressSearchResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""

        return self._raw_response

    @property
    def actresses(self) -> List[Actress]:
        """Get all actresses from the response."""

        return self.result.actresses

    @property
    def actress_count(self) -> int:
        """Get the number of actresses returned."""

        return self.result.result_count

    @property
    def total_actresses(self) -> int:
        """Get the total number of actresses available."""

        return self.result.total_count

    @property
    def status(self) -> int:
        """Get the API response status."""

        return self.result.status
