FROM python:3.11.4-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get upgrade -y

WORKDIR /app

COPY requirements.txt .
COPY requirements.dev.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt -r requirements.dev.txt

COPY . .
COPY .env.example .env
