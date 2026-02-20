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
from app.routers import compatibility, fortune, health, saju

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
app.add_exception_handler(SajuError, saju_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Routers
app.include_router(health.router)
app.include_router(saju.router)
app.include_router(compatibility.router)
app.include_router(fortune.router)
