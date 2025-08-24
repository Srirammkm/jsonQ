import unittest
from src.jquery import Query
from sampledata import data


class TestAdvancedFeatures(unittest.TestCase):
    """Test advanced features added to the Query class."""
    
    def setUp(self):
        self.sample = Query(data.test_data())
    
    def test_advanced_operators(self):
        """Test new operators like, regex, between, etc."""
        # Test like operator
        thor_like = self.sample.where("name.first like Th").tolist()
        self.assertEqual(len(thor_like), 2)  # Thor and Thanos
        
        # Test startswith
        t_names = self.sample.where("name.first startswith T").tolist()
        self.assertEqual(len(t_names), 2)  # Thor and Thanos
        
        # Test between operator
        middle_aged = self.sample.where("age between 30,50").tolist()
        self.assertEqual(len(middle_aged), 2)  # Ironman (45) and Joey (35)
        
        # Test not_in operator
        not_avengers = self.sample.where("family not_in Avengers").tolist()
        self.assertEqual(len(not_avengers), 2)  # Eleven and Joey
    
    def test_order_by(self):
        """Test sorting functionality."""
        # Sort by age ascending
        by_age_asc = self.sample.order_by("age", ascending=True).tolist()
        ages = [item['age'] for item in by_age_asc]
        self.assertEqual(ages, sorted(ages))
        
        # Sort by age descending
        by_age_desc = self.sample.order_by("age", ascending=False).tolist()
        ages_desc = [item['age'] for item in by_age_desc]
        self.assertEqual(ages_desc, sorted(ages_desc, reverse=True))
        
        # Sort by nested field
        by_name = self.sample.order_by("name.first").tolist()
        names = [item['name']['first'] for item in by_name]
        self.assertEqual(names, sorted(names))
    
    def test_group_by(self):
        """Test grouping functionality."""
        # Group by family
        by_family = self.sample.group_by("family")
        self.assertIn("Avengers", by_family)
        self.assertIn("StrangerThings", by_family)
        self.assertIn("Friends", by_family)
        
        # Check Avengers group
        avengers = by_family["Avengers"].tolist()
        self.assertEqual(len(avengers), 4)
        
        # Group by sex
        by_sex = self.sample.group_by("sex")
        males = by_sex["M"].tolist()
        females = by_sex["F"].tolist()
        self.assertEqual(len(males), 5)
        self.assertEqual(len(females), 1)
    
    def test_aggregation_functions(self):
        """Test sum, avg, min, max functions."""
        # Test sum
        total_age = self.sample.sum("age")
        expected_sum = sum(item['age'] for item in data.test_data())
        self.assertEqual(total_age, expected_sum)
        
        # Test average
        avg_age = self.sample.avg("age")
        expected_avg = expected_sum / len(data.test_data())
        self.assertEqual(avg_age, expected_avg)
        
        # Test min and max
        min_age = self.sample.min("age")
        max_age = self.sample.max("age")
        self.assertEqual(min_age, 14)  # Eleven
        self.assertEqual(max_age, 1500)  # Thor
    
    def test_distinct(self):
        """Test distinct functionality."""
        # Distinct families
        families = self.sample.distinct("family")
        expected_families = {"Avengers", "StrangerThings", "Friends"}
        self.assertEqual(set(families), expected_families)
        
        # Distinct items (should return all since all items are unique)
        distinct_items = self.sample.distinct()
        self.assertEqual(len(distinct_items), len(self.sample))
    
    def test_pagination(self):
        """Test pagination functionality."""
        # First page
        page1 = self.sample.paginate(page=1, per_page=2)
        self.assertEqual(len(page1['data']), 2)
        self.assertEqual(page1['page'], 1)
        self.assertEqual(page1['total'], 6)
        self.assertEqual(page1['total_pages'], 3)
        self.assertTrue(page1['has_next'])
        self.assertFalse(page1['has_prev'])
        
        # Last page
        page3 = self.sample.paginate(page=3, per_page=2)
        self.assertEqual(len(page3['data']), 2)
        self.assertFalse(page3['has_next'])
        self.assertTrue(page3['has_prev'])
    
    def test_pluck(self):
        """Test field extraction."""
        # Pluck single field
        names = self.sample.pluck("name")
        self.assertEqual(len(names), 6)
        for item in names:
            self.assertIn("name", item)
            self.assertNotIn("age", item)
        
        # Pluck multiple fields
        basic_info = self.sample.pluck("name", "age")
        for item in basic_info:
            self.assertIn("name", item)
            self.assertIn("age", item)
            self.assertNotIn("family", item)
    
    def test_exists_missing(self):
        """Test exists and missing filters."""
        # Test exists
        has_last_name = self.sample.exists("name.last").tolist()
        self.assertEqual(len(has_last_name), 2)  # Thor and Loki
        
        # Test missing
        no_last_name = self.sample.missing("name.last").tolist()
        self.assertEqual(len(no_last_name), 4)  # Others have None for last name
    
    def test_stats(self):
        """Test statistical summary."""
        age_stats = self.sample.stats("age")
        self.assertEqual(age_stats['count'], 6)
        self.assertEqual(age_stats['min'], 14)
        self.assertEqual(age_stats['max'], 1500)
        self.assertGreater(age_stats['avg'], 0)
        self.assertGreater(age_stats['sum'], 0)
    
    def test_value_counts(self):
        """Test value counting."""
        sex_counts = self.sample.value_counts("sex")
        self.assertEqual(sex_counts['M'], 5)
        self.assertEqual(sex_counts['F'], 1)
        
        family_counts = self.sample.value_counts("family")
        self.assertEqual(family_counts['Avengers'], 4)
        self.assertEqual(family_counts['StrangerThings'], 1)
        self.assertEqual(family_counts['Friends'], 1)
    
    def test_chunk(self):
        """Test chunking functionality."""
        chunks = self.sample.chunk(2)
        self.assertEqual(len(chunks), 3)  # 6 items / 2 = 3 chunks
        
        # Check chunk sizes
        self.assertEqual(len(chunks[0]), 2)
        self.assertEqual(len(chunks[1]), 2)
        self.assertEqual(len(chunks[2]), 2)
    
    def test_sample(self):
        """Test random sampling."""
        # Sample with seed for reproducibility
        sample1 = self.sample.sample(3, seed=42)
        sample2 = self.sample.sample(3, seed=42)
        
        self.assertEqual(len(sample1), 3)
        self.assertEqual(len(sample2), 3)
        # Should be same due to same seed
        self.assertEqual(sample1.tolist(), sample2.tolist())
    
    def test_apply_and_filter_func(self):
        """Test custom function application and filtering."""
        # Apply function to add computed field
        with_full_name = self.sample.apply(
            lambda x: {**x, 'full_name': f"{x['name']['first']} {x['name'].get('last', '')}"} 
        )
        
        first_item = with_full_name.first()
        self.assertIn('full_name', first_item)
        
        # Filter with custom function
        adults = self.sample.filter_func(lambda x: x['age'] >= 18)
        self.assertEqual(len(adults), 5)  # All except Eleven (14)
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        # Convert to dict with name as key
        by_name = self.sample.to_dict("name.first")
        self.assertIn("Thor", by_name)
        self.assertIn("Loki", by_name)
        
        # Convert with specific value field
        name_to_age = self.sample.to_dict("name.first", "age")
        self.assertEqual(name_to_age["Thor"], 1500)
        self.assertEqual(name_to_age["Eleven"], 14)
    
    def test_magic_methods(self):
        """Test magic methods for better usability."""
        # Test length
        self.assertEqual(len(self.sample), 6)
        
        # Test boolean
        self.assertTrue(bool(self.sample))
        empty_query = self.sample.where("age == 999")
        self.assertFalse(bool(empty_query))
        
        # Test iteration
        count = 0
        for item in self.sample:
            count += 1
            self.assertIn('name', item)
        self.assertEqual(count, 6)
        
        # Test indexing
        first_item = self.sample[0]
        self.assertEqual(first_item['name']['first'], 'Thor')
        
        # Test slicing
        first_two = self.sample[:2]
        self.assertEqual(len(first_two), 2)
    
    def test_chaining_advanced_features(self):
        """Test chaining of advanced features."""
        result = (self.sample
                 .where("sex == M")
                 .where("age >= 1000")
                 .order_by("age", ascending=False)
                 .pluck("name", "age"))
        
        self.assertEqual(len(result), 3)
        # Should be ordered by age descending
        ages = [item['age'] for item in result]
        self.assertEqual(ages, [1500, 1054, 1000])


if __name__ == '__main__':
    unittest.main()