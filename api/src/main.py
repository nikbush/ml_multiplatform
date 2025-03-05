import os
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import redis
from rq import Queue

from pydantic import BaseModel


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
    sleep_time: int = 60

@app.post("/tasks")
async def create_task(task: Task):
    task_id = str(uuid.uuid4())
    task_key = f"task:{task_id}"
    print(f"Job {task_id} added to queue")
    task_data = {"sleep_time": task.sleep_time, "status": "Queued"}
    r.hset(task_key, mapping=task_data)
    r.lpush("default", task_id)
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task_key = f"task:{task_id}"
    task = r.hgetall(task_key)
    if not task:
        raise HTTPException(status_code=404) # type: ignore
    return task
