FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ python3-dev libffi-dev

COPY ./router/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./router /app/router

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "router.main:app", "--host", "0.0.0.0", "--port", "8000"]
