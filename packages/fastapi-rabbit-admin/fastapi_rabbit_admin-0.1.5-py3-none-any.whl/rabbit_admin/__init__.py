"""
Rabbit Admin - A FastAPI admin dashboard for Tortoise ORM models

This package provides a ready-to-use admin interface for your FastAPI applications
that use Tortoise ORM for database operations.

Usage:
    from rabbit_admin import admin_app
    
    # In your FastAPI app:
    app.include_router(admin_app.router)
    
    # Mount the admin UI (static files):
    admin_app.mount_ui(app, path="/dash")
    
    # Register your models:
    await admin_app.register(YourModel)
"""

from pathlib import Path
from .adminV2 import admin_app, AdminRegistry

__version__ = "0.1.0"
__all__ = ["admin_app", "AdminRegistry", "get_static_dir"]


def get_static_dir():
    """
    Get the path to the static files directory for the admin UI.
    
    Usage:
        from fastapi.staticfiles import StaticFiles
        from rabbit_admin import get_static_dir
        
        app.mount("/", StaticFiles(directory=get_static_dir(), html=True), name="static")
    
    Returns:
        Path: Path object pointing to the static directory
    """
    return Path(__file__).parent / "static"

