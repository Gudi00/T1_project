from VectorDataBase import VectorDataBase
from VectorSearcher import VectorSearcher

if __name__ == "__main__":
    API_TOKEN = "sk-eK2RKx7syQLko5qdKbvcLQ"
    
    # Загружаем существующую базу (РЕКОМЕНДУЕТСЯ)
    vector_db = VectorDataBase(api_token=API_TOKEN)
    
    try:
        # Пытаемся загрузить сохраненную базу
        vector_db.load_from_file('vector_db.json')
        print("Загружена существующая векторная база")
    except FileNotFoundError:
        # Если файла нет - создаем новую базу
        print("Создаем новую векторную базу...")
        vector_db.create_from_csv('kb.csv')
        vector_db.save_to_file('vector_db.json')  # Сохраняем для будущего использования
    
    # Создаем поисковую систему
    searcher = VectorSearcher(vector_db, API_TOKEN)
    
    query = 'Как получить карту Форсаж?'
    results = searcher.find_similar_questions(query, top_k=3, min_similarity=0.5)
    
    # Выводим красивые результаты
    for i, result in enumerate(results):
        print(f"\n{i+1}. Схожесть: {result['similarity_score']:.3f}")
        print(f"Категория: {result['metadata']['category']}")
        print(f"Вопрос: {result['metadata']['question']}")
        print(f"Ответ: {result['metadata']['answer'][:100]}...")