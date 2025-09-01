import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


def create_open_ai_client():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY is None:
        raise Exception("Could not find OpenAI API key in .env file")
    return OpenAI(api_key=OPENAI_API_KEY)


openai_client = create_open_ai_client()

