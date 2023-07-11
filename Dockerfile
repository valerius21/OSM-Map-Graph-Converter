# Use the official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the environment variable for Redis URI
ENV REDIS_URI=${REDIS_URI}

# Install Uvicorn
RUN pip install uvicorn

# Expose the port your FastAPI app is listening on (replace 8000 with the actual port number if needed)
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
