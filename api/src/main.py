import os
from uuid import uuid4
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg

import redis
from rq import Queue
from rq.job import Job


# с помощью переменных окружения убрать дублирование информации
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
CONNECTION_STR = f"dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} host={POSTGRES_HOST} port={POSTGRES_PORT}"

# Подключение к Redis
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
q = Queue('default', connection=r)  # Создание очереди сообщений в Redis

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods = ["*"], allow_headers=["*"])

def background_task():
    return "Test task"

@app.post("/queue/")
async def add_to_queue():
    try:
        job = q.enqueue(background_task)  # Add task to Redis queue
        print(f"Job {job.id} added to queue")  # Print the job ID to confirm
        return {"message": "Message added to queue", "job_id": job.id}
    except Exception as e:
        print(f"Error adding task to queue: {e}")
        return {"error": str(e)}

@app.get("/queue/")
async def list_all_jobs():
    """Возвращает список всех задач в очереди."""
    jobs = []
    for job in q.jobs:
        jobs.append({
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result,  # Результат выполнения задачи (если она уже завершена)
            "meta": job.meta  # Кастомные данные задачи
        })
    return {"jobs": jobs}

# Новый эндпоинт для получения статуса задачи по ID
@app.get("/queue/{job_id}")
async def get_job_status(job_id: str):
    job = Job.fetch(job_id, connection=r)  # Получаем задачу по ID
    if job:
        return {"job_id": job.id, "status": job.get_status()}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

# Новый эндпоинт для обновления статуса задачи
@app.put("/queue/{job_id}")
async def update_job_status(job_id: str, status: str):
    try:
        job = Job.fetch(job_id, connection=r)  # Получаем задачу
        if job:
            valid_statuses = ["queued", "started", "failed", "finished"]
            
            if status in valid_statuses:
                job.set_status(status)  # Обновляем системный статус
            else:
                job.meta["status"] = status  # Обновляем кастомный статус
                job.save_meta()
            
            return {"job_id": job.id, "updated_status": status}
        return {"error": "Job not found"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/queue/{job_id}")
async def delete_job(job_id: str):
    """Удаляет задачу из очереди по job_id."""
    try:
        job = Job.fetch(job_id, connection=r)  # Получаем задачу по ID
        if job:
            job.delete()  # Удаляем задачу из Redis
            return {"message": f"Job {job_id} has been deleted"}
        else:
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
