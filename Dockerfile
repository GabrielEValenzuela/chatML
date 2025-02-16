# syntax=docker/dockerfile:1

##################################################
# 1️⃣ Builder Stage
##################################################
FROM python:3.10-slim AS builder

# Create a virtual environment path
ENV VENV_PATH=/venv
RUN python -m venv $VENV_PATH

# Activate venv by default
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app

# Install system dependencies needed only for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies in the venv
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

##################################################
# 2️⃣ Final Stage
##################################################
FROM python:3.10-slim AS final

# Create a user to avoid running as root
RUN useradd -m appuser

# Copy the virtual environment from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# Copy the application source code from the builder
COPY --from=builder /app /app

# Expose the application port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Run Gunicorn + Uvicorn
CMD ["gunicorn", "src.api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
