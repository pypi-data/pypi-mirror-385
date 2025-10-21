"""

Data models for the py-dmm library.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from .commons import ApiRequest


class ProductSearchParams(TypedDict, total=False):
    """Type definition for product search parameters."""

    site: Literal["FANZA", "DMM.com"]
    service: str
    floor: str
    keyword: str
    hits: int
    offset: int
    sort: str
    cid: str
    article: List[str]
    article_id: List[str]
    gte_date: str
    lte_date: str
    mono_stock: str


@dataclass
class Review:
    """Represents product review data."""

    count: int
    average: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        """Create Review from dictionary."""

        return cls(
            count=int(data.get("count", 0)), average=float(data.get("average", "0"))
        )


@dataclass
class ImageURL:
    """Represents product image URLs in different sizes."""

    list: Optional[str] = None
    "List page image URL (e.g., http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145pt.jpg)"

    small: Optional[str] = None
    "Small image URL for thumbnails (e.g., http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145ps.jpg)"

    large: Optional[str] = None
    "Large image URL for detailed view (e.g., http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145pl.jpg)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageURL":
        """Create ImageURL from dictionary."""

        return cls(
            list=data.get("list"), small=data.get("small"), large=data.get("large")
        )


@dataclass
class SampleImage:
    """Represents individual sample image data."""

    image: List[str] = field(default_factory=list)
    "List of sample image URLs."

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleImage":
        """Create SampleImage from dictionary."""

        return cls(image=data.get("image", ""))


@dataclass
class SampleImages:
    """Represents product sample image collections in different sizes."""

    sample_s: SampleImage = field(default_factory=SampleImage)
    "Small sample images list (e.g., 'http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145-1.jpg')"

    sample_l: SampleImage = field(default_factory=SampleImage)
    "Large sample images list (e.g., 'http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145jp-1.jpg')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleImages":
        """Create SampleImages from dictionary."""

        sample_s = SampleImage.from_dict(data.get("sample_s", {}))
        sample_l = SampleImage.from_dict(data.get("sample_l", {}))

        return cls(sample_s=sample_s, sample_l=sample_l)


@dataclass
class SampleMovieURL:
    """Represents sample video URLs and compatibility information."""

    size_476_306: Optional[str] = None
    "Sample video URL in 476x306 resolution (e.g., 'http://cc3001.dmm.co.jp/litevideo/freepv/15dss00145_mhb_w.mp4')"

    size_560_360: Optional[str] = None
    "Sample video URL in 560x360 resolution (e.g., 'http://cc3001.dmm.co.jp/litevideo/freepv/15dss00145_dm_w.mp4')"

    size_644_414: Optional[str] = None
    "Sample video URL in 644x414 resolution (e.g., 'http://cc3001.dmm.co.jp/litevideo/freepv/15dss00145_dmb_w.mp4')"

    size_720_480: Optional[str] = None
    "Sample video URL in 720x480 resolution (e.g., 'http://cc3001.dmm.co.jp/litevideo/freepv/15dss00145_sm_w.mp4')"

    pc_flag: Optional[int] = None
    "PC compatibility flag (1 for compatible, 0 for not compatible)"

    sp_flag: Optional[int] = None
    "Smartphone compatibility flag (1 for compatible, 0 for not compatible)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleMovieURL":
        """Create SampleMovieURL from dictionary."""

        return cls(
            size_476_306=data.get("size_476_306"),
            size_560_360=data.get("size_560_360"),
            size_644_414=data.get("size_644_414"),
            size_720_480=data.get("size_720_480"),
            pc_flag=data.get("pc_flag"),
            sp_flag=data.get("sp_flag"),
        )


@dataclass
class TachiyomiInfo:
    """Represents product preview information and links."""

    url: Optional[str] = None
    "Direct preview page URL (e.g., 'http://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_048416/')"

    affiliate_url: Optional[str] = None
    "Affiliate preview page URL with tracking parameters"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TachiyomiInfo":
        """Create TachiyomiInfo from dictionary."""

        return cls(
            url=data.get("URL"),
            affiliate_url=data.get("affiliateURL"),
        )


@dataclass
class Delivery:
    """Represents product delivery options and pricing."""

    type: str
    "Delivery type (e.g., 'download', 'streaming', 'rental')"

    price: str
    "Delivery price with currency symbol (e.g., '¥1980', '¥500')"

    list_price: str
    "Original list price before discount (e.g., '¥1980', '¥1500')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Delivery":
        """Create Delivery from dictionary."""

        return cls(
            type=data.get("type", ""),
            price=data.get("price", ""),
            list_price=data.get("list_price", ""),
        )


@dataclass
class Prices:
    """Represents product pricing and delivery information."""

    price: Optional[str] = None
    "Current sale price with currency symbol (e.g., '¥1584', '¥980')"

    list_price: Optional[str] = None
    "Original list price before discount (e.g., '¥1980', '¥1500')"

    deliveries: List[Delivery] = field(default_factory=list)
    "Available delivery options with their respective pricing"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prices":
        """Create Prices from dictionary."""

        deliveries = []
        if "deliveries" in data and "delivery" in data["deliveries"]:
            delivery_data = data["deliveries"]["delivery"]
            deliveries = [Delivery.from_dict(d) for d in delivery_data]

        return cls(
            price=data.get("price"),
            list_price=data.get("list_price"),
            deliveries=deliveries,
        )

    @property
    def price_int(self) -> Optional[int]:
        """Get price as integer."""

        if self.price:
            match = re.search(r"\d+", self.price)

            return int(match.group()) if match else None

        return None

    @property
    def list_price_int(self) -> Optional[int]:
        """Get list price as integer."""

        if self.list_price:
            match = re.search(r"\d+", self.list_price)

            return int(match.group()) if match else None

        return None


@dataclass
class ItemInfo:
    """Represents detailed information about product-related items."""

    id: int
    "Unique identifier for the item (e.g., 12345, 67890)"

    name: str
    "Item name in Japanese (e.g., 'アダルト', 'S1 NO.1 STYLE', '明日花キララ')"

    ruby: Optional[str] = None
    "Phonetic reading in hiragana/katakana (e.g., 'あだると', 'あすかきらら')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemInfo":
        """Create ItemInfo from dictionary."""

        return cls(
            id=int(data.get("id", 0)), name=data.get("name", ""), ruby=data.get("ruby")
        )


@dataclass
class ItemDetails:
    """Represents comprehensive product metadata and categorization information."""

    genre: List[ItemInfo] = field(default_factory=list)
    "Product genres/categories (e.g., 'アダルト', 'ドラマ', 'コメディ')"

    series: List[ItemInfo] = field(default_factory=list)
    "Series information (e.g., 'S1 NO.1 STYLE', '本中', 'プレステージ')"

    maker: List[ItemInfo] = field(default_factory=list)
    "Production company/studio (e.g., 'エスワン ナンバーワンスタイル', 'プレステージ')"

    actress: List[ItemInfo] = field(default_factory=list)
    "Featured actresses (e.g., '明日花キララ', '桃乃木かな', '三上悠亜')"

    actor: List[ItemInfo] = field(default_factory=list)
    "Featured actors (e.g., '森林原人', 'イケメン翔', 'ダイ')"

    director: List[ItemInfo] = field(default_factory=list)
    "Directors (e.g., 'きとるね川口', '本田教仁')"

    author: List[ItemInfo] = field(default_factory=list)
    "Authors for written content (e.g., manga/book authors)"

    label: List[ItemInfo] = field(default_factory=list)
    "Publishing label/brand (e.g., 'S1 NO.1 STYLE', 'プレステージ')"

    type: List[ItemInfo] = field(default_factory=list)
    "Content type classification (e.g., 'ダウンロード', 'ストリーミング')"

    color: List[ItemInfo] = field(default_factory=list)
    "Color attributes for physical products (e.g., 'ブラック', 'ホワイト')"

    size: List[ItemInfo] = field(default_factory=list)
    "Size attributes for physical products (e.g., 'M', 'L', 'XL')"

    manufacture: List[ItemInfo] = field(default_factory=list)
    "Manufacturer information for physical products (e.g., 'ソニー', 'パナソニック')"

    artist: List[ItemInfo] = field(default_factory=list)
    "Artist/composer (e.g., 'とうけんだんしふぉーめーしょんおぶみちのおくひとつはちす')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemDetails":
        """Create ItemDetails from dictionary."""

        def parse_items(key: str) -> List[ItemInfo]:
            items = data.get(key, [])

            return [ItemInfo.from_dict(item) for item in items]

        def parse_manufacture() -> List[ItemInfo]:
            items = data.get("manufacturer", data.get("manufacture", []))

            return [ItemInfo.from_dict(item) for item in items]

        return cls(
            genre=parse_items("genre"),
            series=parse_items("series"),
            maker=parse_items("maker"),
            actress=parse_items("actress"),
            actor=parse_items("actor"),
            director=parse_items("director"),
            author=parse_items("author"),
            label=parse_items("label"),
            type=parse_items("type"),
            color=parse_items("color"),
            size=parse_items("size"),
            manufacture=parse_manufacture(),
            artist=parse_items("artist"),
        )


@dataclass
class CDInfo:
    """Represents CD-specific product information."""

    kind: Optional[str] = None
    "CD type classification (e.g., 'album', 'single', 'compilation')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CDInfo":
        """Create CDInfo from dictionary."""

        return cls(kind=data.get("kind"))


@dataclass
class Directory:
    """Represents breadcrumb navigation directory information."""

    id: int
    "Directory/category ID for navigation (e.g., 1001, 2002)"

    name: str
    "Directory/category name in Japanese (e.g., 'ビデオ', 'DVD', 'アダルト')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Directory":
        """Create Directory from dictionary."""

        return cls(id=int(data.get("id", 0)), name=data.get("name", ""))


@dataclass
class Campaign:
    """Represents promotional campaign information for products."""

    date_begin: Optional[str] = None
    "Campaign start date (e.g., '2023-10-01', '2024-03-15')"

    date_end: Optional[str] = None
    "Campaign end date (e.g., '2023-10-31', '2024-03-31')"

    title: Optional[str] = None
    "Campaign title/description in Japanese (e.g., '半額セール', '新作キャンペーン')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        """Create Campaign from dictionary."""

        return cls(
            date_begin=data.get("date_begin"),
            date_end=data.get("date_end"),
            title=data.get("title"),
        )


@dataclass
class Product:
    """Represents a complete product from the DMM API with all available metadata."""

    service_code: str
    "Service code (e.g., 'digital', 'mono')"

    service_name: str
    "Service name (e.g., '動画' for Video, '通販' for Shopping)"

    floor_code: str
    "Floor code (e.g., 'videoa', 'dvd')"

    floor_name: str
    "Floor name (e.g., 'ビデオ' for Video, 'DVD')"

    category_name: str
    "Category name (e.g., 'ビデオ (動画)' for Video, 'DVD通販' for DVD Shopping)"

    content_id: str
    "Product ID/Content ID (e.g., '15dss00145', 'sone156')"

    product_id: str
    "Product number/SKU (e.g., '15dss00145dl', 'sone156')"

    title: str
    "Product title"

    volume: Optional[Union[int, str]] = None
    "Runtime in minutes for videos or page count for books (e.g., 350, 150)"

    number: Optional[Union[int, str]] = None
    "Volume number for series content (e.g., 3)"

    date: Optional[datetime] = None
    "Release/distribution/rental start date"

    url: Optional[str] = None
    "Product page URL (e.g., 'http://video.dmm.co.jp/av/content/?id=15dss00145')"

    affiliate_url: Optional[str] = None
    "Affiliate link URL with tracking parameters"

    image_url: Optional[ImageURL] = None
    "Product images in different sizes (list, small, large)"

    sample_image_url: Optional[SampleImages] = None
    "Sample/preview images for the product"

    sample_movie_url: Optional[SampleMovieURL] = None
    "Sample video URLs in different resolutions with compatibility flags"

    tachiyomi: Optional[TachiyomiInfo] = None
    "Preview page information and affiliate links"

    prices: Optional[Prices] = None
    "Pricing information including current price and delivery options"

    review: Optional[Review] = None
    "Customer review data with count and average rating"

    item_info: Optional[ItemDetails] = None
    "Detailed metadata including genres, series, makers, cast, and other categorization"

    jancode: Optional[str] = None
    "Japanese Article Number (JAN) barcode for physical products (e.g., '4988135965905')"

    maker_product: Optional[str] = None
    "Manufacturer's product identifier (e.g., '10003-54653', 'SONE-156')"

    isbn: Optional[str] = None
    "International Standard Book Number for publications"

    stock: Optional[str] = None
    "Stock status (e.g., 'reserve', 'stock')"

    directory: List[Directory] = field(default_factory=list)
    "Breadcrumb navigation path for product categorization"

    cdinfo: Optional[CDInfo] = None
    "CD-specific information for music products (album/single type)"

    campaign: Optional[List[Campaign]] = None
    "Active promotional campaign information with dates and title"

    _raw_data: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Original API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """

        Create a Product instance from a dictionary.

        Args:
            data: Dictionary containing product data from DMM API.

        Returns:
            Product instance.
        """

        date = None
        if "date" in data and data["date"]:
            try:
                date_str = data["date"]
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            except (ValueError, TypeError):
                date = None

        image_url = (
            ImageURL.from_dict(data.get("imageURL", {}))
            if data.get("imageURL")
            else None
        )

        sample_image_url = (
            SampleImages.from_dict(data.get("sampleImageURL", {}))
            if data.get("sampleImageURL")
            else None
        )

        sample_movie_url = (
            SampleMovieURL.from_dict(data.get("sampleMovieURL", {}))
            if data.get("sampleMovieURL")
            else None
        )

        tachiyomi = (
            TachiyomiInfo.from_dict(data.get("tachiyomi", {}))
            if data.get("tachiyomi")
            else None
        )

        prices = (
            Prices.from_dict(data.get("prices", {})) if data.get("prices") else None
        )

        review = (
            Review.from_dict(data.get("review", {})) if data.get("review") else None
        )

        item_info = (
            ItemDetails.from_dict(data.get("iteminfo", {}))
            if data.get("iteminfo")
            else None
        )

        cdinfo = (
            CDInfo.from_dict(data.get("cdinfo", {})) if data.get("cdinfo") else None
        )

        campaign = None
        if "campaign" in data and data["campaign"]:
            campaign_data = data.get("campaign", [])
            campaign = [Campaign.from_dict(c) for c in campaign_data]

        volume = None
        if "volume" in data and data["volume"]:
            volume_data = data["volume"]

            try:
                volume = int(volume_data)
            except (ValueError, TypeError):
                volume = volume_data

        number = None
        if "number" in data and data["number"]:
            number_data = data["number"]

            try:
                number = int(number_data)
            except (ValueError, TypeError):
                number = number_data

        directory = []
        if "directory" in data:
            dir_data = data.get("directory", [])
            directory = [Directory.from_dict(d) for d in dir_data]

        return cls(
            service_code=data.get("service_code", ""),
            service_name=data.get("service_name", ""),
            floor_code=data.get("floor_code", ""),
            floor_name=data.get("floor_name", ""),
            category_name=data.get("category_name", ""),
            content_id=data.get("content_id", ""),
            product_id=data.get("product_id", ""),
            title=data.get("title", ""),
            volume=volume,
            number=number,
            url=data.get("URL"),
            affiliate_url=data.get("affiliateURL"),
            image_url=image_url,
            sample_image_url=sample_image_url,
            sample_movie_url=sample_movie_url,
            tachiyomi=tachiyomi,
            prices=prices,
            review=review,
            date=date,
            jancode=data.get("jancode"),
            maker_product=data.get("maker_product"),
            isbn=data.get("isbn"),
            stock=data.get("stock"),
            item_info=item_info,
            directory=directory,
            cdinfo=cdinfo,
            campaign=campaign,
            _raw_data=data.copy(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """

        Convert the Product instance to a dictionary.

        Returns:
            Dictionary representation of the product.
        """

        result = {
            "service_code": self.service_code,
            "service_name": self.service_name,
            "floor_code": self.floor_code,
            "floor_name": self.floor_name,
            "category_name": self.category_name,
            "content_id": self.content_id,
            "product_id": self.product_id,
            "title": self.title,
            "volume": self.volume,
            "number": self.number,
            "URL": self.url,
            "affiliateURL": self.affiliate_url,
            "jancode": self.jancode,
            "maker_product": self.maker_product,
            "isbn": self.isbn,
            "stock": self.stock,
        }

        if self.date:
            result["date"] = self.date.strftime("%Y/%m/%d %H:%M")

        return result

    @property
    def raw_data(self) -> Optional[Dict[str, Any]]:
        """Access to raw API response data."""

        return self._raw_data

    @property
    def genres(self) -> List[ItemInfo]:
        """Get product genres."""

        return self.item_info.genre if self.item_info else []

    @property
    def actresses(self) -> List[ItemInfo]:
        """Get product actresses."""

        return self.item_info.actress if self.item_info else []

    @property
    def actors(self) -> List[ItemInfo]:
        """Get product actors."""

        return self.item_info.actor if self.item_info else []

    @property
    def manufactures(self) -> List[ItemInfo]:
        """Get product manufacturers."""

        return self.item_info.manufacture if self.item_info else []

    @property
    def artists(self) -> List[ItemInfo]:
        """Get product artists."""

        return self.item_info.artist if self.item_info else []

    @property
    def makers(self) -> List[ItemInfo]:
        """Get product makers."""

        return self.item_info.maker if self.item_info else []

    @property
    def series(self) -> List[ItemInfo]:
        """Get product series."""

        return self.item_info.series if self.item_info else []

    @property
    def directors(self) -> List[ItemInfo]:
        """Get product directors."""

        return self.item_info.director if self.item_info else []

    @property
    def authors(self) -> List[ItemInfo]:
        """Get product authors."""

        return self.item_info.author if self.item_info else []

    @property
    def labels(self) -> List[ItemInfo]:
        """Get product labels."""

        return self.item_info.label if self.item_info else []

    @property
    def types(self) -> List[ItemInfo]:
        """Get product types."""

        return self.item_info.type if self.item_info else []

    @property
    def colors(self) -> List[ItemInfo]:
        """Get product colors."""

        return self.item_info.color if self.item_info else []

    @property
    def sizes(self) -> List[ItemInfo]:
        """Get product sizes."""

        return self.item_info.size if self.item_info else []

    @property
    def sample_images(self) -> List[str]:
        """Get sample image URLs."""

        if self.sample_image_url and self.sample_image_url.sample_s:
            return list(self.sample_image_url.sample_s.image)

        return []

    @property
    def sample_images_large(self) -> List[str]:
        """Get large sample image URLs."""

        if self.sample_image_url and self.sample_image_url.sample_l:
            return list(self.sample_image_url.sample_l.image)
        return []

    @property
    def current_price(self) -> Optional[int]:
        """Get current price as integer."""

        return self.prices.price_int if self.prices else None

    @property
    def original_price(self) -> Optional[int]:
        """Get original list price as integer."""

        return self.prices.list_price_int if self.prices else None

    @property
    def review_count(self) -> int:
        """Get review count."""

        return self.review.count if self.review else 0

    @property
    def review_average(self) -> Optional[float]:
        """Get average review score as float."""

        if self.review and self.review.average:
            return float(self.review.average)

        return None


@dataclass
class ProductApiResult:
    """Represents the result section of the API response."""

    status: int
    "HTTP status code of the API response (e.g., 200, 404, 500)"

    result_count: int
    "Number of products returned in current response (e.g., 20, 50)"

    total_count: int
    "Total number of products matching the search criteria (e.g., 1500, 3200)"

    first_position: int
    "Position of first item in the overall result set (e.g., 1, 21, 41)"

    items: List[Product] = field(default_factory=list)
    "List of product items returned by the API"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductApiResult":
        """Create ProductApiResult from dictionary."""

        items = [Product.from_dict(item) for item in data.get("items", [])]

        return cls(
            status=data.get("status", 200),
            result_count=data.get("result_count", 0),
            total_count=data.get("total_count", 0),
            first_position=data.get("first_position", 1),
            items=items,
        )


@dataclass
class ProductApiResponse:
    """Represents the complete API response from DMM."""

    request: ApiRequest
    "Request information including parameters used for the API call"

    result: ProductApiResult
    "Result data containing products and metadata"

    _raw_response: Optional[Dict[str, Any]] = field(default=None, repr=False)
    "Complete raw API response data (internal use, not displayed)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductApiResponse":
        """

        Create ProductApiResponse from the full API response dictionary.

        Args:
            data: Complete API response dictionary.

        Returns:
            ApiResponse instance.
        """

        return cls(
            request=ApiRequest.from_dict(data.get("request", {})),
            result=ProductApiResult.from_dict(data.get("result", {})),
            _raw_response=data.copy(),
        )

    @property
    def raw_response(self) -> Optional[Dict[str, Any]]:
        """Access to the complete raw API response."""

        return self._raw_response

    @property
    def products(self) -> List[Product]:
        """Get all products from the response."""

        return self.result.items

    @property
    def product_count(self) -> int:
        """Get the number of products returned."""

        return self.result.result_count

    @property
    def total_products(self) -> int:
        """Get the total number of products available."""

        return self.result.total_count

    @property
    def status(self) -> int:
        """Get the API response status."""

        return self.result.status
