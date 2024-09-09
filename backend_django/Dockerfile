FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN apt-get update && apt-get install -y git gunicorn3 && rm -rf /var/lib/apt/lists/*
WORKDIR /webapp
COPY backend_django/requirements.txt requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt
COPY backend_django/ .
