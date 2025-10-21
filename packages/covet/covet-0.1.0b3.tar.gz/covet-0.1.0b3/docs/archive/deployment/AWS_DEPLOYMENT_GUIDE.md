# AWS Deployment Guide for CovetPy

This guide covers deploying CovetPy applications to Amazon Web Services using various deployment strategies.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [ECS Deployment](#ecs-deployment)
3. [EKS Deployment](#eks-deployment)
4. [EC2 Deployment](#ec2-deployment)
5. [Lambda Deployment](#lambda-deployment)
6. [Infrastructure as Code](#infrastructure-as-code)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Security Best Practices](#security-best-practices)
9. [Cost Optimization](#cost-optimization)

## Prerequisites

### Required Tools
```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure

# Docker
# Install Docker based on your OS

# Terraform (for IaC)
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# kubectl (for EKS)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

### AWS Account Setup
- AWS Account with appropriate permissions
- VPC with public/private subnets
- Security groups configured
- IAM roles and policies

## ECS Deployment

### 1. Build and Push Docker Image

```bash
# Build production image
docker build -f Dockerfile.production -t covetpy-app .

# Tag for ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

docker tag covetpy-app:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest
```

### 2. Create ECS Task Definition

```json
{
  "family": "covetpy-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "covetpy-app",
      "image": "<account-id>.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/covetpy-app",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:<account-id>:secret:covetpy-db-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:<account-id>:secret:covetpy-secret-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health/live || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### 3. Create ECS Service with Load Balancer

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
    --name covetpy-alb \
    --subnets subnet-12345678 subnet-87654321 \
    --security-groups sg-12345678 \
    --scheme internet-facing \
    --type application

# Create target group
aws elbv2 create-target-group \
    --name covetpy-targets \
    --protocol HTTP \
    --port 8000 \
    --vpc-id vpc-12345678 \
    --target-type ip \
    --health-check-path /health/ready

# Create ECS service
aws ecs create-service \
    --cluster covetpy-cluster \
    --service-name covetpy-service \
    --task-definition covetpy-app:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-west-2:<account-id>:targetgroup/covetpy-targets,containerName=covetpy-app,containerPort=8000
```

## EKS Deployment

### 1. Create EKS Cluster

```bash
# Create cluster
eksctl create cluster \
    --name covetpy-cluster \
    --region us-west-2 \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 3 \
    --nodes-min 1 \
    --nodes-max 4 \
    --managed

# Configure kubectl
aws eks --region us-west-2 update-kubeconfig --name covetpy-cluster
```

### 2. Deploy with Kubernetes Manifests

```yaml
# deployment.yaml
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
      containers:
      - name: covetpy-app
        image: <account-id>.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        envFrom:
        - secretRef:
            name: covetpy-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
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
```

```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 3. Install AWS Load Balancer Controller

```bash
# Install AWS Load Balancer Controller
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.2/docs/install/iam_policy.json

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

eksctl create iamserviceaccount \
  --cluster=covetpy-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::<account-id>:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=covetpy-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

## EC2 Deployment

### 1. Launch EC2 Instance

```bash
# Launch instance with user data script
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1d0 \
    --count 1 \
    --instance-type t3.medium \
    --key-name my-key-pair \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=covetpy-app}]'
```

### 2. User Data Script (user-data.sh)

```bash
#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install docker-compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone and deploy application
cd /opt
git clone https://github.com/your-org/covetpy-app.git
cd covetpy-app

# Set environment variables
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/covetpy
REDIS_URL=redis://elasticache-endpoint:6379/0
SECRET_KEY=your-secret-key
ENVIRONMENT=production
EOF

# Start application
docker-compose up -d
```

## Lambda Deployment

For serverless deployment using AWS Lambda with Mangum adapter:

### 1. Install Dependencies

```bash
pip install mangum
```

### 2. Create Lambda Handler

```python
# lambda_handler.py
from mangum import Mangum
from app.main import app

lambda_handler = Mangum(app, lifespan="off")
```

### 3. Deploy with SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  CovetPyFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.lambda_handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 1024
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseUrl
          SECRET_KEY: !Ref SecretKey
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

```bash
# Deploy
sam build
sam deploy --guided
```

## Infrastructure as Code

### Terraform Configuration

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC and networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "covetpy-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
}

# RDS Database
resource "aws_db_instance" "covetpy_db" {
  identifier     = "covetpy-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r5.large"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  
  db_name  = "covetpy"
  username = "covetpy"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.covetpy.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "covetpy-final-snapshot"
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "covetpy" {
  name       = "covetpy-cache-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_replication_group" "covetpy_redis" {
  description          = "CovetPy Redis cluster"
  replication_group_id = "covetpy-redis"
  port                 = 6379
  parameter_group_name = "default.redis7"
  node_type           = "cache.r6g.large"
  num_cache_clusters  = 2
  
  subnet_group_name  = aws_elasticache_subnet_group.covetpy.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                = var.redis_auth_token
}

# ECS Cluster
resource "aws_ecs_cluster" "covetpy" {
  name = "covetpy-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "covetpy_alb" {
  name               = "covetpy-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets
  
  enable_deletion_protection = false
}
```

## Monitoring and Logging

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/covetpy-app

# Create custom metrics
aws cloudwatch put-metric-alarm \
  --alarm-name covetpy-high-cpu \
  --alarm-description "Alarm when CPU exceeds 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### X-Ray Tracing

```python
# Add to app/main.py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch all AWS SDK calls
patch_all()

# Configure X-Ray
xray_recorder.configure(
    context_missing='LOG_ERROR',
    plugins=('EC2Plugin', 'ECSPlugin'),
    daemon_address='127.0.0.1:2000',
)

@app.middleware("http")
async def xray_middleware(request: Request, call_next):
    # X-Ray tracing middleware
    pass
```

## Security Best Practices

### 1. IAM Policies
- Use least privilege principle
- Separate roles for different services
- Regular audit of permissions

### 2. VPC Security
- Private subnets for application servers
- Public subnets only for load balancers
- Network ACLs and Security Groups

### 3. Secrets Management
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name covetpy/database/url \
    --secret-string "postgresql://user:pass@host:5432/db"

aws secretsmanager create-secret \
    --name covetpy/app/secret-key \
    --generate-random-password \
    --password-length 32
```

### 4. SSL/TLS Configuration
```bash
# Request ACM certificate
aws acm request-certificate \
    --domain-name api.yourdomain.com \
    --validation-method DNS \
    --subject-alternative-names "*.yourdomain.com"
```

## Cost Optimization

### 1. Right-sizing Resources
- Use AWS Compute Optimizer
- Monitor CloudWatch metrics
- Implement auto-scaling

### 2. Reserved Instances
```bash
# Purchase Reserved Instances for predictable workloads
aws ec2 purchase-reserved-instances-offering \
    --reserved-instances-offering-id <offering-id> \
    --instance-count 2
```

### 3. Spot Instances for Development
```yaml
# Use Spot instances in ECS
spotIamFleetRequestRole: arn:aws:iam::<account-id>:role/aws-ec2-spot-fleet-tagging-role
capacityProviders:
  - name: covetpy-spot-capacity-provider
    spotConfiguration:
      targetCapacity: 2
      minimumScalingStepSize: 1
      maximumScalingStepSize: 100
```

## Deployment Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-aws.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Login to Amazon ECR
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      run: |
        docker build -f Dockerfile.production -t covetpy-app .
        docker tag covetpy-app:latest $ECR_REGISTRY/covetpy-app:$GITHUB_SHA
        docker push $ECR_REGISTRY/covetpy-app:$GITHUB_SHA
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster covetpy-cluster \
          --service covetpy-service \
          --force-new-deployment
```

This comprehensive AWS deployment guide covers multiple deployment strategies and best practices for running CovetPy applications on AWS infrastructure. Choose the deployment method that best fits your application's requirements and scale.