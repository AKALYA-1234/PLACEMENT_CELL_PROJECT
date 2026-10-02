import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.api import import_routes, student_routes, company_routes, analytics_routes

logger = logging.getLogger("placement_cell")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle events."""
    logger.info("Placement Cell API starting up…")
    yield
    logger.info("Placement Cell API shutting down…")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Placement Cell API",
        description="College Placement Management & Analytics Portal — Admin Backend",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow frontend dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth.router)
    app.include_router(import_routes.router)
    app.include_router(student_routes.router)
    app.include_router(company_routes.router)
    app.include_router(analytics_routes.router)

    @app.get("/api/health", tags=["Health"])
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()
