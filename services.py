from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import customers, orders, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_application(create_tables: bool = True) -> FastAPI:
    app_lifespan = lifespan if create_tables else None
    settings = get_settings()

    app = FastAPI(
        title="Inventory & Order Management API",
        version="1.0.0",
        lifespan=app_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(products.router, prefix="/api")
    app.include_router(customers.router, prefix="/api")
    app.include_router(orders.router, prefix="/api")

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_application()
