# Enterprise AI PDF Assistant

An enterprise-style AI PDF Assistant that allows users to upload PDF documents and ask questions about their content using Retrieval-Augmented Generation (RAG).

The application combines a React + TypeScript frontend, FastAPI backend, PostgreSQL with pgvector, and locally hosted Ollama models to provide document-grounded conversational answers with source references.

## Features

* User signup and login with JWT authentication
* Protected user-specific documents and conversations
* PDF upload with file validation and size limits
* PDF text extraction using PyMuPDF
* Recursive text chunking with overlap
* 768-dimensional document embeddings using `embeddinggemma`
* Vector similarity search using PostgreSQL + pgvector
* Retrieval of the top 5 most relevant document chunks using vector similarity
* RAG-based question answering using `qwen3.5:0.8b`
* Responses grounded in retrieved document content
* Conversational context using previous messages
* Up to 10 previous conversation messages included as conversational context
* Source references returned with the current assistant response, including document chunk and page information
* Follow-up questions within conversations
* Multiple conversations per document
* Conversation creation, switching, and persistent message history
* User ownership and access isolation for documents and conversations
* Frontend loading, validation, error and empty states
* Protection against treating untrusted document content as system instructions
* Dockerized frontend, backend and PostgreSQL services
* Local LLM and embedding inference through Ollama

## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### RAG Response
![RAG Response](screenshots/rag-response.png)

### Conversation History
![Conversation History](screenshots/conversation-history.png)

## Architecture

```text
                         Browser
                            │
                            ▼
                  React + TypeScript
                     (Nginx :5173)
                            │
                            │ HTTP
                            ▼
                    FastAPI Backend
                       (:8000)
                     /          \
                    /            \
                   ▼              ▼
        PostgreSQL + pgvector    Ollama
               (:5432)        (Windows host)
                   │            │
                   │            ├── embeddinggemma
                   │            └── qwen3.5:0.8b
                   ▼
              Document Data
              + Embeddings
              + Conversations
              + Messages
```

When running with Docker Compose, the frontend, backend and PostgreSQL services communicate through the automatically created Compose network. Ollama runs locally on the host machine and is accessed by the backend through `host.docker.internal`.

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
Ollama LLM
    │
    ▼
Grounded Answer + Sources
```
## Tech Stack

### Frontend

* React 19
* TypeScript
* React Router
* Vite
* Nginx for production serving

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

* Ollama
* `embeddinggemma` for embeddings
* `qwen3.5:0.8b` for local generation
* Cosine similarity retrieval

### Infrastructure

* Docker
* Docker Compose

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

## Running the Application

### Prerequisites

Install the following:

* Docker Desktop
* Ollama
* Git

Pull the required Ollama models:
```bash
ollama pull embeddinggemma
ollama pull qwen3.5:0.8b
```

### Environment Configuration

Create a root `.env` file:
```text
SECRET_KEY=your_secure_secret_key
```

Do not commit the `.env` file.

The repository includes `.env.example` as a template.

### Start with Docker Compose

From the project root:

```bash
docker compose up --build
```

The application will start:

* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`
* Swagger documentation: `http://localhost:8000/docs`
* PostgreSQL: `localhost:5432`

Ollama remains running on the host machine and is accessed by the backend container through:

```text
http://host.docker.internal:11434
```

To stop the application:

```bash
docker compose down
```

The PostgreSQL volume is retained unless it is explicitly removed.

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

## Security and Design

* JWT-based authentication protects application routes.
* Passwords are hashed using Argon2.
* Users can access only their own documents and conversations.
* Uploaded files are validated by type and size.
* Uploaded filenames are sanitized before storage.
* Database operations use SQLAlchemy.
* Schema changes are managed through Alembic migrations.
* Document content is treated as untrusted input when constructing LLM prompts.
* Environment variables are used for secrets and environment-specific configuration.
* Secrets and local environment files are excluded from version control.

## Testing

The application was tested through the complete user workflow:
```text
Signup
  ↓
Login
  ↓
Dashboard
  ↓
PDF Upload
  ↓
Document Processing
  ↓
Create Conversation
  ↓
Ask Question
  ↓
RAG Retrieval
  ↓
LLM Response + Sources
  ↓
Follow-up Questions
  ↓
Refresh / Conversation History
```

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

The Dockerized application was tested end-to-end with the frontend, FastAPI backend, PostgreSQL/pgvector, and Ollama working together.

Backend linting and frontend linting were run during development, with the frontend lint check completing without errors.

## Current Scope and Future Improvements

The project focuses on demonstrating an end-to-end enterprise-style RAG application rather than production-scale infrastructure.

Possible future extensions include:
* RAG evaluation and automated quality testing
* Response streaming
* Caching for frequently repeated queries
* Rate limiting
* Background document processing
* Observability and centralized logging
* Horizontal scaling
* Additional document formats
* Cloud-hosted model and database infrastructure