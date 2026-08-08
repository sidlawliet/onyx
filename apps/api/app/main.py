from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.app.api.v1.router import api_router
from apps.api.app.core.config import settings
from apps.api.app.core.exceptions import DomainException
from apps.api.app.db.session import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure SQLite tables exist for offline testing mode
    create_db_tables()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Global Domain Exception Handler
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


# Register API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "running",
        "docs_url": f"{settings.API_V1_STR}/docs",
    }
