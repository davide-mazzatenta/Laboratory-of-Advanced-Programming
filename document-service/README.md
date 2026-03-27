# Document Service - Simplified Setup

## Setup & Build

1. **Set Environment Variables**

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-anon-key"
```

2. **Setup Supabase Database**
   Run this SQL in your Supabase SQL editor:

```sql
CREATE TABLE pdf_storage (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    file_data BYTEA NOT NULL,
    file_size BIGINT NOT NULL,
    content_type TEXT DEFAULT 'application/pdf'
);

CREATE TABLE project_documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT
);
```

3. **Build and Run Docker Container**

```bash
# Build image
docker build -t document-service .

# Run container
docker run -p 8000:8000 \
  -e SUPABASE_URL="$SUPABASE_URL" \
  -e SUPABASE_KEY="$SUPABASE_KEY" \
  document-service
```

## Test the API

**Upload PDF:**

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@your-file.pdf" \
  -F "user_id=user123" \
  -F "project_id=proj456" \
  -F "doc_id=doc1" \
  -F "title=Test Document"
```

**Get PDF:**

```bash
curl "http://localhost:8000/api/v1/documents/user123/proj456/doc1" --output test.pdf
```

**Get Text:**

```bash
curl "http://localhost:8000/api/v1/documents/user123/proj456/doc1/text"
```

**List Documents:**

```bash
curl "http://localhost:8000/api/v1/documents/user123/proj456"
```
