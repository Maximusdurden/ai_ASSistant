# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of Cortex's brain into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application (notice host is 0.0.0.0 to allow external access)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]