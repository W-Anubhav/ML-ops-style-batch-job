# Use the official Python 3.9 slim image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code and data
COPY run.py .
COPY config.yaml .
COPY data.csv .

# Default command to run the script
# The script takes --input, --config, --output, and --log-file
# Note: data.csv must exist in the container or be mounted
CMD ["python", "run.py", "--input", "data.csv", "--config", "config.yaml", "--output", "metrics.json", "--log-file", "run.log"]
