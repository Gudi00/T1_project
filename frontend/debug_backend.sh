#!/bin/bash

echo "🔍 Проверка: работает ли backend на порту 8000..."
if curl -s http://localhost:8000 | grep -q "FastAPI"; then
  echo "✅ Backend отвечает на корневой маршрут"
else
  echo "❌ Backend не отвечает. Проверь, запущен ли uvicorn."
  echo "Попробуй: cd backend && uvicorn server:app --reload --port 8000"
  exit 1
fi

echo "📦 Проверка: эндпоинт /search_with_generation..."
RESPONSE=$(curl -s -X POST http://localhost:8000/search_with_generation \
  -H "Content-Type: application/json" \
  -d '{"query":"Как оформить карту?", "chat_history":[]}' | jq .)

echo "📨 Ответ от /search_with_generation:"
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q '"generated":'; then
  echo "✅ Генерация работает"
else
  echo "⚠️ Нет поля 'generated' — возможно ошибка в Qwen или в vector_db"
fi

echo "🧪 Проверка: эндпоинт /search..."
curl -s -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Как оформить карту?", "top_k":3}' | jq .

echo "📁 Проверка: есть ли vector_db.json..."
if [ -f backend/data/vector_db.json ]; then
  echo "✅ vector_db.json найден"
else
  echo "❌ vector_db.json отсутствует — нужно создать через init_vector_db"
fi

echo "📁 Проверка: есть ли kb.csv..."
if [ -f backend/data/kb.csv ]; then
  echo "✅ kb.csv найден"
else
  echo "❌ kb.csv отсутствует — без него не создаётся база"
fi

echo "🧠 Проверка: переменные окружения..."
if grep -q "LLM_API_KEY" backend/.env; then
  echo "✅ LLM_API_KEY найден в .env"
else
  echo "⚠️ LLM_API_KEY не найден — генерация может не работать"
fi

echo "🧪 Проверка: доступен ли Qwen..."
curl -s -X POST https://llm.t1v.scibox.tech/v1/chat/completions \
  -H "Authorization: Bearer sk-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen2.5-72B-Instruct-AWQ","messages":[{"role":"user","content":"Привет"}]}' | jq .

echo "✅ Проверка завершена"

