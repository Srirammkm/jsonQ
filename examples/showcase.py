#!/usr/bin/env python3
"""
Comprehensive showcase of jsonQ v3.0 features.
"""

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jquery import Query

# Sample data - expanded dataset
data = [
    {
        "id": 1,
        "name": {"first": "Thor", "last": "Odinson"},
        "age": 1500,
        "sex": "M",
        "family": "Avengers",
        "score": 95,
        "active": True,
    },
    {
        "id": 2,
        "name": {"first": "Loki", "last": "Odinson"},
        "age": 1054,
        "sex": "M",
        "family": "Avengers",
        "score": 78,
        "active": False,
    },
    {
        "id": 3,
        "name": {"first": "Thanos", "last": None},
        "age": 1000,
        "sex": "M",
        "family": "Avengers",
        "score": 99,
        "active": False,
    },
    {
        "id": 4,
        "name": {"first": "Ironman", "last": None},
        "age": 45,
        "sex": "M",
        "family": "Avengers",
        "score": 88,
        "active": True,
    },
    {
        "id": 5,
        "name": {"first": "Eleven", "last": None},
        "age": 14,
        "sex": "F",
        "family": "StrangerThings",
        "score": 92,
        "active": True,
    },
    {
        "id": 6,
        "name": {"first": "Joey", "last": None},
        "age": 35,
        "sex": "M",
        "family": "Friends",
        "score": 65,
        "active": True,
    },
    {
        "id": 7,
        "name": {"first": "Rachel", "last": "Green"},
        "age": 30,
        "sex": "F",
        "family": "Friends",
        "score": 82,
        "active": True,
    },
    {
        "id": 8,
        "name": {"first": "Chandler", "last": "Bing"},
        "age": 32,
        "sex": "M",
        "family": "Friends",
        "score": 75,
        "active": True,
    },
]


def showcase_basic_operations():
    """Demonstrate basic query operations."""
    print("=== BASIC OPERATIONS ===")
    query = Query(data)

    # Basic filtering
    print(f"Total records: {len(query)}")
    print(f"Males: {query.where('sex == M').count()}")
    print(f"Active users: {query.where('active == True').count()}")
    print(f"Avengers: {query.where('family == Avengers').count()}")
    print()


def showcase_advanced_operators():
    """Demonstrate advanced operators."""
    print("=== ADVANCED OPERATORS ===")
    query = Query(data)

    # String operations
    print("Names starting with 'T':")
    t_names = query.where("name.first startswith T").pluck("name")
    for item in t_names:
        print(f"  - {item['name']['first']}")

    # Like operator
    print("\nNames containing 'an':")
    an_names = query.where("name.first like an").pluck("name")
    for item in an_names:
        print(f"  - {item['name']['first']}")

    # Range queries
    print(f"\nMiddle-aged (30-50): {query.where('age between 30,50').count()}")
    print(f"High scorers (>85): {query.where('score > 85').count()}")
    print(f"Not Avengers: {query.where('family not_in Avengers').count()}")
    print()


def showcase_aggregations():
    """Demonstrate aggregation functions."""
    print("=== AGGREGATIONS ===")
    query = Query(data)

    # Statistical functions
    print(f"Average age: {query.avg('age'):.1f}")
    print(f"Total score: {query.sum('score')}")
    print(f"Age range: {query.min('age')} - {query.max('age')}")

    # Detailed stats
    age_stats = query.stats("age")
    print(f"Age statistics: {age_stats}")

    # Value counts
    family_counts = query.value_counts("family")
    print(f"Family distribution: {family_counts}")

    # Distinct values
    families = query.distinct("family")
    print(f"Unique families: {families}")
    print()


def showcase_grouping_sorting():
    """Demonstrate grouping and sorting."""
    print("=== GROUPING & SORTING ===")
    query = Query(data)

    # Sorting
    print("Top 3 by score:")
    top_scorers = query.order_by("score", ascending=False).tolist(limit=3)
    for item in top_scorers:
        print(f"  {item['name']['first']}: {item['score']}")

    # Grouping
    print("\nBy family:")
    by_family = query.group_by("family")
    for family, group in by_family.items():
        avg_age = group.avg("age")
        print(f"  {family}: {group.count()} members, avg age {avg_age:.1f}")

    # Group by sex with stats
    print("\nBy gender:")
    by_sex = query.group_by("sex")
    for sex, group in by_sex.items():
        stats = group.stats("score")
        print(f"  {sex}: {stats['count']} people, avg score {stats['avg']:.1f}")
    print()


def showcase_data_manipulation():
    """Demonstrate data manipulation features."""
    print("=== DATA MANIPULATION ===")
    query = Query(data)

    # Pluck specific fields
    print("Names and ages:")
    basic_info = query.pluck("name", "age")
    for item in basic_info[:3]:  # Show first 3
        print(f"  {item['name']['first']}: {item['age']}")

    # Apply transformations
    print("\nWith full names:")
    with_full_names = query.apply(
        lambda x: {
            **x,
            "full_name": f"{x['name']['first']} {x['name'].get('last', '')}",
        }
    )

    for item in with_full_names.tolist()[:3]:
        print(f"  {item['full_name'].strip()}")

    # Custom filtering
    print(
        f"\nHigh performers (score > 80): {query.filter_func(lambda x: x['score'] > 80).count()}"
    )

    # Convert to dictionary
    name_to_score = query.to_dict("name.first", "score")
    print(f"Thor's score: {name_to_score.get('Thor')}")
    print()


def showcase_pagination_sampling():
    """Demonstrate pagination and sampling."""
    print("=== PAGINATION & SAMPLING ===")
    query = Query(data)

    # Pagination
    page1 = query.paginate(page=1, per_page=3)
    print(
        f"Page 1 of {page1['total_pages']} (showing {len(page1['data'])} of {page1['total']}):"
    )
    for item in page1["data"]:
        print(f"  {item['name']['first']}")

    # Chunking
    chunks = query.chunk(3)
    print(f"\nSplit into {len(chunks)} chunks of 3")

    # Random sampling
    sample = query.sample(3, seed=42)
    print(f"Random sample of 3:")
    for item in sample:
        print(f"  {item['name']['first']}")
    print()


def showcase_complex_queries():
    """Demonstrate complex query chaining."""
    print("=== COMPLEX QUERIES ===")
    query = Query(data)

    # Complex chaining
    result = (
        query.where("active == True")
        .where("score >= 80")
        .order_by("score", ascending=False)
        .pluck("name", "score", "family")
    )

    print("Active high performers (score >= 80):")
    for item in result:
        print(f"  {item['name']['first']} ({item['family']}): {item['score']}")

    # Multi-step analysis
    print("\nFamily performance analysis:")
    families = query.group_by("family")
    family_performance = []

    for family, group in families.items():
        active_members = group.where("active == True")
        performance = {
            "family": family,
            "total_members": group.count(),
            "active_members": active_members.count(),
            "avg_score": group.avg("score"),
            "top_score": group.max("score"),
        }
        family_performance.append(performance)

    # Sort families by average score
    family_performance.sort(key=lambda x: x["avg_score"], reverse=True)

    for perf in family_performance:
        print(
            f"  {perf['family']}: {perf['active_members']}/{perf['total_members']} active, "
            f"avg score {perf['avg_score']:.1f}, top score {perf['top_score']}"
        )
    print()


def showcase_utility_features():
    """Demonstrate utility features."""
    print("=== UTILITY FEATURES ===")
    query = Query(data)

    # Existence checks
    print(f"Records with last name: {query.exists('name.last').count()}")
    print(f"Records without last name: {query.missing('name.last').count()}")

    # Magic methods
    print(f"Query length: {len(query)}")
    print(f"Query is truthy: {bool(query)}")
    print(f"First record: {query[0]['name']['first']}")
    print(f"Last 2 records: {[item['name']['first'] for item in query[-2:]]}")

    # Iteration
    print("Iterating through first 3:")
    for i, item in enumerate(query):
        if i >= 3:
            break
        print(f"  {i+1}. {item['name']['first']}")
    print()


def main():
    """Run all showcase examples."""
    print("jsonQ v3.0 Feature Showcase")
    print("=" * 50)
    print()

    showcase_basic_operations()
    showcase_advanced_operators()
    showcase_aggregations()
    showcase_grouping_sorting()
    showcase_data_manipulation()
    showcase_pagination_sampling()
    showcase_complex_queries()
    showcase_utility_features()

    print("All features demonstrated successfully!")


if __name__ == "__main__":
    main()
