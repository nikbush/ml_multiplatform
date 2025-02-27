import os
import uuid
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg

import redis
from rq import Queue
from rq.job import Job

from pydantic import BaseModel


# с помощью переменных окружения убрать дублирование информации
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
CONNECTION_STR = f"dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} host={POSTGRES_HOST} port={POSTGRES_PORT}"

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
q = Queue('default', connection=r)  # Create a Message Queue in Redis

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods = ["*"], allow_headers=["*"])

class Task(BaseModel):
    sleep_time: int

@app.post("/tasks")
async def create_task(task: Task):
    task_id = str(uuid.uuid4())
    task_key = f"task:{task_id}"
    print(f"Job {task_id} added to queue")
    task_data = {"sleep_time": 10, "status": "queued"}
    r.hset(task_key, mapping=task_data)
    r.lpush("default", task_id)


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task_key = f"task:{task_id}"
    task = r.hgetall(task_key)
    if not task:
        raise HTTPException(status_code=404)
    return task
