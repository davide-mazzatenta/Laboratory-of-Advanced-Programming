-- Supabase Database Schema for Multiagent Platform

-- Table for storing PDF documents (binary data)
CREATE TABLE pdf_storage (
    id TEXT PRIMARY KEY, -- Format: userId_projectId_docId
    user_id UUID NOT NULL REFERENCES auth.users(id),
    project_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    file_data BYTEA NOT NULL, -- Binary PDF data
    file_size BIGINT NOT NULL,
    content_type TEXT DEFAULT 'application/pdf'
);

-- Table for document metadata and plain text content
CREATE TABLE project_documents (
    id TEXT PRIMARY KEY, -- Same format: userId_projectId_docId
    user_id UUID NOT NULL REFERENCES auth.users(id),
    project_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT -- Plain text extracted from PDF
);

-- Indexes for better query performance
CREATE INDEX idx_pdf_storage_user_project ON pdf_storage(user_id, project_id);
CREATE INDEX idx_pdf_storage_composite ON pdf_storage(user_id, project_id, doc_id);
CREATE INDEX idx_project_documents_user_project ON project_documents(user_id, project_id);
CREATE INDEX idx_project_documents_composite ON project_documents(user_id, project_id, doc_id);

-- Optional: Table for tracking execution plans and results (if needed for persistence)
CREATE TABLE execution_plans (
    plan_id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    project_id TEXT NOT NULL,
    original_prompt TEXT NOT NULL,
    document_ids TEXT[], -- Array of document IDs
    strategy TEXT,
    status TEXT DEFAULT 'pending', -- pending, confirmed, executing, completed, failed
    additional_instructions TEXT
);

CREATE TABLE execution_results (
    execution_id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES execution_plans(plan_id),
    agent_results JSONB, -- Store agent responses as JSON
    final_result TEXT,
    status TEXT DEFAULT 'processing' -- processing, completed, failed
);


-- Table for storing document chunks with embeddings as JSON
CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY, -- Format: userId_projectId_docId_chunkIndex
    user_id UUID NOT NULL REFERENCES auth.users(id),
    project_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding JSON NOT NULL, -- Store embedding as JSON array
    embedding_size INTEGER NOT NULL, -- Store the size for validation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX idx_document_chunks_doc ON document_chunks(user_id, project_id, doc_id);
CREATE INDEX idx_document_chunks_composite ON document_chunks(user_id, project_id, doc_id, chunk_index);