# Rabbit Admin

A modern, production-ready admin dashboard for FastAPI applications using Tortoise ORM. Automatically generates CRUD interfaces for your database models with a beautiful Quasar-based frontend.

## Features

- 🚀 **Auto-generated CRUD interfaces** - Register your Tortoise ORM models and get full CRUD functionality
- 🎨 **Modern UI** - Built with Quasar Framework (Vue.js)
- 🔗 **Relations Support** - Handles ForeignKey and ManyToMany relationships
- 📝 **Field Types** - Supports all common field types including JSON, DateTime, Boolean, and more
- 🎯 **Easy Integration** - Mount to any existing FastAPI application
- 📦 **Zero Configuration** - Works out of the box with sensible defaults

## Installation

### From PyPI (when published)

```bash
pip install rabbit-admin
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/rabbit-admin.git
cd rabbit-admin/backend

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

## Quick Start

### 1. Define Your Models

```python
from tortoise import fields, models

class Product(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    price = fields.FloatField()
    is_available = fields.BooleanField(default=True)
    
    def __str__(self):
        return self.name
```

### 2. Set Up Your FastAPI Application

```python
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from rabbit_admin import admin_app
from contextlib import asynccontextmanager

# Import your models
from your_app.models import Product, Category

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register your models with admin
    await admin_app.register(Product)
    await admin_app.register(Category)
    
    yield

app = FastAPI(lifespan=lifespan)

# Mount the admin router and UI
app.include_router(admin_app.router)
admin_app.mount_ui(app, path="/dash")

# Configure Tortoise ORM
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://./db.sqlite3"
        # Or use PostgreSQL: "postgres://user:pass@localhost:5432/dbname"
    },
    "apps": {
        "models": {
            "models": ["your_app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
```

### 3. Run Your Application

```bash
uvicorn your_app.main:app --reload
```

### 4. Access the Admin Dashboard

Navigate to:
- Admin API: `http://localhost:8000/api/admin/_models`
- Admin UI: `http://localhost:8000/dash` (mounted via admin_app.mount_ui)
- API Docs: `http://localhost:8000/docs`

## Advanced Usage

### Custom Admin Base URL

```python
from rabbit_admin.adminV2 import AdminRegistry

# Create admin with custom base URL
custom_admin = AdminRegistry(base_url="/custom-admin")

# Register models
await custom_admin.register(YourModel)

# Mount to app
app.include_router(custom_admin.router)
```

### Serving the Admin UI

The admin UI is a pre-built Quasar application. To serve it, use the `mount_ui` method:

```python
# Mount the admin UI (do this AFTER including the router)
app.include_router(admin_app.router)
admin_app.mount_ui(app, path="/dash")
```

You can customize the mount path:

```python
# Mount at a different path
admin_app.mount_ui(app, path="/admin-ui")
# UI will be available at http://localhost:8000/admin-ui
```

**Note**: The static files are automatically included in the package installation. The `mount_ui` method handles finding and serving them correctly.

### Model Registration Options

```python
# Simple registration
await admin_app.register(Product)

# Register multiple models
for model in [Product, Category, Order]:
    await admin_app.register(model)
```

## API Endpoints

Once registered, each model gets the following endpoints:

- `GET /api/admin/{model_name}` - List all records
- `POST /api/admin/{model_name}` - Create a new record
- `GET /api/admin/{model_name}/{id}` - Get a specific record
- `PUT /api/admin/{model_name}/{id}` - Update a record
- `DELETE /api/admin/{model_name}/{id}` - Delete a record
- `GET /api/admin/{model_name}/form` - Get form schema for the model
- `GET /api/admin/_models` - Get all registered models

## Supported Field Types

- **IntField** - Integer numbers
- **CharField** - Short text
- **TextField** - Long text
- **FloatField** - Decimal numbers
- **BooleanField** - True/False
- **DatetimeField** - Date and time
- **DateField** - Date only
- **TimeField** - Time only
- **JSONField** - JSON data
- **ForeignKeyField** - Foreign key relationships
- **ManyToManyField** - Many-to-many relationships

## Example Application

See `example_app.py` in the repository for a complete working example.

```bash
# Run the example
cd backend
python example_app.py
```

## Development

### Project Structure

```
backend/
├── __init__.py          # Package initialization
├── adminV2.py           # Core admin functionality
├── admin.py             # Legacy admin (V1)
├── decor.py             # Decorators and utilities
├── models.py            # Empty - for your models
├── example_app.py       # Example application
├── static/              # Frontend build files
├── setup.py             # Package setup
└── README.md            # This file
```

### Building the Frontend

The frontend is built using Quasar Framework:

```bash
cd frontend
npm install
npm run build  # or: quasar build

# The build output goes to backend/static/
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Requirements

- Python >= 3.8
- FastAPI >= 0.104.0
- Tortoise ORM >= 0.20.0
- Pydantic >= 2.0.0

## CORS Configuration

For development with a separate frontend server:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Models not appearing in admin

- Ensure you've registered the model: `await admin_app.register(YourModel)`
- Check that Tortoise ORM is properly initialized
- Verify the model is imported before registration

### Frontend not loading

- Ensure you've called `admin_app.mount_ui(app, path="/dash")`
- Mount the UI AFTER including the router: `app.include_router(admin_app.router)`
- Verify the UI is accessible at the correct path (e.g., `http://localhost:8000/dash`)
- Check that the static files are included in your package installation

### CORS errors

- Add your frontend URL to CORS allowed origins
- Ensure CORS middleware is added before routes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Credits

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database ORM: [Tortoise ORM](https://tortoise.github.io/)
- Frontend: [Quasar Framework](https://quasar.dev/)

## Support

For issues, questions, or contributions, please visit:
- GitHub: https://github.com/yourusername/rabbit-admin
- Issues: https://github.com/yourusername/rabbit-admin/issues

