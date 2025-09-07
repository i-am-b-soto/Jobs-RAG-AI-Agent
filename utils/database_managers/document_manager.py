import json
from pgvector.asyncpg import register_vector
from utils.database_managers.database_manager import DatabaseManager
from utils.openai_client import openai_client


class DocumentManager(DatabaseManager):
    
    async def fetch_relevant_chunks(self, question: str, top_k: int = 5):
        """Embed the question and run similarity search on chunks."""
        # 1. Embed user question
        emb_response = openai_client.create_embeddings(question)

        # 2. Query pgvector
        conn = await self.get_db_connection()
        rows = await conn.fetch(
            """
            SELECT d.description
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.embedding <-> $1 > $2
            ORDER BY title_embedding <-> $1
            LIMIT $3
            """,
            emb_response, 1, top_k
        )
        await conn.close()
        return [r["description"] for r in rows]

    async def get_jobs_with_position_like(self, job_title: str, top_k: int = 100):
        """
            Get all jobs based on job_title
        """
        query_embedding = openai_client.create_embeddings(job_title)
        #query_vector_str = "[" + ",".join(f"{x:.6f}" for x in query_embedding) + "]"

        #query_vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT title, description
                FROM documents
                WHERE title_embedding <-> $1 < $2
                ORDER BY title_embedding <-> $1
                LIMIT $3
            """, query_embedding, 1, top_k)

        #print("filter 1")

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
        """, title_embedding, doc_id)
    
    async def insert_chunk_w_conn(self, conn, doc_id: str | int, 
                                  chunk_index: int, 
                                  chunk_content: str, 
                                  embedding_vector: list):
        return await conn.execute("""
            INSERT INTO chunks (document_id, chunk_index, content, embedding)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT DO NOTHING
        """, doc_id, chunk_index, chunk_content, embedding_vector)
        

document_manager = DocumentManager()