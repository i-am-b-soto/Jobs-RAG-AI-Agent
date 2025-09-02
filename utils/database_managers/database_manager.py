import os
import asyncpg

from dotenv import load_dotenv


# Load .env file
load_dotenv()


class DatabaseManager:
            
    def __init__(self):
        self.DB_DSN = os.getenv("DB_DSN") or "postgresql://postgres:postgres@db:5432/vector_db"

    async def get_pool(self):
        # 🔹 Database connection pool
        return await asyncpg.create_pool(dsn=self.DB_DSN)

    async def get_db_connection(self):
        return await asyncpg.connect(self.DB_DSN)