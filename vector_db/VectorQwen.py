import requests
import json
from typing import List, Dict



"""
Класс для генерации финального ответа на основе найденных в VectorDataBase
шаблонных ответов с использованием большой языковой модели (Qwen).
"""

API_URL = "https://llm.t1v.scibox.tech/v1/chat/completions"
MODEL_NAME = "Qwen2.5-72B-Instruct-AWQ"
SYSTEM_PROMPT = (
    "Ты русскоязычный ассистент, тебе нужно вежливо рассказывать по заготовленным ответам, "
    "но предварительно очеловечить и улучшить текст, но ничего не додумывай, "
    "информация берётся только из переменной data, которая передаётся после истории чата. "
    "История чата нужна только для контекcта, чтобы ты понимал, какой ответ хочет получить пользователь, "
    "но основную часть ответа нужно строить для нынешнего ответа пользователя."
)

def __init__(self, api_token: str):
    """
    Инициализация генератора.

    Args:
        api_token (str): API токен для доступа к сервису LLM.
    """
    self.api_token = api_token

def generate_response(data_for_llm) -> str:
    API_URL = "https://llm.t1v.scibox.tech/v1/chat/completions"
    MODEL_NAME = "Qwen2.5-72B-Instruct-AWQ"
    api_token = 'sk-eK2RKx7syQLko5qdKbvcLQ'
    SYSTEM_PROMPT = (
        "Ты русскоязычный ассистент, тебе нужно вежливо рассказывать по заготовленным ответам, "
        "но предварительно очеловечить и улучшить текст, но ничего не додумывай, "
        "информация берётся только из переменной data, которая передаётся после истории чата. "
        "История чата нужна только для контекта, чтобы ты понимал, какой ответ хочет получить пользователь, "
        "но основную часть ответа нужно строить для нынешнего ответа пользователя."
    )
    chat_history = []
    user_query = ''
    """, user_query: str = '',  chat_history: List[Dict] = None
    Генерирует улучшенный и очеловеченный ответ с помощью LLM.

    Args:
        user_query (str): Текущий вопрос пользователя.
        search_results (List[Dict]): Результаты семантического поиска
                                     (найденные шаблоны вопросов/ответов).
        chat_history (List[Dict]): Предыдущие пары вопрос-ответ для контекста.
                                   Формат: [{'question': '...', 'answer': '...'}, ...]

    Returns:
        str: Финальный ответ, сгенерированный LLM.
    """

    # 1. Форматируем историю чата

    history_str = ""
    if chat_history:
        for entry in chat_history:
            history_str += f"question: {entry.get('question', '')} | answer: {entry.get('answer', '')}\n"

    # 2. Форматируем найденные данные для LLM (контекст)
    # LLM важно передать только релевантные ответы для генерации.

    data_str = json.dumps(data_for_llm, ensure_ascii=False, indent=2)

    # 3. Создаем финальный промпт
    full_system_prompt = f"{SYSTEM_PROMPT} history(question+answer): {history_str} data: {data_str}"

    # 4. Формируем тело запроса к API
    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_query}
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 512  # Увеличим токен лимит для полноценных ответов
    }

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    print("Отправляем запрос к LLM Qwen...")

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Проверка на ошибки HTTP

        result = response.json()
        print(result)

        # Извлекаем сгенерированный ответ
        if result.get('choices') and result['choices'][0].get('message'):
            return result['choices'][0]['message']['content'].strip()

        return "Ошибка: Ответ от LLM не содержит ожидаемых данных."

    except requests.exceptions.HTTPError as err:
        return f"Ошибка HTTP при обращении к LLM: {err}. Ответ: {response.text}"
    except requests.exceptions.RequestException as err:
        return f"Ошибка при запросе к LLM API: {err}"
    except Exception as e:
        return f"Неизвестная ошибка при генерации ответа: {e}"