# syntax=docker/dockerfile:1

FROM python:3.10-slim AS base

# Prevent Python from writing .pyc files, and force stdout/stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps needed (e.g. gcc) if you run into build issues
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential iputils-ping neovim &&
    rm -rf /var/lib/apt/lists/*

# Copy in requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip upgrade && pip install --no-cache-dir -r requirements.txt

# Copy your entire project
COPY . .

# Expose the application port
EXPOSE 8000

# Gunicorn + Uvicorn workers for concurrency
# Adjust `-w 4` (number of workers) based on CPU cores
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
