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
        user_friendly_response = [x.embedding for x in raw_response.data]
        if len(user_friendly_response) == 1:
            user_friendly_response = user_friendly_response[0]
        return user_friendly_response


openai_client = OpenAIClient()

