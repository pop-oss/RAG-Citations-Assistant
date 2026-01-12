# RAG Knowledge Base Q&A System

A RAG (Retrieval-Augmented Generation) knowledge base Q&A system with citation tracing and streaming output.

## Features

- 📚 **Knowledge Base Management**: Create and manage multiple knowledge bases
- 📄 **Document Upload**: Support for PDF, Markdown, and TXT files
- 🔍 **Vector Search**: Semantic search using pgvector
- 🤖 **Multi-Model Support**: DeepSeek, Qwen (Tongyi), Zhipu with fallback
- ⚡ **Streaming Output**: Real-time SSE streaming responses
- 📎 **Citation Tracing**: Track answer sources with page/line references

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js (App Router) + TypeScript + TailwindCSS
- **Database**: PostgreSQL + pgvector
- **LLM Providers**: DeepSeek, Qwen, Zhipu

## Quick Start

### Prerequisites

- Docker & Docker Compose
- API keys for at least one LLM provider

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Backend, Frontend)
docker-compose up -d
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Database

```bash
# Start PostgreSQL with pgvector
docker run -d \
  --name rag-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=rag_kb \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Knowledge Base
- `GET /api/kb` - List knowledge bases
- `POST /api/kb` - Create knowledge base
- `GET /api/kb/{id}` - Get knowledge base details
- `DELETE /api/kb/{id}` - Delete knowledge base

### Documents
- `GET /api/kb/{kb_id}/documents` - List documents
- `POST /api/kb/{kb_id}/documents` - Upload documents (multipart)

### Chat
- `POST /api/kb/{kb_id}/chat/stream` - Stream chat response (SSE)

## SSE Stream Protocol

```
event: token
data: {"token": "Hello"}

event: citations  
data: {"citations": [{...}]}

event: done
data: {}

event: error
data: {"message": "error", "code": "ERROR_CODE"}
```

## Project Structure

```
RAG-Citations-Assistant/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API routes
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── providers/           # LLM providers
│   └── utils/               # Utilities
├── frontend/
│   └── src/
│       ├── app/             # Next.js pages
│       ├── components/      # React components
│       └── lib/             # API client & utils
├── docker-compose.yml
└── .env.example
```

## License

MIT
