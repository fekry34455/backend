# ==============================================================================
# Stage 1: Builder - Install dependencies and prepare the application
# ==============================================================================
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies required for compiling Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for the build stage
WORKDIR /app

# Copy and install Python dependencies
COPY ./requirements.txt /app/requirements.txt

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Install Python packages (no cache to reduce image size)
RUN pip install --no-cache-dir -r /app/requirements.txt

# ==============================================================================
# Stage 2: Runtime - Create minimal production image
# ==============================================================================
FROM python:3.12-slim AS runtime

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group for security
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# Set working directory
WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/

# Change ownership of application files to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user for security
USER appuser

# Expose port 8000 for the application
EXPOSE 8000

# Run gunicorn server with optimized settings
# - reddit_api.wsgi:application: WSGI application entry point
# - --bind 0.0.0.0:8000: Listen on all interfaces, port 8000
# - --timeout 300: Request timeout in seconds
# - --workers 2: Number of worker processes
CMD ["gunicorn", "reddit_api.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "300", "--workers", "2"]