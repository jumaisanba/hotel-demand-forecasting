FROM python:3.13-slim

WORKDIR /app

COPY ./src/router/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/router /app/src/router
COPY ./shared /app/src/shared

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "router.main:app", "--host", "0.0.0.0", "--port", "8000"]
