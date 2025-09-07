# Jobs-RAG-AI-Agent
A Custom Python-built RAG AI Agent for jobs

### To start:
create a .env file in the JOBS-RAG-AI-AGENT directory add the line:
- OPENAI_API_KEY=<your-open-api-key>

You will need docker v2 
-   docker compose up


### To run the Job Ingestor:
-   docker compose exec job_ingestor python job_ingestor/ingest.py

###Go to the UI
localhost:3000


### Go to the UI
localhost:3000



To check on the Postgresql Server: 
-   docker exec -it db psql -U postgres -d mydatabase

