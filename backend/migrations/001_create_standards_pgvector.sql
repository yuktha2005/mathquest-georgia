-- Supabase Migration: 001_create_standards_pgvector.sql
-- Enables pgvector extension, creates standards table, HNSW vector index,
-- and semantic similarity search RPC function for Georgia Standards of Excellence (MGSE).

-- 1. Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the standards table
CREATE TABLE IF NOT EXISTS standards (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,              -- e.g., 'MGSE5.NF.1'
    topic TEXT NOT NULL,                     -- e.g., 'fractions', 'decimals', 'ratios', 'geometry'
    grade INTEGER NOT NULL,                  -- e.g., 5 or 6
    title TEXT NOT NULL DEFAULT '',          -- Short descriptor
    description TEXT NOT NULL,               -- Full standard statement
    summary TEXT NOT NULL DEFAULT '',        -- Student/teacher-friendly explanation in own words
    key_concepts TEXT[] DEFAULT '{}',        -- Key vocabulary and conceptual terms
    embedding vector(768),                   -- Gemini text-embedding-004 vector
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. Create indices for filtering by topic and grade
CREATE INDEX IF NOT EXISTS idx_standards_topic ON standards (topic);
CREATE INDEX IF NOT EXISTS idx_standards_grade ON standards (grade);
CREATE INDEX IF NOT EXISTS idx_standards_topic_grade ON standards (topic, grade);

-- 4. Create HNSW vector index for high-performance approximate cosine similarity search
CREATE INDEX IF NOT EXISTS idx_standards_embedding_hnsw
ON standards USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 5. Semantic similarity search RPC function
CREATE OR REPLACE FUNCTION match_standards (
    query_embedding vector(768),
    match_count INT DEFAULT 2,
    filter_topic TEXT DEFAULT NULL,
    filter_grade INT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    code TEXT,
    topic TEXT,
    grade INT,
    title TEXT,
    description TEXT,
    summary TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.code,
        s.topic,
        s.grade,
        s.title,
        s.description,
        s.summary,
        (1 - (s.embedding <=> query_embedding))::FLOAT AS similarity
    FROM standards s
    WHERE
        (filter_topic IS NULL OR s.topic = filter_topic)
        AND (filter_grade IS NULL OR s.grade = filter_grade)
        AND s.embedding IS NOT NULL
    ORDER BY s.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
