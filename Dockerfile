FROM python:3.11

COPY /app /home/app

WORKDIR /home/app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}" ]