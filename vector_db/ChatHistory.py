import json
import os

class ChatHistory:
    """
    Класс для хранения истории чата (пользователь ↔ ассистент).
    История сохраняется в файл JSON и автоматически подгружается при запуске.
    """

    def __init__(self, filepath: str = "chat_history.json", max_length: int = 20):
        self.filepath = filepath
        self.max_length = max_length
        self.history = self.load_history()

    def load_history(self):
        """Загружает историю из JSON файла, если он существует"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Ошибка при чтении истории — создаём новую.")
        return []

    def save_history(self):
        """Сохраняет историю в JSON файл"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.history[-self.max_length:], f, ensure_ascii=False, indent=2)

    def add_message(self, role: str, content: str):
        """Добавляет сообщение и сохраняет"""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_length:
            self.history.pop(0)
        self.save_history()

    def get_messages(self, extra_messages=None):
        """Возвращает список сообщений с учётом системных/дополнительных"""
        messages = []
        if extra_messages:
            messages.extend(extra_messages)
        messages.extend(self.history)
        return messages

    def clear(self):
        """Очищает историю чата"""
        self.history = []
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        print("История чата очищена.")
