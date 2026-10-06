# Enterprise AI PDF Assistant

Upload PDFs and ask questions about them in natural language. The application uses retrieval-augmented generation (RAG) to answer questions from relevant document passages, with page-level source references. It supports both local inference through Ollama and a hosted deployment using Gemini.

**Live demo:** https://enterprise-ai-pdf-assistant-1.onrender.com
> Hosted on free tiers: the first load may take 30–60 seconds while the server wakes up.
> Please don't upload sensitive documents. In the hosted demo, document text and questions are sent to the Gemini API for embeddings and answers.

**Stack:** React + TypeScript · FastAPI · PostgreSQL + pgvector · Ollama · Gemini API · Docker

## How It Works

On upload, the PDF text is extracted and split into overlapping chunks. Each chunk is converted into an embedding and stored in PostgreSQL with pgvector. When a user asks a question, the application generates a query embedding and uses vector similarity search to retrieve the most relevant document chunks. The retrieved content is combined with conversation context and passed to the configured LLM to generate a grounded answer with document page references.

## Screenshots

### Dashboard

Upload and manage documents from the authenticated dashboard.

![Dashboard](./frontend/screenshots/dashboard.png)

### RAG Response

Ask questions and view grounded answers with document page references.

![RAG Response](./frontend/screenshots/rag-response.png)

### Conversation History

Continue previous conversations and review earlier questions and answers.

![Conversation History](./frontend/screenshots/conversation-history.png)

## Features

### Auth & Security
* User signup and login with JWT authentication
* Protected user-specific documents and conversations
* User ownership and access isolation for documents and conversations
* Protection against treating untrusted document content as system instructions
* Frontend validation, error and empty states

### Document Processing
* PDF upload with file validation and size limits
* PDF text extraction using PyMuPDF
* Recursive text chunking with overlap
* 768-dimensional document embeddings

### RAG & Chat
* Vector similarity search using PostgreSQL + pgvector, retrieving the top 5 relevant document chunks
* RAG-based question answering with configurable LLM providers
* Local inference through Ollama or hosted inference through the Gemini API
* Responses grounded in retrieved document content
* Conversational context using up to 10 previous messages
* Source references with document chunk and page information
* Follow-up questions within conversations
* Multiple conversations per document
* Conversation creation, switching, and persistent message history

### Infrastructure
* Dockerized frontend, backend and PostgreSQL services
* Configurable AI provider for local or hosted inference
* Local AI inference through Ollama

## Architecture

```text
                         Browser
                            │
                            ▼
                  React + TypeScript
                            │
                            │ HTTP
                            ▼
                    FastAPI Backend
                     /          \
                    /            \
                   ▼              ▼
        PostgreSQL + pgvector    AI Provider
                   │                 /    \    
                   │                /      \
                   │               /        \
                   ▼              ▼          ▼    
            Document Data       Ollama      Gemini API
            + Embeddings        |
            + Conversations     ├── embeddinggemma
            + Messages          └── qwen3.5:0.8b

```

The application uses the same RAG architecture in both local and hosted modes. PostgreSQL with pgvector stores document chunks, embeddings, conversations, and messages, while vector similarity search retrieves the most relevant document passages.

The AI provider is configurable by environment. In local mode, Ollama handles both embedding generation and LLM inference using `embeddinggemma` and `qwen3.5:0.8b`. In the hosted deployment, the Gemini API handles both embedding generation and LLM inference.

When running with Docker Compose, the frontend, backend and PostgreSQL services communicate through the created Compose network. Ollama runs locally on the host machine and is accessed by the backend through `host.docker.internal`.

In the hosted deployment, the application runs on Render with Neon PostgreSQL + pgvector, while AI inference and embedding generation are provided by the Gemini API.

## RAG Pipeline

```text
PDF Upload
    │
    ▼
Text Extraction
    │
    ▼
Text Chunking
    │
    ▼
Embedding Generation
    │
    ▼
PostgreSQL + pgvector
    │
    │
User Question
    │
    ▼
Question Embedding
    │
    ▼
Vector Similarity Search
    │
    ▼
Top Relevant Chunks
    │
    + Previous Conversation Context
    │
    ▼
LLM Prompt
    │
    ▼
Configured LLM Provider
    │ 
    ├── Ollama (local)
    │ 
    └── Gemini API (hosted) 
    │
    ▼
Grounded Answer + Sources
```

## Design Decisions

**pgvector inside PostgreSQL**

PostgreSQL already stores the application's relational data, so keeping embeddings in the same database avoids running and syncing a separate vector database. This keeps deployment simple and lets document, chunk and embedding data live under one schema and one set of migrations.

**Chunking: 600 characters, 100 overlap**

Chunks are small enough to keep retrieved context focused, and the overlap reduces the chance of losing information at chunk boundaries. These values are starting defaults and have not yet been tuned against an evaluation set.

**Retrieving the top 5 chunks**

Five chunks provide multiple potentially relevant passages while limiting the amount of retrieved context passed to the LLM. This is a starting default to be tuned through evaluation.

**One conversation per document**

Each conversation is tied to a single document (a document can have many conversations). This keeps retrieval scoped to one source, makes answers and page references easy to trace, and avoids cross-document confusion.

**Configurable AI Provider**

The application separates AI provider integration from the core RAG pipeline, allowing the same application flow to run with different providers. Local mode uses Ollama with `embeddinggemma` for embeddings and `qwen3.5:0.8b` for answer generation, while the hosted deployment uses the Gemini API for both embeddings and answer generation.

**Documents are untrusted input**

Retrieved PDF text is treated as data, not instructions. The prompt separates it from the assistant's own instructions to reduce the risk of prompt injection through uploaded documents.

## Tech Stack

### Frontend

* React 19
* TypeScript
* React Router
* Vite
* Nginx(Docker image only)

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT authentication
* Argon2 password hashing
* PyMuPDF
* LangChain text splitters

### Database

* PostgreSQL 17
* pgvector
* Alembic migrations

### AI / RAG

* Ollama for local inference
* Gemini API for hosted inference
* `embeddinggemma` for local embeddings
* `qwen3.5:0.8b` for local generation
* `gemini-embedding-2` for hosted embeddings
* `gemini-3.6-flash` for hosted generation
* Cosine similarity retrieval

### Infrastructure

* Docker
* Docker Compose
* Render for hosted application deployment
* Neon PostgreSQL for hosted database

## Running the Application

### Local Mode

#### Prerequisites

Install:

* Docker Desktop
* Ollama
* Git

Pull the required Ollama models:

```bash
ollama pull embeddinggemma
ollama pull qwen3.5:0.8b
```

#### Environment Configuration

Create a root `.env` file:

```text
SECRET_KEY=your_secure_secret_key
AI_PROVIDER=ollama
FRONTEND_URL=http://localhost:5173
```

Do not commit the `.env` file.

The repository includes `.env.example` as a template.

#### Start with Docker Compose

From the project root:

```bash
docker compose up --build
```

The application will start:

* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`
* Swagger documentation: `http://localhost:8000/docs`
* PostgreSQL: `localhost:5432`

Ollama runs on the host machine and is accessed by the backend container through:

```text
http://host.docker.internal:11434
```

To stop the application:

```bash
docker compose down
```

The PostgreSQL volume is retained unless it is explicitly removed.

### Hosted Deployment

| Component | Service |
|-----------|---------|
| Frontend  | Render  |
| Backend   | Render  |
| Database  | Neon PostgreSQL + pgvector |
| LLM (hosted demo) | Gemini API |

The app supports two modes: 

* Local: Docker Compose + PostgreSQL + Ollama
* Hosted: Render + Neon PostgreSQL + Gemini API

Environment variables: 

`DATABASE_URL`, `SECRET_KEY`, `AI_PROVIDER`, `GEMINI_API_KEY`, `FRONTEND_URL`

#### 1. Create the PostgreSQL Database

Create a PostgreSQL database on Neon with the `pgvector` extension enabled.

Configure your local environment to use the Neon `DATABASE_URL` and run the Alembic migrations to create the required database schema in Neon.

#### 2. Deploy the Backend

Create a backend service on Render using the backend directory and configure the required environment variables:

```text
DATABASE_URL=<neon_database_url>
SECRET_KEY=<secure_secret_key>
AI_PROVIDER=gemini
GEMINI_API_KEY=<gemini_api_key>
FRONTEND_URL=<render_frontend_url>
```

The backend connects to the existing Neon PostgreSQL database using `DATABASE_URL`.

After deployment, note the backend URL provided by Render.

#### 3. Deploy the Frontend

Create a frontend service on Render and configure it to use the deployed backend URL.

Set the frontend API URL environment variable  `VITE_API_BASE_URL` to the Render backend URL used by the application.

After deployment, note the frontend URL provided by Render.

#### 4. Connect the Frontend and Backend

The frontend must point to the deployed Render backend, while the backend's `FRONTEND_URL` must point to the deployed Render frontend.

For example:

```text
Frontend → https://<frontend-service>.onrender.com
Backend  → https://<backend-service>.onrender.com
```

Configure these URLs in the corresponding Render environment variables before redeploying.

#### 5. Configure Gemini

Set:

```text
AI_PROVIDER=gemini
GEMINI_API_KEY=<gemini_api_key>
```

The hosted deployment uses the Gemini API for both embedding generation and LLM inference.

Gemini embeddings are configured to 768 dimensions to match the schema.

Once the frontend, backend, database, and Gemini API configuration are complete, the deployed application can be accessed through the Render frontend URL.

## API Overview

The FastAPI backend exposes REST endpoints for authentication, documents, conversations, and messages.

| Area                           | Purpose                                             |
| ------------------------------ | --------------------------------------------------- |
| `/auth`                        | User signup and login                               |
| `/documents`                   | PDF upload and document management                  |
| `/conversations`               | Create and manage document conversations            |
| `/conversations/{id}/messages` | Submit questions and retrieve conversation messages |

Interactive API documentation is available through FastAPI Swagger UI at:
```text
http://localhost:8000/docs
```

For the hosted deployment, Swagger UI is available at the deployed backend's `/docs` endpoint.

## Security

* JWT-based authentication protects application routes.
* Passwords are hashed using Argon2.
* Users can access only their own documents and conversations.
* Uploaded files are validated by type and size.
* Uploaded filenames are sanitized before storage.
* Document content is treated as untrusted input when constructing LLM prompts.
* CORS is restricted to the configured `FRONTEND_URL`.
* Environment variables are used for secrets, API keys and environment-specific configuration.
* Secrets and local environment files are excluded from version control.

## Verification & Testing

The following scenarios were manually validated during development:
* User signup and login
* PDF upload and document processing
* RAG-based question answering with source references
* Follow-up questions using conversation context
* Multiple conversations and conversation switching
* Message persistence after page refresh
* User-specific document and conversation access
* Error and empty states
* Dockerized end-to-end application flow
* Hosted end-to-end application flow using the Gemini API

The `tests/` directory contains manual verification scripts for core services, including:

* Embedding generation and vector dimensions
* LLM response generation
* RAG pipeline behavior
* Semantic retrieval behavior

These scripts invoke application services directly and print results for manual verification; they are not automated pytest tests.

Frontend linting was performed using ESLint and completed without errors.

## Project Structure

```text
PDF Assistant/
│
├── Backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── conversations.py
│   │   │   ├── documents.py
│   │   │   └── messages.py
│   │   │
│   │   ├── services/
│   │   │   ├── chunking_service.py
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── prompt_service.py
│   │   │   └── retrieval_service.py
│   │   │
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Known Limitations

* Hosted demo runs on free tiers: cold starts, and Gemini API quota/rate limits may slow or block requests.
* In hosted mode, document text and questions are sent to the Gemini API; use local mode for sensitive documents.
* Switching AI providers requires re-embedding documents (embedding models differ).
* No rate limiting on the public demo yet.
* Scanned or image-only PDFs are not supported because OCR is not currently implemented.
* No formal RAG evaluation or benchmark yet; it is a planned improvement.
* Local mode requires Ollama to be running on the host machine and accessible from the backend container.
* In local mode, `qwen3.5:0.8b` may struggle with complex reasoning, and speed depends on hardware.

## Current Scope and Future Improvements

The project focuses on demonstrating an end-to-end enterprise-style RAG application rather than production-scale infrastructure.

Possible future extensions include:
* RAG evaluation and automated quality testing
* Response streaming
* Caching for frequently repeated queries
* Rate limiting
* Background document processing
* Observability and centralized logging
* Additional document formats