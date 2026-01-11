from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print("🚀 Application startup")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Project: {settings.PROJECT_NAME}")

    yield

    # Shutdown
    print("🛑 Application shutdown")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Custom middleware for request logging (optional)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests."""
    print(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"📤 {request.method} {request.url.path} - {response.status_code}")
    return response


# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "0.1.0",
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to FastAPI Modular Postgres",
            "docs": "/docs",
            "health": "/health",
        },
    )


# Include routers (will be added when modules are ready)
# from src.auth.router import router as auth_router
# from src.users.router import router as users_router

# app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Auth"])
# app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
