# jsonQ
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
```
