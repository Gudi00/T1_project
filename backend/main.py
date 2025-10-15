from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from VectorDataBase import VectorDataBase
from VectorSearcher import VectorSearcher
from Qwen_model import get_qwen_response
from ChatHistory import ChatHistory

# Загружаем токен
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Инициализация FastAPI
app = FastAPI(title="Smart Support API")

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно ограничить позже
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class Query(BaseModel):
    query: str

# Инициализация векторной базы
vector_db = VectorDataBase(api_token=API_TOKEN)
try:
    vector_db.load_from_file("vector_db.json")
    print("✅ Загружена существующая векторная база.")
except FileNotFoundError:
    print("⚙️ Файл базы не найден, создаём новую...")
    vector_db.create_from_csv("kb.csv")
    vector_db.save_to_file("vector_db.json")
    print("✅ Векторная база создана и сохранена.")

# Объекты поиска и истории
searcher = VectorSearcher(vector_db, API_TOKEN)
chat = ChatHistory()


@app.get("/")
def root():
    return {"message": "Smart Support backend is running ✅"}


@app.post("/ask")
def ask_question(data: Query):
    user_query = data.query.strip()
    if not user_query:
        return {"answer": "Пустой запрос"}

    chat.add_message("user", user_query)

    # Находим похожие вопросы
    results = searcher.find_similar_questions(user_query, top_k=3, min_similarity=0.5)
    if not results:
        return {"answer": "Не найдено релевантных ответов."}

    # Формируем контекст
    context = "\n\n".join([
        f"Вопрос: {r['metadata']['question']}\nОтвет: {r['metadata']['answer']}"
        for r in results
    ])

    # Формируем сообщение для Qwen
    messages = chat.get_messages([
        {
            "role": "system",
            "content": "Ты русскоязычный ассистент службы поддержки банка. Отвечай чётко и по контексту."
        },
        {
            "role": "user",
            "content": f"data:\n{context}\n\nВопрос клиента: {user_query}"
        }
    ])

    try:
        answer = get_qwen_response(API_TOKEN, messages)
        chat.add_message("assistant", answer)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Ошибка при обращении к Qwen: {str(e)}"}
