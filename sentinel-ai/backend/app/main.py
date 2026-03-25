from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.core.config import settings
from app.api import auth, users, health, predictions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes the database on startup.
    """
    # Startup: Initialize database
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

    yield

    # Shutdown: Cleanup if needed
    print("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(predictions.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to SentinelAI API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
