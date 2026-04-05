FROM python:3.11-slim

WORKDIR /app

COPY ./src/auth/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/auth /app/src/auth
COPY ./shared /app/src/shared

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8000"]
