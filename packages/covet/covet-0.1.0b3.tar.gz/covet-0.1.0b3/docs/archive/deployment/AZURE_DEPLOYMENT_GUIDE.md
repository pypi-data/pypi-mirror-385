# Azure Deployment Guide for CovetPy

This guide covers deploying CovetPy applications to Microsoft Azure using various deployment strategies.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Container Instances Deployment](#container-instances-deployment)
3. [Azure Kubernetes Service (AKS)](#azure-kubernetes-service-aks)
4. [App Service Deployment](#app-service-deployment)
5. [Virtual Machines Deployment](#virtual-machines-deployment)
6. [Azure Functions Deployment](#azure-functions-deployment)
7. [Infrastructure as Code](#infrastructure-as-code)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Security Best Practices](#security-best-practices)
10. [Cost Optimization](#cost-optimization)

## Prerequisites

### Required Tools
```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login

# Docker
# Install Docker based on your OS

# Terraform (for IaC)
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# kubectl (for AKS)
az aks install-cli
```

### Azure Setup
```bash
# Create resource group
az group create --name covetpy-rg --location eastus

# Register required providers
az provider register --namespace Microsoft.ContainerInstance
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
```

## Container Instances Deployment

Azure Container Instances provides serverless containers for simple deployments.

### 1. Build and Push to Azure Container Registry

```bash
# Create Azure Container Registry
az acr create --resource-group covetpy-rg \
    --name covetpyregistry \
    --sku Basic \
    --location eastus

# Login to ACR
az acr login --name covetpyregistry

# Build and push image
docker build -f Dockerfile.production -t covetpyregistry.azurecr.io/covetpy-app:latest .
docker push covetpyregistry.azurecr.io/covetpy-app:latest
```

### 2. Deploy Container Instance

```bash
# Create container instance
az container create \
    --resource-group covetpy-rg \
    --name covetpy-app \
    --image covetpyregistry.azurecr.io/covetpy-app:latest \
    --cpu 2 \
    --memory 4 \
    --registry-login-server covetpyregistry.azurecr.io \
    --registry-username covetpyregistry \
    --registry-password $(az acr credential show --name covetpyregistry --query "passwords[0].value" -o tsv) \
    --dns-name-label covetpy-app \
    --ports 8000 \
    --environment-variables ENVIRONMENT=production \
    --secure-environment-variables \
        DATABASE_URL=postgresql://user:pass@host:5432/covetpy \
        SECRET_KEY=your-secret-key \
    --location eastus
```

### 3. Container Group YAML Deployment

```yaml
# container-group.yaml
apiVersion: '2021-07-01'
location: eastus
name: covetpy-container-group
properties:
  containers:
  - name: covetpy-app
    properties:
      image: covetpyregistry.azurecr.io/covetpy-app:latest
      resources:
        requests:
          cpu: 2
          memoryInGb: 4
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: ENVIRONMENT
        value: production
      - name: DATABASE_URL
        secureValue: postgresql://user:pass@host:5432/covetpy
      - name: SECRET_KEY
        secureValue: your-secret-key
      livenessProbe:
        exec:
          command:
          - /bin/sh
          - -c
          - "curl -f http://localhost:8000/health/live || exit 1"
        initialDelaySeconds: 30
        periodSeconds: 10
        timeoutSeconds: 5
        successThreshold: 1
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8000
        initialDelaySeconds: 5
        periodSeconds: 5
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8000
    dnsNameLabel: covetpy-app
  imageRegistryCredentials:
  - server: covetpyregistry.azurecr.io
    username: covetpyregistry
    password: registry-password
tags: {}
type: Microsoft.ContainerInstance/containerGroups
```

Deploy with:
```bash
az container create --resource-group covetpy-rg --file container-group.yaml
```

## Azure Kubernetes Service (AKS)

### 1. Create AKS Cluster

```bash
# Create AKS cluster
az aks create \
    --resource-group covetpy-rg \
    --name covetpy-aks \
    --node-count 3 \
    --node-vm-size Standard_D2s_v3 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --attach-acr covetpyregistry \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5 \
    --location eastus

# Get credentials
az aks get-credentials --resource-group covetpy-rg --name covetpy-aks
```

### 2. Deploy Application to AKS

```yaml
# k8s-manifests.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: covetpy
---
apiVersion: v1
kind: Secret
metadata:
  name: covetpy-secrets
  namespace: covetpy
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covetpy-app
  namespace: covetpy
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
        image: covetpyregistry.azurecr.io/covetpy-app:latest
        imagePullPolicy: Always
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
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 30
---
apiVersion: v1
kind: Service
metadata:
  name: covetpy-service
  namespace: covetpy
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
  namespace: covetpy
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: covetpy-tls
  rules:
  - host: api.yourdomain.com
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

Deploy:
```bash
kubectl apply -f k8s-manifests.yaml
```

### 3. Enable Application Gateway Ingress Controller

```bash
# Enable Application Gateway ingress controller
az aks enable-addons \
    --resource-group covetpy-rg \
    --name covetpy-aks \
    --addons ingress-appgw \
    --appgw-name covetpy-appgw \
    --appgw-subnet-cidr "10.2.0.0/16"
```

## App Service Deployment

### 1. Create App Service Plan

```bash
# Create App Service Plan
az appservice plan create \
    --name covetpy-plan \
    --resource-group covetpy-rg \
    --sku P1V3 \
    --is-linux \
    --location eastus

# Create Web App
az webapp create \
    --resource-group covetpy-rg \
    --plan covetpy-plan \
    --name covetpy-webapp \
    --deployment-container-image-name covetpyregistry.azurecr.io/covetpy-app:latest \
    --docker-registry-server-url https://covetpyregistry.azurecr.io \
    --docker-registry-server-user covetpyregistry \
    --docker-registry-server-password $(az acr credential show --name covetpyregistry --query "passwords[0].value" -o tsv)
```

### 2. Configure App Settings

```bash
# Set application settings
az webapp config appsettings set \
    --resource-group covetpy-rg \
    --name covetpy-webapp \
    --settings \
        ENVIRONMENT=production \
        WEBSITES_PORT=8000 \
        DATABASE_URL="postgresql://user:pass@host:5432/covetpy" \
        SECRET_KEY="your-secret-key"

# Configure health check
az webapp config set \
    --resource-group covetpy-rg \
    --name covetpy-webapp \
    --generic-configurations '{"healthCheckPath": "/health"}'

# Enable continuous deployment
az webapp deployment container config \
    --name covetpy-webapp \
    --resource-group covetpy-rg \
    --enable-cd true
```

### 3. Custom Domain and SSL

```bash
# Add custom domain
az webapp config hostname add \
    --webapp-name covetpy-webapp \
    --resource-group covetpy-rg \
    --hostname api.yourdomain.com

# Enable HTTPS only
az webapp update \
    --resource-group covetpy-rg \
    --name covetpy-webapp \
    --https-only true

# Bind SSL certificate
az webapp config ssl bind \
    --certificate-thumbprint <thumbprint> \
    --ssl-type SNI \
    --name covetpy-webapp \
    --resource-group covetpy-rg
```

## Virtual Machines Deployment

### 1. Create Virtual Machine

```bash
# Create VM
az vm create \
    --resource-group covetpy-rg \
    --name covetpy-vm \
    --image Ubuntu2204 \
    --size Standard_D2s_v3 \
    --admin-username azureuser \
    --generate-ssh-keys \
    --custom-data cloud-init.yaml \
    --public-ip-sku Standard \
    --location eastus

# Open ports
az vm open-port --port 80 --resource-group covetpy-rg --name covetpy-vm
az vm open-port --port 443 --resource-group covetpy-rg --name covetpy-vm
```

### 2. Cloud-init Configuration

```yaml
# cloud-init.yaml
#cloud-config
package_upgrade: true

packages:
  - docker.io
  - docker-compose
  - nginx
  - certbot
  - python3-certbot-nginx

runcmd:
  # Start and enable Docker
  - systemctl start docker
  - systemctl enable docker
  - usermod -aG docker azureuser
  
  # Install Azure CLI
  - curl -sL https://aka.ms/InstallAzureCLIDeb | bash
  
  # Create application directory
  - mkdir -p /opt/covetpy
  - chown azureuser:azureuser /opt/covetpy
  
  # Clone application (replace with your repo)
  - sudo -u azureuser git clone https://github.com/your-org/covetpy-app.git /opt/covetpy
  
  # Set up environment
  - cd /opt/covetpy
  - sudo -u azureuser docker-compose -f docker-compose.prod.yml up -d
  
  # Configure nginx
  - |
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
  
  - ln -s /etc/nginx/sites-available/covetpy /etc/nginx/sites-enabled/
  - rm /etc/nginx/sites-enabled/default
  - systemctl restart nginx
  - systemctl enable nginx

write_files:
  - path: /opt/covetpy/.env
    content: |
      DATABASE_URL=postgresql://user:pass@host:5432/covetpy
      SECRET_KEY=your-secret-key
      ENVIRONMENT=production
    owner: azureuser:azureuser
    permissions: '0600'
```

### 3. Create Virtual Machine Scale Set

```bash
# Create VMSS
az vmss create \
    --resource-group covetpy-rg \
    --name covetpy-vmss \
    --image Ubuntu2204 \
    --vm-sku Standard_D2s_v3 \
    --instance-count 3 \
    --admin-username azureuser \
    --generate-ssh-keys \
    --upgrade-policy-mode automatic \
    --custom-data cloud-init.yaml \
    --location eastus

# Configure autoscaling
az monitor autoscale create \
    --resource-group covetpy-rg \
    --resource covetpy-vmss \
    --resource-type Microsoft.Compute/virtualMachineScaleSets \
    --name covetpy-autoscale \
    --min-count 2 \
    --max-count 10 \
    --count 3

az monitor autoscale rule create \
    --resource-group covetpy-rg \
    --autoscale-name covetpy-autoscale \
    --condition "Percentage CPU > 70 avg 5m" \
    --scale out 2

az monitor autoscale rule create \
    --resource-group covetpy-rg \
    --autoscale-name covetpy-autoscale \
    --condition "Percentage CPU < 25 avg 5m" \
    --scale in 1
```

## Azure Functions Deployment

### 1. Create Function App

```bash
# Create storage account
az storage account create \
    --name covetpystorage \
    --location eastus \
    --resource-group covetpy-rg \
    --sku Standard_LRS

# Create function app
az functionapp create \
    --resource-group covetpy-rg \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --name covetpy-functions \
    --storage-account covetpystorage \
    --os-type Linux
```

### 2. Deploy Function

```python
# function_app.py
import azure.functions as func
from app.main import app
from asgi_lifespan import LifespanManager

app_with_lifespan = LifespanManager(app)

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiMiddleware(app_with_lifespan).handle_async(req, context)
```

```json
// host.json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  },
  "functionTimeout": "00:05:00"
}
```

```json
// function.json
{
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "route": "{*route}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ],
  "scriptFile": "function_app.py"
}
```

Deploy:
```bash
func azure functionapp publish covetpy-functions
```

## Infrastructure as Code

### Terraform Configuration

```hcl
# main.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "covetpy" {
  name     = "covetpy-rg"
  location = "East US"
}

# Virtual Network
resource "azurerm_virtual_network" "covetpy" {
  name                = "covetpy-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.covetpy.location
  resource_group_name = azurerm_resource_group.covetpy.name
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.covetpy.name
  virtual_network_name = azurerm_virtual_network.covetpy.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Container Registry
resource "azurerm_container_registry" "covetpy" {
  name                = "covetpyregistry"
  resource_group_name = azurerm_resource_group.covetpy.name
  location            = azurerm_resource_group.covetpy.location
  sku                 = "Premium"
  admin_enabled       = true
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server" "covetpy" {
  name                   = "covetpy-db"
  resource_group_name    = azurerm_resource_group.covetpy.name
  location               = azurerm_resource_group.covetpy.location
  version                = "15"
  administrator_login    = "covetpy"
  administrator_password = var.db_password
  zone                   = "1"
  
  storage_mb   = 32768
  storage_tier = "P10"
  
  sku_name = "GP_Standard_D2s_v3"
}

resource "azurerm_postgresql_flexible_server_database" "covetpy" {
  name      = "covetpy"
  server_id = azurerm_postgresql_flexible_server.covetpy.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Redis Cache
resource "azurerm_redis_cache" "covetpy" {
  name                = "covetpy-redis"
  location            = azurerm_resource_group.covetpy.location
  resource_group_name = azurerm_resource_group.covetpy.name
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  redis_configuration {
    enable_authentication = true
  }
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "covetpy" {
  name                = "covetpy-aks"
  location            = azurerm_resource_group.covetpy.location
  resource_group_name = azurerm_resource_group.covetpy.name
  dns_prefix          = "covetpy"
  
  default_node_pool {
    name                = "default"
    node_count          = 3
    vm_size             = "Standard_D2s_v3"
    type                = "VirtualMachineScaleSets"
    enable_auto_scaling = true
    min_count           = 1
    max_count           = 5
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  network_profile {
    network_plugin = "azure"
  }
  
  monitor_metrics {}
}

# Grant AKS access to ACR
resource "azurerm_role_assignment" "acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.covetpy.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.covetpy.id
  skip_service_principal_aad_check = true
}

# App Service Plan
resource "azurerm_service_plan" "covetpy" {
  name                = "covetpy-plan"
  resource_group_name = azurerm_resource_group.covetpy.name
  location            = azurerm_resource_group.covetpy.location
  os_type             = "Linux"
  sku_name            = "P1v3"
}

# Linux Web App
resource "azurerm_linux_web_app" "covetpy" {
  name                = "covetpy-webapp"
  resource_group_name = azurerm_resource_group.covetpy.name
  location            = azurerm_service_plan.covetpy.location
  service_plan_id     = azurerm_service_plan.covetpy.id
  
  site_config {
    always_on = true
    
    application_stack {
      docker_image     = "${azurerm_container_registry.covetpy.login_server}/covetpy-app"
      docker_image_tag = "latest"
    }
    
    health_check_path = "/health"
  }
  
  app_settings = {
    ENVIRONMENT                         = "production"
    DATABASE_URL                        = "postgresql://${azurerm_postgresql_flexible_server.covetpy.administrator_login}:${var.db_password}@${azurerm_postgresql_flexible_server.covetpy.fqdn}:5432/${azurerm_postgresql_flexible_server_database.covetpy.name}"
    SECRET_KEY                          = var.secret_key
    DOCKER_REGISTRY_SERVER_URL          = azurerm_container_registry.covetpy.login_server
    DOCKER_REGISTRY_SERVER_USERNAME     = azurerm_container_registry.covetpy.admin_username
    DOCKER_REGISTRY_SERVER_PASSWORD     = azurerm_container_registry.covetpy.admin_password
  }
  
  identity {
    type = "SystemAssigned"
  }
}

# Application Insights
resource "azurerm_application_insights" "covetpy" {
  name                = "covetpy-insights"
  location            = azurerm_resource_group.covetpy.location
  resource_group_name = azurerm_resource_group.covetpy.name
  application_type    = "web"
}

# Key Vault
resource "azurerm_key_vault" "covetpy" {
  name                = "covetpy-kv"
  location            = azurerm_resource_group.covetpy.location
  resource_group_name = azurerm_resource_group.covetpy.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    
    secret_permissions = [
      "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"
    ]
  }
  
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_linux_web_app.covetpy.identity[0].principal_id
    
    secret_permissions = [
      "Get", "List"
    ]
  }
}

data "azurerm_client_config" "current" {}

# Store secrets in Key Vault
resource "azurerm_key_vault_secret" "database_url" {
  name         = "database-url"
  value        = "postgresql://${azurerm_postgresql_flexible_server.covetpy.administrator_login}:${var.db_password}@${azurerm_postgresql_flexible_server.covetpy.fqdn}:5432/${azurerm_postgresql_flexible_server_database.covetpy.name}"
  key_vault_id = azurerm_key_vault.covetpy.id
}

resource "azurerm_key_vault_secret" "secret_key" {
  name         = "secret-key"
  value        = var.secret_key
  key_vault_id = azurerm_key_vault.covetpy.id
}
```

### Variables and Outputs

```hcl
# variables.tf
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}
```

```hcl
# outputs.tf
output "webapp_url" {
  value = azurerm_linux_web_app.covetpy.default_hostname
}

output "acr_login_server" {
  value = azurerm_container_registry.covetpy.login_server
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.covetpy.name
}

output "database_fqdn" {
  value = azurerm_postgresql_flexible_server.covetpy.fqdn
}
```

## Monitoring and Logging

### 1. Application Insights Setup

```python
# Add to app/main.py
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace import config_integration

# Configure Application Insights
config_integration.trace_integrations(['requests', 'sqlalchemy'])

exporter = AzureExporter(
    connection_string="InstrumentationKey=your-instrumentation-key"
)

# Add telemetry middleware
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
middleware = FlaskMiddleware(app, exporter=exporter, sampler=ProbabilitySampler(1.0))
```

### 2. Log Analytics Workspace

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group covetpy-rg \
    --workspace-name covetpy-logs \
    --location eastus

# Link AKS to Log Analytics
az aks enable-addons \
    --resource-group covetpy-rg \
    --name covetpy-aks \
    --addons monitoring \
    --workspace-resource-id $(az monitor log-analytics workspace show --resource-group covetpy-rg --workspace-name covetpy-logs --query id -o tsv)
```

### 3. Custom Metrics and Alerts

```bash
# Create action group
az monitor action-group create \
    --resource-group covetpy-rg \
    --name covetpy-alerts \
    --short-name covetpy \
    --email-receiver name=admin email=admin@yourdomain.com

# Create metric alert
az monitor metrics alert create \
    --name "High CPU Usage" \
    --resource-group covetpy-rg \
    --scopes $(az webapp show --resource-group covetpy-rg --name covetpy-webapp --query id -o tsv) \
    --condition "avg Percentage CPU > 80" \
    --window-size 5m \
    --evaluation-frequency 1m \
    --action covetpy-alerts \
    --description "Alert when CPU usage is high"
```

## Security Best Practices

### 1. Managed Identity and RBAC

```bash
# Enable managed identity for webapp
az webapp identity assign \
    --name covetpy-webapp \
    --resource-group covetpy-rg

# Grant Key Vault access
az keyvault set-policy \
    --name covetpy-kv \
    --resource-group covetpy-rg \
    --object-id $(az webapp identity show --name covetpy-webapp --resource-group covetpy-rg --query principalId -o tsv) \
    --secret-permissions get list
```

### 2. Network Security

```bash
# Create Network Security Group
az network nsg create \
    --resource-group covetpy-rg \
    --name covetpy-nsg \
    --location eastus

# Allow HTTP/HTTPS
az network nsg rule create \
    --resource-group covetpy-rg \
    --nsg-name covetpy-nsg \
    --name AllowHTTP \
    --protocol tcp \
    --priority 1000 \
    --destination-port-range 80 \
    --access allow

az network nsg rule create \
    --resource-group covetpy-rg \
    --nsg-name covetpy-nsg \
    --name AllowHTTPS \
    --protocol tcp \
    --priority 1001 \
    --destination-port-range 443 \
    --access allow
```

### 3. Private Endpoints

```bash
# Create private endpoint for PostgreSQL
az network private-endpoint create \
    --resource-group covetpy-rg \
    --name covetpy-db-pe \
    --vnet-name covetpy-vnet \
    --subnet internal \
    --private-connection-resource-id $(az postgres flexible-server show --resource-group covetpy-rg --name covetpy-db --query id -o tsv) \
    --group-ids postgresqlServer \
    --connection-name covetpy-db-connection \
    --location eastus
```

## Cost Optimization

### 1. Reserved Instances

```bash
# Purchase reserved VM instances
az reservations reservation-order purchase \
    --reserved-resource-type VirtualMachines \
    --sku Standard_D2s_v3 \
    --location eastus \
    --quantity 2 \
    --term P1Y \
    --billing-scope-id /subscriptions/{subscription-id}
```

### 2. Spot Instances in AKS

```bash
# Add spot node pool to AKS
az aks nodepool add \
    --resource-group covetpy-rg \
    --cluster-name covetpy-aks \
    --name spotnodepool \
    --node-count 3 \
    --node-vm-size Standard_D2s_v3 \
    --priority Spot \
    --eviction-policy Delete \
    --spot-max-price 0.1 \
    --enable-cluster-autoscaler \
    --min-count 0 \
    --max-count 5
```

### 3. Auto-shutdown for Dev/Test

```bash
# Set up auto-shutdown for VMs
az vm auto-shutdown \
    --resource-group covetpy-rg \
    --name covetpy-vm \
    --time 1900 \
    --email admin@yourdomain.com
```

## Deployment Automation

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  containerRegistry: 'covetpyregistry.azurecr.io'
  imageRepository: 'covetpy-app'
  dockerfilePath: 'Dockerfile.production'
  tag: '$(Build.BuildId)'

stages:
- stage: Build
  displayName: Build and push stage
  jobs:
  - job: Build
    displayName: Build
    steps:
    - task: Docker@2
      displayName: Build and push an image to container registry
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  jobs:
  - job: Deploy
    displayName: Deploy to Azure
    steps:
    - task: AzureWebApp@1
      displayName: 'Deploy to Azure Web App'
      inputs:
        azureSubscription: $(azureServiceConnection)
        appType: webAppForContainers
        appName: covetpy-webapp
        resourceGroupName: covetpy-rg
        imageName: $(containerRegistry)/$(imageRepository):$(tag)
```

### GitHub Actions

```yaml
# .github/workflows/deploy-azure.yml
name: Deploy to Azure

on:
  push:
    branches: [main]

env:
  AZURE_WEBAPP_NAME: covetpy-webapp
  AZURE_GROUP: covetpy-rg

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@v3

    - name: 'Login via Azure CLI'
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: 'Build and push image'
      uses: azure/docker-login@v1
      with:
        login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - run: |
        docker build -f Dockerfile.production -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/covetpy-app:${{ github.sha }} .
        docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/covetpy-app:${{ github.sha }}

    - name: 'Deploy to Azure Web App'
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        images: ${{ secrets.REGISTRY_LOGIN_SERVER }}/covetpy-app:${{ github.sha }}
```

This comprehensive Azure deployment guide covers multiple deployment strategies for CovetPy applications on Microsoft Azure, from simple Container Instances to full AKS orchestration with comprehensive monitoring and security features.