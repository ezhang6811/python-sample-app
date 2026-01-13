FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ADOT dependencies
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp opentelemetry-instrumentation-flask
RUN opentelemetry-bootstrap -a install

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run with OpenTelemetry auto-instrumentation
CMD ["opentelemetry-instrument", "python", "app.py"]
