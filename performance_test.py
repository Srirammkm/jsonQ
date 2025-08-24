#!/usr/bin/env python3
"""
Performance test to demonstrate improvements in the Query module.
"""

import time
import json
from src.jquery import Query
from sampledata.data import test_data

def generate_large_dataset(size=1000):
    """Generate a larger dataset for performance testing."""
    base_data = test_data()
    large_data = []
    
    for i in range(size):
        for item in base_data:
            # Create variations of the base data
            new_item = json.loads(json.dumps(item))  # Deep copy
            new_item['id'] = i * len(base_data) + len(large_data)
            new_item['age'] = new_item['age'] + (i % 100)
            large_data.append(new_item)
    
    return large_data

def benchmark_query(data, description, query_func):
    """Benchmark a query function."""
    print(f"\n{description}")
    print("-" * 50)
    
    start_time = time.time()
    result = query_func(data)
    end_time = time.time()
    
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    print(f"Execution time: {execution_time:.2f}ms")
    print(f"Results found: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    
    return execution_time

def main():
    """Run performance benchmarks."""
    print("jsonQ Performance Benchmarks")
    print("=" * 50)
    
    # Test with different dataset sizes
    sizes = [100, 500, 1000]
    
    for size in sizes:
        print(f"\n\nDataset size: {size * 6} records")  # 6 base records * multiplier
        data = generate_large_dataset(size)
        query = Query(data)
        
        # Test various query patterns
        benchmarks = [
            (
                "Simple equality filter",
                lambda d: Query(d).where("sex == M").tolist()
            ),
            (
                "Chained conditions",
                lambda d: Query(d).where("sex == M").where("age > 1000").tolist()
            ),
            (
                "Nested field access",
                lambda d: Query(d).where("name.first == Thor").tolist()
            ),
            (
                "Array membership",
                lambda d: Query(d).where("peas in favorite.food").tolist()
            ),
            (
                "Wildcard query",
                lambda d: Query(d).where("beer in favorite.*.food").tolist()
            ),
            (
                "Field extraction",
                lambda d: Query(d).where("sex == M").get("age")
            ),
            (
                "Complex chained query",
                lambda d: Query(d).where("sex == M").where("age > 999").where("family == Avengers").get("name.first")
            ),
            (
                "Like operator",
                lambda d: Query(d).where("name.first like Th").tolist()
            ),
            (
                "Between operator",
                lambda d: Query(d).where("age between 30,50").tolist()
            ),
            (
                "Order by operation",
                lambda d: Query(d).where("sex == M").order_by("age").tolist()
            ),
            (
                "Group by operation",
                lambda d: Query(d).group_by("family")
            ),
            (
                "Aggregation (sum)",
                lambda d: Query(d).sum("age")
            ),
            (
                "Distinct values",
                lambda d: Query(d).distinct("family")
            ),
            (
                "Statistical summary",
                lambda d: Query(d).stats("age")
            ),
            (
                "Advanced chaining",
                lambda d: Query(d).where("sex == M").where("age >= 1000").order_by("age").pluck("name", "age")
            )
        ]
        
        total_time = 0
        for description, query_func in benchmarks:
            time_taken = benchmark_query(data, description, query_func)
            total_time += time_taken
        
        print(f"\nTotal time for all queries: {total_time:.2f}ms")
        print(f"Average time per query: {total_time/len(benchmarks):.2f}ms")

if __name__ == "__main__":
    main()