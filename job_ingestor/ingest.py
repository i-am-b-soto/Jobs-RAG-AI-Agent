import os
import asyncio
import httpx

from utils.openai_client import openai_client as client
from utils.database_managers.document_manager import document_manager
from dotenv import load_dotenv
from bs4 import BeautifulSoup


# Load .env file
load_dotenv()

REMOTEOK_API = "https://remoteok.com/api"
CHUNK_SIZE = 200  # words per chunk

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

def clean_html(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


async def insert_jobs(jobs):
    """
        Insert new jobs and their chunks into Postgres using batch embeddings.
    """
    inserted_docs = 0
    inserted_chunks = 0
    pool = await document_manager.get_pool()
    async with pool.acquire() as conn:
        for job in jobs:
            job_id = str(job.get("id"))
            company = job.get("company")
            position = job.get("position")
            description = clean_html(job.get("description") or "")
            url = job.get("url")
            tags = job.get("tags", [])

            # Insert document if not exists, else fetch its ID
            doc_id = await document_manager.insert_job_w_conn(conn=conn, 
                                                        job_id=job_id, 
                                                        company=company, 
                                                        title=position, 
                                                        url=url, 
                                                        description=description, 
                                                        tags=tags)

            if doc_id:
                inserted_docs += 1
                if inserted_docs % 5 == 0:
                    print(f"✅ Added {inserted_docs} to DB")
            else: # skip over the rest if document already exists
                print(f"📝 Already have job {job_id} in DB. Skipping.")
                continue

            try:
                title_embedding = client.create_embeddings(position)
                #print(title_embedding)
                await document_manager.update_job_w_conn(conn, title_embedding, doc_id)
            except Exception as e:
                print(f"❌ failure updating job {job_id} with vector: {e}")
                continue

            # Skip empty descriptions
            if not description.strip():                
                continue

            # split text into chunks
            chunks_texts = chunk_text(description)

            # Create batch embeddings for chunks
            batch_embeddings = client.create_embeddings(chunks_texts)

            # Insert chunks into DB
            for idx, (chunk_text_piece, embedding_vector) in enumerate(zip(chunks_texts, batch_embeddings)):
                try:
                    await document_manager.insert_chunk_w_conn(conn=conn, 
                                                        doc_id=doc_id, 
                                                        chunk_index=idx, 
                                                        chunk_content=chunk_text_piece, 
                                                        embedding_vector=embedding_vector)
                except Exception as e:
                    print(f"❌ failure inserting chunks for {position} - {e}")
                else:
                    inserted_chunks += 1
                    if inserted_chunks % 5 == 0:
                        print(f"⚡ Added {len(inserted_chunks)} chunks to db")

    return inserted_docs, inserted_chunks


async def main():
    jobs = await fetch_jobs()
    print(f"✅ Successfully fetched jobs from the API: {len(jobs)}")
    docs, chunks = await insert_jobs(jobs)
    print(f"✅ Inserted {docs} new documents and \n✅ Inserted {chunks} new chunks")


if __name__ == "__main__":
    asyncio.run(main())