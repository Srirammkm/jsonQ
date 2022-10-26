import unittest

from src.jquery import Query
from sampledata import data


sample = Query(data.test_data())
class TestSimple(unittest.TestCase):

    def test_where_1(self):
        self.assertEqual(sample.where("sex == M").where(f"peas in favorite.food").where("age == 1000").tolist(),[{'name': {'first': 'Thanos', 'last': None}, 'age': 1000, 'sex': 'M', 'family': 'Avengers', 'favorite': {'food': ['peas', 'banana'], 'movie': ['infinity-war']}}])
    
    def test_where_dict_loop_in_list_1(self):
        self.assertEqual(sample.where("beer in favorite.*.food").tolist(),[{
                                                                            "name":{
                                                                                "first": "Ironman",
                                                                                "last": None,
                                                                            },
                                                                            "age": 45,
                                                                            "sex": "M",
                                                                            "family": "Avengers",
                                                                            "favorite":[
                                                                                            {
                                                                                                "food": ["beer","pork"]
                                                                                            }
                                                                                        ]
                                                                            }])

    def test_where_dict_loop_in_list_2(self):
        self.assertEqual(sample.where("favorite.*.food == eggos").tolist(),[{
                                                                            "name":{
                                                                                "first": "Eleven",
                                                                                "last": None,
                                                                            },
                                                                            "age": 14,
                                                                            "sex": "F",
                                                                            "family": "StrangerThings",
                                                                            "favorite":[
                                                                                            {
                                                                                                "food": "eggos"
                                                                                            }
                                                                                        ]
                                                                            }])

    def test_tolist_1(self):
        self.assertEqual(len(sample.where("sex == M").tolist()),4)
    
    def test_tolist_2(self):
        self.assertEqual(len(sample.where("sex == M").tolist(limit=2)),2)

    def test_get(self):
        self.assertEqual(sample.where("sex == M").where("age > 999").get("age"),[1500,1054,1000])

if __name__ == '__main__':
    unittest.main()