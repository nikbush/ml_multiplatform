FROM python:3.12.7

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .
COPY initdb.sql .

CMD [ "fastapi", "run", "src/main.py", "--reload" ]
