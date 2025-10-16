# 🧠 T1_project 

## Краткое описание прокта

Проект из диалогового окна в браузере получает вопрос клиента, после этого происходит сравнение векторного представления запроса с векторной базой "вопросов" и векторной базой "категорий" и "подкатегорий". Лучшие совпадения отправляются пользователю в диалоговое окно браузера. После чего пользователь может начать задавать новый вопрос.

---

## 📂 Краткое содержание репозитория
- `.idea/` — настройки IDE (локально)  
- `Makefile` — набор целевых команд (bootstrap / run / demo)  
- `README.md` — этот файл  
- `backend/` — серверная часть (основная логика, API)  
- `frontend/` — интерфейс для демонстрации (веб-приложение)  
- `venv/` — виртуальное окружение (локальное)  

---

## 💡 Решение
Модульный прототип:  
входные данные → обработка → выбол лучших совпадений → вывод/визуализация.  
Backend отвечает за вычисления, frontend — за удобную демонстрацию UX.

---

## 🚀 Ключевые достижения
- Полный end-to-end поток: от запроса до ответа  
- Интерактивный веб-интерфейс  
- Оптимизация вычислений (векторный поиск + API-модель)   

---

## 🧰 Технологии
- **Основной язык:** Python  
- **Бэкенд:** FastAPI  
- **Фронтенд:** React + TailwindCSS + Axios  
- **Оптимизации:** Cython / C  
- **Сборка:** Makefile, локальное `venv`

---

## ⚡ Быстрый запуск

### 🔹 Ubuntu / Linux

```bash
# 1. Клонировать проект
git clone https://github.com/Gudi00/T1_project.git
cd T1_project

# 2. Настроить backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Запустить backend
uvicorn main:app --reload
```
Бэкенд запустится по адресу: http://127.0.0.1:8000

Открой новое окно терминала и запусти frontend:
```bash
# 4. Настроить frontend
cd ~/T1_project/frontend
npm install

# 5. Запустить frontend
npm run dev
```
Фронтенд откроется по адресу: http://localhost:5173

###🔹 Windows (PowerShell)
```powershell
# 1. Клонировать проект
git clone https://github.com/Gudi00/T1_project.git
cd T1_project

# 2. Настроить backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Запустить backend
uvicorn main:app --reload
```
Открой новое окно PowerShell и запусти frontend:
```powershell
# 4. Настроить frontend
cd frontend
npm install

# 5. Запустить frontend
npm run dev
```


## 📊 Метрики

- Время отклика: ~1.5 сек
- Средняя точность совпадений: 0.8+
- Полная интерактивность интерфейса
