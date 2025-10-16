from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import pandas as pd

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class Query(BaseModel):
    query: str

# --- Новый код: работа с категориями ------------------------

class CategoryDatabase(VectorDataBase):
    """
    Векторная база для категорий и подкатегорий.
    Ожидает CSV с колонками 'category' и 'subcategory'.
    """
    def create_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path, encoding='utf-8')
        texts, metas = [], []
        for idx, row in df.iterrows():
            text = f"Категория: {row['category']} Подкатегория: {row['subcategory']}"
            texts.append(text)
            metas.append({
                'id': idx,
                'category': row['category'],
                'subcategory': row['subcategory']
            })
        embeddings = self.get_embeddings(texts)
        self.vectors = embeddings
        self.metadata = metas

class ExtendedVectorSearcher(VectorSearcher):
    """
    Расширенный searcher: сначала ищет категорию, потом вопросы, затем комбинирует метрики.
    """
    def __init__(self, vector_db, category_db, api_token, α=0.3, β=0.7):
        super().__init__(vector_db, api_token)
        self.category_db = category_db
        self.α = α
        self.β = β

    def find_best_match(self, user_query: str, top_cats: int = 3, top_qs: int = 3, min_cat_sim: float = 0.3):
        # 1. Векторизуем запрос
        q_vec = self.get_query_embedding(user_query)
        if not q_vec:
            return None

        # 2. Поиск по категориям
        cat_sims = []
        for i, vec in enumerate(self.category_db.vectors):
            sim = self.cosine_similarity(q_vec, vec)
            if sim >= min_cat_sim:
                cat_sims.append({'sim': sim, 'meta': self.category_db.metadata[i]})
        cat_sims.sort(key=lambda x: x['sim'], reverse=True)
        cat_sims = cat_sims[:top_cats]
        if not cat_sims:
            return None

        # 3. Поиск по вопросам
        q_results = self.find_similar_questions(user_query, top_k=top_qs)

        # 4. Комбинирование
        best = {'score': -1}
        for cat in cat_sims:
            for qr in q_results:
                total = self.α * cat['sim'] + self.β * qr['similarity_score']
                if total > best['score']:
                    best = {
                        'score': total,
                        'category': cat['meta']['category'],
                        'subcategory': cat['meta']['subcategory'],
                        'question': qr['metadata']['question'],
                        'answer': qr['metadata']['answer'],
                        'question_score': qr['similarity_score'],
                        'category_score': cat['sim']
                    }
        return best

# ------------------------------------------------------------

# Инициализация векторной базы вопросов
vector_db = VectorDataBase(api_token=API_TOKEN)
try:
    vector_db.load_from_file("vector_db.json")
    print("✅ Загружена существующая векторная база вопросов.")
except FileNotFoundError:
    print("⚙️ Файл базы вопросов не найден, создаём новую...")
    vector_db.create_from_csv("kb.csv")
    vector_db.save_to_file("vector_db.json")
    print("✅ Векторная база вопросов создана и сохранена.")

# Инициализация векторной базы категорий
category_db = CategoryDatabase(api_token=API_TOKEN)
try:
    category_db.load_from_file("category_db.json")
    print("Загружена существующая векторная база категорий.")
except FileNotFoundError:
    print("Файл базы категорий не найден, создаём новую...")
    category_db.create_from_csv("categories.csv")
    category_db.save_to_file("category_db.json")
    print("Векторная база категорий создана и сохранена.")

# Создаём расширенный searcher и историю чата
searcher = ExtendedVectorSearcher(vector_db, category_db, API_TOKEN, α=0.3, β=0.7)
chat = ChatHistory()

@app.get("/")
def root():
    return {"message": "Smart Support backend is running ✅"}

@app.post("/ask")
def ask_question(data: Query):
    print(12345678)
    user_query = data.query.strip()
    if not user_query:
        return {"answer": "Пустой запрос"}

# @app.get("/ask")
# def ask_question():
#     print(12345678)
#     user_query = 'Как начать пользоваться картой More?'
#     if not user_query:
#         return {"answer": "Пустой запрос"}
    chat.add_message("user", user_query)

    # Поиск лучшего соответствия с учётом категорий
    result = searcher.find_best_match(user_query, top_cats=3, top_qs=3, min_cat_sim=0.3)
    if not result:
        return {"answer": "Не найдено релевантных ответов."}

    # Сохраняем в историю
    chat.add_message("assistant", result['answer'])

    # Возвращаем результаты
    return {
        "category": result['category'],
        "subcategory": result['subcategory'],
        "question": result['question'],
        "answer": result['answer']
    }