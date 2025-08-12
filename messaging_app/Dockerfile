# messaging_app/Dockerfile

# Base image
FROM python:3.10

# Set work directory in container
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# Prevent Python buffering stdout/stderr
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . /app/

# Expose Django's default port
EXPOSE 8000

# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

