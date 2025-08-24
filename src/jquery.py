from typing import List, Dict, Any, Union, Optional, Callable, Tuple, Set
import operator
import re
from collections import defaultdict, Counter
from functools import lru_cache
import bisect
import hashlib
import json


class QueryIndex:
    """Index for fast field lookups."""
    
    def __init__(self):
        self.field_indexes: Dict[str, Dict[Any, List[int]]] = {}
        self.sorted_indexes: Dict[str, List[Tuple[Any, int]]] = {}
    
    def build_index(self, data: List[Dict[str, Any]], field: str) -> None:
        """Build index for a specific field."""
        if field in self.field_indexes:
            return
        
        index = defaultdict(list)
        sorted_values = []
        
        for i, item in enumerate(data):
            value = self._get_nested_value(item, field)
            if value is not None:
                index[value].append(i)
                sorted_values.append((value, i))
        
        self.field_indexes[field] = dict(index)
        self.sorted_indexes[field] = sorted(sorted_values, key=lambda x: x[0])
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value helper."""
        try:
            keys = path.split('.')
            current = obj
            for key in keys:
                if key == '*':
                    continue
                current = current[key]
            return current
        except (KeyError, TypeError, AttributeError):
            return None
    
    def get_indices(self, field: str, value: Any) -> List[int]:
        """Get indices for field value."""
        return self.field_indexes.get(field, {}).get(value, [])
    
    def range_query(self, field: str, min_val: Any, max_val: Any, 
                   include_min: bool = True, include_max: bool = True) -> List[int]:
        """Get indices for range query."""
        if field not in self.sorted_indexes:
            return []
        
        sorted_vals = self.sorted_indexes[field]
        indices = []
        
        for value, idx in sorted_vals:
            if (include_min and value >= min_val or not include_min and value > min_val) and \
               (include_max and value <= max_val or not include_max and value < max_val):
                indices.append(idx)
            elif value > max_val:
                break
        
        return indices


class Query:
    """
    A jQuery-like query interface for Python dictionaries and JSON data.
    
    Provides chainable methods to filter and extract data from nested structures.
    """
    
    # Operator mapping for safe evaluation
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        'in': lambda x, y: x in y,
        'not_in': lambda x, y: x not in y,
        'like': lambda x, y: str(y).lower() in str(x).lower(),
        'regex': lambda x, y: bool(re.search(str(y), str(x))),
        'startswith': lambda x, y: str(x).startswith(str(y)),
        'endswith': lambda x, y: str(x).endswith(str(y)),
        'between': lambda x, y: y[0] <= x <= y[1] if isinstance(y, (list, tuple)) and len(y) == 2 else False,
    }
    
    # Cache for parsed conditions
    _condition_cache: Dict[str, Tuple[str, str, str]] = {}
    
    def __init__(self, data: List[Dict[str, Any]], use_index: bool = True) -> None:
        """
        Initialize Query with a list of dictionaries.
        
        Args:
            data: List of dictionaries to query
            use_index: Whether to use indexing for performance optimization
        """
        self.data = data if isinstance(data, list) else []
        self.use_index = use_index and len(self.data) > 100  # Only use index for larger datasets
        self.index = QueryIndex() if self.use_index else None
        self._result_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._indexed_fields: Set[str] = set()
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """
        Get value from nested dictionary using dot notation.
        
        Args:
            obj: Dictionary to extract value from
            path: Dot-separated path (e.g., 'name.first')
            
        Returns:
            The value at the specified path, or None if not found
        """
        try:
            keys = path.split('.')
            current = obj
            
            for key in keys:
                if key == '*':
                    # Handle wildcard for list iteration
                    continue
                current = current[key]
            
            return current
        except (KeyError, TypeError, AttributeError):
            return None
    
    def _evaluate_condition(self, obj: Dict[str, Any], field: str, op: str, value: Any) -> bool:
        """
        Safely evaluate a condition without using exec().
        
        Args:
            obj: Object to evaluate condition against
            field: Field path to check
            op: Operator ('==', '!=', '>', '<', '>=', '<=', 'in', 'like', 'regex', etc.)
            value: Value to compare against
            
        Returns:
            True if condition matches, False otherwise
        """
        try:
            # Handle wildcard paths for nested lists
            if '*' in field:
                return self._evaluate_wildcard_condition(obj, field, op, value)
            
            # Get the actual value from the object
            actual_value = self._get_nested_value(obj, field)
            
            if actual_value is None:
                return False
            
            # Handle special operators
            if op in ['in', 'not_in']:
                if isinstance(actual_value, (list, tuple, str)):
                    converted_value = self._convert_value(value, actual_value)
                    return self.OPERATORS[op](converted_value, actual_value)
                return False
            elif op == 'between':
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    min_val = self._convert_value(value[0], actual_value)
                    max_val = self._convert_value(value[1], actual_value)
                    return self.OPERATORS[op](actual_value, [min_val, max_val])
                return False
            else:
                # Convert value to appropriate type
                converted_value = self._convert_value(value, actual_value)
                
                # Use operator mapping for safe evaluation
                if op in self.OPERATORS:
                    return self.OPERATORS[op](actual_value, converted_value)
            
            return False
            
        except (ValueError, TypeError, KeyError, AttributeError):
            return False
    
    def _evaluate_wildcard_condition(self, obj: Dict[str, Any], field: str, op: str, value: str) -> bool:
        """
        Handle wildcard conditions for nested list structures.
        
        Args:
            obj: Object to evaluate condition against
            field: Field path with wildcard
            op: Operator
            value: Value to compare against
            
        Returns:
            True if any item in the wildcard path matches the condition
        """
        try:
            parts = field.split('.')
            wildcard_index = parts.index('*')
            
            # Get the list that contains the wildcard
            list_path = '.'.join(parts[:wildcard_index])
            remaining_path = '.'.join(parts[wildcard_index + 1:])
            
            target_list = self._get_nested_value(obj, list_path) if list_path else obj
            
            if not isinstance(target_list, list):
                return False
            
            # Check each item in the list
            for item in target_list:
                if remaining_path:
                    item_value = self._get_nested_value(item, remaining_path)
                else:
                    item_value = item
                
                if item_value is not None:
                    converted_value = self._convert_value(value, item_value)
                    
                    if op == 'in' and isinstance(item_value, (list, tuple, str)):
                        if converted_value in item_value:
                            return True
                    elif op in self.OPERATORS:
                        if self.OPERATORS[op](item_value, converted_value):
                            return True
            
            return False
            
        except (ValueError, TypeError, KeyError, AttributeError):
            return False
    
    def _convert_value(self, value: str, reference_value: Any) -> Any:
        """
        Convert string value to appropriate type based on reference value.
        
        Args:
            value: String value to convert
            reference_value: Reference value to determine target type
            
        Returns:
            Converted value
        """
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        
        # Try to match the type of the reference value
        if isinstance(reference_value, bool):
            return value.lower() in ('true', '1', 'yes')
        elif isinstance(reference_value, int):
            try:
                return int(value)
            except ValueError:
                return value
        elif isinstance(reference_value, float):
            try:
                return float(value)
            except ValueError:
                return value
        
        return value
    
    def _get_cache_key(self, condition: str) -> str:
        """Generate cache key for condition."""
        data_hash = hashlib.md5(json.dumps(self.data, sort_keys=True, default=str).encode()).hexdigest()[:8]
        return f"{condition}_{data_hash}"
    
    def _parse_condition(self, condition: str) -> tuple:
        """
        Parse condition string into components with caching.
        
        Args:
            condition: Condition string (e.g., 'age > 18', 'name in users')
            
        Returns:
            Tuple of (field, operator, value)
        """
        # Check cache first
        if condition in self._condition_cache:
            return self._condition_cache[condition]
        
        # Handle operators with spaces - order matters for proper parsing
        operators = ['not_in', 'between', 'startswith', 'endswith', 'like', 'regex', 
                    '>=', '<=', '==', '!=', '>', '<', ' in ']
        
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value = parts[1].strip()
                    op = op.strip()
                    
                    # Handle special operators
                    if op == 'in':
                        field, value = value, field
                    elif op == 'between':
                        # Parse between values: "age between 18,65"
                        try:
                            min_val, max_val = [v.strip() for v in value.split(',')]
                            value = [min_val, max_val]
                        except ValueError:
                            raise ValueError(f"Invalid between format: {condition}")
                    
                    result = (field, op, value)
                    self._condition_cache[condition] = result
                    return result
        
        raise ValueError(f"Invalid condition format: {condition}")
    
    def _ensure_index(self, field: str) -> None:
        """Ensure field is indexed if using indexing."""
        if self.use_index and field not in self._indexed_fields and '*' not in field:
            self.index.build_index(self.data, field)
            self._indexed_fields.add(field)
    
    def where(self, condition: str) -> 'Query':
        """
        Filter data based on a condition with caching and indexing.
        
        Args:
            condition: Condition string (e.g., 'age > 18', 'name.first == John')
            
        Returns:
            New Query instance with filtered data
        """
        # Check cache first
        cache_key = self._get_cache_key(condition)
        if cache_key in self._result_cache:
            return Query(self._result_cache[cache_key], use_index=False)
        
        try:
            field, op, value = self._parse_condition(condition)
            
            # Use index for simple equality operations on large datasets
            if (self.use_index and op == '==' and '*' not in field and 
                not isinstance(value, (list, tuple))):
                self._ensure_index(field)
                indices = self.index.get_indices(field, self._convert_value(value, ""))
                filtered_data = [self.data[i] for i in indices if i < len(self.data)]
            else:
                # Fallback to linear search
                filtered_data = []
                for item in self.data:
                    if self._evaluate_condition(item, field, op, value):
                        filtered_data.append(item)
            
            # Cache result for small to medium datasets
            if len(self.data) < 10000:
                self._result_cache[cache_key] = filtered_data
            
            return Query(filtered_data, use_index=False)
            
        except ValueError:
            return Query([], use_index=False)
    
    def get(self, key: str) -> List[Any]:
        """
        Extract values for a specific key from all items.
        
        Args:
            key: Key path to extract (supports dot notation)
            
        Returns:
            List of extracted values
        """
        result = []
        for item in self.data:
            value = self._get_nested_value(item, key)
            if value is not None:
                result.append(value)
        
        return result
    
    def tolist(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Convert query result to list.
        
        Args:
            limit: Optional limit on number of items to return
            
        Returns:
            List of dictionaries
        """
        if limit is not None and isinstance(limit, int) and limit > 0:
            return self.data[:limit]
        return self.data.copy()
    
    def count(self) -> int:
        """
        Get count of items in current query result.
        
        Returns:
            Number of items
        """
        return len(self.data)
    
    def first(self) -> Optional[Dict[str, Any]]:
        """
        Get first item from query result.
        
        Returns:
            First item or None if empty
        """
        return self.data[0] if self.data else None
    
    def last(self) -> Optional[Dict[str, Any]]:
        """
        Get last item from query result.
        
        Returns:
            Last item or None if empty
        """
        return self.data[-1] if self.data else None
    
    def order_by(self, field: str, ascending: bool = True) -> 'Query':
        """
        Sort query results by field.
        
        Args:
            field: Field to sort by (supports dot notation)
            ascending: Sort order (True for ascending, False for descending)
            
        Returns:
            New Query instance with sorted data
        """
        try:
            sorted_data = sorted(
                self.data,
                key=lambda x: self._get_nested_value(x, field) or '',
                reverse=not ascending
            )
            return Query(sorted_data, use_index=False)
        except (TypeError, AttributeError):
            return Query(self.data.copy(), use_index=False)
    
    def group_by(self, field: str) -> Dict[Any, 'Query']:
        """
        Group query results by field value.
        
        Args:
            field: Field to group by (supports dot notation)
            
        Returns:
            Dictionary mapping field values to Query instances
        """
        groups = defaultdict(list)
        
        for item in self.data:
            key = self._get_nested_value(item, field)
            groups[key].append(item)
        
        return {k: Query(v, use_index=False) for k, v in groups.items()}
    
    def distinct(self, field: Optional[str] = None) -> 'Query':
        """
        Get distinct items or distinct values for a field.
        
        Args:
            field: Optional field to get distinct values for
            
        Returns:
            Query with distinct items or list of distinct values
        """
        if field is None:
            # Distinct items (by JSON representation)
            seen = set()
            distinct_items = []
            
            for item in self.data:
                item_str = json.dumps(item, sort_keys=True, default=str)
                if item_str not in seen:
                    seen.add(item_str)
                    distinct_items.append(item)
            
            return Query(distinct_items, use_index=False)
        else:
            # Distinct values for field
            values = self.get(field)
            return list(set(values))
    
    def sum(self, field: str) -> Union[int, float]:
        """
        Calculate sum of numeric field values.
        
        Args:
            field: Field to sum (supports dot notation)
            
        Returns:
            Sum of field values
        """
        values = [v for v in self.get(field) if isinstance(v, (int, float))]
        return sum(values) if values else 0
    
    def avg(self, field: str) -> Union[int, float]:
        """
        Calculate average of numeric field values.
        
        Args:
            field: Field to average (supports dot notation)
            
        Returns:
            Average of field values
        """
        values = [v for v in self.get(field) if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0
    
    def min(self, field: str) -> Any:
        """
        Get minimum value of field.
        
        Args:
            field: Field to find minimum for (supports dot notation)
            
        Returns:
            Minimum field value
        """
        values = [v for v in self.get(field) if v is not None]
        return min(values) if values else None
    
    def max(self, field: str) -> Any:
        """
        Get maximum value of field.
        
        Args:
            field: Field to find maximum for (supports dot notation)
            
        Returns:
            Maximum field value
        """
        values = [v for v in self.get(field) if v is not None]
        return max(values) if values else None
    
    def paginate(self, page: int, per_page: int = 10) -> Dict[str, Any]:
        """
        Paginate query results.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Dictionary with pagination info and data
        """
        total = len(self.data)
        total_pages = (total + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'data': self.data[start:end],
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    
    def pluck(self, *fields: str) -> List[Dict[str, Any]]:
        """
        Extract only specified fields from each item.
        
        Args:
            fields: Field names to extract
            
        Returns:
            List of dictionaries with only specified fields
        """
        result = []
        for item in self.data:
            plucked = {}
            for field in fields:
                value = self._get_nested_value(item, field)
                if value is not None:
                    # Handle nested field names in result
                    if '.' in field:
                        keys = field.split('.')
                        current = plucked
                        for key in keys[:-1]:
                            if key not in current:
                                current[key] = {}
                            current = current[key]
                        current[keys[-1]] = value
                    else:
                        plucked[field] = value
            result.append(plucked)
        return result
    
    def chunk(self, size: int) -> List['Query']:
        """
        Split query results into chunks.
        
        Args:
            size: Chunk size
            
        Returns:
            List of Query instances
        """
        chunks = []
        for i in range(0, len(self.data), size):
            chunk_data = self.data[i:i + size]
            chunks.append(Query(chunk_data, use_index=False))
        return chunks
    
    def sample(self, n: int, seed: Optional[int] = None) -> 'Query':
        """
        Get random sample of items.
        
        Args:
            n: Number of items to sample
            seed: Random seed for reproducibility
            
        Returns:
            Query with sampled items
        """
        import random
        if seed is not None:
            random.seed(seed)
        
        sample_size = min(n, len(self.data))
        sampled_data = random.sample(self.data, sample_size)
        return Query(sampled_data, use_index=False)
    
    def exists(self, field: str) -> 'Query':
        """
        Filter items where field exists and is not None.
        
        Args:
            field: Field to check existence for
            
        Returns:
            Query with items where field exists
        """
        filtered_data = []
        for item in self.data:
            if self._get_nested_value(item, field) is not None:
                filtered_data.append(item)
        return Query(filtered_data, use_index=False)
    
    def missing(self, field: str) -> 'Query':
        """
        Filter items where field is missing or None.
        
        Args:
            field: Field to check for missing values
            
        Returns:
            Query with items where field is missing
        """
        filtered_data = []
        for item in self.data:
            if self._get_nested_value(item, field) is None:
                filtered_data.append(item)
        return Query(filtered_data, use_index=False)
    
    def stats(self, field: str) -> Dict[str, Any]:
        """
        Get statistical summary of numeric field.
        
        Args:
            field: Field to analyze
            
        Returns:
            Dictionary with statistical measures
        """
        values = [v for v in self.get(field) if isinstance(v, (int, float))]
        
        if not values:
            return {'count': 0, 'sum': 0, 'avg': 0, 'min': None, 'max': None}
        
        return {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def value_counts(self, field: str) -> Dict[Any, int]:
        """
        Count occurrences of each value in field.
        
        Args:
            field: Field to count values for
            
        Returns:
            Dictionary mapping values to their counts
        """
        values = self.get(field)
        return dict(Counter(values))
    
    def apply(self, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> 'Query':
        """
        Apply function to each item in query result.
        
        Args:
            func: Function to apply to each item
            
        Returns:
            Query with transformed items
        """
        transformed_data = [func(item) for item in self.data]
        return Query(transformed_data, use_index=False)
    
    def filter_func(self, func: Callable[[Dict[str, Any]], bool]) -> 'Query':
        """
        Filter items using custom function.
        
        Args:
            func: Function that returns True for items to keep
            
        Returns:
            Query with filtered items
        """
        filtered_data = [item for item in self.data if func(item)]
        return Query(filtered_data, use_index=False)
    
    def to_dict(self, key_field: str, value_field: Optional[str] = None) -> Dict[Any, Any]:
        """
        Convert query result to dictionary.
        
        Args:
            key_field: Field to use as dictionary keys
            value_field: Field to use as values (if None, uses entire item)
            
        Returns:
            Dictionary representation
        """
        result = {}
        for item in self.data:
            key = self._get_nested_value(item, key_field)
            if key is not None:
                if value_field:
                    value = self._get_nested_value(item, value_field)
                else:
                    value = item
                result[key] = value
        return result
    
    def clear_cache(self) -> None:
        """Clear query result cache."""
        self._result_cache.clear()
        self._condition_cache.clear()
    
    def __len__(self) -> int:
        """Get length of query result."""
        return len(self.data)
    
    def __iter__(self):
        """Make Query iterable."""
        return iter(self.data)
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Support indexing and slicing."""
        return self.data[index]
    
    def __bool__(self) -> bool:
        """Check if query has results."""
        return bool(self.data)
    