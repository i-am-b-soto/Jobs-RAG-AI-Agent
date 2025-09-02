import json
import asyncpg
from utils.database_managers.database_manager import DatabaseManager
from utils.openai_client import openai_client


class DocumentManager(DatabaseManager):
    
    async def fetch_relevant_chunks(self, question: str, top_k: int = 5):
        """Embed the question and run similarity search on chunks."""
        # 1. Embed user question
        emb_response = openai_client.create_embeddings(question)
        emb_vector_str = "[" + ",".join(str(x) for x in emb_response) + "]"

        # 2. Query pgvector
        conn = await self.get_db_connection()
        rows = await conn.fetch(
            """
            SELECT d.description
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <-> $1
            LIMIT $2
            """,
            emb_vector_str, top_k
        )
        await conn.close()
        return [r["content"] for r in rows]

    async def get_jobs_with_position_like(self, job_title: str):
        """
            Get all jobs based on job_title
        """
        query_embedding = openai_client.create_embeddings(job_title)
        query_vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT title, description
                FROM documents
                ORDER BY title_embedding <-> $1
                LIMIT $2
            """, query_vector_str, 30)

        return rows

    async def insert_job_w_conn(self, conn, job_id: str | int, 
                                company: str, 
                                title: str, 
                                url: str, 
                                description: str,  
                                tags: any):
        """"""
        return await conn.fetchval("""
                        INSERT INTO documents (external_id, company, title, url, description, metadata)
                        SELECT $1, $2, $3, $4, $5, $6
                        WHERE NOT EXISTS (SELECT 1 FROM documents WHERE external_id = $1)
                        RETURNING id
                    """, job_id, company, title, url, description, json.dumps({"tags": tags}))
    
    async def update_job_w_conn(self, conn, title_embedding, doc_id):
        """"""
        return await conn.execute("""
            UPDATE documents
            SET title_embedding = $1
            WHERE id = $2
        """, "[" + ",".join(str(x) for x in title_embedding) + "]", doc_id)
    
    async def insert_chunk_w_conn(self, conn, doc_id: str | int, 
                                  chunk_index: int, 
                                  chunk_content: str, 
                                  embedding_vector: list):
        return await conn.execute("""
            INSERT INTO chunks (document_id, chunk_index, content, embedding)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT DO NOTHING
        """, doc_id, chunk_index, chunk_content, "[" + ",".join(str(x) for x in embedding_vector) + "]")
        

document_manager = DocumentManager()