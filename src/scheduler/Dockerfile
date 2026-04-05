FROM python:3.13-slim

WORKDIR /app

COPY ./src/scheduler/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scheduler /app/src/scheduler
COPY ./shared /app/src/shared

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "scheduler.main:app", "--host", "0.0.0.0", "--port", "8000"]
