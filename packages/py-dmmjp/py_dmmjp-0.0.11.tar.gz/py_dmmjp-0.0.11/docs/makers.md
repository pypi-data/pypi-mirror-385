# Maker API

Documentation to use Py-DMMJP Client with DMM API MakerSearch:

See: [https://affiliate.dmm.com/api/v3/makersearch.html](https://affiliate.dmm.com/api/v3/makersearch.html)

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
| └ maker | Maker information |  |
| 　　├ maker_id | Maker ID | 1509 |
| 　　├ name | Maker name | ムーディーズ |
| 　　├ ruby | Maker name (phonetic reading) | むーでぃーず |
| 　　└ list_url | List page URL (with affiliate ID) | <https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D1509&af_id=affiliate-990&ch=api> |

### Sample response

```json
{
    "request": {
        "parameters": {
            "api_id": "example",
            "affiliate_id": "affiliate-990",
            "floor_id": "43",
            "hits": "10",
            "offset": "100",
            "output": "json"
        }
    },
    "result": {
        "status": "200",
        "result_count": 10,
        "total_count": "4739",
        "first_position": 100,
        "site_name": "FANZA（アダルト）",
        "site_code": "FANZA",
        "service_name": "動画",
        "service_code": "digital",
        "floor_id": "43",
        "floor_name": "ビデオ",
        "floor_code": "videoa",
        "maker": [
            {
                "maker_id": "45556",
                "name": "あたご屋",
                "ruby": "あたごや",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D45556%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "306073",
                "name": "あたご屋/エマニエル",
                "ruby": "あたごやえまにえる",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D306073%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "1227",
                "name": "アタッカーズ",
                "ruby": "あたっかーず",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D1227%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "1228",
                "name": "アタック クィーン",
                "ruby": "あたっくくぃーん",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D1228%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "66056",
                "name": "ATTACK ZONE",
                "ruby": "あたっくぞーん",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D66056%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "46726",
                "name": "アダム書房",
                "ruby": "あだむしょぼう",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D46726%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "4068",
                "name": "あだると！",
                "ruby": "あだると",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D4068%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "4211",
                "name": "アダルトカンパニー",
                "ruby": "あだるとかんぱにー",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D4211%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "5879",
                "name": "アックスユー",
                "ruby": "あっくすゆー",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D5879%2F&af_id=affiliate-990&ch=api"
            },
            {
                "maker_id": "4029",
                "name": "アップグレート",
                "ruby": "あっぷぐれーと",
                "list_url": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Fmaker%3D4029%2F&af_id=affiliate-990&ch=api"
            }
        ]
    }
}
```
