from typing import List
from VectorDataBase import VectorDataBase
import numpy as np

class VectorSearcher:
    """
    Класс для семантического поиска по векторной базе знаний.
    
    Использует косинусное сходство для нахождения наиболее релевантных
    шаблонных ответов на основе пользовательского запроса.
    """

    def __init__(self, vector_db: VectorDataBase, API: str):
        """
        Args:
            vector_db: Объект VectorDataBase с эмбеддингами и метаданными
            api_token: API токен для bge-m3
        """
        self.vector_db = vector_db
        self.api_token = API
        
    def get_query_embedding(self, user_query: str) -> List[float]:
        """
        Преобразует запрос пользователя в векторное представление через bge-m3.
    
        Args:
            user_query (str): Вопрос от пользователя
        
        Returns:
            List[float]: Векторное представление запроса
        """
        # Используем тот же метод, что и для создания базы
        embeddings = self.vector_db.get_embeddings([user_query])
        return embeddings[0] if embeddings else []
    
    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Вычисляет косинусное сходство между двумя векторами.
        
        Returns:
            float: Значение от 0 до 1 (1 - идентичные вектора)
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        
        a = np.array(vec_a)
        b = np.array(vec_b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def find_similar_questions(self, user_query: str, top_k: int = 3, min_similarity: float = 0.6) -> List[dict]:
        """
        Находит наиболее похожие вопросы в векторной базе знаний.
        
        Args:
            user_query (str): Запрос пользователя
            top_k (int): Количество возвращаемых результатов
            min_similarity (float): Минимальный порог схожести
            
        Returns:
            List[dict]: Список найденных шаблонов с метаданными и оценкой схожести
        """
        # 1. Преобразуем запрос пользователя в вектор
        print("Векторизуем запрос пользователя...")
        query_vector = self.get_query_embedding(user_query)
        
        if not query_vector:
            print("Не удалось получить эмбеддинг запроса")
            return []
        
        # 2. Ищем похожие вектора в базе
        print("Ищем похожие вопросы в базе знаний...")
        results = []
        
        for i, db_vector in enumerate(self.vector_db.vectors):
            if db_vector:
                similarity = self.cosine_similarity(query_vector, db_vector)
                
                if similarity >= min_similarity:
                    results.append({
                        'similarity_score': similarity,
                        'metadata': self.vector_db.metadata[i],
                        'vector_index': i
                    })
        
        # 3. Сортируем по убыванию схожести и возвращаем топ-K
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"Найдено {len(results)} релевантных результатов")
        return results[:top_k]
