from fastapi import FastAPI
import psycopg

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World2"}

@app.get("/table/list")
async def table_list():
    res = []

    # Connect to an existing database
    with psycopg.connect("dbname=test user=admin password=admin host=db port=5432") as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:

            # Execute a command: this creates a new table
            cur.execute("""
                CREATE TABLE test (
                    id serial PRIMARY KEY,
                    num integer,
                    data text)
                """)

            # Pass data to fill a query placeholders and let Psycopg perform
            # the correct conversion (no SQL injections!)
            cur.execute(
                "INSERT INTO test (num, data) VALUES (%s, %s)",
                (100, "abc'def"))

            # Query the database and obtain data as Python objects.
            cur.execute("SELECT * FROM test")
            # cur.fetchone()
            # will return (1, 100, "abc'def")

            # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
            # of several records, or even iterate on the cursor
            for record in cur:
                res.append(record)

            # Make the changes to the database persistent
            conn.commit()
    return res

@app.get("/table/add")
async def table_add():
    return {"message": "Adding new table"}
