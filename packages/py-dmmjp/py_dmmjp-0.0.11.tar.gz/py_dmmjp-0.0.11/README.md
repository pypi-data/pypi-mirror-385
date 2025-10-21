# py-dmmjp

[![PyPI version](https://badge.fury.io/py/py-dmmjp.svg)](https://badge.fury.io/py/py-dmmjp)
[![Python Support](https://img.shields.io/pypi/pyversions/py-dmmjp.svg)](https://pypi.org/project/py-dmmjp/)
[![codecov](https://codecov.io/github/richardnguyen99/py-dmmjp/graph/badge.svg?token=K8bIVURAv9)](https://codecov.io/github/richardnguyen99/py-dmmjp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

A Python client library for the DMM (Digital Media Mart) API with full type hints support.

## Features

- [x] **Product Search**: Search for products with various filters and parameters
- [x] **Product Details**: Retrieve detailed information about specific products
- [x] **Genre/Category Support**: Browse and filter by categories and genres
- [x] **Type Safety**: Full type hints support with mypy validation
- [x] **Well Tested**: Comprehensive test suite with pytest
- [x] **Well Documented**: Complete API documentation and examples

## Installation

Install py-dmmjp using pip:

```bash
pip install py-dmmjp
```

For development installation with all optional dependencies:

```bash
pip install py-dmmjp[dev]
```

## Quick Start

```python
from py_dmmjp import DMMClient

def main() -> None:
    dmm_client = DMMClient(api_key="your_api_key", affiliate_id="your_affiliate_key")

    print(dmm_client)

    series = dmm_client.get_series(43, hits=5)

    for s in series:
        print(f"{s.name}")
        print(f" - ID: {s.series_id}")
        print(f" - Ruby: {s.ruby}")
```

## API Reference

### DMMClient

The main client class for interacting with the DMM API.

#### Constructor

```python
DMMClient(
    api_key: str,
    affiliate_id: str,
    timeout: int = 10,
)
```

**Parameters:**

- `api_key`: Your DMM API key
- `affiliate_id`: Your DMM Affiliate key (required)
- `timeout`: Maximum seconds the client should wait for a response (optional)

### Methods

#### get_products

```python
get_products(**kwargs: Unpack[ProductSearchParams]) -> List[Product]
```

Retrieve product information from the DMM API. This method fetches products and returns a list of Product objects, handling the API response internally.

Example:

```python
products = client.get_products(
    site="FANZA",
    service="digital",
    floor="videoa",
    keyword="AIKA",
    hits=10,
    sort="review"
)
```

Reference: `docs/products.md`

#### get_product_by_cid

```python
get_product_by_cid(cid: str, site: Literal["FANZA", "DMM.com"]) -> Optional[Product]
```

Retrieve a single product by its content ID (cid).

Example:

```python
product = client.get_product_by_cid(cid="ABP-477", site="FANZA")
```

Reference: `docs/products.md`

#### get_product_by_product_id

```python
get_product_by_product_id(product_id: str, site: Literal["FANZA", "DMM.com"]) -> Optional[Product]
```

Retrieve a single product by its product ID such as "ABP-477", "MIRD-127", etc.

Example:

```python
product = client.get_product_by_product_id(product_id="ABP-477", site="FANZA")
```

Reference: `docs/products.md`

#### get_floors

```python
get_floors() -> List[Site]
```

Retrieve the floor list from the DMM API. This method fetches all available floors, sites, and services.

Example:

```python
floors = client.get_floors()
```

Reference: `docs/development.md`

#### get_actresses

```python
get_actresses(**kwargs: Unpack[ActressSearchParams]) -> List[Actress]
```

Retrieve actress information from the DMM API. This method fetches actresses and returns a list of Actress objects.

Example:

```python
actresses = client.get_actresses(
    keyword="あさみ",
    gte_bust=80,
    lte_bust=100,
    hits=10,
    sort="bust"
)
```

Reference: `docs/actresses.md`

#### get_genres

```python
get_genres(floor_id: int, **kwargs: Unpack[GenreSearchParams]) -> List[Genre]
```

Retrieve genre information from the DMM API based on floor ID.

Example:

```python
genres = client.get_genres(
    floor_id=43,
    initial="き",
    hits=10
)
```

Reference: `docs/development.md`

#### get_makers

```python
get_makers(floor_id: int, **kwargs: Unpack[MakerSearchParams]) -> List[Maker]
```

Retrieve maker information from the DMM API based on floor ID.

Example:

```python
makers = client.get_makers(
    floor_id=43,
    initial="あ",
    hits=10
)
```

Reference: `docs/makers.md`

#### get_series

```python
get_series(floor_id: int, **kwargs: Unpack[SeriesSearchParams]) -> List[Series]
```

Retrieve series information from the DMM API based on floor ID.

Example:

```python
series = client.get_series(
    floor_id=27,
    initial="お",
    hits=10
)
```

Reference: `docs/development.md`

#### get_authors

```python
get_authors(floor_id: int, **kwargs: Unpack[AuthorSearchParams]) -> List[Author]
```

Retrieve author information from the DMM API based on floor ID.

Example:

```python
authors = client.get_authors(
    floor_id=27,
    initial="う",
    hits=10
)
```

Reference: `docs/development.md`

### Data Models

#### Product

The `Product` dataclass represents detailed product information from the DMM API.

**Key Attributes:**

- `content_id` (str): Content ID for the product
- `product_id` (str): Product ID (e.g., "ABP-477", "MIRD-127")
- `title` (str): Product title in Japanese
- `volume` (str): Volume or episode information
- `URL` (str): Product detail page URL with affiliate tracking
- `affiliate_URL` (str): Affiliate link URL
- `imageURL` (ProductImageURL): Product images in multiple sizes
- `prices` (ProductPrices): Pricing information
- `date` (str): Release date in YYYY-MM-DD format
- `iteminfo` (ProductItemInfo): Detailed product metadata (genres, series, maker, etc.)

**Usage Example:**

```python
products = client.get_products(site="FANZA", service="digital", floor="videoa", keyword="AIKA", hits=5)
for product in products:
    print(f"Title: {product.title}")
    print(f"Product ID: {product.product_id}")
    print(f"Price: {product.prices.price if product.prices else 'N/A'}")
```

Reference: `docs/products.md`

#### Floor

The `Floor`, `Service`, and `Site` dataclasses represent the hierarchical structure of DMM's content organization.

**Site** - Top-level organization:

- `name` (str): Site name (e.g., "DMM.com（一般）", "FANZA（アダルト）")
- `code` (str): Site code (e.g., "DMM.com", "FANZA")
- `services` (List[Service]): List of services available on this site

**Service** - Mid-level organization:

- `name` (str): Service name (e.g., "動画", "通販")
- `code` (str): Service code (e.g., "digital", "mono")
- `floors` (List[Floor]): List of floors within this service

**Floor** - Specific content category:

- `id` (str): Floor ID (e.g., "6", "43")
- `name` (str): Floor name (e.g., "映画・ドラマ", "ビデオ")
- `code` (str): Floor code (e.g., "cinema", "videoa")

**Usage Example:**

```python
floors = client.get_floors()
for site in floors:
    print(f"Site: {site.name}")
    for service in site.services:
        print(f"  Service: {service.name}")
        for floor in service.floors:
            print(f"    Floor: {floor.name} (ID: {floor.id})")
```

Reference: `docs/development.md`

#### Actress

The `Actress` dataclass represents actress information from the DMM Actress Search API.

**Key Attributes:**

- `id` (int): Actress ID
- `name` (str): Actress name in Japanese
- `ruby` (Optional[str]): Name phonetic reading
- `bust` (Optional[int]): Bust measurement in cm
- `cup` (Optional[str]): Cup size (e.g., "H", "B", "C")
- `waist` (Optional[int]): Waist measurement in cm
- `hip` (Optional[int]): Hip measurement in cm
- `height` (Optional[int]): Height in cm
- `birthday` (Optional[str]): Birthday in YYYY-MM-DD format
- `blood_type` (Optional[str]): Blood type
- `hobby` (Optional[str]): Hobbies and interests
- `prefectures` (Optional[str]): Birthplace prefecture
- `image_url` (Optional[ActressImageURL]): Image URLs (small, large)
- `list_url` (Optional[ActressListURL]): Content list URLs (digital, monthly, mono)

**Usage Example:**

```python
actresses = client.get_actresses(keyword="あさみ", gte_bust=80, hits=10)
for actress in actresses:
    print(f"Name: {actress.name} ({actress.ruby})")
    print(f"Measurements: B{actress.bust} W{actress.waist} H{actress.hip}")
    print(f"Height: {actress.height}cm")
```

Reference: `docs/actresses.md`

#### Maker

The `Maker` dataclass represents maker (studio/publisher) information from the DMM Maker Search API.

**Attributes:**

- `maker_id` (str): Maker ID (e.g., "1509", "45556")
- `name` (str): Maker name (e.g., "ムーディーズ", "アタッカーズ")
- `ruby` (str): Maker name phonetic reading
- `list_url` (str): List page URL with affiliate ID

**Usage Example:**

```python
makers = client.get_makers(floor_id=43, initial="あ", hits=10)
for maker in makers:
    print(f"Maker: {maker.name}")
    print(f"ID: {maker.maker_id}")
    print(f"Ruby: {maker.ruby}")
    print(f"URL: {maker.list_url}")
```

Reference: `docs/makers.md`

#### Series

The `Series` dataclass represents series information from the DMM Series Search API.

**Attributes:**

- `series_id` (str): Series ID (e.g., "62226", "105331")
- `name` (str): Series name (e.g., "ARIA", "おあいにくさま二ノ宮くん")
- `ruby` (str): Series name phonetic reading
- `list_url` (str): List page URL with affiliate ID

**Usage Example:**

```python
series = client.get_series(floor_id=27, initial="お", hits=10)
for s in series:
    print(f"Series: {s.name}")
    print(f"ID: {s.series_id}")
    print(f"Ruby: {s.ruby}")
```

Reference: `docs/development.md`

#### Genre

The `Genre` dataclass represents genre/category information from the DMM Genre Search API.

**Attributes:**

- `genre_id` (str): Genre ID (e.g., "2001", "73115")
- `name` (str): Genre name (e.g., "巨乳", "キャラクター")
- `ruby` (str): Genre name phonetic reading
- `list_url` (str): List page URL with affiliate ID

**Usage Example:**

```python
genres = client.get_genres(floor_id=43, initial="き", hits=10)
for genre in genres:
    print(f"Genre: {genre.name}")
    print(f"ID: {genre.genre_id}")
    print(f"Ruby: {genre.ruby}")
```

Reference: `docs/development.md`

#### Author

The `Author` dataclass represents author information from the DMM Author Search API.

**Attributes:**

- `author_id` (str): Author ID (e.g., "21414", "182179")
- `name` (str): Author name (e.g., "ヴィクトル・ユゴー", "ウィクセル")
- `ruby` (str): Author name phonetic reading
- `list_url` (str): List page URL with affiliate ID
- `another_name` (str): Author alias/another name

**Usage Example:**

```python
authors = client.get_authors(floor_id=27, initial="う", hits=10)
for author in authors:
    print(f"Author: {author.name}")
    print(f"ID: {author.author_id}")
    print(f"Ruby: {author.ruby}")
    if author.another_name:
        print(f"Also known as: {author.another_name}")
```

Reference: `docs/development.md`

### Exception Handling

The library provides custom exceptions for better error handling:

#### DMMError

Base exception class for all py-dmm errors.

**Attributes:**

- `message` (str): The error message
- `details` (Optional[Any]): Additional error details

**Usage Example:**

```python
from py_dmmjp.exceptions import DMMError

try:
    # Your code here
    pass
except DMMError as e:
    print(f"Error: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

#### DMMAPIError

Exception raised for API-related errors. Inherits from `DMMError`.

**Attributes:**

- `message` (str): The error message
- `status_code` (Optional[int]): HTTP status code of the failed request
- `response_data` (Optional[Any]): Raw response data from the API

**Usage Example:**

```python
from py_dmmjp.exceptions import DMMAPIError

try:
    products = client.get_products(site="FANZA", service="digital", floor="videoa")
except DMMAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response_data}")
```

#### DMMAuthError

Exception raised for authentication-related errors. Inherits from `DMMError`.

**Attributes:**

- `message` (str): The error message (default: "Authentication failed")

**Usage Example:**

```python
from py_dmmjp import DMMClient
from py_dmmjp.exceptions import DMMAuthError

try:
    client = DMMClient(api_key="invalid_key", affiliate_id="invalid_id")
    products = client.get_products(site="FANZA")
except DMMAuthError as e:
    print(f"Authentication Error: {e.message}")
```

## Development

### Setup Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/richardnguyen99/py-dmmjp.git
   cd py-dmmjp
   ```

2. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=py_dmm

# Run specific test file
pytest tests/test_series_dvd.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to:

1. Update tests as appropriate
2. Follow the existing code style (black + isort)
3. Add type hints to new code
4. Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Support

- 📖 [Documentation](https://py-dmmjp.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/richardnguyen99/py-dmmjp/issues)
- 💬 [Discussions](https://github.com/richardnguyen99/py-dmmjp/discussions)
