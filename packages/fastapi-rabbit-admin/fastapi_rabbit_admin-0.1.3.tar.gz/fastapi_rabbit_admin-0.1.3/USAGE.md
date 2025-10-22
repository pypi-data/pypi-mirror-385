# Usage Guide for Rabbit Admin

This guide covers different ways to use and integrate Rabbit Admin into your FastAPI applications.

## Table of Contents

1. [Basic Integration](#basic-integration)
2. [With Lifespan Events](#with-lifespan-events)
3. [Custom Admin Prefix](#custom-admin-prefix)
4. [Serving Static Files](#serving-static-files)
5. [Multiple Admin Instances](#multiple-admin-instances)
6. [Production Deployment](#production-deployment)

## Basic Integration

The simplest way to add Rabbit Admin to your existing FastAPI app:

```python
from fastapi import FastAPI
from rabbit_admin import admin_app
from your_app.models import Product, Category

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Register your models
    await admin_app.register(Product)
    await admin_app.register(Category)
    
    # Mount the admin router
    app.include_router(admin_app.router)
```

## With Lifespan Events

Using the modern lifespan pattern (recommended):

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rabbit_admin import admin_app
from your_app.models import Product, Category

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await admin_app.register(Product)
    await admin_app.register(Category)
    app.include_router(admin_app.router)
    
    yield
    
    # Shutdown (cleanup if needed)

app = FastAPI(lifespan=lifespan)
```

## Custom Admin Prefix

Change the admin URL prefix:

```python
from rabbit_admin import AdminRegistry

# Create a custom admin instance with different base URL
custom_admin = AdminRegistry(base_url="/my-admin")

@app.on_event("startup")
async def startup():
    await custom_admin.register(YourModel)
    app.include_router(custom_admin.router)

# Admin will be available at:
# /my-admin/_models
# /my-admin/YourModel
```

## Serving Static Files

To serve the admin UI frontend:

```python
from fastapi.staticfiles import StaticFiles
from rabbit_admin import admin_app, get_static_dir

app = FastAPI()

# Register models and mount admin API
@app.on_event("startup")
async def startup():
    await admin_app.register(YourModel)
    app.include_router(admin_app.router)

# Mount static files LAST to avoid catching API routes
app.mount("/", StaticFiles(directory=get_static_dir(), html=True), name="static")
```

**Important**: Mount static files AFTER mounting the admin router to prevent static files from catching API routes.

## Multiple Admin Instances

You can create multiple admin instances for different purposes:

```python
from rabbit_admin import AdminRegistry

# Public admin with limited models
public_admin = AdminRegistry(base_url="/api/public-admin")

# Internal admin with all models
internal_admin = AdminRegistry(base_url="/api/internal-admin")

@app.on_event("startup")
async def startup():
    # Public admin - only safe models
    await public_admin.register(Product)
    await public_admin.register(Category)
    
    # Internal admin - all models including sensitive ones
    await internal_admin.register(User)
    await internal_admin.register(Order)
    await internal_admin.register(Product)
    
    app.include_router(public_admin.router)
    app.include_router(internal_admin.router)
```

## Production Deployment

### 1. Environment-based Configuration

```python
import os
from fastapi import FastAPI
from rabbit_admin import admin_app

# Database configuration from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite://./db.sqlite3"  # Development default
)

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["your_app.models"],
            "default_connection": "default",
        },
    },
}
```

### 2. With Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple HTTP Basic auth for admin"""
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return credentials.username

# Protect admin routes
@app.on_event("startup")
async def startup():
    await admin_app.register(YourModel)
    
    # Apply authentication to all admin routes
    app.include_router(
        admin_app.router,
        dependencies=[Depends(verify_admin)]
    )
```

### 3. Behind a Reverse Proxy

If you're running behind nginx or similar:

```python
# Ensure the admin knows its base path
admin_app = AdminRegistry(base_url="/admin/api")

# In your nginx config:
# location /admin/ {
#     proxy_pass http://localhost:8000/admin/;
# }
```

## Complete Example

Here's a complete, production-ready example:

```python
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager
from rabbit_admin import admin_app, get_static_dir

# Your models
from your_app.models import Product, Category, Order

# Database config
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://./db.sqlite3")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["your_app.models"],
            "default_connection": "default",
        },
    },
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await admin_app.register(Product)
    await admin_app.register(Category)
    await admin_app.register(Order)
    app.include_router(admin_app.router)
    
    yield
    # Shutdown

app = FastAPI(
    title="My Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for development
if os.getenv("ENV") == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:9000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize database
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# Your API routes
@app.get("/")
async def root():
    return {"message": "API is running", "docs": "/docs"}

# Serve admin UI (in production)
if os.getenv("SERVE_ADMIN_UI", "false").lower() == "true":
    app.mount("/", StaticFiles(directory=get_static_dir(), html=True), name="static")
```

## Environment Variables

Example `.env` file:

```bash
# Development
ENV=development
DATABASE_URL=sqlite://./db.sqlite3
SERVE_ADMIN_UI=true

# Production
# ENV=production
# DATABASE_URL=postgresql://user:password@localhost/dbname
# SERVE_ADMIN_UI=true
```

## Docker Deployment

Example `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Example `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db/dbname
      - SERVE_ADMIN_UI=true
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Customization

### Custom Model Display Name

Customize how your model appears in the admin:

```python
class Product(models.Model):
    name = fields.CharField(max_length=255)
    
    class Meta:
        table = "products"  # Custom table name
    
    def __str__(self):
        return self.name  # This is used as the display name
```

### Field Ordering

Fields are displayed in the order they're defined in your model.

## API Reference

### AdminRegistry

```python
from rabbit_admin import AdminRegistry

admin = AdminRegistry(base_url="/api/admin")

# Register a model
await admin.register(YourModel)

# Get registered models info
info = await admin.get_registered_models_info()
```

### admin_app

Pre-configured global admin instance:

```python
from rabbit_admin import admin_app

# Use directly
await admin_app.register(YourModel)
app.include_router(admin_app.router)
```

## Best Practices

1. **Register models during startup** - Use lifespan events or `@app.on_event("startup")`
2. **Mount API routes first** - Always mount admin router before static files
3. **Use authentication in production** - Protect admin routes with proper auth
4. **Database migrations** - Use Aerich or Alembic for database migrations
5. **Environment configuration** - Use environment variables for sensitive config
6. **Logging** - Enable logging to track admin operations

## Troubleshooting

See [README.md](README.md#troubleshooting) for common issues and solutions.

## Further Reading

- [Quick Start Guide](QUICKSTART.md)
- [Installation Guide](INSTALL.md)
- [Example Application](example_app.py)
- [API Documentation](http://localhost:8000/docs) (when running)

