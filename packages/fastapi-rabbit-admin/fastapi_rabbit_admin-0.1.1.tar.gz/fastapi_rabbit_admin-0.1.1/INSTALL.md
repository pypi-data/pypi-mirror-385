# Installation Guide for Rabbit Admin

## For Package Users

### Install from PyPI (Coming Soon)

```bash
pip install rabbit-admin
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/rabbit-admin.git
cd rabbit-admin/backend

# Install the package
pip install .

# Or install in development mode
pip install -e .
```

## For Package Developers

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rabbit-admin.git
   cd rabbit-admin/backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in editable mode with dev dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the example application**
   ```bash
   python example_app.py
   ```

### Building the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# - dist/rabbit_admin-0.1.0-py3-none-any.whl
# - dist/rabbit-admin-0.1.0.tar.gz
```

### Publishing to PyPI

```bash
# Test PyPI (recommended first)
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

## Mounting to Existing FastAPI Apps

### Basic Integration

```python
from fastapi import FastAPI
from rabbit_admin import admin_app

app = FastAPI()

# Register your models
@app.on_event("startup")
async def startup():
    from your_app.models import Product, Category
    
    await admin_app.register(Product)
    await admin_app.register(Category)
    
    # Mount admin router
    app.include_router(admin_app.router)
```

### With Custom Prefix

```python
from rabbit_admin.adminV2 import AdminRegistry

# Create admin with custom prefix
custom_admin = AdminRegistry(base_url="/custom-admin")

@app.on_event("startup")
async def startup():
    await custom_admin.register(YourModel)
    app.include_router(custom_admin.router)

# Admin will be available at /custom-admin/_models
```

### With Static Files

```python
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

# Get the static files directory from the package
static_dir = Path(__file__).parent / "node_modules" / "rabbit-admin" / "static"

# Or if installed via pip:
import rabbit_admin
static_dir = Path(rabbit_admin.__file__).parent / "static"

# Mount admin API first
app.include_router(admin_app.router)

# Then mount static files (must be last to avoid catching API routes)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
```

## Database Setup

### SQLite (Development)

```python
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://./db.sqlite3"
    },
    "apps": {
        "models": {
            "models": ["your_app.models"],
            "default_connection": "default",
        },
    },
}
```

### PostgreSQL (Production)

```python
TORTOISE_ORM = {
    "connections": {
        "default": "postgres://user:password@localhost:5432/dbname"
    },
    "apps": {
        "models": {
            "models": ["your_app.models"],
            "default_connection": "default",
        },
    },
}
```

### MySQL

```python
TORTOISE_ORM = {
    "connections": {
        "default": "mysql://user:password@localhost:3306/dbname"
    },
    "apps": {
        "models": {
            "models": ["your_app.models"],
            "default_connection": "default",
        },
    },
}
```

## Frontend Development

If you want to customize the frontend:

```bash
cd ../frontend
npm install
npm run dev  # Development server

# Build for production
npm run build
# Output goes to backend/static/
```

## Troubleshooting

### Package not found

Ensure you've activated your virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Static files not found

Make sure static files are included in the package:
```bash
python setup.py sdist bdist_wheel
```

Check MANIFEST.in includes static files.

### Database errors

Ensure Tortoise ORM is properly initialized before registering models:
```python
from tortoise.contrib.fastapi import register_tortoise

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/rabbit-admin/issues
- Documentation: https://github.com/yourusername/rabbit-admin

