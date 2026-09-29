import httpx
import os
from dotenv import load_dotenv

load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/embed"
EMBEDDING_MODEL = "embeddinggemma"

class EmbeddingServiceError(Exception):
    pass

def generate_embeddings(texts: list[str])->list:
    try:
        response=httpx.post(
            OLLAMA_URL,
            json={
                "model":EMBEDDING_MODEL,
                "input":texts
            },
            timeout=120.0
        )
        response.raise_for_status()
        
        data=response.json()
        if "embeddings" not in data or not isinstance(data["embeddings"], list) or not data["embeddings"] or len(data["embeddings"]) != len(texts):
            raise EmbeddingServiceError("Invalid embedding response")
        
        return data["embeddings"]

    except (httpx.HTTPError,ValueError) as e:
        raise EmbeddingServiceError(
            "Embedding service unavailable"
        ) from e

