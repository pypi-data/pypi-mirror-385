"""
py-dmmjp: A Python client library for the DMM API.

This package provides a simple and intuitive interface for interacting with
the DMM-JP API.
"""

__version__ = "0.0.11"
__author__ = "Richard Nguyen"
__email__ = "richard@richardhnguyen.com"
__license__ = "MIT"

from .actress import (
    Actress,
    ActressImageURL,
    ActressListURL,
    ActressSearchResponse,
    ActressSearchResult,
)
from .author import Author, AuthorSearchResponse, AuthorSearchResult
from .client import DMMClient
from .commons import ApiRequest, RequestParameters
from .exceptions import DMMAPIError, DMMAuthError, DMMError
from .floor import Floor, FloorListResponse, FloorListResult, Service, Site
from .genre import Genre, GenreSearchResponse, GenreSearchResult
from .maker import Maker, MakerSearchResponse, MakerSearchResult
from .product import (
    Campaign,
    CDInfo,
    Delivery,
    Directory,
    ImageURL,
    ItemDetails,
    ItemInfo,
    Prices,
    Product,
    ProductApiResponse,
    ProductApiResult,
    Review,
    SampleImage,
    SampleImages,
    SampleMovieURL,
    TachiyomiInfo,
)
from .series import Series, SeriesSearchResponse, SeriesSearchResult

__all__ = [
    "DMMClient",
    "DMMError",
    "DMMAPIError",
    "DMMAuthError",
    "Product",
    "ProductApiResponse",
    "ProductApiResult",
    "RequestParameters",
    "Review",
    "ImageURL",
    "SampleImage",
    "SampleImages",
    "SampleMovieURL",
    "TachiyomiInfo",
    "Prices",
    "Delivery",
    "ItemInfo",
    "ItemDetails",
    "Directory",
    "CDInfo",
    "Campaign",
    "Actress",
    "ActressImageURL",
    "ActressListURL",
    "ActressSearchResponse",
    "ActressSearchResult",
    "Floor",
    "Site",
    "Service",
    "FloorListResponse",
    "FloorListResult",
    "Genre",
    "GenreSearchResponse",
    "GenreSearchResult",
    "Series",
    "SeriesSearchResponse",
    "SeriesSearchResult",
    "Author",
    "AuthorSearchResponse",
    "AuthorSearchResult",
    "Maker",
    "MakerSearchResponse",
    "MakerSearchResult",
]
