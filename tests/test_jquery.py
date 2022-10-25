import unittest

from src.jquery import Query

test_data = [
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


sample = Query(test_data)
class TestSimple(unittest.TestCase):

    def test_where_1(self):
        self.assertEqual(sample.where("sex == M").where(f"peas in favorite.food").where("age == 1000").tolist(),[{'name': {'first': 'Thanos', 'last': None}, 'age': 1000, 'sex': 'M', 'family': 'Avengers', 'favorite': {'food': ['peas', 'banana'], 'movie': ['infinity-war']}}])
    
    def test_tolist_1(self):
        self.assertEqual(len(sample.where("sex == M").tolist()),3)
    
    def test_tolist_2(self):
        self.assertEqual(len(sample.where("sex == M").tolist(limit=2)),2)

    def test_get(self):
        self.assertEqual(sample.where("sex == M").where("age > 999").get("age"),[1500,1054,1000])


if __name__ == '__main__':
    unittest.main()