import httpx
import os
from dotenv import load_dotenv

load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/chat"
LLM_MODEL = "qwen3.5:0.8b"

class LLMServiceError(Exception):
    pass

def generate_answer(prompt:str)->str:
    try:
        response=httpx.post(
            OLLAMA_URL,
            json={
                "model":LLM_MODEL,
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
            raise LLMServiceError("Invalid LLM response")
  
        if "content" not in data["message"] or not isinstance(data["message"]["content"], str) or not data["message"]["content"].strip():
            raise LLMServiceError("Invalid LLM response")
        
        return data["message"]["content"]
    
    except (httpx.HTTPError, ValueError) as e:
        raise LLMServiceError(
            "LLM service unavailable"
        ) from e
    