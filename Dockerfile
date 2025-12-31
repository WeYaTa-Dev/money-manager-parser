# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port (Cloud Run will inject PORT env var)
EXPOSE 8080

# Run with gunicorn (already in requirements.txt)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
