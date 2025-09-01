from utils.database_managers.database_manager import DatabaseManager
from utils.openai_client import openai_client


class DocumentManager(DatabaseManager):
        
    async def fetch_relevant_chunks(self, question: str, top_k: int = 5):
        """Embed the question and run similarity search on chunks."""
        # 1. Embed user question
        emb_response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=question
        )
        query_emb = emb_response.data[0].embedding

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
            query_emb, top_k
        )
        await conn.close()
        return [r["content"] for r in rows]


document_manager = DocumentManager()