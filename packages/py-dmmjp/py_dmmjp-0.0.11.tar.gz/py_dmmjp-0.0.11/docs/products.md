# Product API

Documentation to use Py-DMMJP Client with DMM API ItemList:

See: [https://affiliate.dmm.com/api/v3/itemlist.html](https://affiliate.dmm.com/api/v3/itemlist.html)

## Request parameters

| Parameter Name | Parameter Key | Required | Sample Value | Description |
|---|---|---|---|---|
| API ID | `api_id` | ○ | | ID assigned during registration |
| Affiliate ID | `affiliate_id` | ○ | `affiliate-990` | Affiliate ID from 990-999 assigned during registration |
| Site | `site` | ○ | `FANZA` | General (DMM.com) or Adult (FANZA) |
| Service | `service` | | `digital` | Service code obtained from [Floor API](/api/v3/floorlist.html) |
| Floor | `floor` | | `videoa` | Floor code obtained from [Floor API](/api/v3/floorlist.html) |
| Number of Results | `hits` | | `20` | Default: 20, Maximum: 100 |
| Search Start Position | `offset` | | `1` | Default: 1, Maximum: 50000 |
| Sort Order | `sort` | | `rank` | Default: `rank`. Options: `rank` (popularity), `price` (high to low), `-price` (low to high), `date` (release date), `review` (rating), `match` (relevance) |
| Keyword | `keyword` | | `松本いちか` | Specify in UTF-8. See [Keyword Search Tips](https://support.dmm.com/others/article/12107) |
| Product ID | `cid` | | `mizd00320` | Content ID assigned to the product |
| Filter Category | `article` | | `actress` | Filter types: `actress`, `author`, `genre`, `series`, `maker`. For multiple filters, use array notation: `&article[0]=genre&article[1]=actress` |
| Filter ID | `article_id` | | `1011199` | ID for the above filter categories (obtainable from respective search APIs). For multiple filters, use array notation: `&article_id[0]=111111&article_id[1]=222222` |
| Release Date Filter (From) | `gte_date` | | `2016-04-01T00:00:00` | Filter products released on or after this date. Specify date in [ISO8601](https://www.w3.org/TR/NOTE-datetime) format (timezone not supported) |
| Release Date Filter (To) | `lte_date` | | `2016-04-30T23:59:59` | Filter products released on or before this date. Same format as `gte_date` |
| Stock Filter | `mono_stock` | | `mono` | Options: `stock` (in stock), `reserve` (pre-order in stock), `reserve_empty` (pre-order waiting list), `mono` (DMM direct only), `dmp` (marketplace only). *Only available for retail services |
| Output Format | `output` | | `json` | `json` / `xml` |
| Callback | `callback` | | `callback` | When output format is JSON, specify callback function name for JSONP output |

## Response object

### Schema

| Field | Description | Example |
|---|---|---|
| **request** | | |
| └ **parameters** | | |
| &nbsp;&nbsp;&nbsp;&nbsp;└ **parameter** | Request parameter | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Parameter name | `site` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **value** | Value | `FANZA` |
| **result** | | |
| ├ **status** | Status code | `200` |
| ├ **result_count** | Number of results retrieved | `20` |
| ├ **total_count** | Total number of results | `50000` |
| ├ **first_position** | Search start position | `1` |
| ├ **items** | Product information | |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **service_code** | Service code | `digital` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **service_name** | Service name | `動画` (Video) |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **floor_code** | Floor code | `videoa` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **floor_name** | Floor name | `ビデオ` (Video) |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **category_name** | Category name | `ビデオ (動画)` (Video) |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **content_id** | Product ID | `15dss00145` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **product_id** | Product number | `15dss00145dl` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **title** | Title | `GET！！ 素人ナンパ Best100！！ 街角女子ベスト100人 8時間` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **volume** | Runtime or page count | `350` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **number** | Volume number | `3` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **review** | Review information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **count** | Number of reviews | `8` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **average** | Average review score | `3.13` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **URL** | Product page URL | `http://video.dmm.co.jp/av/content/?id=15dss00145` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **affiliateURL** | Affiliate link URL | `https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Fcontent%2F%3Fid%3D15dss00145&af_id=affiliate-990&ch=api` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **imageURL** | Image URLs | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **list** | List page image | `http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145pt.jpg` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **small** | Small image | `http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145ps.jpg` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **large** | Large image | `http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145pl.jpg` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **tachiyomi** | Preview information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **URL** | Preview page URL | `http://book.dmm.co.jp/tachiyomi/?product_id=b468acown00017&item_id=b468acown00017&shop=digital_book` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **affiliateURL** | Preview affiliate link URL | `https://al.fanza.co.jp/?lurl=http%3A%2F%2Fbook.dmm.co.jp%2Ftachiyomi%2F%3Fproduct_id%3Db468acown00017%26item_id%3Db468acown00017%26shop%3Ddigital_book&af_id=affiliate-990&ch=api` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **sampleImageURL** | Sample image URLs | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **sample_s** | Small sample images list | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **image** | Small sample image | `http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145-1.jpg` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **sample_l** | Large sample images list | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **image** | Large sample image | `http://pics.dmm.co.jp/digital/video/15dss00145/15dss00145jp-1.jpg` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **sampleMovieURL** | Sample video URLs | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **size_476_306** | 476×306 video | `http://www.dmm.co.jp/litevideo/-/part/=/cid=15dss145/size=476_306/affi_id=affiliate-990/` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **size_560_360** | 560×360 video | `http://www.dmm.co.jp/litevideo/-/part/=/cid=15dss145/size=560_360/affi_id=affiliate-990/` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **size_644_414** | 644×414 video | `http://www.dmm.co.jp/litevideo/-/part/=/cid=15dss145/size=644_414/affi_id=affiliate-990/` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **size_720_480** | 720×480 video | `http://www.dmm.co.jp/litevideo/-/part/=/cid=15dss145/size=720_480/affi_id=affiliate-990/` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **pc_flag** | PC compatible | `1` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **sp_flag** | Smartphone compatible | `1` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **prices** | Pricing information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **price** | Price | `300～` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **list_price** | List price | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **deliveries** | Delivery options list | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **delivery** | Delivery option | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **type** | Delivery type | `stream` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **price** | Delivery price | `300` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **date** | Release/distribution/rental start date | `2012/8/3 10:00` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **iteminfo** | Product details | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **genre** | Genre information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Genre name | `ベスト・総集編` (Best/Compilation) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Genre ID | `6003` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **series** | Series information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Series name | `GETシリーズ` (GET Series) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Series ID | `1006` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **maker** | Maker information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Maker name | `桃太郎映像出版` (Momotaro Eizo) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Maker ID | `40016` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **actor** | Actor information (general works only) | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Actor name | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Actor ID | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **actress** | Actress information (adult works only) | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Actress name | `小澤マリア` (Maria Ozawa) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Actress ID | `15187` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **director** | Director information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Director name | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Director ID | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **author** | Author/Creator information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Author name | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Author ID | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **label** | Label information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Label name | `LADY HUNTERS` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Label ID | `76` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **type** | Type information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Type name | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Type ID | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **color** | Color information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Color name | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Color ID | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **size** | Size information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **name** | Size name | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **id** | Size ID | |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **cdinfo** | CD information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **kind** | Album or single | |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **jancode** | JAN code | `4988135965905` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **maker_product** | Maker product number | `10003-54653` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **isbn** | ISBN | |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **stock** | Stock status | `reserve` |
| &nbsp;&nbsp;&nbsp;&nbsp;├ **directory** | Breadcrumb navigation | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **id** | Breadcrumb ID | `783` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **name** | Breadcrumb name | `J-POP等` (J-POP etc.) |
| &nbsp;&nbsp;&nbsp;&nbsp;└ **campaign** | Campaign information | |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **date_begin** | Campaign start date | `2023-05-01 10:00:00` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├ **date_end** | Campaign end date | `2023-05-31 23:59:59` |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ **title** | Campaign title | |

### Sample response

```json
{
  "request": {
    "parameters": {
      "api_id": "example-api-id",
      "affiliate_id": "example-affiliate-id",
      "site": "FANZA",
      "service": "mono",
      "floor": "dvd",
      "keyword": "sone-156",
      "output": "json"
    }
  },
  "result": {
    "status": 200,
    "result_count": 1,
    "total_count": 1,
    "first_position": 1,
    "items": [
      {
        "service_code": "mono",
        "service_name": "通販",
        "floor_code": "dvd",
        "floor_name": "DVD",
        "category_name": "DVD通販",
        "content_id": "sone156",
        "product_id": "sone156",
        "title": "女教師 リモートイカされ エロチャット副業がバレた先生は投げ銭バイブで公開調教される一部始終を配信されて… うんぱい",
        "volume": "150",
        "review": {
          "count": 26,
          "average": "3.92"
        },
        "URL": "https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=sone156/",
        "affiliateURL": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Fdetail%2F%3D%2Fcid%3Dsone156%2F&af_id=***REDACTED_AFF_ID***&ch=api",
        "imageURL": {
          "list": "https://pics.dmm.co.jp/mono/movie/adult/sone156/sone156pt.jpg",
          "small": "https://pics.dmm.co.jp/mono/movie/adult/sone156/sone156ps.jpg",
          "large": "https://pics.dmm.co.jp/mono/movie/adult/sone156/sone156pl.jpg"
        },
        "sampleImageURL": {
          "sample_s": {
            "image": [
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-1.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-2.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-3.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-4.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-5.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-6.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-7.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-8.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-9.jpg",
              "https://pics.dmm.co.jp/digital/video/sone00156/sone00156-10.jpg"
            ]
          }
        },
        "prices": {
          "price": "2273",
          "list_price": "3498"
        },
        "date": "2024-04-23 10:00:00",
        "iteminfo": {
          "genre": [
            {
              "id": 300541,
              "name": "秋のシコシコ強化月間"
            },
            {
              "id": 6102,
              "name": "サンプル動画"
            },
            {
              "id": 4009,
              "name": "巨乳フェチ"
            },
            {
              "id": 1016,
              "name": "女教師"
            },
            {
              "id": 6968,
              "name": "アクメ・オーガズム"
            },
            {
              "id": 4114,
              "name": "ドラマ"
            },
            {
              "id": 5017,
              "name": "おもちゃ"
            },
            {
              "id": 4025,
              "name": "単体作品"
            }
          ],
          "maker": [
            {
              "id": 3152,
              "name": "エスワン ナンバーワンスタイル"
            }
          ],
          "actress": [
            {
              "id": 1074740,
              "name": "うんぱい",
              "ruby": "うんぱい"
            }
          ],
          "director": [
            {
              "id": 106690,
              "name": "前田文豪",
              "ruby": "まえだぶんごう"
            }
          ],
          "label": [
            {
              "id": 3474,
              "name": "S1 NO.1 STYLE"
            }
          ]
        },
        "jancode": "4550566108741",
        "maker_product": "SONE-156",
        "stock": "stock",
        "directory": [
          {
            "id": 764,
            "name": "DVD"
          }
        ]
      },
    ]
  }
}
```

## Method result

### Product object

`Product` class (defined at [py_dmmjp/product.py](https://github.com/richardnguyen99/py-dmmjp/blob/main/py_dmmjp/product.py)) define attributes that can be retrieved from the DMM API response. Those attributes are native and defined at Response object.
