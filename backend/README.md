# BharatAce - AI Campus Assistant Backend

A FastAPI-based AI Campus Assistant using RAG (Retrieval-Augmented Generation) with LlamaIndex, Supabase, and Google Gemini.

## Features

- 🚀 **FastAPI Backend**: High-performance async API
- 🤖 **AI-Powered RAG**: LlamaIndex with Google Gemini LLM
- 💾 **Vector Database**: Supabase with pgvector extension
- 📚 **Knowledge Base CMS**: Simple CRUD API for managing content
- 🔍 **Semantic Search**: Advanced embedding-based retrieval

## Prerequisites

Before running this application, you need:

1. **Python 3.10+** installed
2. **Supabase Account** with a project created
3. **Google AI API Key** (for Gemini)

## Supabase Setup

### 1. Create the Knowledge Base Table

Run this SQL in your Supabase SQL Editor:

```sql
-- Create the knowledge_base table
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on category for faster filtering
CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_base_created_at ON knowledge_base(created_at DESC);
```

### 2. Enable pgvector Extension

```sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table for embeddings (used by LlamaIndex)
CREATE TABLE knowledge_base_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding vector(768),  -- dimension for text-embedding-004
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for similarity search
CREATE INDEX ON knowledge_base_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 3. Get Your Supabase Credentials

- **SUPABASE_URL**: Found in Settings → API → Project URL
- **SUPABASE_KEY**: Found in Settings → API → Project API keys (use `anon/public` key)

## Installation

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
GOOGLE_API_KEY=your-google-api-key
```

### 6. Update Database Connection String

⚠️ **Important**: In `main.py`, update the PostgreSQL connection string in the `initialize_llama_index()` function:

```python
vector_store = SupabaseVectorStore(
    postgres_connection_string="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres",
    collection_name="knowledge_base_embeddings",
    dimension=768
)
```

Replace:
- `[YOUR-PASSWORD]`: Your Supabase database password
- `[YOUR-PROJECT-REF]`: Your Supabase project reference (found in Supabase URL)

## Running the Application

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health check with component status

### Knowledge Base Management

- **POST** `/knowledge` - Add new content to knowledge base
  ```json
  {
    "content": "The university offers programs in Computer Science.",
    "category": "courses"
  }
  ```

- **GET** `/knowledge` - Retrieve all knowledge base entries

### Chatbot

- **POST** `/ask` - Ask a question to the AI assistant
  ```json
  {
    "query": "What programs does the university offer?"
  }
  ```

## Usage Example

### 1. Add Knowledge to the Database

```bash
curl -X POST "http://localhost:8000/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "BharatAce University offers undergraduate programs in Computer Science, Electronics, and Mechanical Engineering.",
    "category": "courses"
  }'
```

### 2. Ask Questions

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What undergraduate programs are available?"
  }'
```

## Project Structure

```
backend/
├── main.py              # FastAPI application with all routes
├── settings.py          # Environment configuration
├── models.py            # Pydantic models
├── database.py          # Supabase client
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
└── README.md           # This file
```

## Technology Stack

- **FastAPI**: Modern Python web framework
- **LlamaIndex**: RAG framework for AI applications
- **Supabase**: PostgreSQL database with vector support
- **Google Gemini**: LLM for generating responses
- **text-embedding-004**: Google's embedding model
- **Pydantic**: Data validation

## Troubleshooting

### Common Issues

1. **"Query engine not initialized"**
   - Check your environment variables are set correctly
   - Ensure Supabase is accessible
   - Check the logs for initialization errors

2. **Database connection errors**
   - Verify your `SUPABASE_URL` and `SUPABASE_KEY`
   - Check that the `knowledge_base` table exists
   - Ensure pgvector extension is enabled

3. **Embedding/LLM errors**
   - Verify your `GOOGLE_API_KEY` is valid
   - Check you have API quota available

### Viewing Logs

The application logs to console. Check the terminal for detailed error messages.

## Next Steps

- Add authentication and authorization
- Implement rate limiting
- Add more sophisticated query processing
- Implement caching for frequent queries
- Add support for file uploads
- Create admin dashboard

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.
