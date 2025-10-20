import asyncio
import uuid
import json
import logging
from functools import wraps
from typing import Optional, Callable, Any
import aiopg
import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Retry Decorator ----------------
def retry_on_exception(retries=3, delay=1, exceptions=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return await fn(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Retry {attempt+1}/{retries} for {fn.__name__} due to {e}")
                    await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# ---------------- Background SQL Queue ----------------
class AsyncSqlWorkerQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False

    async def worker(self):
        self.running = True
        while self.running:
            func, args, kwargs = await self.queue.get()
            try:
                await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Background SQL task failed: {e}")
            finally:
                self.queue.task_done()

    async def start(self):
        asyncio.create_task(self.worker())

    async def stop(self):
        self.running = False
        await self.queue.join()

    async def enqueue(self, func: Callable, *args, **kwargs):
        await self.queue.put((func, args, kwargs))

# ---------------- Async Mongo-like Collection ----------------
class AsyncMongoLikeCollection:
    def __init__(
        self,
        pool: aiopg.Pool,
        name: str,
        redis: Optional[aioredis.Redis] = None,
        sql_queue: Optional[AsyncSqlWorkerQueue] = None,
        cache_ttl: int = 60,
        reconnect_interval: int = 2,
        batch_size: int = 50
    ):
        self.pool = pool
        self.name = name
        self.redis = redis
        self.sql_queue = sql_queue
        self.cache_ttl = cache_ttl
        self.reconnect_interval = reconnect_interval
        self.batch_size = batch_size

    # ---------------- Table Setup ----------------
    @retry_on_exception()
    async def _ensure_table(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"""
                    CREATE UNLOGGED TABLE IF NOT EXISTS {self.name} (
                        _id TEXT PRIMARY KEY,
                        document JSONB NOT NULL
                    );
                """)

    # ---------------- Redis Helpers ----------------
    async def _cache_set(self, key: str, value: Any):
        if not self.redis:
            return
        try:
            await self.redis.setex(key, self.cache_ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")

    async def _cache_get(self, key: str) -> Any:
        if not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
        return None

    async def _cache_invalidate(self):
        if not self.redis:
            return
        try:
            async for k in self.redis.scan_iter(f"{self.name}:*"):
                await self.redis.delete(k)
        except Exception as e:
            logger.warning(f"Redis invalidate failed: {e}")

    def _cache_key(self, query: dict, extra="") -> str:
        return f"{self.name}:{json.dumps(query, sort_keys=True)}:{extra}"

    async def _publish_change(self, operation: str, document: dict):
        if not self.redis:
            return
        event = json.dumps({"operation": operation, "document": document})
        try:
            await self.redis.publish(f"{self.name}_changes", event)
        except Exception as e:
            logger.warning(f"Redis publish failed: {e}")

    # ---------------- SQL Condition ----------------
    def _build_condition(self, query: dict):
        if not query:
            return "TRUE", []

        conditions, params = [], []
        for key, val in query.items():
            if isinstance(val, dict):
                for op, v in val.items():
                    if op == "$eq":
                        conditions.append(f"document->>'{key}' = %s")
                        params.append(str(v))
                    elif op == "$ne":
                        conditions.append(f"document->>'{key}' != %s")
                        params.append(str(v))
                    elif op == "$gt":
                        conditions.append(f"(document->>'{key}')::numeric > %s")
                        params.append(v)
                    elif op == "$gte":
                        conditions.append(f"(document->>'{key}')::numeric >= %s")
                        params.append(v)
                    elif op == "$lt":
                        conditions.append(f"(document->>'{key}')::numeric < %s")
                        params.append(v)
                    elif op == "$lte":
                        conditions.append(f"(document->>'{key}')::numeric <= %s")
                        params.append(v)
                    elif op == "$in":
                        conditions.append(f"document->>'{key}' = ANY(%s)")
                        params.append(list(map(str, v)))
                    elif op == "$nin":
                        conditions.append(f"NOT (document->>'{key}' = ANY(%s))")
                        params.append(list(map(str, v)))
                    elif op == "$regex":
                        conditions.append(f"document->>'{key}' ~* %s")
                        params.append(v)
                    elif op == "$exists":
                        conditions.append(f"document ? %s" if v else f"NOT (document ? %s)")
                        params.append(key)
            else:
                conditions.append(f"document->>'{key}' = %s")
                params.append(str(val))
        return " AND ".join(conditions), params

    # ---------------- Insert ----------------
    @retry_on_exception()
    async def insert_one(self, doc: dict):
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        await self.insert_many([doc])
        return {"inserted_id": doc["_id"]}

    @retry_on_exception()
    async def insert_many(self, docs: list):
        for doc in docs:
            if "_id" not in doc:
                doc["_id"] = str(uuid.uuid4())
        await self._ensure_table()

        # Redis + publish
        if self.redis:
            for doc in docs:
                key = self._cache_key({"_id": doc["_id"]})
                await self._cache_set(key, doc)
                asyncio.create_task(self._publish_change("insert", doc))

        # Enqueue SQL insert in background
        async def _sql_insert():
            batches = [docs[i:i+self.batch_size] for i in range(0, len(docs), self.batch_size)]
            for batch in batches:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        for doc in batch:
                            await cur.execute(
                                f"""
                                INSERT INTO {self.name} (_id, document)
                                VALUES (%s, %s)
                                ON CONFLICT (_id) DO UPDATE SET document = EXCLUDED.document;
                                """,
                                (doc["_id"], json.dumps(doc))
                            )
        if self.sql_queue:
            asyncio.create_task(self.sql_queue.enqueue(_sql_insert))
        else:
            asyncio.create_task(_sql_insert())

        return {"inserted_ids": [d["_id"] for d in docs]}

    # ---------------- Find ----------------
    @retry_on_exception()
    async def find(self, query: dict = None, limit: int = 0, sort: list = None, projection: list = None):
        query = query or {}
        key = self._cache_key(query, f"{limit}_{sort}_{projection}")
        cached = await self._cache_get(key) if self.redis else None
        if cached is not None:
            return cached

        sql, params = self._build_condition(query)
        q = f"SELECT document FROM {self.name} WHERE {sql}"
        if sort:
            field, direction = sort[0]
            q += f" ORDER BY document->>'{field}' {'ASC' if direction > 0 else 'DESC'}"
        if limit:
            q += f" LIMIT {limit}"

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(q, params)
                docs = [row[0] for row in await cur.fetchall()]

        if projection:
            for d in docs:
                for k in list(d.keys()):
                    if k not in projection:
                        d.pop(k)

        if self.redis:
            asyncio.create_task(self._cache_set(key, docs))
        return docs

    async def find_one(self, query: dict):
        docs = await self.find(query, limit=1)
        return docs[0] if docs else None

    # ---------------- Update (fire-and-forget SQL) ----------------
    @retry_on_exception()
    async def update_many(self, filter: dict, update: dict, limit: int = 0, upsert: bool = False):
        await self._ensure_table()
        sql, params = self._build_condition(filter)
        set_values = []

        # ---------------- Merge updates into single JSONB expression ----------------
        jsonb_expr = "document"

        # $set
        if "$set" in update:
            for k, v in update["$set"].items():
                jsonb_expr = f"jsonb_set({jsonb_expr}, '{{{k}}}', %s::jsonb, true)"
                set_values.append(json.dumps(v))

        # $inc
        if "$inc" in update:
            for k, v in update["$inc"].items():
                jsonb_expr = (
                    f"jsonb_set({jsonb_expr}, '{{{k}}}', "
                    f"((COALESCE(({jsonb_expr}->>'{k}')::numeric, 0) + {v})::text)::jsonb, true)"
                )

        # $unset
        if "$unset" in update:
            for k in update["$unset"].keys():
                jsonb_expr = f"{jsonb_expr} - '{k}'"

        update_clause = f"document = {jsonb_expr}"

        # ---------------- Redis cache update ----------------
        modified_docs = []
        if self.redis:
            affected_docs = await self.find(filter, limit=limit)
            for doc in affected_docs:
                if "$set" in update:
                    doc.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        doc[k] = doc.get(k, 0) + v
                if "$unset" in update:
                    for k in update["$unset"].keys():
                        doc.pop(k, None)
                key = self._cache_key({"_id": doc["_id"]})
                await self._cache_set(key, doc)
                asyncio.create_task(self._publish_change("update", doc))
                modified_docs.append(doc)

        # ---------------- SQL update ----------------
        async def _sql_update():
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if limit:
                        final_sql = f"""
                            WITH limited AS (SELECT _id FROM {self.name} WHERE {sql} LIMIT {limit})
                            UPDATE {self.name} SET {update_clause}
                            WHERE _id IN (SELECT _id FROM limited)
                            RETURNING document;
                        """
                        await cur.execute(final_sql, params + set_values)
                        rows = await cur.fetchall()
                    else:
                        final_sql = f"UPDATE {self.name} SET {update_clause} WHERE {sql} RETURNING document;"
                        await cur.execute(final_sql, set_values + params)
                        rows = await cur.fetchall()

                    sql_modified_docs = [row[0] for row in rows]

                    # UPSERT if nothing matched
                    if not sql_modified_docs and upsert:
                        new_doc = {}
                        if "$set" in update:
                            new_doc.update(update["$set"])
                        if "$inc" in update:
                            for k, v in update["$inc"].items():
                                new_doc[k] = v
                        for fk, fv in filter.items():
                            if isinstance(fv, dict):
                                continue
                            if fk not in new_doc:
                                new_doc[fk] = fv
                        await self.insert_one(new_doc)
                        sql_modified_docs = [new_doc]

                    asyncio.create_task(self._cache_invalidate())
                    for doc in sql_modified_docs:
                        asyncio.create_task(self._publish_change("update", doc))

        if self.sql_queue:
            asyncio.create_task(self.sql_queue.enqueue(_sql_update))
        else:
            asyncio.create_task(_sql_update())

        return {"modified_count": len(modified_docs) if modified_docs else (1 if upsert else 0)}


    async def update_one(self, filter: dict, update: dict, upsert: bool = False):
        return await self.update_many(filter, update, limit=1, upsert=upsert)

    # ---------------- Delete ----------------
    @retry_on_exception()
    async def delete_many(self, filter: dict, limit: int = 0):
        await self._ensure_table()
        deleted_docs = []
        affected_docs = await self.find(filter, limit=limit) if self.redis else []

        # Redis + publish
        if self.redis:
            for doc in affected_docs:
                key = self._cache_key({"_id": doc["_id"]})
                await self.redis.delete(key)
                asyncio.create_task(self._publish_change("delete", doc))
                deleted_docs.append(doc)

        # Background SQL delete
        async def _sql_delete():
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    final_sql = f"DELETE FROM {self.name} WHERE TRUE"
                    sql_cond, params = self._build_condition(filter)
                    final_sql = f"DELETE FROM {self.name} WHERE {sql_cond}"
                    if limit:
                        final_sql = f"""
                            WITH limited AS (SELECT _id FROM {self.name} WHERE {sql_cond} LIMIT {limit})
                            DELETE FROM {self.name} WHERE _id IN (SELECT _id FROM limited)
                        """
                    await cur.execute(final_sql, params)
                    asyncio.create_task(self._cache_invalidate())

        if self.sql_queue:
            asyncio.create_task(self.sql_queue.enqueue(_sql_delete))
        else:
            asyncio.create_task(_sql_delete())

        return {"deleted_count": len(deleted_docs)}

    async def delete_one(self, filter: dict):
        return await self.delete_many(filter, limit=1)

    # ---------------- Count ----------------
    async def count_documents(self, query: dict = None):
        sql, params = self._build_condition(query or {})
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"SELECT COUNT(*) FROM {self.name} WHERE {sql}", params)
                return (await cur.fetchone())[0]

    # ---------------- Watch ----------------
    async def watch(self, callback: Callable[[dict], Any], stop_event: Optional[asyncio.Event] = None):
        if not self.redis:
            raise RuntimeError("Redis required for watch()")
        stop_event = stop_event or asyncio.Event()
        while not stop_event.is_set():
            try:
                pubsub = self.redis.pubsub()
                await pubsub.subscribe(f"{self.name}_changes")
                async for message in pubsub.listen():
                    if stop_event.is_set():
                        break
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        await callback(data)
            except Exception as e:
                logger.warning(f"Redis watch error, reconnecting in {self.reconnect_interval}s: {e}")
                await asyncio.sleep(self.reconnect_interval)

    # ---------------- Export Database ----------------
    async def export_db(self, filename: str, format: str = "json"):
        """Export the entire collection to a JSON or CSV file."""
        await self._ensure_table()

        format = format.lower()
        if format not in ("json", "csv"):
            raise ValueError("Format must be 'json' or 'csv'")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"SELECT document FROM {self.name}")
                rows = await cur.fetchall()
                docs = [row[0] for row in rows]

        if not docs:
            logger.info(f"No documents found in {self.name}. Nothing to export.")
            return

        if format == "json":
            filename = filename if filename.endswith(".json") else f"{filename}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Exported {len(docs)} documents from '{self.name}' to {filename}")

        elif format == "csv":
            import csv
            filename = filename if filename.endswith(".csv") else f"{filename}.csv"

            # Collect all unique keys across all documents
            fieldnames = sorted({k for d in docs for k in d.keys()})
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for doc in docs:
                    writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in doc.items()})

            logger.info(f"✅ Exported {len(docs)} documents from '{self.name}' to {filename}")

    # ---------------- Import Database ----------------
    async def import_db(self, filename: str, format: str = "json", clear_existing: bool = False):
        """Import documents into the collection from a JSON or CSV file."""
        await self._ensure_table()

        format = format.lower()
        if format not in ("json", "csv"):
            raise ValueError("Format must be 'json' or 'csv'")

        if clear_existing:
            await self.delete_many({})

        docs = []
        if format == "json":
            filename = filename if filename.endswith(".json") else f"{filename}.json"
            with open(filename, "r", encoding="utf-8") as f:
                docs = json.load(f)
                if isinstance(docs, dict):
                    docs = [docs]

        elif format == "csv":
            import csv
            filename = filename if filename.endswith(".csv") else f"{filename}.csv"
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Try to parse JSON-like fields back to Python objects
                    for k, v in row.items():
                        try:
                            row[k] = json.loads(v)
                        except (ValueError, TypeError):
                            pass
                    docs.append(row)

        if not docs:
            logger.warning(f"No documents found in {filename}. Nothing to import.")
            return

        # Ensure unique _id
        for d in docs:
            if "_id" not in d:
                d["_id"] = str(uuid.uuid4())

        await self.insert_many(docs)
        logger.info(f"✅ Imported {len(docs)} documents into '{self.name}' from {filename}")


# ---------------- Async SQL DB ----------------
class AsyncSqlDB:
    """
    MongoDB-like async SQL wrapper with Redis caching and background sync queue.
    Allows both attribute and subscript access for collections.

    Example:
        db = AsyncSqlDB(dsn, redis_url)
        await db.connect()
        users = db.users          # via attribute
        users = db["users"]       # via subscript
    """
    def __init__(
        self,
        dsn: str,
        redis_url: Optional[str] = None,
        cache_ttl: int = 60,
        reconnect_interval: int = 2,
        batch_size: int = 50,
    ):
        self.dsn = dsn
        self.redis_url = redis_url
        self.pool: Optional[aiopg.Pool] = None
        self.redis: Optional[aioredis.Redis] = None
        self.collections = {}
        self.cache_ttl = cache_ttl
        self.reconnect_interval = reconnect_interval
        self.batch_size = batch_size
        self.sql_queue = AsyncSqlWorkerQueue()

    async def connect(self):
        """Initialize PostgreSQL pool, Redis connection, and start SQL worker."""
        self.pool = await aiopg.create_pool(self.dsn)
        if self.redis_url:
            self.redis = await aioredis.from_url(self.redis_url)
        await self.sql_queue.start()

    def _get_or_create_collection(self, collection_name: str):
        """Internal helper to lazy-create and cache a collection wrapper."""
        if collection_name not in self.collections:
            self.collections[collection_name] = AsyncMongoLikeCollection(
                self.pool,
                collection_name,
                self.redis,
                self.sql_queue,
                cache_ttl=self.cache_ttl,
                reconnect_interval=self.reconnect_interval,
                batch_size=self.batch_size,
            )
        return self.collections[collection_name]

    def __getattr__(self, collection_name: str):
        """Allow attribute-style access (db.users)."""
        if collection_name.startswith("__"):
            raise AttributeError(collection_name)
        return self._get_or_create_collection(collection_name)

    def __getitem__(self, collection_name: str):
        """Allow subscript-style access (db["users"])."""
        return self._get_or_create_collection(collection_name)

    async def close(self):
        """Cleanly close all connections."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
        if self.redis:
            await self.redis.close()
        await self.sql_queue.stop()