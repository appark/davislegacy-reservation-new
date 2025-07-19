# Use official Python image
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the app
CMD ["gunicorn", "demo2.wsgi:application", "--bind", "0.0.0.0:3001"]

