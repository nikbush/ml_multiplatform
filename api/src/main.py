import os

from fastapi import FastAPI
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

@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/table/init")
async def table_init():
    with open("initdb.sql") as file:
        content = file.read()

    with psycopg.connect(CONNECTION_STR) as conn:
        with conn.cursor() as cur:
            cur.execute(content)

@app.put("/table/insert")
async def table_insert(name: str):
    with psycopg.connect(CONNECTION_STR) as conn:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO example (name) VALUES ('{name}')")


@app.delete("/table/delete")
async def table_delete(name: str):
    with psycopg.connect(CONNECTION_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM example WHERE name = %s", (name,))


@app.get("/table/list")
async def table_list():
    res = []

    with psycopg.connect(CONNECTION_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM example")
            for record in cur:
                res.append(record)
    return res


@app.delete("/table/delete_tables")
async def delete_tables():
    with psycopg.connect(CONNECTION_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public';
                """)
            tables = cur.fetchall()
            for table in tables:
                    cur.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE;")

            conn.commit()


@app.get("/table/add")
async def table_add():
    return {"message": "Adding new table"}


# Новый эндпоинт для добавления сообщения в очередь
@app.post("/queue/add")
async def add_to_queue(message: str):
    job = q.enqueue(print_message, message)  # Добавляем задачу в очередь
    return {"message": "Message added to queue", "job_id": job.id}

# Новый эндпоинт для получения статуса задачи по ID
@app.get("/queue/status/{job_id}")
async def get_job_status(job_id: str):
    job = Job.fetch(job_id, connection=r)  # Получаем задачу по ID
    if job:
        return {"job_id": job.id, "status": job.get_status()}
    return {"error": "Job not found"}

# Новый эндпоинт для обновления статуса задачи
@app.put("/queue/update_status/{job_id}")
async def update_job_status(job_id: str, status: str):
    job = Job.fetch(job_id, connection=r)
    if job:
        # Для демонстрации мы просто обновляем метку "meta" с новым статусом
        job.meta["status"] = status
        job.save_meta()  # Сохраняем изменения
        return {"job_id": job.id, "updated_status": status}
    return {"error": "Job not found"}

# Функция, которая будет выполнять задачу (например, печать сообщения)
def print_message(message: str):
    print(f"Message from queue: {message}")
