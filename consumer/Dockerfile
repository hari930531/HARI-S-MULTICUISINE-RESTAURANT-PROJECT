# Use lightweight Python 3.11 base image
FROM python:3.11-slim

# Set working directory to /app
WORKDIR /app

# Disable output buffering so event consumption logs print immediately
ENV PYTHONUNBUFFERED=1

# Copy Python requirements file
COPY requirements.txt .

# Install Kafka and MySQL client libraries cleanly
RUN pip install --no-cache-dir -r requirements.txt

# Copy Kafka payment consumer worker script
COPY consumer.py .

# Start the payment event listener script
CMD ["python", "consumer.py"]