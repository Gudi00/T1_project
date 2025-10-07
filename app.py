import os
import time
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_redis import FlaskRedis
import telebot
import structlog
from kb_loader import build_kb
from models import load_models
from intent import detect_intent
from chain import create_chain
from redis import Redis
from langchain.memory import ConversationSummaryMemory

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    REDIS_URL=os.getenv('REDIS_URL')
)
jwt = JWTManager(app)
socketio = SocketIO(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])
redis_client = FlaskRedis(app)

# Telegram
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Logging
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()

# Startup
vectorstore, dynamic_data = build_kb()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
tokenizer, model, zero_shot, kw_model = load_models()
run_chain, memory_template = create_chain(model, tokenizer, retriever, dynamic_data)

# Per-user memory in Redis (dict of user_id: memory_json)
def get_user_memory(user_id):
    mem_json = redis_client.get(f"memory_{user_id}")
    if mem_json:
        memory = ConversationSummaryMemory.from_dict(json.loads(mem_json))
    else:
        memory = ConversationSummaryMemory(llm=model, max_token_limit=1500)
    return memory

def save_user_memory(user_id, memory):
    redis_client.set(f"memory_{user_id}", json.dumps(memory.to_dict()))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Placeholder auth
    access_token = create_access_token(identity=request.json['username'])
    return jsonify(access_token=access_token)

@socketio.on('connect')
@jwt_required()
def handle_connect():
    user_id = request.sid  # Или из JWT
    emit('connected', {'data': 'Connected'})
    logger.info(f"User connected: {user_id}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    logger.info(f"User disconnected: {user_id}")

@socketio.on('message')
@jwt_required()
@limiter.limit("10 per minute")
def handle_message(data):
    start_time = time.time()
    user_id = request.sid
    query = data['message']
    try:
        memory = get_user_memory(user_id)
        history = memory.buffer

        # Intent
        intent, keywords = detect_intent(query, history, zero_shot, kw_model)

        if intent == "приветствие":
            response = "Привет! Помогу с нашим облаком."
        elif intent == "вызов администратора":
            summary = memory.buffer[:500]  # Short history
            bot.send_message(ADMIN_CHAT_ID, f"Эскалация: user_id={user_id}, query={query}, history={summary}")
            emit('popup', {'message': 'Админ подключён!'})  # JS popup
            response = "Администратор уведомлён и скоро подключится."
        else:  # рекомендация
            enhanced_query = f"{query} (ключевые слова: {keywords})"
            result = run_chain(enhanced_query, history)
            response = result['answer']

        # Update memory
        memory.save_context({"input": query}, {"output": response})
        if len(memory.buffer.split('\n')) > 5:  # Summarize if >5 turns
            memory.summarize()  # Использует Saiga для summarize
        save_user_memory(user_id, memory)

        emit('response', {'message': response})
        latency = time.time() - start_time
        logger.info(f"Обработан запрос: intent={intent}, latency={latency:.2f}s")
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        emit('response', {'message': "Извините, произошла ошибка. Попробуйте позже."})

if __name__ == '__main__':
    socketio.run(app, debug=True)