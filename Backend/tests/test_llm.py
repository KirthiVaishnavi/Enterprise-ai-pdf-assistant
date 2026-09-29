from app.services.llm_service import generate_answer

prompt="what is 2+2?"

response=generate_answer(prompt)

print("LLM Answer: ",response)