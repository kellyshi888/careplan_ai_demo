from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import structlog
import os
from pathlib import Path
from contextlib import asynccontextmanager

from app.api import intake_router, draft_router, review_router, auth_router
from app.api.mock_data import router as mock_router
from app.api.batch import router as batch_router
from app.logging.audit import AuditMiddleware
from app.dependencies import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    structlog.get_logger().info("CarePlan AI starting up...")
    yield
    # Shutdown
    structlog.get_logger().info("CarePlan AI shutting down...")


# Create FastAPI application
app = FastAPI(
    title="CarePlan AI",
    description="AI-powered personalized care plan generation system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add audit logging middleware
app.add_middleware(AuditMiddleware)

# Include routers
app.include_router(auth_router)
app.include_router(intake_router)
app.include_router(draft_router)
app.include_router(review_router)
app.include_router(mock_router)
app.include_router(batch_router)

# Health check endpoint (must be before catch-all route)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "careplan-ai",
        "version": "0.1.0"
    }

# Serve static files (React frontend)
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    # Mount the static directory to serve CSS, JS, and other assets
    app.mount("/static", StaticFiles(directory=str(static_path / "static")), name="static")
    
    # Serve other static assets (images, manifest, etc.) from root
    try:
        app.mount("/favicon.ico", StaticFiles(directory=str(static_path)), name="favicon")
        app.mount("/manifest.json", StaticFiles(directory=str(static_path)), name="manifest")
        app.mount("/logo192.png", StaticFiles(directory=str(static_path)), name="logo192")
    except:
        pass  # These files might not exist
    
    @app.get("/")
    async def serve_frontend():
        """Serve React frontend."""
        return FileResponse(str(static_path / "index.html"))
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Serve React frontend for all non-API routes."""
        # Don't serve frontend for API routes
        if path.startswith(("api/", "docs", "redoc", "health")):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        
        # Try to serve static files first
        file_path = static_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Otherwise serve the React app
        return FileResponse(str(static_path / "index.html"))
else:
    @app.get("/")
    async def root():
        """Root endpoint when no frontend is available."""
        return {
            "message": "CarePlan AI - Personalized Care Plan Generation System",
            "version": "0.1.0",
            "docs": "/docs",
            "frontend": "Not available - static files not found"
        }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger = structlog.get_logger()
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc)
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": "Please contact support with this error ID"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )