# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Tell Flask which app to load
ENV FLASK_APP=app.py

# Expose port and run
EXPOSE 5000
CMD bash -lc "flask create-tables && gunicorn -b 0.0.0.0:5000 app:app"