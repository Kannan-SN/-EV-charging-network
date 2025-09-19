# backend/app/main.py (Fixed for FastAPI modern lifespan events)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.routers import optimization, health
from app.services.weaviate_service import WeaviateService

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        # Initialize Weaviate connection
        weaviate_service = WeaviateService()
        await weaviate_service.initialize()
        print("✅ Weaviate connection established")
        
        # Store service in app state
        app.state.weaviate_service = weaviate_service
        
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down services...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="EV Charging Network Optimizer",
    description="Smart EV Charging Station Placement Optimization for Tamil Nadu",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(optimization.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "EV Charging Network Optimizer API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )