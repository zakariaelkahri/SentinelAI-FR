import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

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


def _route_label(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None) if route is not None else None
    if isinstance(route_path, str) and route_path:
        return route_path
    return "unmatched"


def _safe_content_length(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return max(float(value), 0.0)
    except ValueError:
        return 0.0


@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    # Exclude the scrape endpoint from request metrics to reduce noise.
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method.upper()
    status_code = 500
    response_size = 0.0
    start_time = time.perf_counter()

    _metrics.http_requests_in_progress.inc()

    try:
        response = await call_next(request)
        status_code = response.status_code
        response_size = _safe_content_length(response.headers.get("content-length"))
        return response
    except Exception as exc:
        route = _route_label(request)
        _metrics.http_request_exceptions_total.labels(
            method=method,
            route=route,
            exception_type=type(exc).__name__,
        ).inc()
        raise
    finally:
        route = _route_label(request)
        request_size = _safe_content_length(request.headers.get("content-length"))
        duration = time.perf_counter() - start_time

        _metrics.http_requests_total.labels(
            method=method,
            route=route,
            status_code=str(status_code),
        ).inc()
        _metrics.http_request_duration_seconds.labels(
            method=method,
            route=route,
            status_code=str(status_code),
        ).observe(duration)
        _metrics.http_request_size_bytes.labels(
            method=method,
            route=route,
        ).observe(request_size)
        _metrics.http_response_size_bytes.labels(
            method=method,
            route=route,
            status_code=str(status_code),
        ).observe(response_size)
        _metrics.http_requests_in_progress.dec()


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
