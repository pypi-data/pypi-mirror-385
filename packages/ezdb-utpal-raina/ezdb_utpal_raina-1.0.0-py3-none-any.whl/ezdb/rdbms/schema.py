"""
Schema and type system for EzDB RDBMS
Defines data types, columns, and table schemas
"""

from enum import Enum
from typing import Any, List, Optional, Union
from dataclasses import dataclass
import numpy as np


class DataType(Enum):
    """Supported data types in EzDB RDBMS"""
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"
    BLOB = "BLOB"
    VECTOR = "VECTOR"  # Special type for vector embeddings
    JSON = "JSON"  # JSON data type for structured documents

    @classmethod
    def from_string(cls, type_str: str) -> 'DataType':
        """Parse data type from SQL string"""
        type_str = type_str.upper()

        # Handle VECTOR(n) syntax
        if type_str.startswith("VECTOR"):
            return cls.VECTOR

        # Map common SQL type aliases
        type_mapping = {
            'INT': cls.INTEGER,
            'INTEGER': cls.INTEGER,
            'BIGINT': cls.INTEGER,
            'SMALLINT': cls.INTEGER,
            'TINYINT': cls.INTEGER,
            'TEXT': cls.TEXT,
            'VARCHAR': cls.TEXT,
            'CHAR': cls.TEXT,
            'STRING': cls.TEXT,
            'REAL': cls.REAL,
            'FLOAT': cls.REAL,
            'DOUBLE': cls.REAL,
            'NUMERIC': cls.REAL,
            'DECIMAL': cls.REAL,
            'BOOLEAN': cls.BOOLEAN,
            'BOOL': cls.BOOLEAN,
            'BLOB': cls.BLOB,
            'BYTES': cls.BLOB,
            'VECTOR': cls.VECTOR,
            'JSON': cls.JSON,
            'JSONB': cls.JSON  # PostgreSQL-style alias
        }

        if type_str in type_mapping:
            return type_mapping[type_str]

        raise ValueError(f"Unknown data type: {type_str}")


@dataclass
class Column:
    """Represents a column in a table"""
    name: str
    data_type: DataType
    vector_dimension: Optional[int] = None  # For VECTOR type
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Any = None
    auto_increment: bool = False

    def __post_init__(self):
        """Validate column definition"""
        if self.data_type == DataType.VECTOR:
            if self.vector_dimension is None or self.vector_dimension <= 0:
                raise ValueError(f"VECTOR column '{self.name}' must specify dimension > 0")

        if self.primary_key:
            self.nullable = False  # Primary keys cannot be null

    def validate_value(self, value: Any) -> bool:
        """Validate if a value is compatible with this column's type"""
        if value is None:
            return self.nullable

        if self.data_type == DataType.INTEGER:
            return isinstance(value, (int, np.integer))
        elif self.data_type == DataType.TEXT:
            return isinstance(value, str)
        elif self.data_type == DataType.REAL:
            return isinstance(value, (int, float, np.floating, np.integer))
        elif self.data_type == DataType.BOOLEAN:
            return isinstance(value, (bool, np.bool_))
        elif self.data_type == DataType.BLOB:
            return isinstance(value, (bytes, bytearray))
        elif self.data_type == DataType.VECTOR:
            if isinstance(value, (list, np.ndarray)):
                arr = np.array(value)
                return arr.ndim == 1 and len(arr) == self.vector_dimension
            return False
        elif self.data_type == DataType.JSON:
            return isinstance(value, (dict, list, str))

        return False

    def cast_value(self, value: Any) -> Any:
        """Cast value to appropriate type for this column"""
        if value is None:
            if not self.nullable:
                raise ValueError(f"Column '{self.name}' cannot be NULL")
            return None

        try:
            if self.data_type == DataType.INTEGER:
                return int(value)
            elif self.data_type == DataType.TEXT:
                return str(value)
            elif self.data_type == DataType.REAL:
                return float(value)
            elif self.data_type == DataType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 't', 'y')
                return bool(value)
            elif self.data_type == DataType.BLOB:
                if isinstance(value, str):
                    return value.encode()
                return bytes(value)
            elif self.data_type == DataType.VECTOR:
                arr = np.array(value, dtype=np.float32)
                if arr.ndim != 1 or len(arr) != self.vector_dimension:
                    raise ValueError(
                        f"VECTOR column '{self.name}' expects dimension {self.vector_dimension}, "
                        f"got {len(arr)}"
                    )
                return arr
            elif self.data_type == DataType.JSON:
                import json
                if isinstance(value, str):
                    # Parse JSON string
                    return json.loads(value)
                elif isinstance(value, (dict, list)):
                    # Already a Python object, return as-is
                    return value
                else:
                    raise ValueError(f"Cannot convert {type(value)} to JSON")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot cast value to {self.data_type.value} for column '{self.name}': {e}")

    def __repr__(self):
        type_str = self.data_type.value
        if self.data_type == DataType.VECTOR:
            type_str = f"VECTOR({self.vector_dimension})"

        flags = []
        if self.primary_key:
            flags.append("PRIMARY KEY")
        if self.unique:
            flags.append("UNIQUE")
        if not self.nullable:
            flags.append("NOT NULL")
        if self.auto_increment:
            flags.append("AUTO_INCREMENT")

        flag_str = " " + " ".join(flags) if flags else ""
        return f"{self.name} {type_str}{flag_str}"


class TableSchema:
    """Represents the schema of a table"""

    def __init__(self, name: str, columns: List[Column]):
        """
        Initialize table schema.

        Args:
            name: Table name
            columns: List of Column objects
        """
        self.name = name
        self.columns = columns
        self._column_map = {col.name: col for col in columns}

        # Validate schema
        self._validate_schema()

    def _validate_schema(self):
        """Validate table schema"""
        # Check for duplicate column names
        column_names = [col.name for col in self.columns]
        if len(column_names) != len(set(column_names)):
            raise ValueError(f"Duplicate column names in table '{self.name}'")

        # Check for at most one primary key
        pk_columns = [col for col in self.columns if col.primary_key]
        if len(pk_columns) > 1:
            raise ValueError(f"Table '{self.name}' cannot have multiple primary key columns")

        # Check for at most one auto_increment column
        ai_columns = [col for col in self.columns if col.auto_increment]
        if len(ai_columns) > 1:
            raise ValueError(f"Table '{self.name}' cannot have multiple auto_increment columns")

        # Auto increment must be INTEGER and primary key
        for col in ai_columns:
            if col.data_type != DataType.INTEGER:
                raise ValueError(f"AUTO_INCREMENT column '{col.name}' must be INTEGER type")

    def get_column(self, name: str) -> Optional[Column]:
        """Get column by name"""
        return self._column_map.get(name)

    def get_primary_key(self) -> Optional[Column]:
        """Get primary key column if exists"""
        for col in self.columns:
            if col.primary_key:
                return col
        return None

    def get_auto_increment_column(self) -> Optional[Column]:
        """Get auto_increment column if exists"""
        for col in self.columns:
            if col.auto_increment:
                return col
        return None

    def get_vector_columns(self) -> List[Column]:
        """Get all VECTOR type columns"""
        return [col for col in self.columns if col.data_type == DataType.VECTOR]

    def validate_row(self, row: dict) -> bool:
        """Validate if a row dict matches the schema"""
        for col in self.columns:
            value = row.get(col.name)
            if not col.validate_value(value):
                return False
        return True

    def cast_row(self, row: dict) -> dict:
        """Cast row values to appropriate types"""
        casted_row = {}
        for col in self.columns:
            if col.name in row:
                casted_row[col.name] = col.cast_value(row[col.name])
            elif col.default is not None:
                casted_row[col.name] = col.default
            elif not col.nullable and not col.auto_increment:
                raise ValueError(f"Missing required column '{col.name}'")
            else:
                casted_row[col.name] = None
        return casted_row

    def __repr__(self):
        columns_str = ",\n  ".join(str(col) for col in self.columns)
        return f"CREATE TABLE {self.name} (\n  {columns_str}\n)"

    def to_dict(self) -> dict:
        """Convert schema to dictionary"""
        return {
            'name': self.name,
            'columns': [
                {
                    'name': col.name,
                    'type': col.data_type.value,
                    'vector_dimension': col.vector_dimension,
                    'nullable': col.nullable,
                    'primary_key': col.primary_key,
                    'unique': col.unique,
                    'default': col.default,
                    'auto_increment': col.auto_increment
                }
                for col in self.columns
            ]
        }

    @classmethod
    def from_dict(cls, schema_dict: dict) -> 'TableSchema':
        """Create schema from dictionary"""
        columns = []
        for col_dict in schema_dict['columns']:
            col = Column(
                name=col_dict['name'],
                data_type=DataType(col_dict['type']),
                vector_dimension=col_dict.get('vector_dimension'),
                nullable=col_dict.get('nullable', True),
                primary_key=col_dict.get('primary_key', False),
                unique=col_dict.get('unique', False),
                default=col_dict.get('default'),
                auto_increment=col_dict.get('auto_increment', False)
            )
            columns.append(col)

        return cls(name=schema_dict['name'], columns=columns)
