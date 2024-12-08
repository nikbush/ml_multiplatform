FROM python:3.12.7

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY initdb.sql .

CMD [ "fastapi", "run", "main.py" ]
