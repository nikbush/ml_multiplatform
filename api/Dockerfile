FROM python:3.13.2-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .
COPY initdb.sql .

CMD [ "fastapi", "run", "src/main.py", "--reload" ]
