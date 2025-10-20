"""
JSON Path Indexing System for EzDB RDBMS
Provides fast lookups on JSON field paths
"""

from typing import Any, Dict, List, Optional, Set, Callable
import json


class JSONPathExtractor:
    """Extracts values from JSON objects using dot notation paths"""

    @staticmethod
    def extract(json_obj: Any, path: str) -> Optional[Any]:
        """
        Extract value from JSON object using dot notation path.

        Examples:
            extract({'user': {'name': 'John'}}, 'user.name') -> 'John'
            extract({'items': [{'id': 1}, {'id': 2}]}, 'items.0.id') -> 1
            extract({'data': {'price': 99.99}}, 'data.price') -> 99.99

        Args:
            json_obj: JSON object (dict or list)
            path: Dot-separated path (e.g., 'user.profile.name')

        Returns:
            Value at path, or None if not found
        """
        if json_obj is None:
            return None

        if not path:
            return json_obj

        parts = path.split('.')
        current = json_obj

        for part in parts:
            if current is None:
                return None

            # Handle array indexing
            if isinstance(current, list):
                try:
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                except ValueError:
                    # Not an integer, can't index array
                    return None
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                # Can't traverse further
                return None

        return current

    @staticmethod
    def extract_all(json_obj: Any, path: str) -> List[Any]:
        """
        Extract all values matching a path (supports wildcards).

        Examples:
            extract_all({'items': [{'x': 1}, {'x': 2}]}, 'items.*.x') -> [1, 2]

        Args:
            json_obj: JSON object
            path: Path with optional wildcards (*)

        Returns:
            List of values matching the path
        """
        if '*' not in path:
            value = JSONPathExtractor.extract(json_obj, path)
            return [value] if value is not None else []

        # Handle wildcard paths
        parts = path.split('.')
        results = [json_obj]

        for part in parts:
            next_results = []
            for obj in results:
                if part == '*':
                    # Wildcard: collect all elements
                    if isinstance(obj, list):
                        next_results.extend(obj)
                    elif isinstance(obj, dict):
                        next_results.extend(obj.values())
                else:
                    # Regular path component
                    if isinstance(obj, dict):
                        value = obj.get(part)
                        if value is not None:
                            next_results.append(value)
                    elif isinstance(obj, list):
                        try:
                            index = int(part)
                            if 0 <= index < len(obj):
                                next_results.append(obj[index])
                        except ValueError:
                            pass
            results = next_results

        return results


class JSONPathIndex:
    """
    Index for fast lookups on JSON field paths.

    Supports:
    - Equality lookups (O(1))
    - Range queries (O(log n))
    - EXISTS checks (O(1))
    """

    def __init__(self, column_name: str, path: str):
        """
        Initialize JSON path index.

        Args:
            column_name: Name of JSON column
            path: JSON path to index (e.g., 'user.age')
        """
        self.column_name = column_name
        self.path = path

        # Equality index: value -> set of row_ids
        self._eq_index: Dict[Any, Set[int]] = {}

        # Sorted list of (value, row_id) for range queries
        self._sorted_values: List[tuple] = []
        self._sorted_dirty = False

    def insert(self, row_id: int, json_obj: Any):
        """
        Index a JSON value.

        Args:
            row_id: Row ID
            json_obj: JSON object to index
        """
        value = JSONPathExtractor.extract(json_obj, self.path)

        if value is not None:
            # Make hashable for dict keys
            hashable_value = self._make_hashable(value)

            if hashable_value not in self._eq_index:
                self._eq_index[hashable_value] = set()
            self._eq_index[hashable_value].add(row_id)

            # Mark sorted list as dirty
            self._sorted_dirty = True

    def delete(self, row_id: int, json_obj: Any):
        """
        Remove a JSON value from index.

        Args:
            row_id: Row ID to remove
            json_obj: JSON object to remove
        """
        value = JSONPathExtractor.extract(json_obj, self.path)

        if value is not None:
            hashable_value = self._make_hashable(value)
            if hashable_value in self._eq_index:
                self._eq_index[hashable_value].discard(row_id)
                if not self._eq_index[hashable_value]:
                    del self._eq_index[hashable_value]

            self._sorted_dirty = True

    def update(self, row_id: int, old_json: Any, new_json: Any):
        """
        Update indexed value.

        Args:
            row_id: Row ID
            old_json: Old JSON object
            new_json: New JSON object
        """
        self.delete(row_id, old_json)
        self.insert(row_id, new_json)

    def lookup_eq(self, value: Any) -> Set[int]:
        """
        Find rows where JSON path equals value.

        Args:
            value: Value to search for

        Returns:
            Set of row IDs matching the value
        """
        hashable_value = self._make_hashable(value)
        return self._eq_index.get(hashable_value, set()).copy()

    def lookup_range(self, min_value: Any = None, max_value: Any = None,
                     include_min: bool = True, include_max: bool = True) -> Set[int]:
        """
        Find rows where JSON path is in range [min_value, max_value].

        Args:
            min_value: Minimum value (None = no minimum)
            max_value: Maximum value (None = no maximum)
            include_min: Include min_value in results
            include_max: Include max_value in results

        Returns:
            Set of row IDs in range
        """
        self._rebuild_sorted_if_needed()

        results = set()

        for value, row_id in self._sorted_values:
            # Check minimum
            if min_value is not None:
                if include_min:
                    if value < min_value:
                        continue
                else:
                    if value <= min_value:
                        continue

            # Check maximum
            if max_value is not None:
                if include_max:
                    if value > max_value:
                        break
                else:
                    if value >= max_value:
                        break

            results.add(row_id)

        return results

    def exists(self) -> Set[int]:
        """
        Find rows where JSON path exists (has a value).

        Returns:
            Set of row IDs where path exists
        """
        results = set()
        for row_ids in self._eq_index.values():
            results.update(row_ids)
        return results

    def _rebuild_sorted_if_needed(self):
        """Rebuild sorted values list if dirty"""
        if not self._sorted_dirty:
            return

        self._sorted_values = []
        for value, row_ids in self._eq_index.items():
            for row_id in row_ids:
                # Try to convert back from hashable form
                actual_value = value
                if isinstance(value, str) and value.startswith('__tuple__:'):
                    actual_value = eval(value[10:])
                elif isinstance(value, str) and value.startswith('__list__:'):
                    actual_value = eval(value[9:])

                self._sorted_values.append((actual_value, row_id))

        # Sort by value
        try:
            self._sorted_values.sort(key=lambda x: x[0])
            self._sorted_dirty = False
        except TypeError:
            # Values not comparable, can't sort
            pass

    @staticmethod
    def _make_hashable(value: Any) -> Any:
        """Convert value to hashable type for dict keys"""
        if isinstance(value, dict):
            # Convert dict to sorted tuple of items
            return f"__dict__:{json.dumps(value, sort_keys=True)}"
        elif isinstance(value, list):
            # Convert list to tuple
            return f"__list__:{tuple(value)}"
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        else:
            # Convert to string representation
            return str(value)

    def size(self) -> int:
        """Get number of unique values in index"""
        return len(self._eq_index)

    def __repr__(self):
        return f"JSONPathIndex(column={self.column_name}, path={self.path}, values={self.size()})"


class JSONIndexManager:
    """Manages all JSON path indexes for a table"""

    def __init__(self):
        """Initialize JSON index manager"""
        # Map: (column_name, path) -> JSONPathIndex
        self._indexes: Dict[tuple, JSONPathIndex] = {}

    def create_index(self, column_name: str, path: str) -> JSONPathIndex:
        """
        Create a new JSON path index.

        Args:
            column_name: Name of JSON column
            path: JSON path to index

        Returns:
            Created JSONPathIndex
        """
        key = (column_name, path)
        if key in self._indexes:
            return self._indexes[key]

        index = JSONPathIndex(column_name, path)
        self._indexes[key] = index
        return index

    def drop_index(self, column_name: str, path: str):
        """
        Drop a JSON path index.

        Args:
            column_name: Name of JSON column
            path: JSON path
        """
        key = (column_name, path)
        if key in self._indexes:
            del self._indexes[key]

    def get_index(self, column_name: str, path: str) -> Optional[JSONPathIndex]:
        """
        Get an existing JSON path index.

        Args:
            column_name: Name of JSON column
            path: JSON path

        Returns:
            JSONPathIndex if exists, None otherwise
        """
        key = (column_name, path)
        return self._indexes.get(key)

    def get_indexes_for_column(self, column_name: str) -> List[JSONPathIndex]:
        """
        Get all indexes for a column.

        Args:
            column_name: Name of JSON column

        Returns:
            List of JSONPathIndex objects
        """
        return [idx for (col, _), idx in self._indexes.items() if col == column_name]

    def insert(self, row_id: int, row_data: Dict[str, Any]):
        """
        Update all indexes with new row.

        Args:
            row_id: Row ID
            row_data: Row data dictionary
        """
        for (column_name, _), index in self._indexes.items():
            json_obj = row_data.get(column_name)
            if json_obj is not None:
                index.insert(row_id, json_obj)

    def delete(self, row_id: int, row_data: Dict[str, Any]):
        """
        Remove row from all indexes.

        Args:
            row_id: Row ID
            row_data: Row data dictionary
        """
        for (column_name, _), index in self._indexes.items():
            json_obj = row_data.get(column_name)
            if json_obj is not None:
                index.delete(row_id, json_obj)

    def update(self, row_id: int, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        """
        Update indexes after row modification.

        Args:
            row_id: Row ID
            old_data: Old row data
            new_data: New row data (complete row after update)
        """
        for (column_name, _), index in self._indexes.items():
            old_json = old_data.get(column_name)
            new_json = new_data.get(column_name)

            if old_json is not None or new_json is not None:
                if old_json == new_json:
                    # No change, skip
                    continue

                if old_json is not None:
                    index.delete(row_id, old_json)
                if new_json is not None:
                    index.insert(row_id, new_json)

    def list_indexes(self) -> List[Dict[str, Any]]:
        """
        List all JSON indexes.

        Returns:
            List of index info dictionaries
        """
        return [
            {
                'column': col,
                'path': path,
                'size': idx.size()
            }
            for (col, path), idx in self._indexes.items()
        ]

    def __repr__(self):
        return f"JSONIndexManager(indexes={len(self._indexes)})"
