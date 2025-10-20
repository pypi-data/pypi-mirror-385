"""
Auto-Vectorization System for RDBMS Tables
Automatically creates vector collections and embeds text columns
"""

from typing import List, Dict, Any, Optional
import numpy as np


class AutoVectorizer:
    """
    Manages automatic vectorization of RDBMS tables.

    Features:
    - Auto-creates vector collections for RDBMS tables
    - Auto-embeds TEXT columns on INSERT/UPDATE
    - Auto-syncs on DELETE
    - Provides hybrid query capabilities
    """

    def __init__(self, ezdb_instance=None, embedding_model='sentence-transformers/all-MiniLM-L6-v2', dimension=384):
        """
        Initialize auto-vectorizer.

        Args:
            ezdb_instance: EzDB instance for vector operations (deprecated, not used)
            embedding_model: HuggingFace model name
            dimension: Vector dimension
        """
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        self.embedding_function = None
        self.enabled = True

        # Track which tables have vector collections
        self.vectorized_tables = {}  # table_name -> collection_name

        # Store EzDB instances for each collection
        self.vector_collections = {}  # collection_name -> EzDB instance

        # Track which columns to embed for each table
        self.table_text_columns = {}  # table_name -> [col1, col2, ...]

    def _init_embedding_function(self):
        """Lazy initialize embedding function"""
        if self.embedding_function is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_function = SentenceTransformer(self.embedding_model_name)
            except ImportError:
                print("WARNING: sentence-transformers not installed. Auto-vectorization disabled.")
                print("Install with: pip install sentence-transformers")
                self.enabled = False

    def should_vectorize_table(self, table_name: str, columns: List[Any]) -> bool:
        """
        Determine if table should be auto-vectorized.

        Criteria:
        - Table has at least one TEXT column
        - Table name doesn't end with '_vectors'
        """
        if table_name.endswith('_vectors'):
            return False

        # Check for TEXT columns
        text_columns = []
        for col in columns:
            # Handle both string data_type and DataType enum
            if hasattr(col, 'data_type'):
                col_type = str(col.data_type).upper()
            else:
                col_type = ''

            if 'TEXT' in col_type or col_type == 'VARCHAR':
                text_columns.append(col.name)

        return len(text_columns) > 0

    def create_vector_collection(self, table_name: str, columns: List[Any]) -> Optional[str]:
        """
        Create vector collection for RDBMS table.

        Args:
            table_name: Name of RDBMS table
            columns: List of column definitions

        Returns:
            Collection name if created, None otherwise
        """
        # Check if disabled
        if not self.enabled:
            return None

        if not self.should_vectorize_table(table_name, columns):
            return None

        # Identify TEXT columns
        text_columns = []
        for col in columns:
            # Handle both string data_type and DataType enum
            if hasattr(col, 'data_type'):
                col_type = str(col.data_type).upper()
            else:
                col_type = ''

            if 'TEXT' in col_type or col_type == 'VARCHAR':
                # Skip password, hash, and other sensitive columns
                col_name_lower = col.name.lower()
                if any(skip in col_name_lower for skip in ['password', 'hash', 'secret', 'key', 'token']):
                    continue
                text_columns.append(col.name)

        if not text_columns:
            return None

        # Create vector collection
        collection_name = f"{table_name}_vectors"

        try:
            # Create actual EzDB collection for vectors
            from ..database import EzDB

            vector_db = EzDB(
                dimension=self.dimension,
                metric='cosine',
                index_type='hnsw'
            )

            # Store the collection
            self.vector_collections[collection_name] = vector_db
            self.vectorized_tables[table_name] = collection_name
            self.table_text_columns[table_name] = text_columns

            print(f"✓ Auto-created vector collection: {collection_name}")
            print(f"  Tracking TEXT columns: {', '.join(text_columns)}")

            return collection_name

        except Exception as e:
            print(f"WARNING: Failed to create vector collection for {table_name}: {e}")
            return None

    def extract_text_for_embedding(self, table_name: str, row_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract and concatenate text from relevant columns.

        Args:
            table_name: Name of table
            row_data: Row data dictionary

        Returns:
            Concatenated text string or None
        """
        if table_name not in self.table_text_columns:
            return None

        text_columns = self.table_text_columns[table_name]

        # Concatenate text from all text columns
        text_parts = []
        for col_name in text_columns:
            value = row_data.get(col_name)
            if value and isinstance(value, str) and len(value.strip()) > 0:
                text_parts.append(f"{col_name}: {value}")

        if not text_parts:
            return None

        return "\n".join(text_parts)

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Embed text using configured embedding model.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None
        """
        if not self.enabled or not text:
            return None

        # Lazy init embedding function
        self._init_embedding_function()

        if self.embedding_function is None:
            return None

        try:
            # Encode text to vector
            embedding = self.embedding_function.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"WARNING: Failed to embed text: {e}")
            return None

    def on_insert(self, table_name: str, row_id: Any, row_data: Dict[str, Any]):
        """
        Handle INSERT - embed and store vector.

        Args:
            table_name: Name of table
            row_id: ID of inserted row
            row_data: Inserted row data
        """
        if not self.enabled or table_name not in self.vectorized_tables:
            return

        # Extract text
        text = self.extract_text_for_embedding(table_name, row_data)
        if not text:
            return

        # Embed text
        embedding = self.embed_text(text)
        if embedding is None:
            return

        # Store in vector collection
        collection_name = self.vectorized_tables[table_name]

        try:
            # Get the vector collection
            vector_db = self.vector_collections.get(collection_name)
            if vector_db is None:
                print(f"WARNING: Vector collection {collection_name} not found")
                return

            # Insert vector with metadata containing row_id and table_name
            metadata = {
                'row_id': row_id,
                'table_name': table_name
            }

            # Use row_id as the vector ID for easy lookup
            vector_id = f"{table_name}_{row_id}"
            vector_db.insert(
                vector=embedding,
                metadata=metadata,
                id=vector_id,
                document=text
            )

            print(f"  ↳ Auto-embedded text for {table_name} row {row_id} ({len(text)} chars → {len(embedding)}D vector)")
        except Exception as e:
            print(f"WARNING: Failed to store vector for {table_name} row {row_id}: {e}")

    def on_insert_batch(self, table_name: str, row_ids: List[Any], row_data_list: List[Dict[str, Any]]):
        """
        Handle batch INSERT - embed and store vectors efficiently.

        This is optimized for bulk inserts by batching the embedding operations.

        Args:
            table_name: Name of table
            row_ids: List of inserted row IDs
            row_data_list: List of inserted row data dictionaries
        """
        if not self.enabled or table_name not in self.vectorized_tables:
            return

        if len(row_ids) != len(row_data_list):
            print(f"WARNING: Mismatched row_ids and row_data_list lengths")
            return

        # Extract texts for all rows
        texts = []
        valid_indices = []
        for i, (row_id, row_data) in enumerate(zip(row_ids, row_data_list)):
            text = self.extract_text_for_embedding(table_name, row_data)
            if text:
                texts.append(text)
                valid_indices.append(i)

        if not texts:
            return

        # Batch embed all texts
        embeddings = self.embed_text_batch(texts)
        if not embeddings:
            return

        collection_name = self.vectorized_tables[table_name]

        try:
            # Get the vector collection
            vector_db = self.vector_collections.get(collection_name)
            if vector_db is None:
                print(f"WARNING: Vector collection {collection_name} not found")
                return

            # Prepare batch data
            vectors = []
            metadata_list = []
            vector_ids = []
            documents = []

            for i, embedding in zip(valid_indices, embeddings):
                row_id = row_ids[i]
                text = texts[valid_indices.index(i)]

                vectors.append(embedding)
                metadata_list.append({
                    'row_id': row_id,
                    'table_name': table_name
                })
                vector_ids.append(f"{table_name}_{row_id}")
                documents.append(text)

            # Batch insert vectors
            vector_db.insert_batch(
                vectors=vectors,
                metadata_list=metadata_list,
                ids=vector_ids,
                documents=documents
            )

            print(f"  ↳ Batch auto-embedded {len(vectors)} rows for {table_name} ({len(vectors)} vectors)")
        except Exception as e:
            print(f"WARNING: Failed to batch store vectors for {table_name}: {e}")
            import traceback
            traceback.print_exc()

    def embed_text_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Batch embed multiple texts efficiently.

        This is significantly faster than embedding one at a time.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not self.enabled or not texts:
            return []

        # Lazy init embedding function
        self._init_embedding_function()

        if self.embedding_function is None:
            return []

        try:
            # Batch encode all texts at once (much faster!)
            embeddings = self.embedding_function.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10  # Show progress for large batches
            )

            # Convert to list of arrays
            if len(embeddings.shape) == 1:
                # Single embedding
                return [embeddings]
            else:
                # Multiple embeddings
                return [emb for emb in embeddings]

        except Exception as e:
            print(f"WARNING: Failed to batch embed texts: {e}")
            return []

    def on_update(self, table_name: str, row_id: Any, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        """
        Handle UPDATE - re-embed if text columns changed.

        Args:
            table_name: Name of table
            row_id: ID of updated row
            old_data: Old row data
            new_data: New row data (updated values only)
        """
        if not self.enabled or table_name not in self.vectorized_tables:
            return

        # Check if any text columns changed
        text_columns = self.table_text_columns.get(table_name, [])
        text_changed = any(col in new_data for col in text_columns)

        if not text_changed:
            return  # No need to re-embed

        # Merge old and new data
        merged_data = {**old_data, **new_data}

        # Extract and embed updated text
        text = self.extract_text_for_embedding(table_name, merged_data)
        if not text:
            return

        embedding = self.embed_text(text)
        if embedding is None:
            return

        # Update vector in collection
        collection_name = self.vectorized_tables[table_name]

        try:
            # Get the vector collection
            vector_db = self.vector_collections.get(collection_name)
            if vector_db is None:
                print(f"WARNING: Vector collection {collection_name} not found")
                return

            # Update the vector using upsert (safer than update)
            vector_id = f"{table_name}_{row_id}"
            metadata = {
                'row_id': row_id,
                'table_name': table_name
            }

            vector_db.upsert(
                vector=embedding,
                id=vector_id,
                metadata=metadata,
                document=text
            )

            print(f"  ↳ Re-embedded text for {table_name} row {row_id}")
        except Exception as e:
            print(f"WARNING: Failed to update vector for {table_name} row {row_id}: {e}")

    def on_delete(self, table_name: str, row_id: Any):
        """
        Handle DELETE - remove corresponding vector.

        Args:
            table_name: Name of table
            row_id: ID of deleted row
        """
        if not self.enabled or table_name not in self.vectorized_tables:
            return

        collection_name = self.vectorized_tables[table_name]

        try:
            # Get the vector collection
            vector_db = self.vector_collections.get(collection_name)
            if vector_db is None:
                print(f"WARNING: Vector collection {collection_name} not found")
                return

            # Delete the vector
            vector_id = f"{table_name}_{row_id}"
            success = vector_db.delete(vector_id)

            if success:
                print(f"  ↳ Removed vector for {table_name} row {row_id}")
            else:
                print(f"  ⚠ Vector for {table_name} row {row_id} not found (may not have been embedded)")
        except Exception as e:
            print(f"WARNING: Failed to delete vector for {table_name} row {row_id}: {e}")

    def hybrid_search(
        self,
        table_name: str,
        query_text: str,
        top_k: int = 5,
        sql_filters: Optional[Dict[str, Any]] = None,
        rdbms_executor=None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search: vector similarity + SQL filters.

        This combines semantic vector search with traditional SQL filtering.

        Args:
            table_name: Name of table to search
            query_text: Text query for semantic search
            top_k: Number of results to return
            sql_filters: Optional metadata filters (e.g., {'price': {'$lt': 1000}})
            rdbms_executor: Optional RDBMSEngine executor for fetching row data

        Returns:
            List of dicts with row data and similarity scores
            Format: [{'row_id': 0, 'score': 0.85, 'row_data': {...}}, ...]
        """
        if not self.enabled or table_name not in self.vectorized_tables:
            return []

        # Embed query text
        query_embedding = self.embed_text(query_text)
        if query_embedding is None:
            print(f"WARNING: Could not embed query text: '{query_text}'")
            return []

        collection_name = self.vectorized_tables[table_name]

        try:
            # Get the vector collection
            vector_db = self.vector_collections.get(collection_name)
            if vector_db is None:
                print(f"WARNING: Vector collection {collection_name} not found")
                return []

            # Perform vector search
            # If SQL filters provided, convert to metadata filters
            metadata_filters = None
            if sql_filters:
                # For now, we search all vectors and filter afterward
                # More advanced: pre-filter vectors by metadata
                pass

            # Search vector collection
            search_results = vector_db.search(
                query_vector=query_embedding,
                top_k=top_k * 2,  # Get more candidates for post-filtering
                filters=None  # Could add metadata filters here
            )

            # Build results with row IDs and scores
            results = []
            for result in search_results:
                row_id = result.metadata.get('row_id')
                if row_id is None:
                    continue

                # Optionally fetch row data from RDBMS
                row_data = None
                if rdbms_executor:
                    # Fetch actual row data
                    try:
                        # Get the table and fetch the row
                        table = rdbms_executor.tables.get(table_name)
                        if table:
                            row_data = table.get(row_id)
                    except Exception as e:
                        print(f"WARNING: Could not fetch row data for {table_name}[{row_id}]: {e}")

                results.append({
                    'row_id': row_id,
                    'score': result.score,
                    'document': result.document,
                    'row_data': row_data
                })

            # Apply SQL filters if provided
            if sql_filters and rdbms_executor:
                results = self._apply_sql_filters(results, sql_filters)

            # Return top_k results
            return results[:top_k]

        except Exception as e:
            print(f"WARNING: Hybrid search failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _apply_sql_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply SQL-like filters to search results.

        Args:
            results: List of search results with row_data
            filters: Filter conditions (e.g., {'price': {'$lt': 1000}})

        Returns:
            Filtered results
        """
        filtered = []
        for result in results:
            row_data = result.get('row_data')
            if row_data is None:
                continue

            # Check all filter conditions
            match = True
            for field, condition in filters.items():
                value = row_data.get(field)

                if isinstance(condition, dict):
                    # Complex condition (e.g., {'$lt': 1000})
                    for op, target in condition.items():
                        if op == '$lt' and not (value is not None and value < target):
                            match = False
                        elif op == '$lte' and not (value is not None and value <= target):
                            match = False
                        elif op == '$gt' and not (value is not None and value > target):
                            match = False
                        elif op == '$gte' and not (value is not None and value >= target):
                            match = False
                        elif op == '$eq' and value != target:
                            match = False
                        elif op == '$ne' and value == target:
                            match = False
                else:
                    # Simple equality condition
                    if value != condition:
                        match = False

                if not match:
                    break

            if match:
                filtered.append(result)

        return filtered

    def get_stats(self) -> Dict[str, Any]:
        """Get auto-vectorization statistics"""
        return {
            'enabled': self.enabled,
            'embedding_model': self.embedding_model_name,
            'dimension': self.dimension,
            'vectorized_tables': len(self.vectorized_tables),
            'tables': list(self.vectorized_tables.keys())
        }


# Demo/test code
if __name__ == "__main__":
    print("="*80)
    print("AUTO-VECTORIZATION DEMO")
    print("="*80)

    # Create auto-vectorizer
    vectorizer = AutoVectorizer(dimension=384)

    print(f"\nConfiguration:")
    print(f"  Model: {vectorizer.embedding_model_name}")
    print(f"  Dimension: {vectorizer.dimension}")
    print(f"  Enabled: {vectorizer.enabled}")

    # Simulate CREATE TABLE
    class MockColumn:
        def __init__(self, name, data_type):
            self.name = name
            self.data_type = data_type

    columns = [
        MockColumn('id', 'INTEGER'),
        MockColumn('name', 'TEXT'),
        MockColumn('description', 'TEXT'),
        MockColumn('price', 'REAL'),
    ]

    print(f"\n1. CREATE TABLE products...")
    if vectorizer.should_vectorize_table('products', columns):
        print(f"   ✓ Table qualifies for auto-vectorization")
        vectorizer.table_text_columns['products'] = ['name', 'description']
        vectorizer.vectorized_tables['products'] = 'products_vectors'

    # Simulate INSERT
    print(f"\n2. INSERT INTO products...")
    row_data = {
        'id': 1,
        'name': 'Laptop',
        'description': 'High-performance gaming laptop with RTX 4090',
        'price': 2499.99
    }

    text = vectorizer.extract_text_for_embedding('products', row_data)
    print(f"   Extracted text: {text}")

    embedding = vectorizer.embed_text(text)
    if embedding is not None:
        print(f"   ✓ Embedded to {len(embedding)}D vector")
        print(f"   Vector sample: [{embedding[:5]}...]")
    else:
        print(f"   ✗ Embedding failed (sentence-transformers not installed?)")

    # Stats
    print(f"\n3. Statistics:")
    stats = vectorizer.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "="*80)
    print("Demo complete! Install sentence-transformers to enable embeddings:")
    print("  pip install sentence-transformers")
    print("="*80)
