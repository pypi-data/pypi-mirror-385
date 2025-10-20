"""
FastAPI REST API for PyArchInit-Mini
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .site import router as site_router
from .us import router as us_router
from .inventario import router as inventario_router
from .auth import router as auth_router
from .graphml import router as graphml_router

def create_app(database_url: str = None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="PyArchInit-Mini API",
        description="REST API for archaeological data management",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth_router)  # Auth routes already have /api/auth prefix
    app.include_router(site_router, prefix="/api/v1/sites", tags=["sites"])
    app.include_router(us_router, prefix="/api/v1/us", tags=["stratigraphic-units"])
    app.include_router(inventario_router, prefix="/api/v1/inventario", tags=["inventory"])
    app.include_router(graphml_router, prefix="/api/graphml", tags=["graphml-converter"])
    
    # Store database URL in app state
    if database_url:
        app.state.database_url = database_url
    
    @app.get("/")
    async def root():
        return {
            "message": "PyArchInit-Mini API",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


def run_server():
    """
    Entry point for running the API server via console script.
    """
    import uvicorn
    import os

    # Get configuration from environment or use defaults
    host = os.getenv("PYARCHINIT_API_HOST", "0.0.0.0")
    port = int(os.getenv("PYARCHINIT_API_PORT", "8000"))
    reload = os.getenv("PYARCHINIT_API_RELOAD", "false").lower() == "true"

    print(f"Starting PyArchInit-Mini API server on {host}:{port}")
    print(f"API Documentation: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")

    # Run the server
    uvicorn.run(
        "pyarchinit_mini.api:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True
    )


__all__ = ["create_app", "run_server"]