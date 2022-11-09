# jsonQ

<p align="center">
  <a href="https://github.com/Srirammkm/jsonQ/misc/logo.png"><img src="" alt="Logo" height=170></a>
  <br />
  <br />
  <a href="https://github.com/Srirammkm/jsonQ/actions/workflows/linux-test.yaml" target="_blank"><img src="https://github.com/Srirammkm/jsonQ/actions/workflows/linux-test.yaml/badge.svg" /></a>
  <a href="https://github.com/Srirammkm/jsonQ/actions/workflows/mac-test.yaml" target="_blank"><img src="https://github.com/Srirammkm/jsonQ/actions/workflows/mac-test.yaml/badge.svg" /></a>
  <a href="https://github.com/Srirammkm/jsonQ/actions/workflows/windows-test.yaml" target="_blank"><img src="https://github.com/Srirammkm/jsonQ/actions/workflows/windows-test.yaml/badge.svg" /></a>
</p>


Installation
```sh
pip install jsonQ
```
Example main.py
```
import json
from jquery import Query
a = [
    {
        "name":{
            "first": "Thor",
            "last": "Odinson"
        },
        "age": 1500,
        "gender":"M",
        "family": "Avengers",
        "favorite":{
            "food": ["banana","pizza"]
        }
    },
    {
        "name":{
            "first": "Loki",
            "last": "Odinson"
        },
        "age": 1054,
        "gender": "M",
        "family": "Avengers",
        "favorite":{
            "food": ["peas","pizza"]
        }
    },
    {
        "name":{
            "first": "Thanos",
            "last": None,
        },
        "age": 1000,
        "gender": "M",
        "family": "Avengers",
        "favorite":{
            "food": ["peas","banana"],
            "movie": ["infinity-war"]
        }

    }
]


out = Query(a)
food = "peas"
out = out.where("gender == M").where(f"{food} in favorite.food").where("age == 1000").tolist()

print(json.dumps(out,indent=4))

```
Output
```
➜  python3  main.py
[
    {
        "name": {
            "first": "Thanos",
            "last": null
        },
        "age": 1000,
        "gender": "M",
        "family": "Avengers",
        "favorite": {
            "food": [
                "peas",
                "banana"
            ],
            "movie": [
                "infinity-war"
            ]
        }
    }
]
```
```
out.where("favorite.*.food == eggos").tolist()
out.where("beer in favorite.*.food").tolist()
out.where("food in favorite.*.food").get("age")
out.where("food in favorite.*.food").get("name.first")
```

