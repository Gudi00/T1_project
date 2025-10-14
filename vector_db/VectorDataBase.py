import requests
import json
from typing import List
import pandas as pd

class VectorDataBase:
    """
    Векторная база данных для семантического поиска по базе знаний банка.
    
    Основная задача: преобразовывать текстовые вопросы в числовые вектора (эмбеддинги)
    и сохранять их вместе с метаданными для последующего быстрого поиска.
    
    Используется в связке:
    - bge-m3: для создания векторных представлений текста
    - Qwen: для генерации финальных ответов на основе найденных шаблонов
    """

    def __init__(self, api_token: str):
        """
        Инициализация векторной базы данных.
        
        Args:
            api_token (str): API токен для доступа к сервису эмбеддингов Scibox
        """
        self.api_token = api_token
        self.vectors = []      # Здесь хранятся числовые вектора вопросов (эмбеддинги)
        self.metadata = []     # Здесь хранятся исходные данные: вопросы, ответы, категории
    
    def save_to_file(self, filepath: str):
        """Сохраняет векторную базу в файл"""
        data = {
            'vectors': self.vectors,
            'metadata': self.metadata
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Векторная база сохранена в {filepath}")
    
    def load_from_file(self, filepath: str):
        """Загружает векторную базу из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.vectors = data['vectors']
        self.metadata = data['metadata']
        print(f"Векторная база загружена из {filepath}")

    def get_embeddings(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Преобразует тексты в векторные представления через API модели bge-m3.
        
        Каждый текст превращается в вектор из 1024 чисел, который захватывает 
        семантическое значение текста. Похожие по смыслу тексты будут иметь 
        близкие векторные представления.
        
        Args:
            texts (List[str]): Список текстов для векторизации
            batch_size (int): Размер батча для отправки в API (оптимально 10-20)
            
        Returns:
            List[List[float]]: Список векторов (эмбеддингов) для каждого текста
            
        Пример:
            >>> texts = ["Как оформить карту?", "Что такое МСИ?"]
            >>> embeddings = get_embeddings(texts)
            >>> len(embeddings[0])  # 1024 - размерность вектора
            1024
        """
        url = "https://llm.t1v.scibox.tech/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        all_embeddings = []
        
        # Обрабатываем тексты батчами для оптимизации скорости и избежания перегрузки API
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            data = {
                "model": "bge-m3",
                "input": batch_texts
            }
            
            try:
                # Отправляем запрос к API эмбеддингов
                response = requests.post(url, headers=headers, json=data, timeout=10)
                response.raise_for_status()  # Проверяем успешность запроса
                
                # Парсим ответ и извлекаем вектора
                result = response.json()
                batch_embeddings = [item['embedding'] for item in result['data']]
                all_embeddings.extend(batch_embeddings)
                
                print(f"Обработан батч {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
            except Exception as e:
                # В случае ошибки добавляем пустые вектора для сохранения порядка данных
                print(f"Ошибка в батче {i//batch_size + 1}: {e}")
                all_embeddings.extend([[] for _ in range(len(batch_texts))])
        
        return all_embeddings

    def create_from_csv(self, csv_path: str):
        """
        Создает векторную базу знаний из CSV файла с шаблонными вопросами и ответами.
        
        Процесс:
        1. Читает CSV с банковскими вопросами и ответами
        2. Подготавливает тексты для векторизации (вопрос + категория для контекста)
        3. Получает векторные представления через bge-m3
        4. Сохраняет вектора и метаданные для последующего семантического поиска
        
        Args:
            csv_path (str): Путь к CSV файлу с базой знаний
            
        Структура CSV ожидается:
            - Пример вопроса: текстовый вопрос от клиента
            - Основная категория: категория вопроса (например, "Новые клиенты")
            - Подкатегория: подкатегория (например, "Регистрация")
            - Шаблонный ответ: готовый ответ для оператора
        """
        # Загружаем данные из CSV файла
        df = pd.read_csv(csv_path, encoding='utf-8')
        texts_to_embeddings = []  # Тексты для преобразования в вектора
        metadata_list = []         # Метаданные для каждого вопроса

        # Обрабатываем каждую строку CSV файла
        for index, row in df.iterrows():
            # Создаем обогащенный текст для векторизации: вопрос + категория
            # Это помогает модели лучше понимать контекст и различать похожие вопросы
            # из разных категорий
            text_to_embeddings = f"Вопрос: {row['Пример вопроса']} Категория: {row['Основная категория']} {row['Подкатегория']}"
            texts_to_embeddings.append(text_to_embeddings)

            # Сохраняем полные метаданные для передачи в Qwen
            metadata_list.append({
                'id': len(texts_to_embeddings) - 1,  # Уникальный идентификатор
                'question': row['Пример вопроса'],    # Оригинальный вопрос
                'answer': row['Шаблонный ответ'],     # Шаблонный ответ для оператора
                'category': row['Основная категория'], # Основная категория
                'subcategory': row['Подкатегория'],   # Подкатегория
                'priority': row['Приоритет'],         # Приоритет вопроса (высокий/средний)
                'audience': row['Целевая аудитория']  # Целевая аудитория
            })

        # Получаем векторные представления для всех подготовленных текстов
        print('Получаем эмбеддинги через bge-m3...')
        embeddings = self.get_embeddings(texts_to_embeddings)

        # Сохраняем результаты в объекте класса
        self.metadata = metadata_list
        self.vectors = embeddings

        print(f'Векторная база знаний создана! Загружено {len(self.vectors)} записей')
