# Quick Start Guide

Get started with Rabbit Admin in 5 minutes!

## 1. Installation

```bash
pip install rabbit-admin
```

Or install from source:
```bash
git clone https://github.com/yourusername/rabbit-admin.git
cd rabbit-admin/backend
pip install -e .
```

## 2. Create Your Models

Create a file `models.py`:

```python
from tortoise import fields, models

class Product(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    price = fields.FloatField()
    description = fields.TextField(null=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    
    def __str__(self):
        return self.name
```

## 3. Create Your FastAPI App

Create a file `app.py`:

```python
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager
from rabbit_admin import admin_app

# Import your models
from models import Product, Category

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register models with admin
    await admin_app.register(Product)
    await admin_app.register(Category)
    
    # Mount admin router
    app.include_router(admin_app.router)
    
    yield

# Create app
app = FastAPI(lifespan=lifespan)

# Configure database
TORTOISE_ORM = {
    "connections": {"default": "sqlite://./db.sqlite3"},
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        },
    },
}

# Initialize Tortoise
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# Your API routes
@app.get("/")
async def root():
    return {"message": "API with Rabbit Admin", "admin": "/api/admin/_models"}
```

## 4. Run Your App

```bash
uvicorn app:app --reload
```

## 5. Access the Admin

Open your browser:

- **API Docs**: http://localhost:8000/docs
- **Admin API**: http://localhost:8000/api/admin/_models
- **List Products**: http://localhost:8000/api/admin/Product
- **Create Product**: POST to http://localhost:8000/api/admin/Product

## 6. Serve the Admin UI (Optional)

To serve the frontend UI:

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import rabbit_admin

# Get static directory from package
static_dir = Path(rabbit_admin.__file__).parent / "static"

# Mount static files (do this AFTER mounting admin router)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
```

Now visit http://localhost:8000 for the admin UI!

## Example CRUD Operations

### Create a Product

```bash
curl -X POST "http://localhost:8000/api/admin/Product" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product",
    "fields": [
      {"name": "name", "data": "Laptop"},
      {"name": "price", "data": 999.99},
      {"name": "description", "data": "A great laptop"}
    ]
  }'
```

### List Products

```bash
curl "http://localhost:8000/api/admin/Product"
```

### Get a Specific Product

```bash
curl "http://localhost:8000/api/admin/Product/1"
```

### Update a Product

```bash
curl -X PUT "http://localhost:8000/api/admin/Product/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product",
    "fields": [
      {"name": "name", "data": "Updated Laptop"},
      {"name": "price", "data": 899.99}
    ]
  }'
```

### Delete a Product

```bash
curl -X DELETE "http://localhost:8000/api/admin/Product/1"
```

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Check out [example_app.py](example_app.py) for a complete example
- Customize the admin by extending the AdminRegistry class

## Common Issues

### "Module not found: rabbit_admin"

Make sure you've installed the package:
```bash
pip install -e .  # If developing locally
```

### Database errors

Ensure Tortoise ORM is initialized before registering models.

### CORS errors in development

Add CORS middleware to your FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Support

- GitHub: https://github.com/yourusername/rabbit-admin
- Issues: https://github.com/yourusername/rabbit-admin/issues

