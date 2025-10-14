from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/classify")
def classify_route(q: Query):
    return {"category": "Оплата", "score": 0.95}

@app.post("/recommend")
def recommend_route(q: Query):
    return {
        "category": "Оплата",
        "score": 0.95,
        "recommendations": [
            ["Проверьте, списаны ли средства", 0.92],
            ["Отправьте номер заказа", 0.89]
        ]
    }
