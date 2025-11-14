# Use a small official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Prevent Python from writing .pyc files & use unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (useful for psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Default command to run the app
# If your FastAPI app is in app/main.py and variable is "app"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
