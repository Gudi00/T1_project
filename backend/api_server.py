from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from VectorDataBase import VectorDataBase
from VectorSearcher import VectorSearcher
from Qwen_model import get_qwen_response
from ChatHistory import ChatHistory
import os
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Инициализация FastAPI
app = FastAPI(title="Smart Support API", version="1.0")

# Разрешаем запросы с фронтенда (React/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно заменить на ['http://localhost:5173']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы и чата
vector_db = VectorDataBase(api_token=API_TOKEN)
try:
    vector_db.load_from_file("vector_db.json")
except FileNotFoundError:
    vector_db.create_from_csv("kb.csv")
    vector_db.save_to_file("vector_db.json")

searcher = VectorSearcher(vector_db, API_TOKEN)
chat = ChatHistory()


class QueryRequest(BaseModel):
    question: str


@app.post("/chat")
def chat_with_ai(request: QueryRequest):
    """
    Основной эндпоинт — принимает вопрос и возвращает ответ ассистента
    """
    user_query = request.question.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустым")

    # Добавляем в историю
    chat.add_message("user", user_query)

    # Ищем похожие вопросы
    results = searcher.find_similar_questions(user_query, top_k=3, min_similarity=0.5)
    if not results:
        return {"answer": "Не найдено релевантных ответов."}

    # Собираем контекст
    context = "\n\n".join([
        f"Вопрос: {r['metadata']['question']}\nОтвет: {r['metadata']['answer']}"
        for r in results
    ])

    messages = chat.get_messages([
        {
            "role": "system",
            "content": (
                "Ты ассистент службы поддержки банка. "
                "Отвечай вежливо, кратко и по сути, используя только данные из контекста."
            ),
        },
        {"role": "user", "content": f"data:\n{context}\n\nВопрос клиента: {user_query}"}
    ])

    try:
        answer = get_qwen_response(API_TOKEN, messages)
        chat.add_message("assistant", answer)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении ответа: {e}")


@app.get("/")
def root():
    return {"message": "Smart Support API is running 🚀"}
