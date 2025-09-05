import unittest
import sys
import os

# Add both src and project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sampledata import data
from jsonQ import Query


class TestNewFeatures(unittest.TestCase):
    """Test new features added to the Query class."""

    def setUp(self):
        self.sample = Query(data.test_data())

    def test_count(self):
        """Test count method."""
        # Count all males
        male_count = self.sample.where("sex == M").count()
        self.assertEqual(male_count, 5)

        # Count all items
        total_count = self.sample.count()
        self.assertEqual(total_count, 6)

        # Count with no matches
        no_match_count = self.sample.where("age == 999").count()
        self.assertEqual(no_match_count, 0)

    def test_first(self):
        """Test first method."""
        # Get first male
        first_male = self.sample.where("sex == M").first()
        self.assertEqual(first_male["name"]["first"], "Thor")

        # Get first from empty result
        empty_first = self.sample.where("age == 999").first()
        self.assertIsNone(empty_first)

        # Get first from all data
        first_overall = self.sample.first()
        self.assertEqual(first_overall["name"]["first"], "Thor")

    def test_last(self):
        """Test last method."""
        # Get last male
        last_male = self.sample.where("sex == M").last()
        self.assertEqual(last_male["name"]["first"], "Joey")

        # Get last from empty result
        empty_last = self.sample.where("age == 999").last()
        self.assertIsNone(empty_last)

        # Get last from all data
        last_overall = self.sample.last()
        self.assertEqual(last_overall["name"]["first"], "Joey")

    def test_type_conversion(self):
        """Test automatic type conversion in conditions."""
        # Test with integer comparison (age >= 1000 includes Thanos)
        old_people = self.sample.where("age >= 1000").tolist()
        self.assertEqual(len(old_people), 3)

        # Test with string comparison
        thor = self.sample.where("name.first == Thor").tolist()
        self.assertEqual(len(thor), 1)
        self.assertEqual(thor[0]["name"]["first"], "Thor")

    def test_error_handling(self):
        """Test error handling for invalid conditions."""
        # Invalid condition format should return empty result
        result = self.sample.where("invalid condition format").tolist()
        self.assertEqual(len(result), 0)

        # Non-existent field should return empty result
        result = self.sample.where("nonexistent.field == value").tolist()
        self.assertEqual(len(result), 0)

    def test_chaining_with_new_methods(self):
        """Test chaining queries with new methods."""
        # Chain multiple conditions and get count (age >= 1000 includes Thanos)
        count = self.sample.where("sex == M").where("age >= 1000").count()
        self.assertEqual(count, 3)

        # Chain and get first
        first = self.sample.where("sex == M").where("age >= 1000").first()
        self.assertEqual(first["name"]["first"], "Thor")

        # Chain and get last
        last = self.sample.where("sex == M").where("age >= 1000").last()
        self.assertEqual(last["name"]["first"], "Thanos")


if __name__ == "__main__":
    unittest.main()
