from VectorDataBase import VectorDataBase
from VectorSearcher import VectorSearcher
import requests

def get_qwen_response(api_token, messages, model='Qwen2.5-72B-Instruct-AWQ'):
    
    url = 'https://llm.t1v.scibox.tech/v1/chat/completions'

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 512
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
