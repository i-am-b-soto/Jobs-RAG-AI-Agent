import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


class OpenAIClient():
    """Client to interact with OpoenAI"""
    
    def __init__(self):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY is None:
            raise Exception("Could not find OpenAI API key in .env file")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def create_embeddings(self, query: str | list):
        """Create Emebeddings for word or list"""
        raw_response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=query
            )
        user_friendly_response = raw_response.data[0].embedding
        return user_friendly_response

    def create_embeddings_bulk(self, query: str | list):
        """Create Emebeddings for word or list"""
        raw_response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=query
            )
        user_friendly_response = [x.embedding for x in raw_response.data]
        return user_friendly_response
    
    def generate_chat(self, messages: list[any] ):
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content


openai_client = OpenAIClient()

