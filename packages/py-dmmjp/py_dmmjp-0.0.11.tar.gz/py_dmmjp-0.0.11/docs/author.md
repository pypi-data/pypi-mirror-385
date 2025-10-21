# Author API

Documentation to use Py-DMMJP Client with DMM API AuthorSearch:

See: [https://affiliate.dmm.com/api/v3/authorsearch.html](https://affiliate.dmm.com/api/v3/authorsearch.html)

## Request parameters

| Logical Name | Physical Name | Required | Sample Value | Description |
|--------------|---------------|----------|--------------|-------------|
| API ID | api_id | ○ | | ID assigned during registration |
| Affiliate ID | affiliate_id | ○ | affiliate-990 | Affiliate ID from 990-999 assigned during registration |
| Floor ID | floor_id | ○ | | Floor ID available from Floor Search API |
| Phonetic reading | initial | | う゛ぃくとる | Specify author name (phonetic reading) in UTF-8, performs forward match search |
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
| ├ site_name | Site name | DMM.com（一般） |
| ├ site_code | Site code | DMM.com |
| ├ service_name | Service name | 通販 |
| ├ service_code | Service code | mono |
| ├ floor_id | Floor ID | 24 |
| ├ floor_name | Floor name | 本・コミック |
| ├ floor_code | Floor code | book |
| └ author | Author information |  |
| 　　├ author_id | Author ID | 21414 |
| 　　├ name | Author name | ヴィクトル・ユゴー |
| 　　├ ruby | Author name (phonetic reading) | う゛ぃくとるゆごー |
| 　　├ another_name | Author alias | ヴィクトル・ユーゴー/ヴィクトル=ユーゴー |
| 　　└ list_url | List page URL (with affiliate ID) | <https://al.dmm.com/?lurl=http%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D21414%2F&af_id=affiliate-990&ch=api> |

### Sample response

```json
{
    "request": {
        "parameters": {
            "api_id": "example",
            "affiliate_id": "affiliate-990",
            "floor_id": "27",
            "initial": "う",
            "hits": "10",
            "output": "json"
        }
    },
    "result": {
        "status": "200",
        "result_count": 10,
        "total_count": "2311",
        "first_position": 1,
        "site_name": "DMM.com（一般）",
        "site_code": "DMM.com",
        "service_name": "通販",
        "service_code": "mono",
        "floor_id": "27",
        "floor_name": "本・コミック",
        "floor_code": "book",
        "author": [
            {
                "author_id": "182179",
                "name": "王青翔",
                "ruby": "うぁんちぃんしゃん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D182179%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108270",
                "name": "ウィクセル",
                "ruby": "うぃくせる",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108270%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108293",
                "name": "魏晶玄",
                "ruby": "うぃじょんひょん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108293%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108295",
                "name": "ウィスット・ポンニミット",
                "ruby": "うぃすっとぽんにみっと",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108295%2F&af_id=affiliate-990&ch=api",
                "another_name": "W.ポンニミット"
            },
            {
                "author_id": "20085",
                "name": "WIZ",
                "ruby": "うぃず",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D20085%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108309",
                "name": "ウィックスティード",
                "ruby": "うぃっくすてぃーど",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108309%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108314",
                "name": "ウィティ・イヒマエラ",
                "ruby": "うぃてぃいひまえら",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108314%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108316",
                "name": "ウィトゲンシュタイン",
                "ruby": "うぃとげんしゅたいん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108316%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108322",
                "name": "ウィニコット",
                "ruby": "うぃにこっと",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108322%2F&af_id=affiliate-990&ch=api"
            },
            {
                "author_id": "108332",
                "name": "ウィラサクレック・ウォンパーサー",
                "ruby": "うぃらさくれっくうぉんぱーさー",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dauthor%2Fid%3D108332%2F&af_id=affiliate-990&ch=api"
            }
        ]
    }
}
```
