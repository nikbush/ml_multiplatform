from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World2"}

@app.get("/table/add")
async def tabel_add():
    return {"message": "Adding new table"}
