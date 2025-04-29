from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import json
from fastapi import FastAPI

# Загрузка .env файла
load_dotenv()

# Together API
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Файл для хранения отзывов
REVIEWS_FILE = "reviews.json"

# Создание приложения
app = FastAPI()

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можешь сюда поставить конкретный домен вместо '*'
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели запросов
class ReviewInput(BaseModel):
    review: str

class ReviewsResponse(BaseModel):
    results: list[dict]

# Хелпер для загрузки и сохранения отзывов
def load_reviews():
    if not os.path.exists(REVIEWS_FILE):
        return []
    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_review(review_text):
    reviews = load_reviews()
    reviews.append(review_text)
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

# 1. Эндпоинт для добавления нового отзыва
@app.post("/add-review")
async def add_review(request: ReviewInput):
    try:
        save_review(request.review)
        return {"message": "Отзыв успешно сохранен."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-reviews")
async def get_reviews():
    reviews = load_reviews()
    return {"reviews": reviews}
# 2. Эндпоинт для классификации всех сохраненных отзывов
@app.get("/classify-reviews", response_model=ReviewsResponse)
async def classify_reviews():
    reviews = load_reviews()
    if not reviews:
        raise HTTPException(status_code=404, detail="Нет сохраненных отзывов.")

    results = []

    for review in reviews:
        try:
            payload = {
                "model": MODEL_ID,
                "messages": [
                    {"role": "system", "content": "Ты помощник по анализу отзывов. Классифицируй отзыв как 'Positive' или 'Negative'. Пиши только на русском."},
                    {"role": "user", "content": f"Отзыв: \"{review}\". Какой это отзыв?"}
                ],
                "temperature": 0.0,
                "top_p": 0.7,
                "max_tokens": 50
            }

            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            classification = data["choices"][0]["message"]["content"].strip()

            results.append({"review": review, "classification": classification})

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return ReviewsResponse(results=results)