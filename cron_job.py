import os
import asyncio
import httpx
import asyncpg
import uuid
from openai import OpenAI
from dotenv import load_dotenv


# Load .env file
load_dotenv()

REMOTEOK_API = "https://remoteok.com/api"
DB_DSN = os.getenv("DB_DSN")
CHUNK_SIZE = 200  # words per chunk

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into chunks of approximately chunk_size words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


async def fetch_jobs():
    """Fetch jobs from RemoteOK API."""
    async with httpx.AsyncClient() as client_http:
        resp = await client_http.get(REMOTEOK_API)
        resp.raise_for_status()
        data = resp.json()
        return data[1:]  # skip metadata element


async def insert_jobs(pool, jobs):
    """Insert new jobs and their chunks into Postgres using batch embeddings."""
    inserted_docs = 0
    inserted_chunks = 0

    async with pool.acquire() as conn:
        for job in jobs:
            job_id = str(job.get("id"))
            company = job.get("company")
            position = job.get("position")
            description = job.get("description") or ""
            url = job.get("url")
            tags = job.get("tags", [])

            # Insert document if not exists, else fetch its ID
            doc_id = await conn.fetchval("""
                INSERT INTO documents (external_id, company, title, url, metadata)
                SELECT $1, $2, $3, $4, $5
                WHERE NOT EXISTS (SELECT 1 FROM documents WHERE external_id = $1)
                RETURNING id
            """, job_id, company, position, url, {"tags": tags})

            if doc_id:
                inserted_docs += 1
            else:
                doc_id = await conn.fetchval(
                    "SELECT id FROM documents WHERE external_id = $1", job_id
                )

            # Skip empty descriptions
            if not description.strip():
                continue

            # Chunk text
            chunks_texts = chunk_text(description)

            # Batch embed chunks
            response = client.embeddings.create(
                model="text-embedding-3-large",
                input=chunks_texts
            )
            embeddings = [item.embedding for item in response.data]

            # Insert chunks into DB
            for idx, (chunk_text_piece, embedding_vector) in enumerate(zip(chunks_texts, embeddings)):
                await conn.execute("""
                    INSERT INTO chunks (id, document_id, chunk_index, content, embedding)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT DO NOTHING
                """, str(uuid.uuid4()), doc_id, idx, chunk_text_piece, embedding_vector)
                inserted_chunks += 1

    return inserted_docs, inserted_chunks


async def main():
    jobs = await fetch_jobs()
    pool = await asyncpg.create_pool(dsn=DB_DSN)
    async with pool:
        docs, chunks = await insert_jobs(pool, jobs)
        print(f"✅ Inserted {docs} new documents and {chunks} new chunks")


if __name__ == "__main__":
    asyncio.run(main())