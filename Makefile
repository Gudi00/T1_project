init-env:
\tcp backend/.env.example backend/.env || echo ".env уже существует"

run-backend:
\tcd backend && source .venv/bin/activate && uvicorn app:app --reload --host 0.0.0.0 --port 8000
