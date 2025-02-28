FROM python:3.13.2-alpine

WORKDIR /app

COPY worker.py .

RUN pip install redis rq

CMD ["python", "worker.py"]
