# RAG-AI-Agent-Jobs
A Custom Python-built RAG AI Agent for jobs

###To start: 

-   docker compose up


###To run the Job Ingestor:
-   docker compose exec job_ingestor python job_ingestor/ingest.py



To check on the Postgresql Server: 
-   docker exec -it db psql -U postgres -d mydatabase
