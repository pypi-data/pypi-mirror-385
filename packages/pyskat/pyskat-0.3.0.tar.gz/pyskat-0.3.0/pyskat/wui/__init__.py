from pathlib import Path
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from pydantic_core import InitErrorDetails
from pyskat.wui.jinja import RenderTemplateDep
from pyskat.wui.messages import Message, MessageCategory, flash_message
import pyskat.wui.players as players
import pyskat.wui.sessions as sessions
import pyskat.wui.matches as matches
import pyskat.wui.results as results
import pyskat.wui.evaluation as evaluation
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
import pyskat.dependencies as dependencies
import pyskat.api
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

__all__ = ["create_app"]

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        middleware=[
            Middleware(
                SessionMiddleware, secret_key=dependencies.get_settings().session_secret
            )
        ]
    )

    api = pyskat.api.create_app()
    app.mount("/api", api)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="wui_static")

    app.include_router(players.router)
    app.include_router(sessions.router)
    app.include_router(matches.router)
    app.include_router(results.router)
    app.include_router(evaluation.router)

    @app.get("/", response_class=HTMLResponse)
    async def wui_index(render_template: RenderTemplateDep):
        return render_template("index.html")

    @app.post("/flash_message", response_model=Message)
    async def wui_flash_message(request: Request, message: Message):
        flash_message(request, message)
        return message

    @app.exception_handler(StarletteHTTPException)
    @api.exception_handler(StarletteHTTPException)
    async def wui_http_exception_handler(request: Request, exc: StarletteHTTPException):
        flash_message(
            request,
            Message(
                text=f"{request.method} request to {request.url} failed with status code {exc.status_code}: {exc.detail}",
                category=MessageCategory.DANGER,
            ),
        )
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    @api.exception_handler(RequestValidationError)
    async def wui_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        pydantic_error = ValidationError.from_exception_data(
            "", [InitErrorDetails(**e) for e in exc.errors()], "json"
        )
        flash_message(
            request,
            Message(
                text=f"{request.method} request to {request.url} failed with {pydantic_error}",
                category=MessageCategory.DANGER,
            ),
        )
        return await request_validation_exception_handler(request, exc)

    return app
