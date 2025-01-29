import os

from fastapi import FastAPI
import psycopg

# с помощью переменных окружения убрать дублирование информации
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
CONNECTION_STR = f"dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} host={POSTGRES_HOST} port={POSTGRES_PORT}"

app = FastAPI()


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
