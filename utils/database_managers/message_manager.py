
import datetime
from utils.database_managers.database_manager import DatabaseManager


class MessageManager(DatabaseManager):

    async def save_message(self, conv_id: int, role: str, content: str):
        """Save a message"""
        conn = await self.get_db_connection()
        await conn.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES ($1, $2, $3)",
            conv_id, role, content,
        )
        await conn.close()

    async def create_conversation(self, initial_message: str):
        """Create a new conversation and store the initial assistant message."""
        conn = await self.get_db_connection()
        # Insert a new conversation
        conv_id = await conn.fetchval("INSERT INTO conversations DEFAULT VALUES RETURNING id")
        # Save the assistant's initial message
        await conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES ($1, $2, $3, $4)",
            conv_id, "assistant", initial_message, datetime.utcnow()
        )
        await conn.close()
        return conv_id

    async def fetch_messages(self, conv_id: int):
        conn = await self.get_db_connection()
        rows = await conn.fetch(
            "SELECT role, content FROM messages WHERE conversation_id=$1 ORDER BY created_at ASC",
            conv_id,
        )
        await conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows]




message_manager = MessageManager()