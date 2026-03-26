from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.core.config import settings
from app.core import metrics as _metrics
from app.api import assistant, auth, health, predictions, users
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


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
app.include_router(assistant.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to SentinelAI API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
