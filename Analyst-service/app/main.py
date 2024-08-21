import requests
import redis
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

USER_SERVICE_URL = "http://localhost:8000/users/"
POST_SERVICE_URL = "http://localhost:8001/posts/"

r = redis.Redis(host='localhost', port=6379, db=0)

app = FastAPI()

def analyze_data():
    try:
        # Отримання всіх користувачів
        users_response = requests.get(USER_SERVICE_URL)
        users = users_response.json()

        user_post_count = {}

        # Для кожного користувача отримати кількість постів
        for user in users:
            user_id = user['id']
            posts_response = requests.get(f"{POST_SERVICE_URL}?user_id={user_id}")
            posts = posts_response.json()
            user_post_count[user_id] = len(posts)

            # Збереження результатів у Redis
            r.set(str(user_id), user_post_count[user_id])

        print(f"Analyst Service: Updated analytics for {len(users)} users.")
    except Exception as e:
        print(f"Analyst Service: Error occurred during data analysis: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(analyze_data, 'interval', minutes=10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    analyze_data()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Analyst service is running"}
