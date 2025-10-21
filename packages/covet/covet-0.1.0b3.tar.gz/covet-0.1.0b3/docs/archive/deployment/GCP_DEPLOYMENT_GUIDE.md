# GCP Deployment Guide for CovetPy

This guide covers deploying CovetPy applications to Google Cloud Platform using various deployment strategies.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Cloud Run Deployment](#cloud-run-deployment)
3. [GKE Deployment](#gke-deployment)
4. [Compute Engine Deployment](#compute-engine-deployment)
5. [App Engine Deployment](#app-engine-deployment)
6. [Cloud Functions Deployment](#cloud-functions-deployment)
7. [Infrastructure as Code](#infrastructure-as-code)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Security Best Practices](#security-best-practices)
10. [Cost Optimization](#cost-optimization)

## Prerequisites

### Required Tools
```bash
# Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Docker
# Install Docker based on your OS

# Terraform (for IaC)
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# kubectl (for GKE)
gcloud components install kubectl
```

### GCP Project Setup
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    container.googleapis.com \
    sql-component.googleapis.com \
    redis.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    secretmanager.googleapis.com
```

## Cloud Run Deployment

Cloud Run is Google's serverless container platform, ideal for HTTP-driven applications.

### 1. Build and Deploy with Cloud Build

Create `cloudbuild.yaml`:
```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.production', '-t', 'gcr.io/$PROJECT_ID/covetpy-app:$COMMIT_SHA', '.']
    
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/covetpy-app:$COMMIT_SHA']
    
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
    - 'run'
    - 'deploy'
    - 'covetpy-app'
    - '--image=gcr.io/$PROJECT_ID/covetpy-app:$COMMIT_SHA'
    - '--region=us-central1'
    - '--platform=managed'
    - '--allow-unauthenticated'
    - '--port=8000'
    - '--memory=2Gi'
    - '--cpu=2'
    - '--concurrency=80'
    - '--timeout=300'
    - '--max-instances=100'
    - '--set-env-vars=ENVIRONMENT=production'
    - '--set-secrets=DATABASE_URL=DATABASE_URL:latest,SECRET_KEY=SECRET_KEY:latest'

images:
  - 'gcr.io/$PROJECT_ID/covetpy-app:$COMMIT_SHA'
```

Deploy:
```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml .

# Or deploy directly
gcloud run deploy covetpy-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --concurrency 80 \
    --timeout 300 \
    --max-instances 100
```

### 2. Configure Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service covetpy-app \
    --domain api.yourdomain.com \
    --region us-central1 \
    --platform managed
```

### 3. Cloud Run Service YAML

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: covetpy-app
  namespace: 'your-project-id'
  labels:
    cloud.googleapis.com/location: us-central1
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/ingress-status: all
spec:
  template:
    metadata:
      labels:
        run.googleapis.com/startupProbeType: Default
      annotations:
        autoscaling.knative.dev/maxScale: '100'
        autoscaling.knative.dev/minScale: '0'
        run.googleapis.com/cloudsql-instances: your-project-id:us-central1:covetpy-db
        run.googleapis.com/cpu-throttling: 'true'
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/memory: 2Gi
        run.googleapis.com/cpu: '2'
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      serviceAccountName: covetpy-sa@your-project-id.iam.gserviceaccount.com
      containers:
      - name: covetpy-app-1
        image: gcr.io/your-project-id/covetpy-app:latest
        ports:
        - name: http1
          containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              key: latest
              name: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              key: latest
              name: SECRET_KEY
        resources:
          limits:
            cpu: '2'
            memory: 2Gi
        startupProbe:
          timeoutSeconds: 240
          periodSeconds: 240
          failureThreshold: 1
          tcpSocket:
            port: 8000
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          timeoutSeconds: 1
          periodSeconds: 3
          failureThreshold: 3
```

## GKE Deployment

### 1. Create GKE Cluster

```bash
# Create zonal cluster
gcloud container clusters create covetpy-cluster \
    --zone us-central1-a \
    --machine-type n1-standard-2 \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --network default \
    --subnetwork default \
    --enable-ip-alias \
    --enable-cloud-logging \
    --enable-cloud-monitoring \
    --disk-size 50GB \
    --disk-type pd-standard

# Get credentials
gcloud container clusters get-credentials covetpy-cluster --zone us-central1-a
```

### 2. Deploy Application

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covetpy-app
  labels:
    app: covetpy-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: covetpy-app
  template:
    metadata:
      labels:
        app: covetpy-app
    spec:
      serviceAccountName: covetpy-ksa
      containers:
      - name: covetpy-app
        image: gcr.io/your-project-id/covetpy-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: covetpy-service
spec:
  selector:
    app: covetpy-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: covetpy-ingress
  annotations:
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: covetpy-ip
    networking.gke.io/managed-certificates: covetpy-ssl-cert
spec:
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: covetpy-service
            port:
              number: 80
```

### 3. Workload Identity Setup

```bash
# Create Google Service Account
gcloud iam service-accounts create covetpy-gsa

# Create Kubernetes Service Account
kubectl create serviceaccount covetpy-ksa

# Bind accounts
gcloud iam service-accounts add-iam-policy-binding \
    covetpy-gsa@your-project-id.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:your-project-id.svc.id.goog[default/covetpy-ksa]"

# Annotate KSA
kubectl annotate serviceaccount covetpy-ksa \
    iam.gke.io/gcp-service-account=covetpy-gsa@your-project-id.iam.gserviceaccount.com
```

## Compute Engine Deployment

### 1. Create Instance Template

```bash
# Create instance template
gcloud compute instance-templates create covetpy-template \
    --machine-type n1-standard-2 \
    --network-interface network-tier=PREMIUM,subnet=default \
    --maintenance-policy MIGRATE \
    --provisioning-model STANDARD \
    --service-account covetpy-sa@your-project-id.iam.gserviceaccount.com \
    --scopes cloud-platform \
    --tags http-server,https-server \
    --image-family ubuntu-2204-lts \
    --image-project ubuntu-os-cloud \
    --boot-disk-size 50GB \
    --boot-disk-type pd-standard \
    --boot-disk-device-name covetpy-template \
    --metadata-from-file startup-script=startup-script.sh
```

### 2. Startup Script

```bash
#!/bin/bash
# startup-script.sh

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install docker-compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Stackdriver agent
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
bash add-logging-agent-repo.sh --also-install

# Clone application
cd /opt
git clone https://github.com/your-org/covetpy-app.git
cd covetpy-app

# Get secrets from Secret Manager
DATABASE_URL=$(gcloud secrets versions access latest --secret="DATABASE_URL")
SECRET_KEY=$(gcloud secrets versions access latest --secret="SECRET_KEY")

# Create environment file
cat > .env << EOF
DATABASE_URL=$DATABASE_URL
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=production
EOF

# Start application
docker-compose -f docker-compose.prod.yml up -d

# Configure nginx reverse proxy
apt-get update && apt-get install -y nginx
cat > /etc/nginx/sites-available/covetpy << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

ln -s /etc/nginx/sites-available/covetpy /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx
```

### 3. Create Managed Instance Group

```bash
# Create instance group
gcloud compute instance-groups managed create covetpy-mig \
    --template covetpy-template \
    --size 3 \
    --zone us-central1-a

# Set autoscaling
gcloud compute instance-groups managed set-autoscaling covetpy-mig \
    --max-num-replicas 10 \
    --min-num-replicas 2 \
    --target-cpu-utilization 0.6 \
    --zone us-central1-a

# Create health check
gcloud compute health-checks create http covetpy-health-check \
    --port 80 \
    --request-path /health

# Set health check on instance group
gcloud compute instance-groups managed set-autohealing covetpy-mig \
    --health-check covetpy-health-check \
    --initial-delay 300 \
    --zone us-central1-a
```

## App Engine Deployment

### 1. Configure app.yaml

```yaml
# app.yaml
runtime: python311
service: default

instance_class: F2

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6
  target_throughput_utilization: 0.6

network:
  session_affinity: false

env_variables:
  ENVIRONMENT: production

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10

handlers:
- url: /static
  static_dir: static
  secure: always

- url: /.*
  script: auto
  secure: always

includes:
- requirements.txt
```

### 2. Deploy to App Engine

```bash
# Deploy
gcloud app deploy app.yaml

# Set traffic
gcloud app services set-traffic default --splits v1=100

# View logs
gcloud app logs tail -s default
```

## Cloud Functions Deployment

For lightweight API endpoints or event-driven functions:

### 1. Create Function

```python
# main.py
from functions_framework import create_app
from app.main import app

# Create the Cloud Functions app
cloud_function = create_app(app)
```

### 2. Deploy Function

```bash
# Deploy HTTP function
gcloud functions deploy covetpy-function \
    --gen2 \
    --runtime python311 \
    --source . \
    --entry-point cloud_function \
    --trigger-http \
    --allow-unauthenticated \
    --memory 1GB \
    --cpu 1 \
    --timeout 300s \
    --max-instances 100 \
    --min-instances 0 \
    --region us-central1
```

## Infrastructure as Code

### Terraform Configuration

```hcl
# main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "covetpy_vpc" {
  name                    = "covetpy-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "covetpy_subnet" {
  name          = "covetpy-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.covetpy_vpc.id
}

# Cloud SQL Database
resource "google_sql_database_instance" "covetpy_db" {
  name             = "covetpy-db-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_15"
  region          = var.region

  settings {
    tier = "db-g1-small"
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
      transaction_log_retention_days = 7
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.covetpy_vpc.id
      require_ssl     = true
    }
    
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
  }

  deletion_protection = false
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database" "covetpy" {
  name     = "covetpy"
  instance = google_sql_database_instance.covetpy_db.name
}

resource "google_sql_user" "covetpy_user" {
  name     = "covetpy"
  instance = google_sql_database_instance.covetpy_db.name
  password = var.db_password
}

# Redis Instance
resource "google_redis_instance" "covetpy_redis" {
  name           = "covetpy-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = 1
  region         = var.region
  
  authorized_network = google_compute_network.covetpy_vpc.id
  redis_version      = "REDIS_6_X"
  display_name      = "CovetPy Redis"
}

# Cloud Run Service
resource "google_cloud_run_service" "covetpy_app" {
  name     = "covetpy-app"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/covetpy-app:latest"
        ports {
          container_port = 8000
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
        
        env {
          name = "ENVIRONMENT"
          value = "production"
        }
        
        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.database_url.secret_id
              key  = "latest"
            }
          }
        }
      }
      
      service_account_name = google_service_account.covetpy_sa.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "100"
        "autoscaling.knative.dev/minScale" = "1"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.covetpy_db.connection_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_service.covetpy_app.location
  project  = google_cloud_run_service.covetpy_app.project
  service  = google_cloud_run_service.covetpy_app.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

# Service Account
resource "google_service_account" "covetpy_sa" {
  account_id   = "covetpy-sa"
  display_name = "CovetPy Service Account"
  description  = "Service account for CovetPy application"
}

# Secrets
resource "google_secret_manager_secret" "database_url" {
  secret_id = "DATABASE_URL"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = "postgresql://${google_sql_user.covetpy_user.name}:${var.db_password}@${google_sql_database_instance.covetpy_db.private_ip_address}:5432/${google_sql_database.covetpy.name}"
}
```

## Monitoring and Logging

### 1. Cloud Operations Setup

```bash
# Install monitoring agent on Compute Engine
curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
sudo bash add-monitoring-agent-repo.sh --also-install

# Install logging agent
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
sudo bash add-logging-agent-repo.sh --also-install
```

### 2. Custom Metrics

```python
# Add to app/main.py
from google.cloud import monitoring_v3
import time

def create_custom_metric():
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{PROJECT_ID}"
    
    descriptor = monitoring_v3.MetricDescriptor()
    descriptor.type = "custom.googleapis.com/covetpy/request_count"
    descriptor.metric_kind = monitoring_v3.MetricDescriptor.MetricKind.COUNTER
    descriptor.value_type = monitoring_v3.MetricDescriptor.ValueType.INT64
    descriptor.description = "Number of requests processed"
    
    client.create_metric_descriptor(
        name=project_name, 
        metric_descriptor=descriptor
    )
```

### 3. Alerting Policies

```bash
# Create alerting policy
gcloud alpha monitoring policies create \
    --policy-from-file=alerting-policy.yaml
```

```yaml
# alerting-policy.yaml
displayName: "CovetPy High Error Rate"
conditions:
  - displayName: "HTTP 5xx error rate"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.label.service_name="covetpy-app"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_MEAN
notificationChannels:
  - "projects/your-project-id/notificationChannels/notification-channel-id"
```

## Security Best Practices

### 1. IAM and Service Accounts
```bash
# Create minimal service account
gcloud iam service-accounts create covetpy-sa \
    --description="CovetPy application service account" \
    --display-name="CovetPy SA"

# Grant minimal permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:covetpy-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:covetpy-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 2. VPC Security
```bash
# Create firewall rules
gcloud compute firewall-rules create allow-covetpy-internal \
    --network covetpy-vpc \
    --allow tcp:8000 \
    --source-ranges 10.0.0.0/24 \
    --target-tags covetpy-app

gcloud compute firewall-rules create allow-lb-to-covetpy \
    --network covetpy-vpc \
    --allow tcp:80,tcp:443 \
    --source-ranges 130.211.0.0/22,35.191.0.0/16 \
    --target-tags covetpy-app
```

### 3. SSL/TLS Configuration
```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create covetpy-ssl-cert \
    --domains api.yourdomain.com \
    --global
```

## Cost Optimization

### 1. Preemptible Instances
```bash
# Use preemptible instances in GKE
gcloud container node-pools create preemptible-pool \
    --cluster covetpy-cluster \
    --zone us-central1-a \
    --machine-type n1-standard-2 \
    --preemptible \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 0 \
    --max-nodes 10
```

### 2. Committed Use Discounts
```bash
# Purchase committed use contracts
gcloud compute commitments create covetpy-commitment \
    --region us-central1 \
    --plan 12-month \
    --resources type=n1-standard-2,count=3
```

### 3. Cloud Run Optimization
- Use minimum instances sparingly
- Optimize container startup time
- Use request-based pricing model

## Deployment Automation

### Cloud Build Configuration

```yaml
# cloudbuild.yaml
steps:
  # Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements-test.txt
        python -m pytest tests/
    
  # Build and push image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.production', '-t', 'gcr.io/$PROJECT_ID/covetpy-app:$SHORT_SHA', '.']
    
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/covetpy-app:$SHORT_SHA']
    
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'covetpy-app'
      - '--image=gcr.io/$PROJECT_ID/covetpy-app:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'

options:
  logging: CLOUD_LOGGING_ONLY

timeout: '1200s'
```

### GitHub Actions Integration

```yaml
# .github/workflows/deploy-gcp.yml
name: Deploy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true
        
    - name: Configure Docker
      run: gcloud auth configure-docker
      
    - name: Build and Deploy
      run: |
        gcloud builds submit --config cloudbuild.yaml .
```

This comprehensive GCP deployment guide provides multiple deployment options for CovetPy applications on Google Cloud Platform, from serverless Cloud Run to full Kubernetes orchestration with GKE.