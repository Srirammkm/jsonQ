# jsonQ
Installation
```sh
pip install jsonQ
```
Example
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
        "sex":"M",
        "family": "Avengers",
        "favorite":{
            "food": ["junkfood","coke"]
        }
    },
    {
        "name":{
            "first": "Loki",
            "last": "Odinson"
        },
        "age": 1054,
        "sex": "M",
        "family": "Avengers",
        "favorite":{
            "food": ["pear","pizza"]
        }
    },
    {
        "name":{
            "first": "Thanos",
            "last": None,
        },
        "age": 1000,
        "sex": "M",
        "family": "Avengers",
        "favorite":{
            "food": ["peas","banana"],
            "movie": ["infinity-war"]
        }

    }
]


out = Query(a)
food = "peas"
out = out.where("sex == M").where(f"{food} in favorite.food").where("age == 1000").tolist()

print(json.dumps(out,indent=4))

```
Output
```
➜  jquery python3  main.py
[
    {
        "name": {
            "first": "Thanos",
            "last": null
        },
        "age": 1000,
        "sex": "M",
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
