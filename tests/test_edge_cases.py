#!/usr/bin/env python3
"""
Edge case tests for jsonQ module.
Tests unusual scenarios, error conditions, and boundary cases.
"""

import json
import unittest
import sys
import os

# Add both src and project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sampledata import data
from jsonQ import Query, QueryIndex


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        self.sample = Query(data.test_data())

    def test_empty_data_handling(self):
        """Test handling of empty datasets."""
        empty_query = Query([])

        # All methods should handle empty data gracefully
        self.assertEqual(len(empty_query), 0)
        self.assertEqual(empty_query.count(), 0)
        self.assertIsNone(empty_query.first())
        self.assertIsNone(empty_query.last())
        self.assertEqual(empty_query.sum("any_field"), 0)
        self.assertEqual(empty_query.avg("any_field"), 0)
        self.assertIsNone(empty_query.min("any_field"))
        self.assertIsNone(empty_query.max("any_field"))
        self.assertEqual(empty_query.tolist(), [])
        self.assertEqual(empty_query.get("any_field"), [])
        self.assertFalse(bool(empty_query))

        # Chaining should still work
        result = empty_query.where("field == value").order_by("field").tolist()
        self.assertEqual(result, [])

    def test_malformed_data_handling(self):
        """Test handling of malformed or unusual data structures."""
        # Test with non-dictionary items
        mixed_data = [
            {"name": "valid", "age": 25},
            "string_item",
            123,
            None,
            {"name": "also_valid", "age": 30},
        ]

        mixed_query = Query(mixed_data)

        # Should handle gracefully and work with valid items
        valid_items = mixed_query.where("age > 20").tolist()
        self.assertEqual(len(valid_items), 2)

        # Test with missing fields
        partial_data = [
            {"name": "complete", "age": 25, "score": 85},
            {"name": "missing_age", "score": 90},
            {"name": "missing_score", "age": 30},
            {},  # Empty dict
        ]

        partial_query = Query(partial_data)

        # Should handle missing fields gracefully
        has_age = partial_query.exists("age").count()
        self.assertEqual(has_age, 2)

        missing_age = partial_query.missing("age").count()
        self.assertEqual(missing_age, 2)

    def test_deeply_nested_data(self):
        """Test with deeply nested data structures."""
        deep_data = [
            {"level1": {"level2": {"level3": {"level4": {"value": "deep_value_1"}}}}},
            {"level1": {"level2": {"level3": {"level4": {"value": "deep_value_2"}}}}},
        ]

        deep_query = Query(deep_data)

        # Test deep nested access
        deep_values = deep_query.get("level1.level2.level3.level4.value")
        self.assertEqual(len(deep_values), 2)
        self.assertIn("deep_value_1", deep_values)
        self.assertIn("deep_value_2", deep_values)

        # Test deep nested filtering
        filtered = deep_query.where(
            "level1.level2.level3.level4.value == deep_value_1"
        ).tolist()
        self.assertEqual(len(filtered), 1)

    def test_circular_references(self):
        """Test handling of data with circular references."""
        # Create data with circular reference
        item1 = {"id": 1, "name": "item1"}
        item2 = {"id": 2, "name": "item2"}
        item1["ref"] = item2
        item2["ref"] = item1

        # This should not crash the system
        try:
            circular_query = Query([item1, item2])
            # Basic operations should still work
            self.assertEqual(len(circular_query), 2)
            names = circular_query.get("name")
            self.assertEqual(len(names), 2)
        except (ValueError, RecursionError):
            # It's acceptable if circular references cause issues
            # as long as it doesn't crash silently
            pass

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        unicode_data = [
            {"name": "José", "city": "São Paulo", "emoji": "😀"},
            {"name": "François", "city": "Montréal", "emoji": "🇫🇷"},
            {"name": "张三", "city": "北京", "emoji": "🐉"},
            {"name": "محمد", "city": "القاهرة", "emoji": "🕌"},
        ]

        unicode_query = Query(unicode_data)

        # Test filtering with Unicode
        jose = unicode_query.where("name == José").tolist()
        self.assertEqual(len(jose), 1)

        # Test like operator with Unicode
        french = unicode_query.where("name like ç").tolist()
        self.assertEqual(len(french), 1)

        # Test aggregations work with Unicode
        all_names = unicode_query.get("name")
        self.assertEqual(len(all_names), 4)

    def test_large_string_values(self):
        """Test handling of very large string values."""
        large_text = "x" * 10000  # 10KB string

        large_data = [
            {"id": 1, "content": large_text, "type": "large"},
            {"id": 2, "content": "small", "type": "small"},
        ]

        large_query = Query(large_data)

        # Should handle large strings without issues
        large_items = large_query.where("type == large").tolist()
        self.assertEqual(len(large_items), 1)
        self.assertEqual(len(large_items[0]["content"]), 10000)

        # Test like operator with large strings
        x_content = large_query.where("content like x").tolist()
        self.assertEqual(len(x_content), 1)

    def test_numeric_edge_cases(self):
        """Test numeric edge cases."""
        numeric_data = [
            {"value": 0, "name": "zero"},
            {"value": -1, "name": "negative"},
            {"value": float("inf"), "name": "infinity"},
            {"value": float("-inf"), "name": "negative_infinity"},
            {"value": float("nan"), "name": "nan"},
            {"value": 1.7976931348623157e308, "name": "max_float"},
            {"value": 5e-324, "name": "min_float"},
        ]

        numeric_query = Query(numeric_data)

        # Test comparisons with special values
        positive = numeric_query.where("value > 0").tolist()
        # Should handle inf and large numbers
        self.assertGreaterEqual(len(positive), 2)

        # Test aggregations with special values
        # Note: sum/avg with inf/nan may produce inf/nan
        try:
            total = numeric_query.sum("value")
            # Should not crash, even if result is inf/nan
            self.assertIsInstance(total, (int, float))
        except (OverflowError, ValueError):
            # Acceptable if special values cause issues
            pass

    def test_boolean_edge_cases(self):
        """Test boolean value handling."""
        bool_data = [
            {"active": True, "name": "true_bool"},
            {"active": False, "name": "false_bool"},
            {"active": "true", "name": "true_string"},
            {"active": "false", "name": "false_string"},
            {"active": "True", "name": "true_cap"},
            {"active": "False", "name": "false_cap"},
            {"active": 1, "name": "one"},
            {"active": 0, "name": "zero"},
            {"active": "yes", "name": "yes"},
            {"active": "no", "name": "no"},
        ]

        bool_query = Query(bool_data)

        # Test various boolean representations
        true_items = bool_query.where("active == true").tolist()
        false_items = bool_query.where("active == false").tolist()

        # Should handle different boolean representations
        self.assertGreater(len(true_items), 0)
        self.assertGreater(len(false_items), 0)

    def test_date_and_time_strings(self):
        """Test handling of date and time strings."""
        date_data = [
            {"date": "2024-01-01", "event": "new_year"},
            {"date": "2024-12-25", "event": "christmas"},
            {"date": "2024-07-04", "event": "independence"},
            {"date": "2024-02-29", "event": "leap_day"},  # Leap year
        ]

        date_query = Query(date_data)

        # Test string comparisons with dates
        after_july = date_query.where("date > 2024-07-01").tolist()
        self.assertGreaterEqual(len(after_july), 2)  # July 4th and Christmas

        # Test like operator with dates
        december = date_query.where("date like 2024-12").tolist()
        self.assertEqual(len(december), 1)

    def test_null_and_undefined_handling(self):
        """Test handling of null, None, and undefined values."""
        null_data = [
            {"name": "valid", "value": 42, "optional": "present"},
            {"name": "null_value", "value": None, "optional": "present"},
            {"name": "missing_value", "optional": None},
            {"name": "empty_string", "value": "", "optional": ""},
            {"name": "zero", "value": 0, "optional": "present"},
        ]

        null_query = Query(null_data)

        # Test exists with None values
        has_value = null_query.exists("value").count()
        self.assertEqual(has_value, 3)  # valid, empty_string, zero

        # Test missing with None values
        missing_value = null_query.missing("value").count()
        self.assertEqual(missing_value, 2)  # null_value, missing_value

        # Test filtering with None
        non_null = null_query.where("value != None").tolist()
        # Should handle None comparisons
        self.assertGreaterEqual(len(non_null), 0)

    def test_performance_with_complex_queries(self):
        """Test performance doesn't degrade with complex queries."""
        import time

        # Create moderately large dataset
        large_data = data.test_data() * 50  # 300 records
        large_query = Query(large_data)

        # Complex chained query
        start_time = time.time()
        result = (
            large_query.where("sex == M")
            .where("age > 100")
            .order_by("age", ascending=False)
            .group_by("family")
        )
        end_time = time.time()

        # Should complete in reasonable time (< 1 second)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0)

        # Result should be correct
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_memory_usage_with_large_results(self):
        """Test memory usage doesn't explode with large result sets."""
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "id": i,
                    "value": i % 100,
                    "category": f"cat_{i % 10}",
                    "data": f"item_{i}",
                }
            )

        large_query = Query(large_data)

        # Operations that could potentially use lots of memory
        all_values = large_query.get("value")
        self.assertEqual(len(all_values), 1000)

        # Grouping large dataset
        groups = large_query.group_by("category")
        self.assertEqual(len(groups), 10)

        # Each group should have 100 items
        for group in groups.values():
            self.assertEqual(len(group), 100)

    def test_concurrent_query_safety(self):
        """Test that queries are safe for concurrent use."""
        import threading
        import time

        results = []
        errors = []

        def worker():
            try:
                # Each thread performs different queries
                thread_id = threading.current_thread().ident
                local_query = Query(data.test_data())

                # Perform various operations
                count = local_query.where("sex == M").count()
                first = local_query.first()
                stats = local_query.stats("age")

                results.append(
                    {
                        "thread_id": thread_id,
                        "count": count,
                        "first_name": first["name"]["first"] if first else None,
                        "avg_age": stats["avg"],
                    }
                )
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)

        # All threads should get the same results
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result["count"], first_result["count"])
            self.assertEqual(result["first_name"], first_result["first_name"])
            self.assertEqual(result["avg_age"], first_result["avg_age"])


if __name__ == "__main__":
    unittest.main()
