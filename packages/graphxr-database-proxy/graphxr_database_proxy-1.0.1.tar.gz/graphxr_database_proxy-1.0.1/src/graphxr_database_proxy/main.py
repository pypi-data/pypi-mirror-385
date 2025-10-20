# -*- coding: utf-8 -*-
"""
Main FastAPI application
"""

import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .api.projects import router as projects_router
from .api.database import router as database_router
from .api.google import router as google_router

# Create FastAPI app
app = FastAPI(
    title="GraphXR Database Proxy",
    description="Secure middleware for connecting GraphXR to databases",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(projects_router)
app.include_router(database_router)
app.include_router(google_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "GraphXR Database Proxy is running",
        "version": "1.0.0",
        "environment": "development",
        "auto_reload": "enabled"
    }

# Mount static files from package
static_dir = Path(__file__).parent / "static"
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
 
if static_dir.exists() or frontend_dist.exists():
    static_dir = frontend_dist if frontend_dist.exists() else static_dir
    print(f"[INFO] Serving static files from: {static_dir}")
    # Development: Use frontend dist directory
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the frontend application for all unmatched paths"""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend not available"}
        
else:
    @app.get("/")
    async def serve_fallback():
        """Fallback when frontend is not built"""
        return {
            "message": "Frontend not available", 
            "hint": "Run 'python scripts/build_frontend.py' to build and package frontend"
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GraphXR Database Proxy")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9080, help="Port to bind to")
    parser.add_argument("--ui", action="store_true", help="Enable UI mode")
    parser.add_argument("--dev", action="store_true", help="Development mode with hot reload")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the server
    uvicorn.run(
        "src.graphxr_database_proxy.main:app",
        host=args.host,
        port=args.port,
        reload=args.dev,
        log_level="info" if not args.dev else "debug"
    )


if __name__ == "__main__":
    main()