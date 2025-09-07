import os
import asyncpg
from pgvector.asyncpg import register_vector
from dotenv import load_dotenv


# Load .env file
load_dotenv()


class DatabaseManager:

    def __init__(self):
        self.DB_DSN = os.getenv("DB_DSN") or "postgresql://postgres:postgres@db:5432/vector_db"
        self._pool = None
        self._conn = None

    async def get_pool(self):
        # 🔹 Database connection pool
        if self._pool is None:
            self._pool = await asyncpg.create_pool(dsn=self.DB_DSN)

            # Register pgvector type once at pool creation
            async with self._pool.acquire() as conn:
                await register_vector(conn)
        
        return self._pool

    async def get_db_connection(self):
        if self._conn is None or self._conn.is_closed():
            self._conn = await asyncpg.connect(self.DB_DSN)
            await register_vector(self._conn)

        return self._conn