# Floor API

Documentation to use Py-DMMJP Client with DMM API FloorList:

See: [https://affiliate.dmm.com/api/v3/floorlist.html](https://affiliate.dmm.com/api/v3/floorlist.html)

## Request parameters

| Logical Name | Physical Name | Required | Sample Value | Description |
|--------------|---------------|----------|--------------|-------------|
| API ID | api_id | ○ | | ID assigned during registration |
| Affiliate ID | affiliate_id | ○ | affiliate-990 | Affiliate ID from 990-999 assigned during registration |
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
| └ site | Site information |  |
| 　　├ name | Site name | DMM.com（一般） |
| 　　├ code | Site code | DMM.com |
| 　　└ service | Service information |  |
| 　　　　├ name | Service name | 動画 |
| 　　　　├ code | Service code | digital |
| 　　　　└ floor | Floor information |  |
| 　　　　　　├ id | Floor ID | 6 |
| 　　　　　　├ name | Floor name | 映画・ドラマ |
| 　　　　　　└ code | Floor code | cinema |

### Sample response

```json
({
    "request": {
        "parameters": {
            "api_id": "example",
            "affiliate_id": "affiliate-990",
            "output": "json",
            "callback": "example"
        }
    },
    "result": {
        "site": [
            {
                "name": "DMM.com（一般）",
                "code": "DMM.com",
                "service": [
                    {
                        "name": "AKB48グループ",
                        "code": "lod",
                        "floor": [
                            {
                                "id": "1",
                                "name": "AKB48",
                                "code": "akb48"
                            },
                            {
                                "id": "2",
                                "name": "SKE48",
                                "code": "ske48"
                            },
                            {
                                "id": "3",
                                "name": "NMB48",
                                "code": "nmb48"
                            },
                            {
                                "id": "4",
                                "name": "HKT48",
                                "code": "hkt48"
                            },
                            {
                                "id": "5",
                                "name": "NGT48",
                                "code": "ngt48"
                            },
                            {
                                "id": "6",
                                "name": "REVIVAL!! ON DEMAND",
                                "code": "rod"
                            }
                        ]
                    },
                    {
                        "name": "DMMブックス",
                        "code": "ebook",
                        "floor": [
                            {
                                "id": "19",
                                "name": "コミック",
                                "code": "comic"
                            },
                            {
                                "id": "20",
                                "name": "写真集",
                                "code": "photo"
                            },
                            {
                                "id": "21",
                                "name": "文芸・ラノベ",
                                "code": "novel"
                            },
                            {
                                "id": "22",
                                "name": "ビジネス・実用",
                                "code": "otherbooks"
                            }
                        ]
                    },
                    {
                        "name": "PCゲーム/ソフトウェア",
                        "code": "pcsoft",
                        "floor": [
                            {
                                "id": "23",
                                "name": "PCゲーム",
                                "code": "digital_pcgame"
                            },
                            {
                                "id": "24",
                                "name": "ソフトウェア",
                                "code": "digital_pcsoft"
                            }
                        ]
                    },
                    {
                        "name": "通販",
                        "code": "mono",
                        "floor": [
                            {
                                "id": "25",
                                "name": "DVD・Blu-ray",
                                "code": "dvd"
                            },
                            {
                                "id": "26",
                                "name": "CD",
                                "code": "cd"
                            },
                            {
                                "id": "27",
                                "name": "本・コミック",
                                "code": "book"
                            },
                            {
                                "id": "28",
                                "name": "ゲーム",
                                "code": "game"
                            },
                            {
                                "id": "29",
                                "name": "ホビー",
                                "code": "hobby"
                            }
                        ]
                    },
                    {
                        "name": "DMMTV",
                        "code": "dmmtv",
                        "floor": [
                            {
                                "id": "95",
                                "name": "DMMTV舞台",
                                "code": "dmmtv_video"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "FANZA（アダルト）",
                "code": "FANZA",
                "service": [
                    {
                        "name": "動画",
                        "code": "digital",
                        "floor": [
                            {
                                "id": "43",
                                "name": "ビデオ",
                                "code": "videoa"
                            },
                            {
                                "id": "44",
                                "name": "素人",
                                "code": "videoc"
                            },
                            {
                                "id": "45",
                                "name": "成人映画",
                                "code": "nikkatsu"
                            },
                            {
                                "id": "46",
                                "name": "アニメ動画",
                                "code": "anime"
                            }
                        ]
                    },
                    {
                        "name": "月額動画",
                        "code": "monthly",
                        "floor": [
                            {
                                "id": "68",
                                "name": "見放題ch デラックス",
                                "code": "premium"
                            },
                            {
                                "id": "91",
                                "name": "VRch",
                                "code": "vr"
                            },
                            {
                                "id": "98",
                                "name": "見放題ch",
                                "code": "standard"
                            }
                        ]
                    },
                    {
                        "name": "通販",
                        "code": "mono",
                        "floor": [
                            {
                                "id": "74",
                                "name": "DVD",
                                "code": "dvd"
                            },
                            {
                                "id": "75",
                                "name": "大人のおもちゃ",
                                "code": "goods"
                            },
                            {
                                "id": "76",
                                "name": "アニメ",
                                "code": "anime"
                            },
                            {
                                "id": "77",
                                "name": "PCゲーム",
                                "code": "pcgame"
                            },
                            {
                                "id": "78",
                                "name": "ブック",
                                "code": "book"
                            }
                        ]
                    },
                    {
                        "name": "アダルトPCゲーム",
                        "code": "pcgame",
                        "floor": [
                            {
                                "id": "80",
                                "name": "アダルトPCゲーム",
                                "code": "digital_pcgame"
                            }
                        ]
                    },
                    {
                        "name": "同人",
                        "code": "doujin",
                        "floor": [
                            {
                                "id": "81",
                                "name": "同人",
                                "code": "digital_doujin"
                            }
                        ]
                    },
                    {
                        "name": "FANZAブックス",
                        "code": "ebook",
                        "floor": [
                            {
                                "id": "82",
                                "name": "コミック",
                                "code": "comic"
                            },
                            {
                                "id": "83",
                                "name": "美少女ノベル・官能小説",
                                "code": "novel"
                            },
                            {
                                "id": "84",
                                "name": "アダルト写真集・雑誌",
                                "code": "photo"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}
```
