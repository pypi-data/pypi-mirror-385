"""
Table storage engine for EzDB RDBMS
Row-based storage with support for all data types including VECTOR and JSON
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from .schema import TableSchema, Column, DataType
from .json_index import JSONIndexManager


class TableStore:
    """
    Row-based storage for a single table.
    Stores rows as dictionaries with column names as keys.
    """

    def __init__(self, schema: TableSchema):
        """
        Initialize table store.

        Args:
            schema: Table schema definition
        """
        self.schema = schema
        self.rows: List[Dict[str, Any]] = []
        self._next_auto_increment = 1

        # Create indexes for quick lookups
        self._primary_key_index: Dict[Any, int] = {}  # PK value -> row index
        self._unique_indexes: Dict[str, Dict[Any, int]] = {}  # column -> {value -> row index}

        # JSON path indexes
        self.json_indexes = JSONIndexManager()

        # Initialize unique indexes
        for col in schema.columns:
            if col.unique or col.primary_key:
                self._unique_indexes[col.name] = {}

    def insert(self, row: Dict[str, Any]) -> int:
        """
        Insert a row into the table.

        Args:
            row: Dictionary with column names as keys

        Returns:
            Row ID (index)

        Raises:
            ValueError: If row violates schema or constraints
        """
        # Handle auto-increment
        auto_inc_col = self.schema.get_auto_increment_column()
        if auto_inc_col:
            if auto_inc_col.name not in row or row[auto_inc_col.name] is None:
                row[auto_inc_col.name] = self._next_auto_increment
                self._next_auto_increment += 1
            else:
                # User provided value, update next auto increment
                provided_value = row[auto_inc_col.name]
                if provided_value >= self._next_auto_increment:
                    self._next_auto_increment = provided_value + 1

        # Cast and validate row
        casted_row = self.schema.cast_row(row)

        # Check unique constraints
        pk_col = self.schema.get_primary_key()
        if pk_col:
            pk_value = casted_row[pk_col.name]
            if pk_value in self._primary_key_index:
                raise ValueError(f"Duplicate primary key value: {pk_value}")

        for col_name, index in self._unique_indexes.items():
            value = casted_row.get(col_name)
            if value is not None and value in index:
                raise ValueError(f"Duplicate value for unique column '{col_name}': {value}")

        # Insert row
        row_id = len(self.rows)
        self.rows.append(casted_row)

        # Update indexes
        if pk_col:
            self._primary_key_index[casted_row[pk_col.name]] = row_id

        for col_name, index in self._unique_indexes.items():
            value = casted_row.get(col_name)
            if value is not None:
                index[value] = row_id

        # Update JSON indexes
        self.json_indexes.insert(row_id, casted_row)

        return row_id

    def insert_batch(self, rows: List[Dict[str, Any]]) -> List[int]:
        """
        Insert multiple rows efficiently.

        Args:
            rows: List of row dictionaries

        Returns:
            List of row IDs
        """
        row_ids = []
        for row in rows:
            row_id = self.insert(row)
            row_ids.append(row_id)
        return row_ids

    def get(self, row_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a row by ID.

        Args:
            row_id: Row index

        Returns:
            Row dictionary or None if not found
        """
        if 0 <= row_id < len(self.rows):
            return self.rows[row_id].copy()
        return None

    def get_by_primary_key(self, pk_value: Any) -> Optional[Dict[str, Any]]:
        """
        Get a row by primary key value.

        Args:
            pk_value: Primary key value

        Returns:
            Row dictionary or None if not found
        """
        row_id = self._primary_key_index.get(pk_value)
        if row_id is not None:
            return self.rows[row_id].copy()
        return None

    def update(self, row_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a row.

        Args:
            row_id: Row index
            updates: Dictionary of column updates

        Returns:
            True if updated, False if row not found

        Raises:
            ValueError: If update violates schema or constraints
        """
        if row_id < 0 or row_id >= len(self.rows):
            return False

        current_row = self.rows[row_id]
        updated_row = current_row.copy()
        updated_row.update(updates)

        # Cast and validate
        casted_row = self.schema.cast_row(updated_row)

        # Check unique constraints (excluding current row)
        pk_col = self.schema.get_primary_key()
        if pk_col and pk_col.name in updates:
            new_pk = casted_row[pk_col.name]
            existing_row_id = self._primary_key_index.get(new_pk)
            if existing_row_id is not None and existing_row_id != row_id:
                raise ValueError(f"Duplicate primary key value: {new_pk}")

        for col_name in updates.keys():
            if col_name in self._unique_indexes:
                new_value = casted_row[col_name]
                existing_row_id = self._unique_indexes[col_name].get(new_value)
                if existing_row_id is not None and existing_row_id != row_id:
                    raise ValueError(f"Duplicate value for unique column '{col_name}': {new_value}")

        # Update indexes
        if pk_col and pk_col.name in updates:
            old_pk = current_row[pk_col.name]
            new_pk = casted_row[pk_col.name]
            del self._primary_key_index[old_pk]
            self._primary_key_index[new_pk] = row_id

        for col_name in updates.keys():
            if col_name in self._unique_indexes:
                old_value = current_row.get(col_name)
                new_value = casted_row[col_name]
                if old_value is not None and old_value in self._unique_indexes[col_name]:
                    del self._unique_indexes[col_name][old_value]
                if new_value is not None:
                    self._unique_indexes[col_name][new_value] = row_id

        # Update JSON indexes
        self.json_indexes.update(row_id, current_row, casted_row)

        # Apply update
        self.rows[row_id] = casted_row
        return True

    def delete(self, row_id: int) -> bool:
        """
        Delete a row.

        Args:
            row_id: Row index

        Returns:
            True if deleted, False if row not found
        """
        if row_id < 0 or row_id >= len(self.rows):
            return False

        row = self.rows[row_id]

        # Remove from indexes
        pk_col = self.schema.get_primary_key()
        if pk_col:
            pk_value = row[pk_col.name]
            if pk_value in self._primary_key_index:
                del self._primary_key_index[pk_value]

        for col_name, index in self._unique_indexes.items():
            value = row.get(col_name)
            if value is not None and value in index:
                del index[value]

        # Update JSON indexes
        self.json_indexes.delete(row_id, row)

        # Mark as deleted (tombstone)
        # For simplicity, we'll use None to mark deleted rows
        # In production, use a proper deletion strategy
        self.rows[row_id] = None

        return True

    def scan(self,
             where: Optional[callable] = None,
             limit: Optional[int] = None,
             offset: int = 0) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Scan table rows with optional filtering.

        Args:
            where: Optional filter function (row -> bool)
            limit: Maximum number of rows to return
            offset: Number of rows to skip

        Returns:
            List of (row_id, row) tuples
        """
        results = []
        count = 0
        skipped = 0

        for row_id, row in enumerate(self.rows):
            # Skip deleted rows
            if row is None:
                continue

            # Apply where filter
            if where and not where(row):
                continue

            # Apply offset
            if skipped < offset:
                skipped += 1
                continue

            # Add to results
            results.append((row_id, row.copy()))
            count += 1

            # Apply limit
            if limit and count >= limit:
                break

        return results

    def count(self, where: Optional[callable] = None) -> int:
        """
        Count rows matching optional filter.

        Args:
            where: Optional filter function (row -> bool)

        Returns:
            Number of matching rows
        """
        count = 0
        for row in self.rows:
            if row is None:  # Skip deleted
                continue
            if where is None or where(row):
                count += 1
        return count

    def size(self) -> int:
        """Get total number of non-deleted rows"""
        return sum(1 for row in self.rows if row is not None)

    def create_json_index(self, column_name: str, path: str):
        """
        Create a JSON path index for fast lookups.

        Args:
            column_name: Name of JSON column
            path: JSON path to index (e.g., 'user.age')

        Example:
            table.create_json_index('metadata', 'user.age')
            # Now queries on metadata.user.age will use the index
        """
        # Validate column exists and is JSON type
        col = self.schema.get_column(column_name)
        if col is None:
            raise ValueError(f"Column '{column_name}' does not exist")
        if col.data_type != DataType.JSON:
            raise ValueError(f"Column '{column_name}' is not JSON type")

        # Create the index
        index = self.json_indexes.create_index(column_name, path)

        # Build index for existing rows
        for row_id, row in enumerate(self.rows):
            if row is not None:
                json_obj = row.get(column_name)
                if json_obj is not None:
                    index.insert(row_id, json_obj)

        return index

    def clear(self):
        """Remove all rows"""
        self.rows.clear()
        self._primary_key_index.clear()
        for index in self._unique_indexes.values():
            index.clear()
        self.json_indexes = JSONIndexManager()
        self._next_auto_increment = 1

    def get_all_rows(self) -> List[Dict[str, Any]]:
        """Get all non-deleted rows"""
        return [row.copy() for row in self.rows if row is not None]

    def __repr__(self):
        return f"TableStore(table={self.schema.name}, rows={self.size()})"
