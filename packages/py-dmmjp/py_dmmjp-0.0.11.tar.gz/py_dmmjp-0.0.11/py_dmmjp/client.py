"""
Main client class for the py-dmm library.
"""

import json
from typing import Any, Dict, List, Literal, Optional, cast

import requests
import requests.exceptions

from .actress import Actress, ActressSearchParams, ActressSearchResponse
from .author import Author, AuthorSearchParams, AuthorSearchResponse
from .exceptions import DMMAPIError, DMMAuthError, DMMError
from .floor import FloorListResponse, Site
from .genre import Genre, GenreSearchParams, GenreSearchResponse
from .maker import Maker, MakerSearchParams, MakerSearchResponse
from .product import Product, ProductSearchParams
from .series import Series, SeriesSearchParams, SeriesSearchResponse

try:
    from typing import Unpack
except ImportError:  # pragma: no cover
    from typing_extensions import Unpack


class DMMClient:
    """
    A client for interacting with the DMM API.

    Core class to handle main DMM API interactions.
    """

    def __init__(
        self,
        api_key: str,
        affiliate_id: str,
        timeout: int = 10,
    ) -> None:
        """
        Initialize the DMM client.

        Args:
            api_key: Your DMM API key for authentication.
            affiliate_id: Your DMM affiliate ID.
            timeout: Request timeout in seconds.

        Raises:
            DMMAuthError: If the API key is invalid or missing.
        """

        if (
            not api_key
            or not api_key.strip()
            or not affiliate_id
            or not affiliate_id.strip()
        ):
            raise DMMAuthError("API_KEY and AFFILIATE_KEY are required")

        self._api_key = api_key
        self._affiliate_id = affiliate_id
        self._base_url = "https://api.dmm.com/affiliate/v3"
        self._timeout = timeout
        self._session = requests.Session()

        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the DMM API.

        Args:
            endpoint: API endpoint to call.
            params: Query parameters to include.
            method: HTTP method to use.

        Returns:
            JSON response data.

        Raises:
            DMMAPIError: If the API request fails.
            DMMAuthError: If authentication fails.
        """

        url = f"{self._base_url}{endpoint}"

        if params is None:  # pragma: no cover
            params = {}

        params["api_id"] = self._api_key
        params["affiliate_id"] = self._affiliate_id
        params["output"] = "json"

        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise DMMAPIError("Request timed out") from e
        except requests.exceptions.ConnectionError as e:
            raise DMMAPIError("Connection error occurred") from e
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise DMMAuthError("Invalid API key or authentication failed") from e

            if response.status_code == 403:
                raise DMMAuthError(
                    "Access forbidden - check your API key permissions"
                ) from e

            raise DMMAPIError(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
                response_data=response.text,
            ) from e
        except requests.exceptions.RequestException as e:
            raise DMMAPIError(f"Request failed: {str(e)}") from e

        try:
            return cast(Dict[str, Any], json.loads(response.text))
        except ValueError as e:
            raise DMMAPIError("Error while formatting DMM Response") from e

    @property
    def app_id(self) -> str:
        """
        Get the API key used by the client.

        Returns:
            The API key as a string.
        """
        return self._api_key

    @property
    def affiliate_id(self) -> str:
        """
        Get the affiliate ID used by the client.

        Returns:
            The affiliate ID as a string.
        """
        return self._affiliate_id

    def get_products(
        self,
        **kwargs: Unpack[ProductSearchParams],
    ) -> List[Product]:
        """
        Retrieve product information from the DMM API.

        This method fetches products from the DMM API and returns a simple list
        of Product objects, handling the API response internally.

        Args:
            site: Site to search. Either "FANZA" for adult content or "DMM.com" for general content.
            service: Service code that the products can be retrieved from.
                    Can be obtained from Floor API.
            floor: Floor code that the products can be retrieved from.
                   Can be obtained from Floor API.
            keyword: Search keyword. Can be title, actress name, product ID, maker ID, etc.
            hits: Number of results to return. Default is 20, maximum is 100.
            offset: Starting position for results. Default is 1, maximum is 50000.
            sort: Sort order for results. Options:
                - "rank": Popularity (default)
                - "price": Price (high to low)
                - "-price": Price (low to high)
                - "date": Release date
                - "review": Rating
                - "match": Relevance
            cid: Product ID (content_id) for specific product lookup.
            article: Filter categories for refined search. Options:
                - "actress": Filter by actress
                - "author": Filter by author
                - "genre": Filter by genre
                - "series": Filter by series
                - "maker": Filter by maker
            article_id: Filter IDs corresponding to article categories.
                       Obtainable from respective search APIs.
            gte_date: Release date filter (from) in ISO8601 format (YYYY-MM-DDTHH:MM:SS).
                     Filter products released on or after this date.
            lte_date: Release date filter (to) in ISO8601 format (YYYY-MM-DDTHH:MM:SS).
                     Filter products released on or before this date.
            mono_stock: Stock filter for retail services. Options:
                - "stock": In stock items
                - "reserve": Pre-order items (in stock)
                - "reserve_empty": Pre-order items (waiting list)
                - "mono": DMM direct sales only
                - "dmp": Marketplace items only
            **kwargs: Additional product search parameters (typed as ProductSearchParams).

        Returns:
            List[Product]: List of Product objects containing product information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> products = client.get_products(
            ...     site="FANZA",
            ...     service="digital",
            ...     floor="videoa",
            ...     keyword="AIKA",
            ...     hits=10,
            ...     sort="review"
            ... )
            >>> print(f"Found {len(products)} products")
            >>> for product in products:
            ...     print(f"- {product.title}")
        """

        params: Dict[str, Any] = {}
        params.update(kwargs)

        try:
            response_data = self._make_request("/ItemList", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            result = response_data["result"]
            items = result.get("items", [])
            products = [Product.from_dict(item) for item in items]

            return products

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get products: {str(e)}") from e

    def get_product_by_cid(
        self, cid: str, site: Literal["FANZA", "DMM.com"]
    ) -> Optional[Product]:
        """
        Retrieve a single product by its content ID (cid).

        This method fetches a specific product from the DMM API using its content ID.

        Args:
            cid: The content ID of the product to retrieve.
            site: Site to search. Either "FANZA" for adult content or "DMM.com" for general content.

        Returns:
            Optional[Product]: The Product object if found, otherwise None.
        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.
        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> product = client.get_product_by_cid(cid="ABP-477", site="FANZA")
            >>> if product:
            ...     print(f"Product Title: {product.title}")
            ... else:
            ...     print("Product not found")
        """

        products = self.get_products(site=site, cid=cid, hits=1)

        return products[0] if products else None

    def get_product_by_product_id(
        self, product_id: str, site: Literal["FANZA", "DMM.com"]
    ) -> Optional[Product]:
        """
        Retrieve a single product by its product ID such as "ABP-477", "MIRD-127", etc.

        Args:
            product_id: The product ID of the product to retrieve.
        Returns:
            Optional[Product]: The Product object if found, otherwise None.
        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> product = client.get_product_by_product_id(product_id="ABP-477", site="FANZA")
            >>> if product:
            ...     print(f"Product Title: {product.title}")
            ... else:
            ...     print("Product not found")
        """

        def __predicate(p: Product) -> bool:
            if p.maker_product:
                if p.maker_product.lower() == product_id.lower():
                    return True

                # some response product ids drop leading zeroes after the dash
                if "-" in p.maker_product:
                    prefix, suffix = p.maker_product.split("-", 1)

                    if len(suffix) == 2:
                        new_maker_product = f"{prefix}-0{suffix}"

                        return new_maker_product.lower() == product_id.lower()

            return False

        products = self.get_products(site=site, keyword=product_id)
        product = next((p for p in products if __predicate(p)), None)

        return product

    def get_floors(self) -> List[Site]:
        """
        Retrieve the floor list from the DMM API.

        This method fetches all available floors, sites, and services from the DMM API and returns a flat list of Floor objects.

        Returns:
            List[Service]: List of Service objects containing floor information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            ... floors = client.get_floors()
            ... print(f"Found {len(floors)} floors")
            ... for site in floors:
            ...     print(f"- {site.name} ({site.code})")
            ...     for service in site.services:
            ...         print(f"  Service: {service.name} ({service.code})")
            ...         for floor in service.floors:
            ...             print(f"    Floor: {floor.name} ({floor.code})")
            ...
        """

        params: Dict[str, Any] = {}

        try:
            response_data = self._make_request("/FloorList", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            floor_response = FloorListResponse.from_dict(response_data)
            sites = floor_response.result.sites

            return sites

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get floors: {str(e)}") from e

    def get_actresses(
        self,
        **kwargs: Unpack[ActressSearchParams],
    ) -> List[Actress]:
        """
        Retrieve actress information from the DMM API.

        This method fetches actresses from the DMM API and returns a list
        of Actress objects, handling the API response internally.

        Args:
            initial: Specify 50-sound in UTF-8 (e.g., 'あ', 'か').
            actress_id: Specific actress ID to retrieve.
            keyword: Search keyword in UTF-8 (e.g., 'あさみ').
            gte_bust: Bust measurement equal or greater than (cm).
            lte_bust: Bust measurement equal or less than (cm).
            gte_waist: Waist measurement equal or greater than (cm).
            lte_waist: Waist measurement equal or less than (cm).
            gte_hip: Hip measurement equal or greater than (cm).
            lte_hip: Hip measurement equal or less than (cm).
            gte_height: Height equal or greater than (cm).
            lte_height: Height equal or less than (cm).
            gte_birthday: Birthday filter (from) in YYYY-MM-DD format.
            lte_birthday: Birthday filter (to) in YYYY-MM-DD format.
            hits: Number of results to return. Default is 20, maximum is 100.
            offset: Starting position for results. Default is 1.
            sort: Sort order. Options: 'name', '-name', 'bust', '-bust',
                  'waist', '-waist', 'hip', '-hip', 'height', '-height',
                  'birthday', '-birthday', 'id', '-id'.
            **kwargs: Additional actress search parameters (typed as ActressSearchParams).

        Returns:
            List[Actress]: List of Actress objects containing actress information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> actresses = client.get_actresses(
            ...     keyword="あさみ",
            ...     gte_bust=80,
            ...     lte_bust=100,
            ...     hits=10,
            ...     sort="bust"
            ... )
            >>> print(f"Found {len(actresses)} actresses")
            >>> for actress in actresses:
            ...     print(f"- {actress.name} (ID: {actress.id})")
        """

        params: Dict[str, Any] = {}
        params.update(kwargs)

        try:
            response_data = self._make_request("/ActressSearch", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            actress_response = ActressSearchResponse.from_dict(response_data)

            return actress_response.actresses

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get actresses: {str(e)}") from e

    def get_genres(
        self, floor_id: int, **kwargs: Unpack["GenreSearchParams"]
    ) -> List["Genre"]:
        """
        Retrieve genre information from the DMM API.

        This method fetches genres from the DMM API based on floor ID and returns a list
        of Genre objects, handling the API response internally.

        Args:
            floor_id: Floor ID available from Floor Search API (required).
            initial: Specify 50-sound in UTF-8 (e.g., 'あ', 'き').
            hits: Number of results to return. Default is 100, maximum is 500.
            offset: Search start position. Default is 1.
            **kwargs: Additional genre search parameters (typed as GenreSearchParams).

        Returns:
            List[Genre]: List of Genre objects containing genre information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> genres = client.get_genres(
            ...     floor_id="43",
            ...     initial="き",
            ...     hits=10
            ... )
            >>> print(f"Found {len(genres)} genres")
            >>> for genre in genres:
            ...     print(f"- {genre.name} ({genre.genre_id})")
        """

        if not floor_id or not isinstance(floor_id, int):
            raise DMMAPIError("floor_id is required and must be a non-zero integer")

        params: Dict[str, Any] = {"floor_id": floor_id}
        params.update(kwargs)

        try:
            response_data = self._make_request("/GenreSearch", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            genre_response = GenreSearchResponse.from_dict(response_data)
            return genre_response.genres

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get genres: {str(e)}") from e

    def get_makers(
        self, floor_id: int, **kwargs: Unpack[MakerSearchParams]
    ) -> List[Maker]:
        """
        Retrieve maker information from the DMM API.

        This method fetches makers from the DMM API based on floor ID and returns a list
        of Maker objects, handling the API response internally.

        Args:
            floor_id: Floor ID available from Floor Search API (required).
            initial: Specify 50-sound in UTF-8 (e.g., 'あ', 'む').
            hits: Number of results to return. Default is 100, maximum is 500.
            offset: Search start position. Default is 1.
            **kwargs: Additional maker search parameters (typed as MakerSearchParams).

        Returns:
            List[Maker]: List of Maker objects containing maker information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> makers = client.get_makers(
            ...     floor_id=43,
            ...     initial="あ",
            ...     hits=10
            ... )
            >>> print(f"Found {len(makers)} makers")
            >>> for maker in makers:
            ...     print(f"- {maker.name} ({maker.maker_id})")
        """

        if not floor_id or not isinstance(floor_id, int):
            raise DMMAPIError("floor_id is required and must be a non-zero integer")

        params: Dict[str, Any] = {"floor_id": floor_id}
        params.update(kwargs)

        try:
            response_data = self._make_request("/MakerSearch", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            maker_response = MakerSearchResponse.from_dict(response_data)

            return maker_response.makers

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get makers: {str(e)}") from e

    def get_series(
        self, floor_id: int, **kwargs: Unpack["SeriesSearchParams"]
    ) -> List["Series"]:
        """
        Retrieve series information from the DMM API.

        This method fetches series from the DMM API based on floor ID and returns a list
        of Series objects, handling the API response internally.

        Args:
            floor_id: Floor ID available from Floor Search API (required).
            initial: Specify 50-sound in UTF-8 (e.g., 'あ', 'お').
            hits: Number of results to return. Default is 100, maximum is 500.
            offset: Search start position. Default is 1.
            **kwargs: Additional series search parameters (typed as SeriesSearchParams).

        Returns:
            List[Series]: List of Series objects containing series information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> series = client.get_series(
            ...     floor_id=27,
            ...     initial="お",
            ...     hits=10
            ... )
            >>> print(f"Found {len(series)} series")
            >>> for s in series:
            ...     print(f"- {s.name} ({s.series_id})")
        """

        if not floor_id or not isinstance(floor_id, int):
            raise DMMAPIError("floor_id is required and must be a non-zero integer")

        params: Dict[str, Any] = {"floor_id": floor_id}
        params.update(kwargs)

        try:
            response_data = self._make_request("/SeriesSearch", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            series_response = SeriesSearchResponse.from_dict(response_data)

            return series_response.series

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get series: {str(e)}") from e

    def get_authors(
        self, floor_id: int, **kwargs: Unpack[AuthorSearchParams]
    ) -> List[Author]:
        """
        Retrieve author information from the DMM API.

        This method fetches authors from the DMM API based on floor ID and returns a list
        of Author objects, handling the API response internally.

        Args:
            floor_id: Floor ID available from Floor Search API (required).
            initial: Specify author name phonetic reading in UTF-8 (e.g., 'う', 'あ').
            hits: Number of results to return. Default is 100, maximum is 500.
            offset: Search start position. Default is 1.
            **kwargs: Additional author search parameters (typed as AuthorSearchParams).

        Returns:
            List[Author]: List of Author objects containing author information.

        Raises:
            DMMAPIError: If the API request fails or returns an error.
            DMMAuthError: If authentication fails or API key is invalid.

        Example:
            >>> client = DMMClient(api_key="your_key", affiliate_id="your_id")
            >>> authors = client.get_authors(
            ...     floor_id=27,
            ...     initial="う",
            ...     hits=10
            ... )
            >>> print(f"Found {len(authors)} authors")
            >>> for author in authors:
            ...     print(f"- {author.name} ({author.author_id})")
        """

        if not floor_id or not isinstance(floor_id, int):
            raise DMMAPIError("floor_id is required and must be a non-zero integer")

        params: Dict[str, Any] = {"floor_id": floor_id}
        params.update(kwargs)

        try:
            response_data = self._make_request("/AuthorSearch", params)

            if "result" not in response_data:
                raise DMMAPIError("Invalid API response: missing 'result' field")

            author_response = AuthorSearchResponse.from_dict(response_data)

            return author_response.authors

        except Exception as e:
            if isinstance(e, (DMMError, DMMAPIError, DMMAuthError)):
                raise

            raise DMMAPIError(f"Failed to get authors: {str(e)}") from e

    def close(self) -> None:
        """
        Explicitly close the HTTP session.
        """

        self._session.close()

    def __del__(self) -> None:
        """
        Destructor to ensure the session is closed.
        """

        if hasattr(self, "_session"):
            self.close()

    def __enter__(self) -> "DMMClient":
        """
        Context manager entry.

        Allows using the client with the 'with' statement for automatic
        resource management.

        Returns:
            DMMClient: The client instance for use in the context.
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit.

        Automatically closes the session when exiting the 'with' block.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.
        """
        self.close()
