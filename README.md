# 🧠 T1_project

## Коротко
Прототип (PoC) — приложение, которое решает конкретную задачу (см. презентацию в репозитории).  
Реализовано как **backend + frontend**; основная логика — на Python, часть оптимизирована с помощью Cython/C.  
Цель — показать работоспособное решение за хакатон: воспроизводимый поток от данных до результата и удобная демонстрация.

---

## Elevator pitch
Практичный прототип, который автоматизирует ключевой процесс/решение в выбранной доменной области.  
Проект сделан так, чтобы быстро продемонстрировать ценность:  
**measurable result → объяснимые выводы → простая демонстрация.**

---

## 📂 Краткое содержание репозитория
- `.idea/` — настройки IDE (локально)  
- `Makefile` — набор целевых команд (bootstrap / run / demo)  
- `README.md` — этот файл  
- `backend/` — серверная часть (основная логика, API)  
- `frontend/` — интерфейс для демонстрации (веб-приложение)  
- `venv/` — виртуальное окружение (локальное)  
- `Презентация Microsoft PowerPoint (4).pptx` — презентация проекта

---

## ❗️Проблема
Существующие инструменты недостаточно быстры и неудобны для целевого сценария, что приводит к потере времени и снижению эффективности.

---

## 💡 Решение
Модульный прототип:  
входные данные → предобработка → ядро (алгоритм/модель) → вывод/визуализация.  
Backend отвечает за вычисления, frontend — за удобную демонстрацию UX.

---

## 🚀 Ключевые достижения
- Полный end-to-end поток: от запроса до ответа  
- Интерактивный веб-интерфейс  
- Оптимизация вычислений (векторный поиск + API-модель)  
- Готовая презентация и документация  

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

## 🧭 Структура проекта

- backend/ — сервер и API (FastAPI, векторный поиск, интеграция с моделью)
- frontend/ — интерфейс (React + Tailwind)
- Makefile — команды для сборки и запуска
- presentation.pptx — слайды проекта

## 📊 Метрики

- Время отклика: ~1.5 сек
- Средняя точность совпадений: 0.8+
- Полная интерактивность интерфейса
