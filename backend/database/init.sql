-- PostgreSQL initialization script for CogniForge

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path VARCHAR(512) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64),
    mime_type VARCHAR(100),
    file_type VARCHAR(20),
    document_type VARCHAR(50) DEFAULT 'other' CHECK (document_type IN ('due_diligence', 'resume', 'vacancy', 'script', 'other')),
    
    -- Content extraction
    extracted_text TEXT,
    total_pages INTEGER,
    total_characters INTEGER,
    total_chunks INTEGER,
    
    -- Processing status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'archived')),
    is_processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    title VARCHAR(500),
    author VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    page_count INTEGER,
    word_count INTEGER,
    
    -- Structured content
    structured_content JSONB,
    doc_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Embeddings
    embedding_vector BYTEA,
    embedding_model VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT unique_file_path UNIQUE (file_path)
);

-- Document chunks for RAG
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_type VARCHAR(50) CHECK (chunk_type IN ('text', 'table', 'code', 'section', 'list')),
    
    -- Embeddings
    embedding_vector BYTEA,
    embedding_model VARCHAR(100),
    
    -- Metadata
    page_number INTEGER,
    section_title VARCHAR(500),
    chunk_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT unique_document_chunk UNIQUE (document_id, chunk_index)
);

-- Resume-specific data
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Personal info
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    
    -- Skills
    technical_skills JSONB DEFAULT '[]'::jsonb,
    soft_skills JSONB DEFAULT '[]'::jsonb,
    languages JSONB DEFAULT '[]'::jsonb,
    tools JSONB DEFAULT '[]'::jsonb,
    
    -- Experience
    experience JSONB DEFAULT '[]'::jsonb,
    total_experience_years DECIMAL(4,1),
    
    -- Education
    education JSONB DEFAULT '[]'::jsonb,
    
    -- Projects
    projects JSONB DEFAULT '[]'::jsonb,
    
    -- Certifications
    certifications JSONB DEFAULT '[]'::jsonb,
    
    -- Analysis
    skill_score DECIMAL(5,2),
    experience_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vacancy-specific data
CREATE TABLE vacancies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Job details
    job_title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    
    -- Requirements
    required_skills JSONB DEFAULT '[]'::jsonb,
    preferred_skills JSONB DEFAULT '[]'::jsonb,
    responsibilities JSONB DEFAULT '[]'::jsonb,
    qualifications JSONB DEFAULT '[]'::jsonb,
    
    -- Job details
    salary_range VARCHAR(100),
    location VARCHAR(255),
    work_type VARCHAR(50) CHECK (work_type IN ('remote', 'hybrid', 'onsite')),
    experience_level VARCHAR(50) CHECK (experience_level IN ('entry', 'mid', 'senior', 'lead', 'executive')),
    
    -- Analysis
    skill_count INTEGER,
    responsibility_count INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Similarity relationships
CREATE TABLE document_similarities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    similarity_type VARCHAR(50) NOT NULL CHECK (similarity_type IN ('content', 'skills', 'topic', 'semantic')),
    similarity_score DECIMAL(5,4) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    
    -- Metadata
    overlapping_sections JSONB DEFAULT '[]'::jsonb,
    contradictions JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT unique_similarity_pair UNIQUE (source_document_id, target_document_id, similarity_type),
    CONSTRAINT different_documents CHECK (source_document_id != target_document_id)
);

-- Processing jobs
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('extraction', 'embedding', 'similarity', 'export', 'cleanup')),
    
    -- Job status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    priority INTEGER NOT NULL DEFAULT 0,
    
    -- Execution details
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    progress DECIMAL(5,2) CHECK (progress >= 0 AND progress <= 100),
    
    -- Parameters
    parameters JSONB DEFAULT '{}'::jsonb,
    result JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Export jobs
CREATE TABLE export_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    export_type VARCHAR(50) NOT NULL CHECK (export_type IN ('json', 'markdown', 'pdf', 'excel', 'csv')),
    
    -- Export details
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    file_path VARCHAR(500),
    file_size BIGINT,
    
    -- Parameters
    parameters JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- System metrics
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(12,4) NOT NULL,
    unit VARCHAR(20),
    
    -- Context
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tags JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for performance
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_document_type ON documents(document_type);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_resumes_document_id ON resumes(document_id);
CREATE INDEX idx_vacancies_document_id ON vacancies(document_id);
CREATE INDEX idx_document_similarities_source ON document_similarities(source_document_id);
CREATE INDEX idx_document_similarities_target ON document_similarities(target_document_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX idx_processing_jobs_created_at ON processing_jobs(created_at);
CREATE INDEX idx_export_jobs_status ON export_jobs(status);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vacancies_updated_at BEFORE UPDATE ON vacancies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_jobs_updated_at BEFORE UPDATE ON processing_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for document statistics
CREATE VIEW document_statistics AS
SELECT
    document_type,
    status,
    COUNT(*) as count,
    AVG(file_size) as avg_file_size,
    MIN(created_at) as oldest_document,
    MAX(created_at) as newest_document
FROM documents
GROUP BY document_type, status;

-- Insert initial system metrics
INSERT INTO system_metrics (metric_type, metric_name, metric_value, unit, tags)
VALUES 
    ('system', 'database_initialized', 1, 'boolean', '{"version": "1.0.0"}'::jsonb),
    ('performance', 'initial_schema_version', 1, 'version', '{"migration": "initial"}'::jsonb);

-- Create comment on schema
COMMENT ON SCHEMA public IS 'CogniForge RAG System Database Schema v1.0.0';
