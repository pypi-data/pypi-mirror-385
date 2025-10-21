# CovetPy AWS Deployment Guide

**Version:** 1.0.0  
**Last Updated:** September 30, 2025  
**Deployment Target:** Production-Ready AWS Infrastructure

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Container Deployment](#container-deployment)
5. [Database Configuration](#database-configuration)
6. [Load Balancing & Auto Scaling](#load-balancing--auto-scaling)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Configuration](#security-configuration)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Production Architecture Diagram

```
Internet → CloudFront → ALB → EKS Cluster → Pods
                          ↓
                        RDS (PostgreSQL)
                        ElastiCache (Redis)
                        S3 (Static Files)
                        CloudWatch (Monitoring)
```

### Components

- **Amazon EKS**: Managed Kubernetes for container orchestration
- **Application Load Balancer (ALB)**: Traffic distribution and SSL termination
- **Amazon RDS**: Managed PostgreSQL database
- **Amazon ElastiCache**: Managed Redis for caching
- **Amazon CloudFront**: Global CDN for static content
- **Amazon S3**: Static file storage and backups
- **AWS CloudWatch**: Monitoring and logging
- **AWS IAM**: Access control and security
- **AWS Secrets Manager**: Secure credential storage

---

## Prerequisites

### Required Tools

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
```

### AWS Configuration

```bash
# Configure AWS credentials
aws configure
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-west-2
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

---

## Infrastructure Setup

### 1. Create VPC and Networking

```bash
# Create VPC using CloudFormation
aws cloudformation create-stack \
  --stack-name covetpy-vpc \
  --template-body file://infrastructure/aws/vpc.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production

# Wait for stack creation
aws cloudformation wait stack-create-complete --stack-name covetpy-vpc
```

**VPC CloudFormation Template** (`infrastructure/aws/vpc.yaml`):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'CovetPy Production VPC Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
    Description: Environment name

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-covetpy-vpc

  # Public Subnets for Load Balancers
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-public-subnet-1
        - Key: kubernetes.io/role/elb
          Value: 1

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-public-subnet-2
        - Key: kubernetes.io/role/elb
          Value: 1

  # Private Subnets for Applications
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.10.0/24
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-private-subnet-1
        - Key: kubernetes.io/role/internal-elb
          Value: 1

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.11.0/24
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-private-subnet-2
        - Key: kubernetes.io/role/internal-elb
          Value: 1

  # Database Subnets
  DatabaseSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.20.0/24
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-database-subnet-1

  DatabaseSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.21.0/24
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-database-subnet-2

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-covetpy-igw

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      InternetGatewayId: !Ref InternetGateway
      VpcId: !Ref VPC

  # NAT Gateways
  NatGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-nat-gateway-1

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-public-routes

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet1

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet2

  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-private-routes-1

  DefaultPrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet1

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet2

  # Security Groups
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${Environment}-alb-security-group
      GroupDescription: Security group for Application Load Balancer
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0

  EKSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${Environment}-eks-security-group
      GroupDescription: Security group for EKS cluster
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          SourceSecurityGroupId: !Ref ALBSecurityGroup
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0

  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${Environment}-database-security-group
      GroupDescription: Security group for RDS database
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref EKSSecurityGroup
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0

Outputs:
  VPC:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub ${Environment}-VPC

  PublicSubnets:
    Description: Public subnet IDs
    Value: !Join [',', [!Ref PublicSubnet1, !Ref PublicSubnet2]]
    Export:
      Name: !Sub ${Environment}-PublicSubnets

  PrivateSubnets:
    Description: Private subnet IDs
    Value: !Join [',', [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
    Export:
      Name: !Sub ${Environment}-PrivateSubnets

  DatabaseSubnets:
    Description: Database subnet IDs
    Value: !Join [',', [!Ref DatabaseSubnet1, !Ref DatabaseSubnet2]]
    Export:
      Name: !Sub ${Environment}-DatabaseSubnets

  SecurityGroups:
    Description: Security group IDs
    Value: !Join [',', [!Ref ALBSecurityGroup, !Ref EKSSecurityGroup, !Ref DatabaseSecurityGroup]]
    Export:
      Name: !Sub ${Environment}-SecurityGroups
```

### 2. Create EKS Cluster

```bash
# Create EKS cluster
eksctl create cluster \
  --name covetpy-production \
  --version 1.28 \
  --region us-west-2 \
  --vpc-from-stack covetpy-vpc \
  --nodegroup-name covetpy-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 6 \
  --ssh-access \
  --ssh-public-key ~/.ssh/id_rsa.pub \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name covetpy-production

# Verify cluster
kubectl get nodes
```

### 3. Setup Database Infrastructure

```bash
# Create RDS PostgreSQL instance
aws cloudformation create-stack \
  --stack-name covetpy-database \
  --template-body file://infrastructure/aws/database.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production \
               ParameterKey=MasterUsername,ParameterValue=covetpy \
               ParameterKey=MasterPassword,ParameterValue=SecurePassword123!

# Wait for database creation
aws cloudformation wait stack-create-complete --stack-name covetpy-database
```

**Database CloudFormation Template** (`infrastructure/aws/database.yaml`):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'CovetPy Production Database Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
  MasterUsername:
    Type: String
    NoEcho: true
  MasterPassword:
    Type: String
    NoEcho: true

Resources:
  DatabaseSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupName: !Sub ${Environment}-covetpy-db-subnet-group
      DBSubnetGroupDescription: Subnet group for CovetPy database
      SubnetIds:
        - !Select [0, !Split [',', !ImportValue !Sub '${Environment}-DatabaseSubnets']]
        - !Select [1, !Split [',', !ImportValue !Sub '${Environment}-DatabaseSubnets']]

  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub ${Environment}-covetpy-db
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: '15.3'
      AllocatedStorage: 100
      StorageType: gp3
      StorageEncrypted: true
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterPassword
      VPCSecurityGroups:
        - !Select [2, !Split [',', !ImportValue !Sub '${Environment}-SecurityGroups']]
      DBSubnetGroupName: !Ref DatabaseSubnetGroup
      BackupRetentionPeriod: 30
      DeleteAutomatedBackups: false
      DeletionProtection: true
      MultiAZ: true
      PubliclyAccessible: false
      MonitoringInterval: 60
      MonitoringRoleArn: !GetAtt DatabaseMonitoringRole.Arn
      PerformanceInsightsEnabled: true
      PerformanceInsightsRetentionPeriod: 7

  DatabaseMonitoringRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: ''
            Effect: Allow
            Principal:
              Service: monitoring.rds.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole'

  # ElastiCache Redis Cluster
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      CacheSubnetGroupName: !Sub ${Environment}-covetpy-cache-subnet-group
      Description: Subnet group for CovetPy cache
      SubnetIds:
        - !Select [0, !Split [',', !ImportValue !Sub '${Environment}-PrivateSubnets']]
        - !Select [1, !Split [',', !ImportValue !Sub '${Environment}-PrivateSubnets']]

  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ElastiCache
      VpcId: !ImportValue !Sub '${Environment}-VPC'
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Select [1, !Split [',', !ImportValue !Sub '${Environment}-SecurityGroups']]

  CacheReplicationGroup:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupId: !Sub ${Environment}-covetpy-redis
      Description: Redis cluster for CovetPy
      NodeType: cache.t3.micro
      NumCacheClusters: 2
      Engine: redis
      EngineVersion: 7.0
      Port: 6379
      ParameterGroupName: default.redis7
      SubnetGroupName: !Ref CacheSubnetGroup
      SecurityGroupIds:
        - !Ref CacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true

Outputs:
  DatabaseEndpoint:
    Description: RDS PostgreSQL endpoint
    Value: !GetAtt DatabaseInstance.Endpoint.Address
    Export:
      Name: !Sub ${Environment}-DatabaseEndpoint

  RedisEndpoint:
    Description: ElastiCache Redis endpoint
    Value: !GetAtt CacheReplicationGroup.PrimaryEndPoint.Address
    Export:
      Name: !Sub ${Environment}-RedisEndpoint
```

### 4. Create S3 Bucket for Static Files

```bash
# Create S3 bucket
aws s3 mb s3://covetpy-production-static --region us-west-2

# Configure bucket for static website hosting
aws s3 website s3://covetpy-production-static \
  --index-document index.html \
  --error-document error.html

# Set bucket policy for public read
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::covetpy-production-static/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket covetpy-production-static \
  --policy file://bucket-policy.json
```

---

## Container Deployment

### 1. Build and Push Docker Image

```bash
# Build Docker image
docker build -t covetpy-app:latest .

# Tag for ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name covetpy-app --region us-west-2

# Tag and push
docker tag covetpy-app:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest
```

### 2. Kubernetes Deployment Configuration

**Deployment Manifest** (`k8s/production/deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covetpy-app
  namespace: production
  labels:
    app: covetpy-app
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: covetpy-app
  template:
    metadata:
      labels:
        app: covetpy-app
        version: v1.0.0
    spec:
      serviceAccountName: covetpy-service-account
      containers:
      - name: covetpy-app
        image: 123456789012.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest
        ports:
        - containerPort: 8000
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: secret-key
        - name: ENVIRONMENT
          value: "production"
        - name: AWS_DEFAULT_REGION
          value: "us-west-2"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
---
apiVersion: v1
kind: Service
metadata:
  name: covetpy-service
  namespace: production
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internal"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: covetpy-app
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: covetpy-service-account
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/covetpy-pod-role
```

### 3. Secrets Management

```bash
# Create namespace
kubectl create namespace production

# Get database endpoint
DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name covetpy-database \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text)

# Get Redis endpoint
REDIS_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name covetpy-database \
  --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' \
  --output text)

# Create secrets
kubectl create secret generic covetpy-secrets \
  --namespace=production \
  --from-literal=database-url="postgresql://covetpy:SecurePassword123!@${DB_ENDPOINT}:5432/postgres" \
  --from-literal=redis-url="redis://${REDIS_ENDPOINT}:6379" \
  --from-literal=secret-key="$(openssl rand -base64 32)"

# Deploy the application
kubectl apply -f k8s/production/
```

---

## Load Balancing & Auto Scaling

### 1. Application Load Balancer

**ALB Ingress Configuration** (`k8s/production/ingress.yaml`):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: covetpy-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: "15"
    alb.ingress.kubernetes.io/healthcheck-timeout-seconds: "5"
    alb.ingress.kubernetes.io/healthy-threshold-count: "2"
    alb.ingress.kubernetes.io/unhealthy-threshold-count: "2"
spec:
  rules:
  - host: api.covetpy.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: covetpy-service
            port:
              number: 80
```

### 2. Horizontal Pod Autoscaler

**HPA Configuration** (`k8s/production/hpa.yaml`):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: covetpy-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: covetpy-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### 3. Cluster Autoscaler

```bash
# Install cluster autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

# Configure cluster autoscaler
kubectl -n kube-system annotate deployment.apps/cluster-autoscaler \
  cluster-autoscaler.kubernetes.io/safe-to-evict="false"

kubectl -n kube-system edit deployment.apps/cluster-autoscaler
# Add the following args:
# - --balance-similar-node-groups
# - --skip-nodes-with-system-pods=false
# - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/covetpy-production
```

---

## Monitoring & Logging

### 1. Install Prometheus and Grafana

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=SecurePassword123!

# Get Grafana admin password
kubectl get secret --namespace monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

### 2. CloudWatch Container Insights

```bash
# Install CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml

# Verify installation
kubectl get pods -n amazon-cloudwatch
```

### 3. Application Monitoring Configuration

**Prometheus ServiceMonitor** (`k8s/production/monitoring.yaml`):

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: covetpy-metrics
  namespace: production
  labels:
    app: covetpy-app
spec:
  selector:
    matchLabels:
      app: covetpy-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
---
apiVersion: v1
kind: Service
metadata:
  name: covetpy-metrics
  namespace: production
  labels:
    app: covetpy-app
spec:
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
  selector:
    app: covetpy-app
```

---

## Security Configuration

### 1. Pod Security Standards

**Pod Security Policy** (`k8s/production/security.yaml`):

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: covetpy-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: covetpy-psp-user
rules:
- apiGroups: ['policy']
  resources: ['podsecuritypolicies']
  verbs: ['use']
  resourceNames:
  - covetpy-psp
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: covetpy-psp-binding
roleRef:
  kind: ClusterRole
  name: covetpy-psp-user
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: covetpy-service-account
  namespace: production
```

### 2. Network Policies

**Network Policy** (`k8s/production/network-policy.yaml`):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: covetpy-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: covetpy-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 443   # HTTPS
    - protocol: TCP
      port: 53    # DNS
    - protocol: UDP
      port: 53    # DNS
```

### 3. AWS IAM Roles for Service Accounts (IRSA)

```bash
# Create IAM role for pods
aws iam create-role \
  --role-name covetpy-pod-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name covetpy-pod-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-role-policy \
  --role-name covetpy-pod-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
```

**Trust Policy** (`trust-policy.json`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-west-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.us-west-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B716D3041E:sub": "system:serviceaccount:production:covetpy-service-account"
        }
      }
    }
  ]
}
```

---

## CI/CD Pipeline

### 1. GitHub Actions Workflow

**GitHub Workflow** (`.github/workflows/aws-deploy.yml`):

```yaml
name: Deploy to AWS EKS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-west-2
  EKS_CLUSTER_NAME: covetpy-production
  ECR_REPOSITORY: covetpy-app

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=src/covet --cov-report=xml

    - name: Security scan
      run: |
        bandit -r src/covet/
        safety check

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, tag, and push image to Amazon ECR
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Update kube config
      run: aws eks update-kubeconfig --name $EKS_CLUSTER_NAME --region $AWS_REGION

    - name: Deploy to EKS
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        kubectl set image deployment/covetpy-app covetpy-app=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -n production
        kubectl rollout status deployment/covetpy-app -n production

    - name: Verify deployment
      run: |
        kubectl get pods -n production
        kubectl get services -n production
```

### 2. Deployment Scripts

**Deployment Script** (`scripts/deploy-aws.sh`):

```bash
#!/bin/bash
set -e

# Configuration
ENVIRONMENT="production"
REGION="us-west-2"
CLUSTER_NAME="covetpy-production"
NAMESPACE="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting CovetPy AWS Deployment${NC}"

# Verify prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v aws >/dev/null 2>&1 || { echo -e "${RED}❌ AWS CLI is required${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}❌ kubectl is required${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required${NC}"; exit 1; }

# Update kubeconfig
echo -e "${YELLOW}Updating kubeconfig...${NC}"
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Build and push Docker image
echo -e "${YELLOW}Building and pushing Docker image...${NC}"
ECR_REGISTRY=$(aws ecr describe-registry --query 'registryId' --output text)
ECR_URI="${ECR_REGISTRY}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE_URI="${ECR_URI}/covetpy-app:latest"

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

docker build -t covetpy-app:latest .
docker tag covetpy-app:latest $IMAGE_URI
docker push $IMAGE_URI

echo -e "${GREEN}✅ Docker image pushed: $IMAGE_URI${NC}"

# Deploy to Kubernetes
echo -e "${YELLOW}Deploying to Kubernetes...${NC}"
kubectl apply -f k8s/production/

# Wait for deployment
echo -e "${YELLOW}Waiting for deployment to complete...${NC}"
kubectl rollout status deployment/covetpy-app -n $NAMESPACE --timeout=300s

# Verify deployment
echo -e "${YELLOW}Verifying deployment...${NC}"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

# Get application URL
ALB_HOST=$(kubectl get ingress covetpy-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}🌐 Application URL: https://$ALB_HOST${NC}"

# Run health check
echo -e "${YELLOW}Running health check...${NC}"
sleep 30  # Wait for ALB to be ready
curl -f https://$ALB_HOST/health || echo -e "${RED}❌ Health check failed${NC}"

echo -e "${GREEN}🎉 CovetPy successfully deployed to AWS!${NC}"
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Pod Startup Issues

```bash
# Check pod status
kubectl get pods -n production

# Describe problematic pod
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production

# Common fixes:
# - Check image availability in ECR
# - Verify secrets are created correctly
# - Check resource limits
# - Validate environment variables
```

#### 2. Database Connection Issues

```bash
# Test database connectivity from pod
kubectl exec -it <pod-name> -n production -- psql $DATABASE_URL -c "SELECT 1;"

# Check security groups
aws ec2 describe-security-groups --group-ids <sg-id>

# Verify database status
aws rds describe-db-instances --db-instance-identifier production-covetpy-db
```

#### 3. Load Balancer Issues

```bash
# Check ALB status
kubectl describe ingress covetpy-ingress -n production

# View ALB in AWS Console
aws elbv2 describe-load-balancers

# Check target group health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

#### 4. Auto Scaling Issues

```bash
# Check HPA status
kubectl get hpa -n production

# View HPA details
kubectl describe hpa covetpy-hpa -n production

# Check metrics server
kubectl top pods -n production
kubectl top nodes
```

### Monitoring and Alerting

#### CloudWatch Alarms

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "CovetPy-HighCPU" \
  --alarm-description "High CPU utilization" \
  --metric-name CPUUtilization \
  --namespace AWS/EKS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

aws cloudwatch put-metric-alarm \
  --alarm-name "CovetPy-HighMemory" \
  --alarm-description "High memory utilization" \
  --metric-name MemoryUtilization \
  --namespace AWS/EKS \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

#### Log Analysis

```bash
# View application logs in CloudWatch
aws logs describe-log-groups --log-group-name-prefix "/aws/eks/covetpy"

# Stream logs
aws logs tail /aws/eks/covetpy-production/application --follow

# Search logs
aws logs filter-log-events \
  --log-group-name "/aws/eks/covetpy-production/application" \
  --filter-pattern "ERROR"
```

### Performance Optimization

#### Database Performance

```bash
# Enable Performance Insights
aws rds modify-db-instance \
  --db-instance-identifier production-covetpy-db \
  --enable-performance-insights \
  --performance-insights-retention-period 7

# Monitor slow queries
aws rds describe-db-log-files \
  --db-instance-identifier production-covetpy-db
```

#### Application Performance

```bash
# Scale application
kubectl scale deployment covetpy-app --replicas=5 -n production

# Update resource limits
kubectl patch deployment covetpy-app -n production -p '{"spec":{"template":{"spec":{"containers":[{"name":"covetpy-app","resources":{"limits":{"memory":"2Gi","cpu":"1000m"}}}]}}}}'
```

---

This completes the comprehensive AWS deployment guide for CovetPy. The infrastructure is production-ready with high availability, auto-scaling, monitoring, and security best practices.