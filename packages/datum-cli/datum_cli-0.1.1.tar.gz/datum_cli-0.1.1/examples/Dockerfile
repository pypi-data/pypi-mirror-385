FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install dbt and datum
RUN pip install --no-cache-dir \
    dbt-postgres==1.8.0 \
    datum-dbt==0.1.0 \
    python-crontab==2.10.0

# Create directories
RUN mkdir -p /root/.datum/keys /root/.datum/runs

# Start cron service
RUN service cron start

# Copy projects
COPY project-1 /app/project-1
COPY project-2 /app/project-2

# Set environment
ENV PATH="/root/.local/bin:$PATH"

# Default command
CMD ["cron", "-f"]
