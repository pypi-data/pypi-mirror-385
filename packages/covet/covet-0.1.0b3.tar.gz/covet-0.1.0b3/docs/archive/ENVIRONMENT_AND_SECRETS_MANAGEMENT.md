# CovetPy Framework - Environment Variables and Secrets Management

## Table of Contents
1. [Configuration Philosophy](#configuration-philosophy)
2. [Environment Variables](#environment-variables)
3. [Secrets Management](#secrets-management)
4. [Configuration Sources](#configuration-sources)
5. [Security Best Practices](#security-best-practices)
6. [Cloud Provider Integration](#cloud-provider-integration)
7. [Development vs Production](#development-vs-production)
8. [Configuration Validation](#configuration-validation)

## Configuration Philosophy

The CovetPy Framework follows the **12-Factor App** methodology for configuration management:

1. **Strict separation** of config from code
2. **Environment-based** configuration
3. **No secrets in code** or version control
4. **Type-safe** configuration with validation
5. **Multiple sources** with precedence rules
6. **Hot-reload** support for development

## Environment Variables

### Basic Usage

```python
from covet import CovetPy
from covet.config import Config, env

# Simple environment variable access
DEBUG = env('DEBUG', default=False, cast=bool)
DATABASE_URL = env('DATABASE_URL', required=True)
PORT = env('PORT', default=8000, cast=int)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost', cast=list)

app = CovetPy(
    debug=DEBUG,
    port=PORT,
    allowed_hosts=ALLOWED_HOSTS
)
```

### Type-Safe Configuration

```python
from covet.config import BaseConfig, EnvField
from typing import List, Optional

class AppConfig(BaseConfig):
    """Type-safe configuration with validation"""
    
    # Required fields
    database_url: str = EnvField('DATABASE_URL')
    secret_key: str = EnvField('SECRET_KEY')
    
    # Optional with defaults
    debug: bool = EnvField('DEBUG', default=False)
    port: int = EnvField('PORT', default=8000)
    workers: int = EnvField('WORKERS', default=4)
    
    # Complex types
    allowed_hosts: List[str] = EnvField(
        'ALLOWED_HOSTS',
        default=['localhost'],
        parser=lambda x: x.split(',')
    )
    
    redis_url: Optional[str] = EnvField('REDIS_URL', default=None)
    
    # Validation
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('workers')
    def validate_workers(cls, v):
        if v < 1:
            raise ValueError('Workers must be at least 1')
        return v

# Load configuration
config = AppConfig()

# Access with type safety
app = CovetPy(
    debug=config.debug,  # bool
    port=config.port,    # int
    workers=config.workers  # int
)
```

### Environment File Support

```python
# .env file
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1,example.com

# .env.local (overrides .env)
DEBUG=false
DATABASE_URL=postgresql://prod-db/myapp

# Load order (later overrides earlier):
# 1. .env
# 2. .env.{environment}
# 3. .env.local
# 4. .env.{environment}.local
# 5. System environment variables

from covet.config import load_env

# Automatic loading based on COVET_ENV
load_env()  # Loads appropriate .env files

# Or specify environment
load_env(env='production')
```

### Dynamic Configuration

```python
# Hot-reload configuration in development
from covet.config import ConfigManager

config_manager = ConfigManager(auto_reload=True)

@config_manager.on_change('DEBUG')
def handle_debug_change(old_value, new_value):
    """React to configuration changes"""
    if new_value:
        app.enable_debug_mode()
    else:
        app.disable_debug_mode()

# Watch for file changes
config_manager.watch_files(['.env', '.env.local'])
```

## Secrets Management

### Built-in Secrets Manager

```python
from covet.secrets import SecretsManager, Secret

# Initialize secrets manager
secrets = SecretsManager(
    provider='vault',  # or 'aws', 'azure', 'gcp', 'env'
    vault_url='https://vault.example.com',
    vault_token=env('VAULT_TOKEN')
)

# Define secrets
class AppSecrets(BaseConfig):
    database_password: Secret = secrets.secret('database/password')
    api_key: Secret = secrets.secret('external/api-key')
    jwt_secret: Secret = secrets.secret('auth/jwt-secret')
    encryption_key: bytes = secrets.secret(
        'crypto/master-key',
        decoder='base64'
    )

# Async secret loading
async def load_secrets():
    app_secrets = AppSecrets()
    await app_secrets.load()
    return app_secrets

# Use in application
@app.on_event('startup')
async def startup():
    app.secrets = await load_secrets()
    
    # Connect to database with secret
    app.db = await connect_db(
        url=f"postgresql://user:{app.secrets.database_password}@host/db"
    )
```

### HashiCorp Vault Integration

```python
from covet.secrets.vault import VaultProvider

# Configure Vault provider
vault = VaultProvider(
    url='https://vault.example.com',
    token=env('VAULT_TOKEN'),
    namespace='myapp',
    mount_point='secret',
    cache_ttl=300  # Cache for 5 minutes
)

# Key-value secrets
db_creds = await vault.get('database/creds')
api_keys = await vault.get('api/keys')

# Dynamic secrets (database credentials)
dynamic_creds = await vault.get_dynamic(
    'database/creds/readonly',
    ttl='1h'
)

# PKI certificates
cert_data = await vault.get_certificate(
    'pki/issue/web-server',
    common_name='api.example.com'
)

# Encryption as a service
encrypted = await vault.encrypt(
    'transit/encrypt/myapp',
    plaintext=b'sensitive data'
)
decrypted = await vault.decrypt(
    'transit/decrypt/myapp',
    ciphertext=encrypted
)
```

### AWS Secrets Manager

```python
from covet.secrets.aws import AWSSecretsProvider

# Configure AWS Secrets Manager
aws_secrets = AWSSecretsProvider(
    region='us-east-1',
    cache_config={
        'cache_enabled': True,
        'cache_item_ttl': 3600,
        'max_cache_size': 1024
    }
)

# Get secret
db_secret = await aws_secrets.get('prod/myapp/database')

# Automatic rotation support
@aws_secrets.on_rotation('prod/myapp/database')
async def handle_db_rotation(old_secret, new_secret):
    """Handle database password rotation"""
    await app.db.update_password(new_secret['password'])
    await app.db.reconnect()
```

### Azure Key Vault

```python
from covet.secrets.azure import AzureKeyVaultProvider

# Configure Azure Key Vault
azure_vault = AzureKeyVaultProvider(
    vault_url='https://myapp.vault.azure.net/',
    credential=DefaultAzureCredential(),
    cache_ttl=300
)

# Get secrets
api_key = await azure_vault.get_secret('api-key')
cert = await azure_vault.get_certificate('web-cert')
key = await azure_vault.get_key('encryption-key')

# Use with managed identity
azure_vault_mi = AzureKeyVaultProvider(
    vault_url='https://myapp.vault.azure.net/',
    use_managed_identity=True
)
```

### Google Secret Manager

```python
from covet.secrets.gcp import GCPSecretProvider

# Configure GCP Secret Manager
gcp_secrets = GCPSecretProvider(
    project_id='my-project',
    cache_duration=300
)

# Get secret
secret = await gcp_secrets.get('myapp-database-password')

# Get specific version
secret_v2 = await gcp_secrets.get('myapp-api-key', version='2')

# List secrets
all_secrets = await gcp_secrets.list_secrets()
```

## Configuration Sources

### Hierarchical Configuration

```python
from covet.config import ConfigBuilder

# Build configuration from multiple sources
config = ConfigBuilder()\
    .add_env_file('.env')\
    .add_env_file('.env.local', optional=True)\
    .add_yaml_file('config.yaml')\
    .add_json_file('secrets.json', optional=True)\
    .add_env_vars(prefix='MYAPP_')\
    .add_secrets_manager(vault)\
    .add_consul('config/myapp/')\
    .build()

# Priority order (highest to lowest):
# 1. Command-line arguments
# 2. Environment variables
# 3. Secrets managers
# 4. Consul/etcd
# 5. Local config files
# 6. Default values
```

### YAML Configuration

```yaml
# config.yaml
app:
  name: MyApp
  version: 1.0.0
  debug: false

server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  
database:
  host: localhost
  port: 5432
  name: myapp
  # Password from environment variable
  password: ${DATABASE_PASSWORD}
  
redis:
  url: redis://localhost:6379
  
features:
  - authentication
  - rate_limiting
  - caching
```

```python
# Load YAML config
from covet.config import YamlConfig

config = YamlConfig('config.yaml')

# Access nested values
app_name = config.get('app.name')
db_host = config.get('database.host')
features = config.get('features')

# With environment variable substitution
config = YamlConfig(
    'config.yaml',
    enable_env_substitution=True
)
```

### Consul Integration

```python
from covet.config.consul import ConsulConfig

# Configure Consul
consul = ConsulConfig(
    host='consul.example.com',
    port=8500,
    prefix='myapp/',
    watch=True  # Auto-reload on changes
)

# Get configuration
db_config = await consul.get('database')
feature_flags = await consul.get('features')

# Watch for changes
@consul.on_change('features/new_ui')
async def handle_feature_change(old_value, new_value):
    if new_value:
        await app.enable_new_ui()
```

## Security Best Practices

### Secure Defaults

```python
from covet.config import SecureConfig

class ProductionConfig(SecureConfig):
    """Production configuration with security enforcements"""
    
    # Enforce HTTPS
    force_https: bool = True
    
    # Security headers
    security_headers: dict = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # Session security
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = 'Lax'
    
    # Required secrets
    secret_key: str = SecureField(
        env='SECRET_KEY',
        min_length=32,
        validator=validate_secret_strength
    )
    
    # Database encryption
    database_encryption_key: bytes = SecureField(
        env='DB_ENCRYPTION_KEY',
        decoder='base64',
        length=32  # 256 bits
    )
```

### Secret Validation

```python
from covet.config import validate_secrets

@validate_secrets
class APIConfig:
    """Validate secrets meet security requirements"""
    
    api_key: str = EnvField(
        'API_KEY',
        validator=lambda x: len(x) >= 32 and x.isalnum()
    )
    
    jwt_secret: str = EnvField(
        'JWT_SECRET',
        validator=lambda x: validate_jwt_secret(x)
    )
    
    encryption_key: bytes = EnvField(
        'ENCRYPTION_KEY',
        decoder='base64',
        validator=lambda x: len(x) == 32  # 256-bit key
    )

def validate_jwt_secret(secret: str) -> bool:
    """Ensure JWT secret is strong enough"""
    if len(secret) < 64:
        raise ValueError("JWT secret must be at least 64 characters")
    
    # Check entropy
    import math
    entropy = calculate_entropy(secret)
    if entropy < 4.0:
        raise ValueError("JWT secret has insufficient entropy")
    
    return True
```

### Secret Rotation

```python
from covet.secrets import SecretRotation

# Configure automatic rotation
rotation = SecretRotation(
    secrets_manager=vault,
    rotation_interval=timedelta(days=30)
)

# Define rotation handlers
@rotation.handler('database/password')
async def rotate_db_password(old_secret, new_secret):
    """Handle database password rotation"""
    # Update application
    await app.db.update_password(new_secret)
    
    # Update other services
    await update_backup_service(new_secret)
    await update_monitoring(new_secret)
    
    # Verify connectivity
    await app.db.test_connection()

# Schedule rotation
await rotation.schedule('database/password')
await rotation.schedule('api/keys', interval=timedelta(days=90))

# Manual rotation
await rotation.rotate_now('encryption/keys')
```

## Cloud Provider Integration

### AWS Parameter Store

```python
from covet.config.aws import ParameterStoreConfig

# Configure Parameter Store
ps_config = ParameterStoreConfig(
    region='us-east-1',
    prefix='/myapp/',
    decrypt=True,
    cache_ttl=300
)

# Get parameters
db_config = await ps_config.get_parameters([
    'database/host',
    'database/port',
    'database/name',
    'database/username',
    'database/password'
])

# Hierarchical parameters
all_config = await ps_config.get_parameters_by_path(
    '/myapp/production/',
    recursive=True
)
```

### Kubernetes ConfigMaps and Secrets

```python
from covet.config.k8s import KubernetesConfig

# Configure Kubernetes
k8s_config = KubernetesConfig(
    namespace='production',
    in_cluster=True  # Use pod service account
)

# Load from ConfigMap
config = await k8s_config.load_configmap('myapp-config')

# Load from Secret
secrets = await k8s_config.load_secret('myapp-secrets')

# Watch for changes
@k8s_config.watch_configmap('myapp-config')
async def handle_config_update(config):
    await app.reload_configuration(config)

# Mount as files
k8s_config.mount_secret(
    'tls-certs',
    mount_path='/etc/tls',
    items={
        'tls.crt': 'server.crt',
        'tls.key': 'server.key'
    }
)
```

### Docker Secrets

```python
from covet.config.docker import DockerSecretsConfig

# Configure Docker Secrets
docker_secrets = DockerSecretsConfig(
    secrets_path='/run/secrets'
)

# Load secrets
db_password = docker_secrets.get('db_password')
api_key = docker_secrets.get('api_key')

# Load all secrets
all_secrets = docker_secrets.load_all()

# Use in Docker Compose
"""
# docker-compose.yml
services:
  api:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
    
secrets:
  db_password:
    external: true
  api_key:
    file: ./secrets/api_key.txt
"""
```

## Development vs Production

### Environment-Specific Configuration

```python
from covet.config import config_for_env

# Base configuration
class BaseConfig:
    app_name: str = 'MyApp'
    api_version: str = 'v1'
    
class DevelopmentConfig(BaseConfig):
    debug: bool = True
    database_url: str = 'sqlite:///dev.db'
    cache_backend: str = 'memory'
    
class ProductionConfig(BaseConfig):
    debug: bool = False
    database_url: str = env('DATABASE_URL')
    cache_backend: str = 'redis'
    ssl_required: bool = True
    
class TestConfig(BaseConfig):
    testing: bool = True
    database_url: str = 'sqlite:///:memory:'
    
# Auto-select based on environment
config = config_for_env(
    development=DevelopmentConfig,
    production=ProductionConfig,
    test=TestConfig
)
```

### Local Development Tools

```python
# Development secrets management
from covet.config.dev import DevSecretsManager

# Use local file-based secrets in development
dev_secrets = DevSecretsManager(
    secrets_dir='.secrets',
    encryption_key=env('DEV_MASTER_KEY')
)

# Generate development secrets
await dev_secrets.generate_defaults({
    'jwt_secret': 64,  # Generate 64-char secret
    'api_key': 32,
    'encryption_key': 32
})

# Export for team sharing
await dev_secrets.export('dev-secrets.encrypted')

# Import on another machine
await dev_secrets.import_file('dev-secrets.encrypted')
```

## Configuration Validation

### Schema Validation

```python
from covet.config import ConfigSchema
from pydantic import BaseModel, validator

class DatabaseConfig(BaseModel):
    host: str
    port: int = 5432
    name: str
    username: str
    password: str
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Invalid port number')
        return v

class AppConfigSchema(ConfigSchema):
    debug: bool = False
    database: DatabaseConfig
    redis_url: str
    allowed_hosts: List[str]
    
    @validator('redis_url')
    def validate_redis_url(cls, v):
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('Invalid Redis URL')
        return v
    
    def validate(self):
        """Custom validation logic"""
        super().validate()
        
        if self.debug and 'production' in self.database.host:
            raise ValueError('Cannot use production database in debug mode')

# Load and validate
try:
    config = AppConfigSchema.from_env()
except ValidationError as e:
    print(f"Configuration errors: {e}")
    sys.exit(1)
```

### Runtime Validation

```python
from covet.config import RuntimeValidator

# Define validation rules
validator = RuntimeValidator()

@validator.rule('database.connections')
def check_db_connections(value, config):
    """Ensure connection pool size is appropriate"""
    max_workers = config.get('workers', 1) * 4
    if value > max_workers * 10:
        return f"Too many connections ({value}) for {max_workers} workers"

@validator.rule('cache.size')
def check_cache_size(value, config):
    """Validate cache size based on available memory"""
    import psutil
    available_memory = psutil.virtual_memory().available
    cache_bytes = parse_size(value)
    
    if cache_bytes > available_memory * 0.5:
        return "Cache size exceeds 50% of available memory"

# Run validation
errors = validator.validate(config)
if errors:
    for error in errors:
        logger.error(f"Config validation error: {error}")
```

### Health Checks

```python
from covet.config import ConfigHealthCheck

# Define health checks for configuration
health_check = ConfigHealthCheck()

@health_check.check('database')
async def check_database(config):
    """Verify database connectivity"""
    try:
        async with connect_db(config.database_url) as conn:
            await conn.execute('SELECT 1')
        return True, "Database connection OK"
    except Exception as e:
        return False, f"Database error: {e}"

@health_check.check('redis')
async def check_redis(config):
    """Verify Redis connectivity"""
    try:
        redis = await aioredis.create_redis_pool(config.redis_url)
        await redis.ping()
        return True, "Redis connection OK"
    except Exception as e:
        return False, f"Redis error: {e}"

@health_check.check('external_api')
async def check_api(config):
    """Verify external API key"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://api.example.com/validate',
            headers={'Authorization': f'Bearer {config.api_key}'}
        )
        if response.status_code == 200:
            return True, "API key valid"
        return False, f"API key invalid: {response.status_code}"

# Run health checks
@app.on_event('startup')
async def startup_checks():
    results = await health_check.run_all(config)
    for check_name, (success, message) in results.items():
        if not success:
            logger.error(f"Config check failed: {check_name} - {message}")
            if not config.debug:
                sys.exit(1)
```

## Best Practices Summary

1. **Never commit secrets** to version control
2. **Use environment-specific** configuration files
3. **Validate configuration** at startup
4. **Implement secret rotation** for production
5. **Use type-safe configuration** classes
6. **Cache secrets appropriately** to reduce API calls
7. **Monitor configuration changes** in production
8. **Encrypt sensitive configuration** at rest
9. **Use least privilege** for secret access
10. **Audit configuration access** and changes

This comprehensive configuration and secrets management system ensures your CovetPy applications remain secure, maintainable, and scalable across all environments.