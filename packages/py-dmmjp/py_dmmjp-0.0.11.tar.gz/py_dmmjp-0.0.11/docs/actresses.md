# Actress API

Documentation to use Py-DMMJP Client with DMM API ActressSearch:

See: [https://affiliate.dmm.com/api/v3/actresssearch.html](https://affiliate.dmm.com/api/v3/actresssearch.html)

## Request parameters

| Logical Name | Physical Name | Required | Sample Value | Description |
|--------------|---------------|----------|--------------|-------------|
| API ID | api_id | ○ | | ID assigned during registration |
| Affiliate ID | affiliate_id | ○ | affiliate-990 | Affiliate ID from 990-999 assigned during registration |
| Initial (50-sound) | initial | | あ | Specify 50-sound in UTF-8 |
| Actress ID | actress_id | | 15365 | Actress ID |
| Keyword | keyword | | あさみ | Specify in UTF-8 |
| Bust | gte_bust, lte_bust | | 90 | gte_bust=90 means bust 90cm or more, lte_bust=90 means bust 90cm or less, gte_bust=90&lte_bust=100 means bust 90cm or more to 100cm or less |
| Waist | gte_waist, lte_waist | | 60 | Same as above |
| Hip | gte_hip, lte_hip | | 90 | Same as above |
| Height | gte_height, lte_height | | 160 | Same as above |
| Birthday | gte_birthday, lte_birthday | | 1990-01-01 | Specify in yyyymmdd format. gte_birthday=1990-01-01 means born on or after January 1, 1990. lte_birthday=1990-01-01 means born on or before January 1, 1990. gte_birthday=1980-01-01&lte_birthday=1989-12-31 means born from January 1, 1980 to December 31, 1989 |
| Number of hits | hits | | 20 | Default: 20, Maximum: 100 |
| Search start position | offset | | 1 | Default: 1 |
| Sort order | sort | | -name | Name ascending: name, Name descending: -name, Bust ascending: bust, Bust descending: -bust, Waist ascending: waist, Waist descending: -waist, Hip ascending: hip, Hip descending: -hip, Height ascending: height, Height descending: -height, Birthday ascending: birthday, Birthday descending: -birthday, Actress ID ascending: id, Actress ID descending: -id |
| Output format | output | | json | json / xml |
| Callback | callback | | callback | When json is specified as output format, specifying a callback function name with this parameter will output in JSONP format |

## Response object

### Schema

| Field | Description | Example |
|-------|-------------|---------|
| request |  |  |
| parameters |  |  |
| └ parameter | Request parameters |  |
| 　　├ name | Parameter name | keyword |
| 　　└ value | Value | あさみ |
| result |  |  |
| ├ status | Status code | 200 |
| ├ result_count | Number of results | 20 |
| ├ total_count | Total count | 64964 |
| ├ first_position | Search start position | 1 |
| └ actress | Actress information |  |
| 　├ id | Actress ID | 15365 |
| 　├ name | Actress name | 麻美ゆま |
| 　├ ruby | Actress name (phonetic reading) | あさみゆま |
| 　├ bust | Bust | 96 |
| 　├ cup | Cup size | H |
| 　├ waist | Waist | 58 |
| 　├ hip | Hip | 88 |
| 　├ height | Height | 158 |
| 　├ birthday | Birthday | 1987-03-24 |
| 　├ blood_type | Blood type | AB |
| 　├ hobby | Hobby | 香水集め、英会話、ピアノ |
| 　├ prefectures | Birthplace | 東京都 |
| 　├ imageURL | Image URL |  |
| 　　├ small | Image (small) | <http://pics.dmm.co.jp/mono/actjpgs/thumbnail/asami_yuma.jpg> |
| 　　└ large | Image (large) | <http://pics.dmm.co.jp/mono/actjpgs/asami_yuma.jpg> |
| 　└ listURL | List page URL (with affiliate ID) |  |
| 　　├ digital | Video | <https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D15365&af_id=affiliate-990&ch=api> |
| 　　├ monthly | Monthly video unlimited ch deluxe | <https://al.fanza.co.jp/?lurl=http%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D15365%2F&af_id=affiliate-001&ch=api> |
| 　　└ mono | DVD mail order | <https://al.fanza.co.jp/?lurl=http%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D15365%2F&af_id=affiliate-001&ch=api> |

### Sample response

```json
{
    "request": {
        "parameters": {
            "api_id": "example",
            "affiliate_id": "affiliate-990",
            "keyword": "いちか",
            "bust": "80",
            "waist": "-60",
            "hits": "10",
            "sort": "bust"
            "output": "json"
        }
    },
    "result": {
        "status": "200",
        "result_count": 10,
        "total_count": "20",
        "first_position": 1,
        "actress": [
            {
                "id": "1058259",
                "name": "市川花音",
                "ruby": "いちかわかのん",
                "bust": "80",
                "cup": "B",
                "waist": "55",
                "hip": "82",
                "height": "141",
                "birthday": null,
                "blood_type": null,
                "hobby": "",
                "prefectures": "",
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/itikawa_kanon2.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/itikawa_kanon2.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1058259%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1058259%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1058259%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1011652",
                "name": "瀬名一花",
                "ruby": "せないちか",
                "bust": "81",
                "waist": "55",
                "hip": "79",
                "height": "161",
                "birthday": "1991-05-30",
                "blood_type": "O",
                "hobby": "コスプレ、サバイバルゲーム、ピアノ、ドラム、木琴、ヴァイオリン",
                "prefectures": "東京都",
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/sena_itika.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/sena_itika.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1011652%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1011652%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1011652%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1039046",
                "name": "いちか",
                "ruby": "いちか",
                "bust": "82",
                "cup": "C",
                "waist": "58",
                "hip": "84",
                "height": "155",
                "birthday": null,
                "blood_type": null,
                "hobby": "お買いもの、エッチ",
                "prefectures": null,
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/ichika2.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/ichika2.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1039046%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1039046%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1039046%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1026634",
                "name": "一花のあ",
                "ruby": "いちかのあ",
                "bust": "83",
                "waist": "57",
                "hip": "85",
                "height": null,
                "birthday": "1996-02-22",
                "blood_type": null,
                "hobby": "ダンス",
                "prefectures": null,
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/itika_noa.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/itika_noa.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1026634%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1026634%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1026634%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1010139",
                "name": "市川まほ",
                "ruby": "いちかわまほ",
                "bust": "83",
                "cup": "C",
                "waist": "58",
                "hip": "83",
                "height": "154",
                "birthday": "1992-03-03",
                "blood_type": "O",
                "hobby": "ショッピング、歌うこと",
                "prefectures": "東京都",
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/itikawa_maho.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/itikawa_maho.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1010139%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1010139%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1010139%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "26672",
                "name": "黒木いちか（東条かれん）",
                "ruby": "くろきいちか（とうじょうかれん）",
                "bust": "83",
                "cup": "C",
                "waist": "60",
                "hip": "88",
                "height": "156",
                "birthday": "1987-04-10",
                "blood_type": null,
                "hobby": "カラオケ、買い物",
                "prefectures": "北海道",
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/touzyou_karen.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/touzyou_karen.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D26672%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D26672%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D26672%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1054998",
                "name": "松本いちか",
                "ruby": "まつもといちか",
                "bust": "83",
                "cup": "C",
                "waist": "55",
                "hip": "82",
                "height": "153",
                "birthday": null,
                "blood_type": null,
                "hobby": null,
                "prefectures": null,
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/matumoto_itika.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/matumoto_itika.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1054998%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1054998%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1054998%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1017395",
                "name": "神波多一花",
                "ruby": "かみはたいちか",
                "bust": "84",
                "cup": "C",
                "waist": "60",
                "hip": "88",
                "height": "172",
                "birthday": null,
                "blood_type": null,
                "hobby": null,
                "prefectures": null,
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/kamihata_itika.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/kamihata_itika.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1017395%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1017395%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1017395%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "2465",
                "name": "筒井チカ",
                "ruby": "つついちか",
                "bust": "84",
                "waist": "55",
                "hip": "85",
                "height": null,
                "birthday": "1976-11-11",
                "blood_type": null,
                "hobby": null,
                "prefectures": null,
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/tutui_tika.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/tutui_tika.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D2465%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D2465%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D2465%2F&af_id=affiliate-990&ch=api"
                }
            },
            {
                "id": "1048277",
                "name": "星宮一花",
                "ruby": "ほしみやいちか",
                "bust": "85",
                "cup": "D",
                "waist": "59",
                "hip": "89",
                "height": "168",
                "birthday": "1998-06-28",
                "blood_type": null,
                "hobby": "カフェ巡り、料理",
                "prefectures": "神奈川県",
                "imageURL": {
                    "small": "http://pics.dmm.co.jp/mono/actjpgs/thumbnail/hosimiya_itika.jpg",
                    "large": "http://pics.dmm.co.jp/mono/actjpgs/hosimiya_itika.jpg"
                },
                "listURL": {
                    "digital": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fvideo.dmm.co.jp%2Fav%2Flist%2F%3Factress%3D1048277%2F&af_id=affiliate-990&ch=api",
                    "monthly": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmonthly%2Fpremium%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1048277%2F&af_id=affiliate-990&ch=api",
                    "mono": "https://al.fanza.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fmono%2Fdvd%2F-%2Flist%2F%3D%2Farticle%3Dactress%2Fid%3D1048277%2F&af_id=affiliate-990&ch=api"
                }
            }
        ]
    }
}
```
