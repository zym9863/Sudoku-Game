from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import router
from app.core.errors import AppError
from app.repositories.games import GameRepository
from app.services.games import GameService

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def create_app(db_path: str | None = None, puzzle_factory=None) -> FastAPI:
    database_path = db_path or os.getenv("SUDOKU_DB_PATH", "data/sudoku.sqlite")
    repository = GameRepository(database_path)
    repository.init_schema()

    app = FastAPI(
        title="Sudoku Game API",
        version="1.0.0",
        description="A persistent Sudoku game API with puzzle generation, validation, hints, and stats.",
    )
    app.state.game_service = GameService(repository, puzzle_factory=puzzle_factory) if puzzle_factory else GameService(repository)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "msg": exc.msg})

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(status_code=exc.status_code, content={"code": exc.status_code, "msg": message})

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "msg": "Validation failed",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logging.getLogger(__name__).exception("unhandled application error", exc_info=exc)
        return JSONResponse(status_code=500, content={"code": 500, "msg": "Internal server error"})

    return app
