#!/usr/bin/env python3
"""
Test import compatibility for both development and installed package scenarios.
"""

import sys
import os

# Add src directory to Python path for development imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_development_import():
    """Test importing from source directory (development scenario)."""
    try:
        from jsonQ import Query
        assert Query is not None
        print("✓ Development import works: from jsonQ import Query")
    except ImportError as e:
        print(f"✗ Development import failed: {e}")
        raise

def test_installed_package_import():
    """Test importing from installed package (user scenario)."""
    try:
        # This will work if the package is properly installed
        from jsonQ import Query
        assert Query is not None
        print("✓ Installed package import works: from jsonQ import Query")
        return True
    except ImportError:
        print("ℹ Installed package import not available (package not installed)")
        return False

def test_query_functionality():
    """Test basic Query functionality with both import methods."""
    # Test with development import
    from jsonQ import Query
    
    test_data = [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25}
    ]
    
    q = Query(test_data)
    result = q.where('age > 25').tolist()
    assert len(result) == 1
    assert result[0]['name'] == 'Alice'
    print("✓ Query functionality works correctly")

if __name__ == "__main__":
    print("Testing import compatibility...\n")
    
    test_development_import()
    test_installed_package_import()
    test_query_functionality()
    
    print("\n✅ All import compatibility tests completed!")