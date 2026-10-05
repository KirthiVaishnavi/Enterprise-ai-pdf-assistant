import httpx
import os
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/embed"
OLLAMA_EMBEDDING_MODEL = "embeddinggemma"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-embedding-2:batchEmbedContents"
)

class EmbeddingServiceError(Exception):
    pass

def generate_embeddings(texts: list[str])->list:
    if AI_PROVIDER == "ollama":
        return generate_ollama_embeddings(texts)
    if AI_PROVIDER == "gemini":
        return generate_gemini_embeddings(texts)
    raise EmbeddingServiceError(
        f"Unsupported AI provider: {AI_PROVIDER}"
    )

def generate_ollama_embeddings(texts: list[str]) -> list:    
    try:
        response=httpx.post(
            OLLAMA_URL,
            json={
                "model":OLLAMA_EMBEDDING_MODEL,
                "input":texts
            },
            timeout=120.0
        )
        response.raise_for_status()
        
        data=response.json()
        if "embeddings" not in data or not isinstance(data["embeddings"], list) or not data["embeddings"] or len(data["embeddings"]) != len(texts):
            raise EmbeddingServiceError("Invalid ollama embedding response")
        
        return data["embeddings"]

    except (httpx.HTTPError,ValueError) as e:
        raise EmbeddingServiceError(
            "Ollama embedding service unavailable"
        ) from e

def generate_gemini_embeddings(texts: list[str]) -> list:
    if not GEMINI_API_KEY:
        raise EmbeddingServiceError(
            "GEMINI_API_KEY is not configured"
        )
        
    requests = [
        {
            "model": "models/gemini-embedding-2",
            "content": {
                "parts": [
                    {
                        "text": text
                    }
                ]
            },
            "output_dimensionality": 768
        }
        for text in texts
    ]
    
    try:
        response = httpx.post(
            GEMINI_URL,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "requests": requests
            },
            timeout=120.0
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        if (
                "embeddings" not in data
                or not isinstance(data["embeddings"], list)
                or len(data["embeddings"]) != len(texts)
            ):
                raise EmbeddingServiceError(
                    "Invalid Gemini embedding response"
                )
        embeddings = []
        
        for embedding in data["embeddings"]:
            if (    
                not isinstance(embedding, dict)
                or "values" not in embedding
                or not isinstance(embedding["values"], list)
                or len(embedding["values"]) != 768
            ):
                raise EmbeddingServiceError(
                    "Invalid Gemini embedding response"
                )
            embeddings.append(embedding["values"])
        return embeddings
    
    except(httpx.HTTPError, ValueError) as e:
        raise EmbeddingServiceError(
            "Gemini embedding service unavailable"
        ) from e