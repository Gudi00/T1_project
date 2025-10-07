import os
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma
import structlog

logger = structlog.get_logger()

def build_kb(csv_path='kb.csv', json_path='dynamic.json', persist_dir='./chroma_db'):
    """
    Загружает KB из CSV, сплитит на чанки, эмбеддит и сохраняет в Chroma.
    Также загружает динамический JSON.
    """
    try:
        # Загрузка CSV
        loader = CSVLoader(file_path=csv_path, encoding='utf-8')
        documents = loader.load()
        logger.info(f"Загружено {len(documents)} документов из CSV.")

        # Сплит на чанки
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(documents)
        logger.info(f"Создано {len(splits)} чанков.")

        # Эмбеддинги (обновлённая многоязычная модель для RU)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

        # Сохранение в Chroma
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_dir)
        logger.info("KB сохранена в Chroma.")

        # Загрузка динамического JSON (placeholder, реализуйте парсинг по нужде)
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            dynamic_data = json.load(f)
        logger.info("Динамический JSON загружен.")

        return vectorstore, dynamic_data
    except Exception as e:
        logger.error(f"Ошибка при построении KB: {e}")
        raise

if __name__ == "__main__":
    build_kb()