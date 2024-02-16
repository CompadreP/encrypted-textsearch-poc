from fastapi import FastAPI

from app.modules.messages.views import router as settings_router


def setup_routes(app: FastAPI) -> None:
    app.include_router(settings_router)
