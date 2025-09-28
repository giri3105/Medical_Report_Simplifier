# Use a specific, slim Python version for a reproducible and small image
FROM python:3.12.3-slim

# Set the working directory inside the container
WORKDIR /app

# Set environment variables
# Prevents Python from buffering logs, ensuring they appear immediately
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential
# Sets a dedicated, writable cache directory for Hugging Face models to prevent permission errors
ENV HF_HOME=/app/cache

# Create and set permissions for the cache directory
RUN mkdir -p $HF_HOME && chmod -R 777 /app/cache

# Copy only the requirements file first to leverage Docker's layer caching
# This makes subsequent builds much faster if your dependencies don't change.
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
# This assumes your code (main.py, model.py, etc.) is in a folder named 'app'
COPY ./app .

# Expose the port that the app runs on
EXPOSE 8000

# The command to run your FastAPI application when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]