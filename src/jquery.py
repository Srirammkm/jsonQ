import json
from typing import List, Any, Union

class Query:
    def __init__(self, data: List[dict]) -> None:
        """Initializes the Query class with the provided dataset.
        
        Args:
            data (List[dict]): The dataset to be queried.
        """
        self.data = data
        self.result = data

    def __evaluate_condition(self, value: Any, operator: str, target: Any) -> bool:
        """Evaluates a condition between a value and a target using the specified operator.
        
        Args:
            value (Any): The value from the data.
            operator (str): The comparison operator (e.g., '==', '>', 'in').
            target (Any): The target value to compare against.
        
        Returns:
            bool: The result of the condition.
        """
        try:
            if operator == '==':
                return value == target
            elif operator == '!=':
                return value != target
            elif operator == '>':
                return value > target
            elif operator == '<':
                return value < target
            elif operator == '>=':
                return value >= target
            elif operator == '<=':
                return value <= target
            elif operator == 'in':
                return target in value
            elif operator == 'not in':
                return target not in value
            elif operator == 'mode':
                return value == max(set(value), key=value.count) if isinstance(value, list) else False
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        except Exception as e:
            return False

    def __get_nested_value(self, obj: dict, keys: List[str]) -> Any:
        """Retrieves a nested value from a dictionary based on a list of keys.
        
        Args:
            obj (dict): The dictionary to retrieve the value from.
            keys (List[str]): The list of keys representing the nested path.
        
        Returns:
            Any: The retrieved value or None if the path does not exist.
        """
        try:
            for key in keys:
                if isinstance(obj, list):
                    obj = [self.__get_nested_value(item, keys[1:]) for item in obj]
                    return [item for item in obj if item is not None]
                obj = obj.get(key)
            return obj
        except (AttributeError, TypeError, IndexError):
            return None

    def where(self, condition: str) -> 'Query':
        """Filters the dataset based on a given condition.
        
        Args:
            condition (str): The condition to filter the data (e.g., 'age > 30').
        
        Returns:
            Query: The updated Query object with filtered results.
        """
        operator_map = ['==', '!=', '>', '<', '>=', '<=', 'in', 'not in', 'mode']
        for op in operator_map:
            if op in condition:
                field, target = condition.split(op, 1)
                field = field.strip()
                target = target.strip().strip('"\'')
                keys = field.split('.')
                break
        else:
            raise ValueError("Invalid condition format")

        filtered_result = []
        for item in self.result:
            value = self.__get_nested_value(item, keys)
            if self.__evaluate_condition(value, op, target):
                filtered_result.append(item)
        
        self.result = filtered_result
        return self

    def get(self, key: str) -> List[Any]:
        """Retrieves values for a given key from the filtered dataset.
        
        Args:
            key (str): The key to extract values for (supports nested keys).
        
        Returns:
            List[Any]: A list of values corresponding to the specified key.
        """
        keys = key.split('.')
        return [self.__get_nested_value(item, keys) for item in self.result]

    def tolist(self, limit: int = None) -> List[dict]:
        """Converts the current filtered result to a list with an optional limit.
        
        Args:
            limit (int, optional): The maximum number of items to return. Defaults to None.
        
        Returns:
            List[dict]: The filtered dataset as a list.
        """
        return self.result[:limit] if limit else self.result
