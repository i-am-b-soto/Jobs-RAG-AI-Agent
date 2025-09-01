from fastapi import FastAPI
from fastapi import Query

from utils.database_managers.document_manager import document_manager
from utils.database_managers.message_manager import message_manager
from utils.openai_client import openai_client

app = FastAPI()


@app.get("/generate-report")
async def generate_report(job_title: str = Query(..., description="Job title to filter by")):
    """
        Generate the report
    """

    rows = await message_manager.get_jobs_with_position_like(job_title)

    job_texts = [r["description"] for r in rows]
    combined_jobs = "\n\n".join(job_texts)

    # Ask OpenAI for the report
    prompt = (
        "You are analyzing a database of job postings. "
        "From the text below, extract the 50 most commonly listed skills and keywords "
        "along with a count of how many times they appear.\n\n"
        f"{combined_jobs}"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert labor market analyst."},
            {"role": "user", "content": prompt},
        ],
    )

    report = response.choices[0].message["content"]
    return {"report": report}


@app.post("/ask")
async def ask_question(conv_id: int = Query(...), question: str = Query(...)):
    """
        Followup questions
    """
    # 1. Save user question
    await message_manager.save_message(conv_id, "user", question)

    # 2. Fetch conversation history
    history = await message_manager.fetch_messages(conv_id)

    # 3. Fetch relevant job chunks
    context_docs = await document_manager.fetch_relevant_chunks(question)
    context_text = "\n\n".join(context_docs)

    # 4. Build system message
    system_prompt = f"""
    You are a helpful assistant analyzing job postings.
    Use the following job data when answering:

    {context_text}
    """

    # 5. Combine system + history
    messages = [{"role": "system", "content": system_prompt}] + history

    # 6. Call OpenAI
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    answer = response.choices[0].message.content

    # 7. Save assistant answer
    await message_manager.save_message(conv_id, "assistant", answer)

    return {"openai_response": answer}