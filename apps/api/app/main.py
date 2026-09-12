import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import (
    ai,
    assessments,
    audit,
    auth,
    career_goals,
    dashboard,
    evidence,
    gaps,
    graph,
    learning,
    portfolio,
    profile,
    projects,
    recommendations,
    roles,
    simulations,
    skills,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("skillgraph")

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_rate_buckets: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _rate_buckets[client_ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"error": {"code": "RATE_LIMITED", "message": "Too many requests. Please slow down."}},
        )
    bucket.append(now)

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        content = detail
    else:
        content = {"error": {"code": "HTTP_ERROR", "message": str(detail)}}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed.", "details": exc.errors()}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
    )


@app.get("/health")
def health():
    return {"status": "ok", "ai_provider": settings.ai_provider}


for router in (
    auth.router,
    profile.router,
    skills.router,
    evidence.router,
    projects.router,
    roles.router,
    gaps.router,
    learning.router,
    recommendations.router,
    simulations.router,
    assessments.router,
    ai.router,
    graph.router,
    audit.router,
    career_goals.router,
    dashboard.router,
    portfolio.router,
):
    app.include_router(router)
