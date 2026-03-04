from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import init_dependencies, shutdown_dependencies
from app.middleware.error_handler import (
    SajuError,
    generic_error_handler,
    saju_error_handler,
)
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.token_validator import TokenValidatorMiddleware
from app.routers import celebrity, compatibility, fortune, health, relationship, saju, timing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_dependencies()
    yield
    await shutdown_dependencies()


app = FastAPI(
    title="Saju API",
    description="Four Pillars of Destiny (사주팔자) calculation and interpretation API",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware (last added = first to execute)
# Execution order: TokenValidator -> RateLimiter -> CORS -> route handler
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(TokenValidatorMiddleware)

# Error handlers
app.add_exception_handler(SajuError, saju_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Routers
app.include_router(health.router)
app.include_router(saju.router)
app.include_router(compatibility.router)
app.include_router(celebrity.router)
app.include_router(fortune.router)
app.include_router(relationship.router)
app.include_router(timing.router)
