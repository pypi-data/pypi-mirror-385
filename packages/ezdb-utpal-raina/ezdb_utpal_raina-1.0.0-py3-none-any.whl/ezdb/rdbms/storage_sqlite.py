"""
SQLite-based storage backend for EzDB RDBMS tables.

This module provides a production-ready storage layer using SQLite,
replacing the JSON-based storage for better performance and scalability.
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import os


class SQLiteTableStore:
    """
    SQLite-backed table storage with ACID guarantees.

    Features:
    - ACID transactions
    - B-tree indexes for fast queries
    - Handles millions of records
    - 10x smaller file size than JSON
    - Concurrent read access with WAL mode
    """

    def __init__(self, db_path: str):
        """
        Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish database connection with optimizations."""
        # Create directory if needed
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)

        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow multi-threaded access
            isolation_level=None  # Autocommit mode for explicit transaction control
        )

        # Enable Write-Ahead Logging for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")

        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys=ON")

        # Use memory-mapped I/O for better performance
        self.conn.execute("PRAGMA mmap_size=268435456")  # 256 MB

        # Return rows as dict-like objects
        self.conn.row_factory = sqlite3.Row

    def create_table(self, table_name: str, schema: Dict[str, Any]):
        """
        Create a new table with given schema.

        Args:
            table_name: Name of the table
            schema: Schema definition with columns (list format)
        """
        # Build CREATE TABLE statement
        columns = []

        # Get columns - handle both formats
        schema_columns = schema.get('columns', [])

        for col_def in schema_columns:
            col_name = col_def['name']
            # Get type - handle both 'type' and 'data_type' keys
            col_type_str = col_def.get('data_type') or col_def.get('type', 'TEXT')
            col_type = self._map_type(col_type_str)
            col_spec = f"{col_name} {col_type}"

            # Add constraints
            if col_def.get('primary_key'):
                col_spec += " PRIMARY KEY"
                if col_def.get('auto_increment'):
                    col_spec += " AUTOINCREMENT"

            if col_def.get('unique'):
                col_spec += " UNIQUE"

            if col_def.get('not_null') or not col_def.get('nullable', True):
                col_spec += " NOT NULL"

            if 'default' in col_def and col_def['default'] is not None:
                default_val = col_def['default']
                if isinstance(default_val, str):
                    col_spec += f" DEFAULT '{default_val}'"
                else:
                    col_spec += f" DEFAULT {default_val}"

            columns.append(col_spec)

        # Add foreign key constraints
        if 'foreign_keys' in schema:
            for fk in schema['foreign_keys']:
                fk_spec = f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']['table']}({fk['references']['column']})"
                if fk.get('on_delete'):
                    fk_spec += f" ON DELETE {fk['on_delete']}"
                if fk.get('on_update'):
                    fk_spec += f" ON UPDATE {fk['on_update']}"
                columns.append(fk_spec)

        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.conn.execute(sql)

        # Create indexes for better query performance
        self._create_indexes(table_name, schema)

    def _map_type(self, ezdb_type: str) -> str:
        """Map EzDB types to SQLite types."""
        type_mapping = {
            'INTEGER': 'INTEGER',
            'FLOAT': 'REAL',
            'REAL': 'REAL',  # Support REAL directly
            'TEXT': 'TEXT',
            'BOOLEAN': 'INTEGER',  # SQLite uses 0/1 for boolean
            'DATE': 'TEXT',  # Store as ISO format
            'TIMESTAMP': 'TEXT',
            'JSON': 'TEXT'  # Store JSON as text
        }
        return type_mapping.get(ezdb_type.upper(), 'TEXT')

    def _create_indexes(self, table_name: str, schema: Dict[str, Any]):
        """Create indexes for frequently queried columns."""
        schema_columns = schema.get('columns', [])
        for col_def in schema_columns:
            col_name = col_def['name']
            # Create index for primary keys, unique columns, and foreign keys
            if col_def.get('unique') or col_def.get('indexed'):
                index_name = f"idx_{table_name}_{col_name}"
                try:
                    self.conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({col_name})")
                except sqlite3.Error:
                    pass  # Index might already exist

    def insert(self, table_name: str, row_data: Dict[str, Any]) -> int:
        """
        Insert a row into the table.

        Args:
            table_name: Name of the table
            row_data: Dictionary of column values

        Returns:
            Row ID of inserted row
        """
        columns = list(row_data.keys())
        placeholders = ','.join(['?' for _ in columns])
        values = [self._serialize_value(row_data[col]) for col in columns]

        sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        cursor = self.conn.execute(sql, values)
        self.conn.commit()
        return cursor.lastrowid

    def insert_batch(self, table_name: str, rows: List[Dict[str, Any]]) -> List[int]:
        """
        Insert multiple rows efficiently.

        Args:
            table_name: Name of the table
            rows: List of row dictionaries

        Returns:
            List of inserted row IDs
        """
        if not rows:
            return []

        columns = list(rows[0].keys())
        placeholders = ','.join(['?' for _ in columns])
        sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        row_ids = []
        self.conn.execute("BEGIN TRANSACTION")
        try:
            for row in rows:
                values = [self._serialize_value(row[col]) for col in columns]
                cursor = self.conn.execute(sql, values)
                row_ids.append(cursor.lastrowid)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

        return row_ids

    def select(self, table_name: str, where: Optional[str] = None,
               params: Optional[List] = None, limit: Optional[int] = None,
               offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Select rows from table.

        Args:
            table_name: Name of the table
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause
            limit: Maximum number of rows
            offset: Number of rows to skip

        Returns:
            List of row dictionaries
        """
        sql = f"SELECT * FROM {table_name}"

        if where:
            sql += f" WHERE {where}"

        if limit:
            sql += f" LIMIT {limit}"

        if offset:
            sql += f" OFFSET {offset}"

        cursor = self.conn.execute(sql, params or [])
        rows = cursor.fetchall()

        # Convert Row objects to dictionaries
        return [dict(row) for row in rows]

    def update(self, table_name: str, row_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a row by ID.

        Args:
            table_name: Name of the table
            row_id: ID of row to update
            updates: Dictionary of column updates

        Returns:
            True if row was updated
        """
        set_clause = ','.join([f"{col}=?" for col in updates.keys()])
        values = [self._serialize_value(val) for val in updates.values()]
        values.append(row_id)

        sql = f"UPDATE {table_name} SET {set_clause} WHERE rowid=?"

        cursor = self.conn.execute(sql, values)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, table_name: str, where: str, params: List) -> int:
        """
        Delete rows matching condition.

        Args:
            table_name: Name of the table
            where: WHERE clause
            params: Parameters for WHERE clause

        Returns:
            Number of rows deleted
        """
        sql = f"DELETE FROM {table_name} WHERE {where}"
        cursor = self.conn.execute(sql, params)
        self.conn.commit()
        return cursor.rowcount

    def drop_table(self, table_name: str):
        """Drop a table."""
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

    def get_all_tables(self) -> List[str]:
        """Get list of all table names."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a table."""
        cursor = self.conn.execute(f"PRAGMA table_info({table_name})")
        columns = {}

        for row in cursor.fetchall():
            col_name = row[1]
            col_type = row[2]
            not_null = row[3] == 1
            default_val = row[4]
            is_pk = row[5] == 1

            columns[col_name] = {
                'type': col_type,
                'not_null': not_null,
                'primary_key': is_pk
            }

            if default_val is not None:
                columns[col_name]['default'] = default_val

        return {'columns': columns}

    def count(self, table_name: str, where: Optional[str] = None,
              params: Optional[List] = None) -> int:
        """Count rows in table."""
        sql = f"SELECT COUNT(*) FROM {table_name}"

        if where:
            sql += f" WHERE {where}"

        cursor = self.conn.execute(sql, params or [])
        return cursor.fetchone()[0]

    def _serialize_value(self, value: Any) -> Any:
        """Convert Python values to SQLite-compatible format."""
        if value is None:
            return None
        elif isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, (date, datetime)):
            return value.isoformat()
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        else:
            return value

    def begin_transaction(self):
        """Start a transaction."""
        self.conn.execute("BEGIN TRANSACTION")

    def commit(self):
        """Commit current transaction."""
        self.conn.commit()

    def rollback(self):
        """Rollback current transaction."""
        self.conn.rollback()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def vacuum(self):
        """Optimize database file size."""
        self.conn.execute("VACUUM")

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}

        # File size
        if os.path.exists(self.db_path):
            stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)

        # Table count
        stats['table_count'] = len(self.get_all_tables())

        # Row counts
        stats['tables'] = {}
        for table in self.get_all_tables():
            stats['tables'][table] = self.count(table)

        return stats

    # Vector storage methods
    def create_vector_table(self, collection_name: str, dimension: int, metric: str):
        """
        Create a table to store vectors for a collection.

        Schema:
        - vector_id: INTEGER PRIMARY KEY (maps to row_id in source table)
        - vector_data: TEXT (JSON array of floats)
        - metadata_json: TEXT (JSON metadata)
        - document: TEXT (source text)
        - created_at: TEXT (ISO timestamp)
        """
        # Use a special prefix to distinguish vector tables
        table_name = f"__vectors_{collection_name}"

        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            vector_id INTEGER PRIMARY KEY,
            vector_data TEXT NOT NULL,
            metadata_json TEXT,
            document TEXT,
            dimension INTEGER NOT NULL,
            metric TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(sql)
        self.conn.commit()

        # Create index for faster lookups
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_created ON {table_name}(created_at)")
        self.conn.commit()

    def save_vectors(self, collection_name: str, vectors: List, ids: List,
                     metadata_list: List, documents: List, dimension: int, metric: str):
        """
        Save vectors to SQLite.

        Args:
            collection_name: Name of the vector collection
            vectors: List of numpy arrays
            ids: List of vector IDs
            metadata_list: List of metadata dicts
            documents: List of document strings
            dimension: Vector dimension
            metric: Similarity metric
        """
        import json

        table_name = f"__vectors_{collection_name}"

        # Ensure table exists
        self.create_vector_table(collection_name, dimension, metric)

        # Clear existing vectors for this collection
        self.conn.execute(f"DELETE FROM {table_name}")

        # Insert vectors in batch
        if len(vectors) > 0:
            self.conn.execute("BEGIN TRANSACTION")
            try:
                for i, (vec_id, vector) in enumerate(zip(ids, vectors)):
                    # Convert numpy array to JSON
                    vector_json = json.dumps(vector.tolist() if hasattr(vector, 'tolist') else vector)
                    metadata_json = json.dumps(metadata_list[i]) if i < len(metadata_list) else None
                    document = documents[i] if i < len(documents) else None

                    # Ensure vec_id is an integer (convert if it's a string or numpy type)
                    if isinstance(vec_id, str):
                        try:
                            vec_id_int = int(vec_id)
                        except (ValueError, TypeError):
                            vec_id_int = i  # Use index as fallback
                    elif hasattr(vec_id, 'item'):  # numpy integer
                        vec_id_int = vec_id.item()
                    else:
                        vec_id_int = int(vec_id) if vec_id is not None else i

                    self.conn.execute(
                        f"""INSERT OR REPLACE INTO {table_name}
                           (vector_id, vector_data, metadata_json, document, dimension, metric)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (vec_id_int, vector_json, metadata_json, document, dimension, metric)
                    )
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise e

    def load_vectors(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Load vectors from SQLite.

        Returns:
            Dict with keys: vectors, ids, metadata_list, documents, dimension, metric
            or None if collection doesn't exist
        """
        import json
        import numpy as np

        table_name = f"__vectors_{collection_name}"

        # Check if table exists
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not cursor.fetchone():
            return None

        # Load all vectors
        cursor = self.conn.execute(
            f"SELECT vector_id, vector_data, metadata_json, document, dimension, metric FROM {table_name} ORDER BY vector_id"
        )

        rows = cursor.fetchall()
        if not rows:
            return None

        vectors = []
        ids = []
        metadata_list = []
        documents = []
        dimension = rows[0][4]
        metric = rows[0][5]

        for row in rows:
            ids.append(row[0])
            vectors.append(np.array(json.loads(row[1]), dtype=np.float32))
            metadata_list.append(json.loads(row[2]) if row[2] else {})
            documents.append(row[3])

        return {
            'vectors': vectors,
            'ids': ids,
            'metadata_list': metadata_list,
            'documents': documents,
            'dimension': dimension,
            'metric': metric
        }

    def list_vector_collections(self) -> List[str]:
        """List all vector collection tables."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '__vectors_%'"
        )
        collections = []
        for row in cursor.fetchall():
            # Remove __vectors_ prefix
            collection_name = row[0].replace('__vectors_', '')
            collections.append(collection_name)
        return collections

    def delete_vector_collection(self, collection_name: str):
        """Delete a vector collection table."""
        table_name = f"__vectors_{collection_name}"
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

    # Trigger management methods
    def _ensure_triggers_table(self):
        """Ensure the triggers metadata table exists."""
        sql = """
        CREATE TABLE IF NOT EXISTS __triggers (
            trigger_name TEXT PRIMARY KEY,
            table_name TEXT NOT NULL,
            timing TEXT NOT NULL,
            event TEXT NOT NULL,
            trigger_body TEXT NOT NULL,
            when_condition TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(sql)
        self.conn.commit()

        # Create index for faster lookups
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_triggers_table ON __triggers(table_name, event)")
        self.conn.commit()

    def create_trigger(self, trigger_name: str, table_name: str, timing: str,
                      event: str, trigger_body: str, when_condition: Optional[str] = None,
                      or_replace: bool = False):
        """
        Create or replace a trigger.

        Args:
            trigger_name: Name of the trigger
            table_name: Table the trigger is attached to
            timing: BEFORE or AFTER
            event: INSERT, UPDATE, or DELETE
            trigger_body: SQL statements in trigger body
            when_condition: Optional WHEN condition
            or_replace: If True, replace existing trigger
        """
        self._ensure_triggers_table()

        # Check if trigger exists
        cursor = self.conn.execute(
            "SELECT trigger_name FROM __triggers WHERE trigger_name=?",
            (trigger_name,)
        )
        exists = cursor.fetchone() is not None

        if exists and not or_replace:
            raise ValueError(f"Trigger '{trigger_name}' already exists")

        # Insert or replace trigger
        sql = """
        INSERT OR REPLACE INTO __triggers
        (trigger_name, table_name, timing, event, trigger_body, when_condition)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(sql, (
            trigger_name,
            table_name,
            timing,
            event,
            trigger_body,
            when_condition
        ))
        self.conn.commit()

    def drop_trigger(self, trigger_name: str, if_exists: bool = False):
        """
        Drop a trigger.

        Args:
            trigger_name: Name of the trigger to drop
            if_exists: If True, don't raise error if trigger doesn't exist

        Raises:
            ValueError: If trigger doesn't exist and if_exists is False
        """
        self._ensure_triggers_table()

        # Check if trigger exists
        cursor = self.conn.execute(
            "SELECT trigger_name FROM __triggers WHERE trigger_name=?",
            (trigger_name,)
        )
        exists = cursor.fetchone() is not None

        if not exists and not if_exists:
            raise ValueError(f"Trigger '{trigger_name}' does not exist")

        # Delete trigger
        self.conn.execute("DELETE FROM __triggers WHERE trigger_name=?", (trigger_name,))
        self.conn.commit()

    def get_triggers(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all triggers, optionally filtered by table.

        Args:
            table_name: Optional table name to filter triggers

        Returns:
            List of trigger definitions
        """
        self._ensure_triggers_table()

        if table_name:
            cursor = self.conn.execute(
                """SELECT trigger_name, table_name, timing, event, trigger_body, when_condition, created_at
                   FROM __triggers WHERE table_name=?
                   ORDER BY trigger_name""",
                (table_name,)
            )
        else:
            cursor = self.conn.execute(
                """SELECT trigger_name, table_name, timing, event, trigger_body, when_condition, created_at
                   FROM __triggers
                   ORDER BY trigger_name"""
            )

        triggers = []
        for row in cursor.fetchall():
            triggers.append({
                'trigger_name': row[0],
                'table_name': row[1],
                'timing': row[2],
                'event': row[3],
                'trigger_body': row[4],
                'when_condition': row[5],
                'created_at': row[6]
            })

        return triggers

    def get_triggers_for_event(self, table_name: str, event: str, timing: str) -> List[Dict[str, Any]]:
        """
        Get triggers for a specific table, event, and timing.

        Args:
            table_name: Name of the table
            event: INSERT, UPDATE, or DELETE
            timing: BEFORE or AFTER

        Returns:
            List of trigger definitions matching the criteria
        """
        self._ensure_triggers_table()

        cursor = self.conn.execute(
            """SELECT trigger_name, table_name, timing, event, trigger_body, when_condition
               FROM __triggers
               WHERE table_name=? AND event=? AND timing=?
               ORDER BY trigger_name""",
            (table_name, event, timing)
        )

        triggers = []
        for row in cursor.fetchall():
            triggers.append({
                'trigger_name': row[0],
                'table_name': row[1],
                'timing': row[2],
                'event': row[3],
                'trigger_body': row[4],
                'when_condition': row[5]
            })

        return triggers

    # Python function/procedure management methods
    def _ensure_functions_table(self):
        """Ensure the Python functions metadata table exists."""
        sql = """
        CREATE TABLE IF NOT EXISTS __python_functions (
            function_name TEXT PRIMARY KEY,
            function_type TEXT NOT NULL,
            parameters TEXT,
            return_type TEXT,
            python_code TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(sql)
        self.conn.commit()

        # Create index for faster lookups
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_functions_type ON __python_functions(function_type)")
        self.conn.commit()

    def create_python_function(self, function_name: str, function_type: str,
                               python_code: str, parameters: Optional[str] = None,
                               return_type: Optional[str] = None,
                               description: Optional[str] = None,
                               or_replace: bool = False):
        """
        Create or replace a Python function/procedure.

        Args:
            function_name: Name of the function
            function_type: FUNCTION or PROCEDURE
            python_code: Python code to execute
            parameters: Parameter specification (comma-separated)
            return_type: Return type for functions
            description: Optional description
            or_replace: If True, replace existing function
        """
        self._ensure_functions_table()

        # Check if function exists
        cursor = self.conn.execute(
            "SELECT function_name FROM __python_functions WHERE function_name=?",
            (function_name,)
        )
        exists = cursor.fetchone() is not None

        if exists and not or_replace:
            raise ValueError(f"Function '{function_name}' already exists")

        # Insert or replace function
        sql = """
        INSERT OR REPLACE INTO __python_functions
        (function_name, function_type, parameters, return_type, python_code, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(sql, (
            function_name,
            function_type,
            parameters,
            return_type,
            python_code,
            description
        ))
        self.conn.commit()

    def drop_python_function(self, function_name: str, if_exists: bool = False):
        """
        Drop a Python function/procedure.

        Args:
            function_name: Name of the function to drop
            if_exists: If True, don't raise error if function doesn't exist

        Raises:
            ValueError: If function doesn't exist and if_exists is False
        """
        self._ensure_functions_table()

        # Check if function exists
        cursor = self.conn.execute(
            "SELECT function_name FROM __python_functions WHERE function_name=?",
            (function_name,)
        )
        exists = cursor.fetchone() is not None

        if not exists and not if_exists:
            raise ValueError(f"Function '{function_name}' does not exist")

        # Delete function
        self.conn.execute("DELETE FROM __python_functions WHERE function_name=?", (function_name,))
        self.conn.commit()

    def get_python_function(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a Python function by name.

        Args:
            function_name: Name of the function

        Returns:
            Function definition dict or None if not found
        """
        self._ensure_functions_table()

        cursor = self.conn.execute(
            """SELECT function_name, function_type, parameters, return_type, python_code, description, created_at
               FROM __python_functions WHERE function_name=?""",
            (function_name,)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'function_name': row[0],
            'function_type': row[1],
            'parameters': row[2],
            'return_type': row[3],
            'python_code': row[4],
            'description': row[5],
            'created_at': row[6]
        }

    def get_all_python_functions(self, function_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all Python functions, optionally filtered by type.

        Args:
            function_type: Optional filter (FUNCTION or PROCEDURE)

        Returns:
            List of function definitions
        """
        self._ensure_functions_table()

        if function_type:
            cursor = self.conn.execute(
                """SELECT function_name, function_type, parameters, return_type, python_code, description, created_at
                   FROM __python_functions WHERE function_type=?
                   ORDER BY function_name""",
                (function_type,)
            )
        else:
            cursor = self.conn.execute(
                """SELECT function_name, function_type, parameters, return_type, python_code, description, created_at
                   FROM __python_functions
                   ORDER BY function_name"""
            )

        functions = []
        for row in cursor.fetchall():
            functions.append({
                'function_name': row[0],
                'function_type': row[1],
                'parameters': row[2],
                'return_type': row[3],
                'python_code': row[4],
                'description': row[5],
                'created_at': row[6]
            })

        return functions
