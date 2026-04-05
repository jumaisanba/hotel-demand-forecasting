import logging

from fastapi import FastAPI

from auth.api.routers import sessions, users
from shared.errors import (
    register_error_handlers,
    setup_openapi_with_errors,
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Auth Service API")
    register_error_handlers(app)
    setup_openapi_with_errors(app)

    app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
    app.include_router(users.router, prefix="/users", tags=["Users"])

    @app.get("/", tags=["system"])
    async def root():
        return {"message": "AUTH_SERVICE is running"}

    return app


app = create_app()
