FROM python:3.12-slim

# Prevent python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and dbt project
COPY . .

# Default port for Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default environment configuration
ENV TALENTFLOW_MODE=local
ENV TALENTFLOW_DATA_DIR=/app/data

# Run Streamlit dashboard
ENTRYPOINT ["streamlit", "run", "talentflow/dashboards/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
