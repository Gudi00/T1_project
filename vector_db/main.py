from VectorDataBase import VectorDataBase
from VectorSearcher import VectorSearcher
from Qwen_model import get_qwen_response
from ChatHistory import ChatHistory
import os

from dotenv import load_dotenv
load_dotenv()

def init_vector_db(api_token: str):
    """
    Загружает или создаёт векторную базу из CSV.
    """
    vector_db = VectorDataBase(api_token=api_token)

    try:
        vector_db.load_from_file("vector_db.json")
        print("Загружена существующая векторная база.")
    except FileNotFoundError:
        print("Файл базы не найден, создаём новую...")
        vector_db.create_from_csv("kb.csv")
        vector_db.save_to_file("vector_db.json")
        print("Векторная база создана и сохранена.")

    return vector_db


def build_context(results):
    """
    Собирает контекст из найденных релевантных ответов.
    """
    return "\n\n".join([
        f"Вопрос: {r['metadata']['question']}\nОтвет: {r['metadata']['answer']}"
        for r in results
    ])


def build_messages(chat, context, user_query):
    """
    Формирует список сообщений для Qwen.
    """
    system_prompt = {
        "role": "system",
        "content": """
        Ты русскоязычный ассистент службы поддержки банка.
        Отвечай вежливо, коротко и понятно. 
        Используй только факты из переменной data (контекста), 
        не придумывай ничего нового.
        История чата помогает понять, что пользователь уже спрашивал.
        Основывай текущий ответ только на текущем вопросе и контексте.
        """
    }

    user_prompt = {
        "role": "user",
        "content": f"data:\n{context}\n\nВопрос клиента: {user_query}"
    }

    return chat.get_messages([system_prompt, user_prompt])


if __name__ == "__main__":
    API_TOKEN = os.getenv('API_TOKEN')

    # Инициализация базы и чата
    vector_db = init_vector_db(API_TOKEN)
    searcher = VectorSearcher(vector_db, API_TOKEN)
    chat = ChatHistory()

    print("\nSmart Support Assistant (Qwen + VectorDB)")
    print("Введите 'exit' для выхода.\n")

    while True:
        user_query = input("Пользователь: ").strip()
        if user_query.lower() in ["exit", "quit", "выход"]:
            print("Завершение работы. История сохранена.")
            break

        # Добавляем запрос в историю
        chat.add_message("user", user_query)

        # Находим похожие вопросы
        results = searcher.find_similar_questions(user_query, top_k=3, min_similarity=0.5)
        if not results:
            print("Не найдено релевантных ответов.")
            continue

        # Формируем контекст и сообщения
        context = build_context(results)
        messages = build_messages(chat, context, user_query)

        # Получаем ответ Qwen
        try:
            answer = get_qwen_response(API_TOKEN, messages)
        except Exception as e:
            print(f"Ошибка при обращении к Qwen: {e}")
            continue

        # Сохраняем ответ в историю
        chat.add_message("assistant", answer)

        # Выводим ответ
        print(f"\nQwen: {answer}\n")
