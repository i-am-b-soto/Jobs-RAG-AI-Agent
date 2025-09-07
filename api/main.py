from fastapi import FastAPI
from fastapi import Query, Body

from utils.database_managers.document_manager import document_manager
from utils.database_managers.message_manager import message_manager
from utils.openai_client import openai_client
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware to allow everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)


class GenerateReportBody(BaseModel):
    job_title: str


class AskBody(BaseModel):
    conv_id: str | int
    question: str
    

@app.post("/generate-report")
async def generate_report(body: GenerateReportBody):
    """
        Generate the report
    """

    rows = await document_manager.get_jobs_with_position_like(body.job_title)

    job_texts = [r["description"] for r in rows]

    combined_jobs = "\n\n".join(job_texts)


    #job_titles = [r["title"] for r in rows]
    #print(job_titles)


    if len(rows) > 1:

        # Ask OpenAI for the report
        prompt = (
            "You are analyzing a database of job postings. "
            f"The text below contains job information from {len(rows)} jobs related to {body.job_title} that the user is asking about. From this list, extract the {int(len(rows) * 3/4)} most commonly listed skills and keywords "
            "along with a count of how many times they appear.\n\n"
            f"{combined_jobs}"
        )
    else: 
        # Ask OpenAI for the report
        prompt = (
            "You are analyzing a database of job postings. "
            f"The Job title the user has searched for has returned no similar results. Please let the user know this."
        )

    messages = [{"role": "system", "content": "You are an expert labor market analyst."},
                {"role": "user", "content": prompt}]
    
    conv_id = -1
    try:
        conv_id = await message_manager.create_conversation(messages)
    except Exception as e:
        print(f"Problem communicating with the DB: {str(e)}")

    report = openai_client.generate_chat(messages)
    return {"report": report, "conv_id": conv_id}


@app.post("/ask")
async def ask_question(ask_body: AskBody):
    """
        Followup questions
    """
    # 1. Save user question
    await message_manager.save_message(ask_body.conv_id, "user", ask_body.question)

    # 2. Fetch conversation history
    history = await message_manager.fetch_messages(ask_body.conv_id)

    # 3. Fetch relevant job chunks
    context_docs = await document_manager.fetch_relevant_chunks(ask_body.question)
    context_text = "\n\n".join(context_docs)

    # 4. Build system message
    system_prompt = f"""
    You are a helpful assistant analyzing job postings.
    Use the following job data when answering:

    {context_text}
    """

    # 5. Combine system + history
    messages = [{"role": "system", "content": system_prompt}] + history
    response = openai_client.generate_chat(messages)

    # 7. Save assistant answer
    await message_manager.save_message(ask_body.conv_id, "assistant", response)

    return {"openai_response": response}
