"""INSERT query builder."""
import asyncio
import numpy as np
from typing import Dict, List, Union, Any
from veclite.query.ir import InsertIR
from veclite.query.sqlgen import generate_insert
from veclite.query.dialect.sqlite import SQLiteDialect
from veclite.core.results import Result


class InsertBuilder:
    """Fluent builder for INSERT queries."""

    def __init__(self, client, schema, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]):
        self.db = client
        self.schema = schema
        self.table = table
        self.dialect = SQLiteDialect()
        self.rows = [data] if isinstance(data, dict) else data

        if self.table in schema.views:
            raise ValueError(f"Cannot INSERT into view '{table}'.")

    async def execute(self):
        """Execute the INSERT query."""
        validated_rows = [self.db._validate_insert_data(self.table, row) for row in self.rows]
        with_defaults = [self.db._apply_runtime_defaults(self.table, row) for row in validated_rows]
        serialized_rows = [self.db._serialize_json_fields(self.table, row) for row in with_defaults]

        if not serialized_rows:
            return Result([])

        cols = list(serialized_rows[0].keys())
        num_cols = len(cols)
        max_vars = self.db._get_max_vars()

        total_params = num_cols * len(serialized_rows)

        from veclite.query.validation import check_vector_embedder_required
        has_vector_fields = check_vector_embedder_required(
            self.table, self.schema, self.db.embedder, "INSERT into"
        )

        use_executemany = total_params > max_vars and not has_vector_fields

        all_results = []
        if use_executemany:
            sql = f"INSERT INTO {self.dialect.q(self.table)} ({', '.join(self.dialect.q(c) for c in cols)}) VALUES ({', '.join(['?'] * num_cols)})"
            param_rows = [[row[c] for c in cols] for row in serialized_rows]
            with self.db._lock:
                self.db.conn.executemany(sql, param_rows)
                self.db.conn.commit()
            all_results = None
        else:
            batch_size = max(1, max_vars // num_cols)
            for i in range(0, len(serialized_rows), batch_size):
                batch = serialized_rows[i:i + batch_size]
                ir = InsertIR(table=self.table, rows=batch)
                sql, params = generate_insert(ir, self.dialect)
                rows = await self.db._exec(sql, params)

                for row in rows:
                    row = self.db._deserialize_json_fields(self.table, row)
                    all_results.append(row)

        if all_results is None:
            return Result([], count=len(serialized_rows))

        await self._embed_vectors(all_results)

        return Result(all_results)

    async def _embed_vectors(self, rows: List[Dict[str, Any]]):
        """Embed and store vectors for vector-enabled fields.

        If inside batch_embeddings() context, enqueue for batch processing
        instead of generating immediately (mirrors Upsert behavior).
        """
        if not rows or not self.db.embedder:
            return

        table_cls = self.schema.get_table(self.table)
        if not table_cls:
            return

        vector_fields = []
        for field_name, field in table_cls.get_fields().items():
            if getattr(field, 'vector', False):
                vector_fields.append(field_name)

        if not vector_fields:
            return

        # Check if we're inside async batch_embeddings context
        from veclite.core.context import emb_queue_var
        queue = emb_queue_var.get()
        in_batch_context = queue is not None

        for field_name in vector_fields:
            field = table_cls.get_fields()[field_name]
            is_contextualized = getattr(field, 'contextualized', False)

            texts = []
            ids = []
            for row in rows:
                if field_name in row and row[field_name]:
                    texts.append(row[field_name])
                    ids.append(row['id'])

            if not texts:
                continue

            if in_batch_context:
                # Defer embedding to batch flush
                self.db._enqueue_embedding(self.table, field_name, ids, texts)
            else:
                # Generate immediately
                if is_contextualized:
                    inputs = [[text] for text in texts]
                    nested_embeddings = await self.db.embedder.contextualized_embed(
                        inputs=inputs,
                        model="voyage-context-3",
                        input_type="document",
                        output_dimension=getattr(field, 'contextualized_dim', 512)
                    )
                    embeddings = [doc_embs[0] for doc_embs in nested_embeddings]
                else:
                    embeddings = await self.db.embedder.embed(texts)

                vectors = [np.array(emb, dtype=np.float32) for emb in embeddings]

                vector_store = self.db.get_or_create_vector_store(self.table, field_name)
                vector_store.add_batch(ids, vectors)
