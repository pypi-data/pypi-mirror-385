# Series API

Documentation to use Py-DMMJP Client with DMM API SeriesSearch:

See: [https://affiliate.dmm.com/api/v3/seriessearch.html](https://affiliate.dmm.com/api/v3/seriessearch.html)

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
| ├ site_name | Site name | DMM.com（一般） |
| ├ site_code | Site code | DMM.com |
| ├ service_name | Service name | 通販 |
| ├ service_code | Service code | mono |
| ├ floor_id | Floor ID | 24 |
| ├ floor_name | Floor name | 本・コミック |
| ├ floor_code | Floor code | book |
| └ series | Series information |  |
| 　　├ series_id | Series ID | 62226 |
| 　　├ name | Series name | ARIA |
| 　　├ ruby | Series name (phonetic reading) | ありあ |
| 　　└ list_url | List page URL (with affiliate ID) | <https://al.dmm.com/?lurl=http%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D62226%2F&af_id=affiliate-001&ch=api> |

### Sample response

```json
{
    "request": {
        "parameters": {
            "api_id": "example",
            "affiliate_id": "affiliate-990",
            "floor_id": "27",
            "initial": "お",
            "hits": "10",
            "output": "json"
        }
    },
    "result": {
        "status": "200",
        "result_count": 10,
        "total_count": "970",
        "first_position": 1,
        "site_name": "DMM.com（一般）",
        "site_code": "DMM.com",
        "service_name": "通販",
        "service_code": "mono",
        "floor_id": "27",
        "floor_name": "本・コミック",
        "floor_code": "book",
        "series": [
            {
                "series_id": "105331",
                "name": "おあいにくさま二ノ宮くん",
                "ruby": "おあいにくさまにのみやくん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D105331%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "112264",
                "name": "お家さん",
                "ruby": "おいえさん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D112264%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "115305",
                "name": "オイ！！オバさん",
                "ruby": "おいおばさん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D115305%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "105332",
                "name": "おいしい関係",
                "ruby": "おいしいかんけい",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D105332%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "100864",
                "name": "おいしい銀座",
                "ruby": "おいしいぎんざ",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D100864%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "110050",
                "name": "おいしいコーヒーのいれ方",
                "ruby": "おいしいこーひーのいれかた",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D110050%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "112232",
                "name": "おいしい生活",
                "ruby": "おいしいせいかつ",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D112232%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "112231",
                "name": "おいしいパン屋さん",
                "ruby": "おいしいぱんやさん",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D112231%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "62647",
                "name": "おいしいプロポーズ",
                "ruby": "おいしいぷろぽーず",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D62647%2F&af_id=affiliate-990&ch=api"
            },
            {
                "series_id": "116147",
                "name": "おいしい学び夜",
                "ruby": "おいしいまなびや",
                "list_url": "https://al.dmm.com/?lurl=https%3A%2F%2Fwww.dmm.com%2Fmono%2Fbook%2F-%2Flist%2F%3D%2Farticle%3Dseries%2Fid%3D116147%2F&af_id=affiliate-990&ch=api"
            }
        ]
    }
}
```
