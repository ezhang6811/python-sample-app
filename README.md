# Python Sample App with ADOT Instrumentation

A Flask-based sample application with multiple endpoints designed to demonstrate AWS Distro for OpenTelemetry (ADOT) Python instrumentation and CloudWatch telemetry.

## Features

- **Multiple Endpoints**: Organized in separate files for modularity
  - `/api/users` - User management endpoints
  - `/api/products` - Product catalog endpoints
  - `/api/error` - Intentionally failing endpoints for error tracking
  - `/api/slow` - High-latency endpoints for performance monitoring
- **Traffic Generator**: Automated script to generate continuous traffic
- **ADOT Ready**: Designed for easy instrumentation with ADOT Python
- **CloudWatch Integration**: Telemetry can be sent to AWS CloudWatch

## Project Structure

```
python-sample-app/
├── app.py                  # Main Flask application
├── endpoints/              # API endpoints (organized by functionality)
│   ├── __init__.py
│   ├── users.py           # User endpoints
│   ├── products.py        # Product endpoints
│   ├── error.py           # Error endpoints (intentional failures)
│   └── slow.py            # Slow endpoints (high latency)
├── traffic_generator.py    # Traffic generation script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Available Endpoints

### Healthy Endpoints
- `GET /` - Basic health check
- `GET /health` - Detailed health check
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get specific user
- `GET /api/users/random` - Get random user
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get specific product
- `GET /api/products/random` - Get random product

### Error Endpoints (for testing error handling)
- `GET /api/error` - Always returns 500 error
- `GET /api/error/random` - Returns random error codes (400, 401, 403, 404, 500, 503)
- `GET /api/error/exception` - Raises unhandled exception

### Slow Endpoints (for testing latency)
- `GET /api/slow` - Fixed 3-second delay
- `GET /api/slow/random` - Random 1-5 second delay
- `GET /api/slow/custom?delay=5` - Custom delay (max 10 seconds)

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ezhang6811/python-sample-app.git
cd python-sample-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will start on `http://localhost:8080`

### Running the Traffic Generator

In a separate terminal:
```bash
python traffic_generator.py
```

Or specify a custom URL:
```bash
python traffic_generator.py http://your-server:8080
```

## AWS Deployment with ADOT Instrumentation

### Option 1: EC2 Deployment

#### Step 1: Launch EC2 Instance

1. Launch an Amazon Linux 2023 or Ubuntu EC2 instance
2. Instance type: t2.micro or larger
3. Security group: Allow inbound traffic on port 8080
4. Attach an IAM role with permissions:
   - `CloudWatchAgentServerPolicy`
   - `AWSXRayDaemonWriteAccess`

#### Step 2: Install Dependencies

SSH into your EC2 instance and run:

```bash
# Update system
sudo yum update -y  # For Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install Python and pip
sudo yum install python3 python3-pip git -y  # For Amazon Linux
# OR
sudo apt install python3 python3-pip git -y  # For Ubuntu

# Clone the repository
git clone https://github.com/ezhang6811/python-sample-app.git
cd python-sample-app

# Install application dependencies
pip3 install -r requirements.txt
```

#### Step 3: Install ADOT Python Instrumentation

```bash
# Install OpenTelemetry packages
pip3 install opentelemetry-distro
pip3 install opentelemetry-exporter-otlp
pip3 install opentelemetry-instrumentation-flask

# Auto-instrument Flask
opentelemetry-bootstrap -a install
```

#### Step 4: Install and Configure ADOT Collector

```bash
# Download ADOT Collector
wget https://aws-otel-collector.s3.amazonaws.com/amazon_linux/amd64/latest/aws-otel-collector.rpm
sudo rpm -Uvh aws-otel-collector.rpm

# Create configuration file
sudo tee /opt/aws/aws-otel-collector/etc/config.yaml > /dev/null <<EOF
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s

exporters:
  awsxray:
  awsemf:
    namespace: PythonSampleApp
    log_group_name: '/aws/application/python-sample-app'
    region: us-east-1  # Change to your region

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [awsxray]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [awsemf]
EOF

# Start ADOT Collector
sudo systemctl start aws-otel-collector
sudo systemctl enable aws-otel-collector
```

#### Step 5: Run Application with ADOT

```bash
# Set environment variables
export OTEL_SERVICE_NAME=python-sample-app
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

# Run with auto-instrumentation
opentelemetry-instrument python3 app.py
```

#### Step 6: Run Traffic Generator

In a separate SSH session:
```bash
cd python-sample-app
python3 traffic_generator.py http://localhost:8080
```

### Option 2: EKS Deployment

#### Step 1: Create EKS Cluster

```bash
# Install eksctl if not already installed
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name python-sample-app \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
```

#### Step 2: Install ADOT Operator

```bash
# Add cert-manager (prerequisite)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Install ADOT Operator
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

#### Step 3: Create Docker Image

```bash
# Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ADOT dependencies
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp opentelemetry-instrumentation-flask
RUN opentelemetry-bootstrap -a install

COPY . .

EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "app.py"]
EOF

# Build and push to ECR
# First, get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=us-east-1  # Change to your preferred region

# Create ECR repository
aws ecr create-repository --repository-name python-sample-app --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push image
docker build -t python-sample-app .
docker tag python-sample-app:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/python-sample-app:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/python-sample-app:latest
```

#### Step 4: Deploy ADOT Collector

```bash
# Create collector configuration
cat > adot-collector.yaml <<EOF
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: adot-collector
  namespace: default
spec:
  mode: deployment
  serviceAccount: adot-collector
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    
    processors:
      batch:
        timeout: 10s
    
    exporters:
      awsxray:
        region: us-east-1
      awsemf:
        namespace: PythonSampleApp
        log_group_name: '/aws/containerinsights/python-sample-app/application'
        region: us-east-1
    
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [awsxray]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [awsemf]
EOF

kubectl apply -f adot-collector.yaml
```

#### Step 5: Deploy Application

```bash
# Use the AWS_ACCOUNT_ID and AWS_REGION variables from Step 3
# Create deployment
cat > deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-sample-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: python-sample-app
  template:
    metadata:
      labels:
        app: python-sample-app
    spec:
      containers:
      - name: app
        image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/python-sample-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: OTEL_SERVICE_NAME
          value: "python-sample-app"
        - name: OTEL_TRACES_EXPORTER
          value: "otlp"
        - name: OTEL_METRICS_EXPORTER
          value: "otlp"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://adot-collector-collector:4318"
        - name: OTEL_EXPORTER_OTLP_PROTOCOL
          value: "http/protobuf"
        - name: OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
          value: "true"
---
apiVersion: v1
kind: Service
metadata:
  name: python-sample-app
  namespace: default
spec:
  type: LoadBalancer
  selector:
    app: python-sample-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
EOF

kubectl apply -f deployment.yaml
```

#### Step 6: Get Service URL and Generate Traffic

```bash
# Get LoadBalancer URL
export APP_URL=$(kubectl get svc python-sample-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "Application URL: http://$APP_URL"

# Run traffic generator locally pointing to EKS
python3 traffic_generator.py http://$APP_URL
```

## Viewing Telemetry in CloudWatch

### CloudWatch Logs
1. Go to AWS CloudWatch Console
2. Navigate to Log Groups
3. Find `/aws/application/python-sample-app` (EC2) or `/aws/containerinsights/python-sample-app/application` (EKS)

### CloudWatch Metrics
1. Go to CloudWatch Metrics
2. Look for namespace: `PythonSampleApp`
3. View metrics like request count, latency, errors

### X-Ray Traces
1. Go to AWS X-Ray Console
2. View Service Map to see application topology
3. View Traces to see individual request traces
4. Analyze trace details for slow requests and errors

### Key Metrics to Observe
- **Request Rate**: Total requests per minute
- **Error Rate**: Failed requests (especially from `/api/error/*`)
- **Latency**: Response times (especially from `/api/slow/*`)
- **HTTP Status Codes**: Distribution of 2xx, 4xx, 5xx responses

## Troubleshooting

### Application not starting
- Check Python version: `python3 --version`
- Verify dependencies installed: `pip3 list`
- Check port 8080 is not in use: `lsof -i :8080`

### No telemetry in CloudWatch
- Verify ADOT Collector is running: `sudo systemctl status aws-otel-collector` (EC2)
- Check IAM permissions for CloudWatch and X-Ray
- Review collector logs: `sudo journalctl -u aws-otel-collector -f`
- Verify environment variables are set correctly

### Traffic generator not connecting
- Verify application is running and accessible
- Check security group allows inbound traffic on port 8080
- Verify URL is correct (including http:// prefix)

## License

MIT