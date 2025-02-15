"""
    Home route for the API.
"""

from fastapi import APIRouter, Request
import sys
import pkg_resources

router = APIRouter()


@router.get("/")
async def home(request: Request):
    """
    Returns metadata about the API:
    - API Name & Version
    - Author
    - Python Version
    - Installed Libraries & Versions
    - Available Endpoints
    """
    api_info = {
        "name": "Similarity Detection API",
        "version": "1.0.0",
        "author": "GabrielEValenzuela",
        "description": "A FastAPI microservice for detecting entity similarity in knowledge graphs.",
        "python_version": sys.version.split()[0],
    }

    # List installed packages (like `pip freeze`)
    installed_packages = {
        pkg.key: pkg.version for pkg in pkg_resources.working_set
    }

    # Dynamically fetch available endpoints
    routes_info = [
        {"path": route.path, "methods": list(route.methods)}
        for route in request.app.routes
    ]

    return {
        "message": "Welcome to the Similarity Detection API!",
        "api_info": api_info,
        "dependencies": installed_packages,
        "endpoints": routes_info,
        "status": "✅ UP and running!"
    }
