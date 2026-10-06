import httpx
import os
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_LLM_MODEL = "qwen3.5:0.8b"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.6-flash:generateContent"
)

class LLMServiceError(Exception):
    pass

def generate_answer(prompt:str)->str:
    if AI_PROVIDER == "ollama":
        return generate_ollama_answer(prompt)

    if AI_PROVIDER == "gemini":
        return generate_gemini_answer(prompt)

    raise LLMServiceError(
        f"Unsupported AI provider: {AI_PROVIDER}"
    )
    
def generate_ollama_answer(prompt: str) -> str:
    try:
        response=httpx.post(
            OLLAMA_URL,
            json={
                "model":OLLAMA_LLM_MODEL,
                "messages":[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ],
                "think":False,
                "stream":False
            },
            timeout=300.0
        )
    
        response.raise_for_status()
    
        data=response.json() 
        if "message" not in data or not isinstance(data["message"], dict):
            raise LLMServiceError("Invalid OLLAMA LLM response")
  
        if "content" not in data["message"] or not isinstance(data["message"]["content"], str) or not data["message"]["content"].strip():
            raise LLMServiceError("Invalid OLLAMA LLM response")
        
        return data["message"]["content"]
    
    except (httpx.HTTPError, ValueError) as e:
        raise LLMServiceError(
            "Ollama LLM service unavailable"
        ) from e
    
    
def generate_gemini_answer(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise LLMServiceError(
            "GEMINI_API_KEY is not configured"
        )

    try:
        response = httpx.post(
            GEMINI_URL,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            timeout=300.0
        )

        response.raise_for_status()

        data = response.json()

        if (
            "candidates" not in data
            or not isinstance(data["candidates"], list)
            or not data["candidates"]
            or "content" not in data["candidates"][0]
            or "parts" not in data["candidates"][0]["content"]
            or not isinstance(data["candidates"][0]["content"]["parts"], list)
        ):
            raise LLMServiceError(
                "Invalid Gemini LLM response"
            )

        answer_parts = []

        for part in data["candidates"][0]["content"]["parts"]:
            if (
                isinstance(part, dict)
                and isinstance(part.get("text"), str)
                and part["text"].strip()
            ):
                answer_parts.append(part["text"])

        answer = "".join(answer_parts).strip()

        if not answer:
            raise LLMServiceError(
                "Invalid Gemini LLM response"
            )

        return answer

    except httpx.HTTPStatusError as e:
        print(
            f"Gemini API error: status={e.response.status_code}, "
            f"body={e.response.text}"
        )
        raise LLMServiceError(
            "Gemini LLM service unavailable"
        ) from e
    
    except (httpx.RequestError, ValueError) as e:
        print(f"Gemini API request/parsing error: {e}")
        raise LLMServiceError(
            "Gemini LLM service unavailable"
        ) from e