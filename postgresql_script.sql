-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- =========================
-- Knowledge base: documents & chunks
-- =========================

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY,
  source TEXT,                 -- e.g., 'remoteok'
  doc_type TEXT,               -- e.g., 'job_post'
  company TEXT,
  title TEXT,
  url TEXT,
  published_at TIMESTAMPTZ,
  ingested_at TIMESTAMPTZ DEFAULT now(),
  metadata JSONB               -- tags, location, salary, apply_url, etc.
);

CREATE TABLE IF NOT EXISTS chunks (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS chunks_embedding_ivfflat
  ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS chunks_metadata_gin
  ON chunks USING GIN (metadata);

CREATE INDEX IF NOT EXISTS chunks_content_tsv_gin
  ON chunks USING GIN (content_tsv);

-- =========================
-- Conversation memory
-- =========================

CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY,
  user_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  sender TEXT CHECK (sender IN ('user','assistant','system')),
  content TEXT,
  embedding VECTOR(3072),      -- embed messages for semantic recall
  metadata JSONB,
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
  id UUID PRIMARY KEY,
  message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
  chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
  relevance FLOAT
);