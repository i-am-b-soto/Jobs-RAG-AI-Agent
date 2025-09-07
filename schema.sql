-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- =========================
-- Knowledge base: documents & chunks
-- =========================

CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  external_id TEXT,
  source TEXT,                 -- e.g., 'remoteok'
  doc_type TEXT,               -- e.g., 'job_post'
  company TEXT,
  title TEXT,
  title_embedding VECTOR(3072),
  url TEXT,
  description TEXT,
  published_at TIMESTAMPTZ,
  ingested_at TIMESTAMPTZ DEFAULT now(),
  metadata JSONB               -- tags, location, salary, apply_url, etc.
);


--CREATE INDEX IF NOT EXISTS documents_title_embedding_ivfflat
--ON documents USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);


CREATE TABLE IF NOT EXISTS chunks (
  id BIGSERIAL PRIMARY KEY,
  document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INT,
  content TEXT,
  embedding VECTOR(3072),      -- must match your embedding model dimension
  metadata JSONB
);

-- Hybrid search helpers (optional but recommended)
ALTER TABLE chunks
  ADD COLUMN IF NOT EXISTS content_tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED;

-- Indexes
--CREATE INDEX IF NOT EXISTS chunks_embedding_ivfflat
--  ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS chunks_metadata_gin
  ON chunks USING GIN (metadata);

CREATE INDEX IF NOT EXISTS chunks_content_tsv_gin
  ON chunks USING GIN (content_tsv);

-- =========================
-- Conversation memory
-- =========================

CREATE TABLE IF NOT EXISTS conversations (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
  id BIGSERIAL PRIMARY KEY,
  conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE,
  sender TEXT CHECK (sender IN ('user','assistant','system')),
  content TEXT,
  embedding VECTOR(3072),      -- embed messages for semantic recall
  metadata JSONB,
  role TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE messages
  ADD COLUMN IF NOT EXISTS content_tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED;

CREATE INDEX IF NOT EXISTS messages_embedding_ivfflat
  ON messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

CREATE INDEX IF NOT EXISTS messages_content_tsv_gin
  ON messages USING GIN (content_tsv);

-- =========================
-- Provenance (which KB chunks supported which answer)
-- =========================

CREATE TABLE IF NOT EXISTS citations (
  id BIGSERIAL PRIMARY KEY,
  message_id BIGINT REFERENCES messages(id) ON DELETE CASCADE,
  chunk_id BIGINT REFERENCES chunks(id) ON DELETE CASCADE,
  relevance FLOAT
);