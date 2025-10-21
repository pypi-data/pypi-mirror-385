# Genre API

Documentation to use Py-DMMJP Client with DMM API GenreSearch:

See: [https://affiliate.dmm.com/api/v3/genresearch.html](https://affiliate.dmm.com/api/v3/genresearch.html)

## Request parameters

| Logical Name | Physical Name | Required | Sample Value | Description |
|--------------|---------------|----------|--------------|-------------|
| API ID | api_id | ○ | | ID assigned during registration |
| Affiliate ID | affiliate_id | ○ | affiliate-990 | Affiliate ID from 990-999 assigned during registration |
| Floor ID | floor_id | ○ | | Floor ID available from Floor Search API |
| Initial (50-sound) | initial | | あ | Specify 50-sound in UTF-8 |
| Number of hits | hits | | 100 | Default: 100, Maximum: 500 |
| Search start position | offset | | 1 | Default: 1 |
| Output format | output | | json | json / xml |
| Callback | callback | | callback | When json is specified as output format, specifying a callback function name with this parameter will output in JSONP format |

## Response object

### Schema

| Field | Description | Example |
|-------|-------------|---------|
| request |  |  |
| parameters |  |  |
| └ parameter | Request parameters |  |
| 　　├ name | Parameter name | affiliate_id |
| 　　└ value | Value | affiliate-990 |
| result |  |  |
| ├ status | Status code | 200 |
| ├ result_count | Number of results | 100 |
| ├ total_count | Total count | 1000 |
| ├ first_position | Search start position | 1 |
| ├ site_name | Site name | FANZA（アダルト） |
| ├ site_code | Site code | FANZA |
| ├ service_name | Service name | 動画 |
| ├ service_code | Service code | digital |
| ├ floor_id | Floor ID | 40 |
| ├ floor_name | Floor name | ビデオ |
| ├ floor_code | Floor code | videoa |
| └ genre | Genre information |  |
| 　　├ genre_id | Genre ID | 2001 |
| 　　├ name | Genre name | 巨乳 |
| 　　├ ruby | Genre name (phonetic reading) | きょにゅう |
| 　　└ list_url | List page URL (with affiliate ID) | <https://al.fanza.co.jp/?lurl=http%3A%2F%2Fwww.dmm.co.jp%2Fdigital%2Fvideoa%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D2001%2F&af_id=affiliate-001&ch=api> |

### Sample response

```json
{
    "request": {
        "parameters": {
            "api_id": "example",
            "affiliate_id": "affiliate-990",
            "floor_id": "25",
            "initial": "き",
            "hits": "10",
            "offset": "10",
            "output": "json"
        }
    },
    "result": {
        "status": "200",
        "result_count": 10,
        "total_count": "20",
        "first_position": 10,
        "site_name": "DMM.com（一般）",
        "site_code": "DMM.com",
        "service_name": "通販",
        "service_code": "mono",
        "floor_id": "25",
        "floor_name": "DVD・Blu-ray",
        "floor_code": "dvd",
        "genre": [
            {
                "genre_id": "73115",
                "name": "キャラクター",
                "ruby": "きゃらくたー",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D73115%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "78012",
                "name": "キャラクター",
                "ruby": "きゃらくたー",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D78012%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "138",
                "name": "キャンペーン対象商品",
                "ruby": "きゃんぺーんたいしょうしょうひん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D138%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "73145",
                "name": "教育",
                "ruby": "きょういく",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D73145%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "66352",
                "name": "競泳・スクール水着",
                "ruby": "きょうえいすくーるみずぎ",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D66352%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "71142",
                "name": "近未来",
                "ruby": "きんみらい",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D71142%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "72138",
                "name": "近未来",
                "ruby": "きんみらい",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D72138%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "78038",
                "name": "近未来",
                "ruby": "きんみらい",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D78038%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "73130",
                "name": "近未来",
                "ruby": "きんみらい",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D73130%2F&af_id=affiliate-990&ch=api"
            },
            {
                "genre_id": "70027",
                "name": "近未来",
                "ruby": "きんみらい",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dkeyword%2Fid%3D70027%2F&af_id=affiliate-990&ch=api"
            }
        ]
    }
}
```
