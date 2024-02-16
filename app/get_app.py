import os.path
import tomllib

from fastapi import FastAPI

from app.app_init.app_lifespan import lifespan
from app.app_init.logging import setup_logging
from app.app_init.routes import setup_routes
from app.app_init.settings_validation import validate_settings
from config import settings


def get_app() -> FastAPI:
    validate_settings(settings)
    setup_logging()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with open(os.path.join(base_dir, "pyproject.toml"), "rb") as f:
        _app = FastAPI(
            title=tomllib.load(f)["tool"]["poetry"]["name"],
            openapi_url=f"/openapi.json",
            lifespan=lifespan,
        )

    setup_routes(_app)

    return _app


app = get_app()
