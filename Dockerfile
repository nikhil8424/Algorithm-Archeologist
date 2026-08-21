FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

ENV PYTHONPATH=/app
EXPOSE 3000

# Default command: launch Streamlit interface
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=3000", "--server.address=0.0.0.0"]
