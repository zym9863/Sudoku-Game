from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from app.schemas import (
    CheckResponse,
    CreateGameRequest,
    GameResponse,
    HintResponse,
    StatsResponse,
    UpdateCellRequest,
)
from app.services.games import GameService

router = APIRouter()


def get_game_service(request: Request) -> GameService:
    return request.app.state.game_service


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sudoku-api"}


@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(payload: CreateGameRequest, service: GameService = Depends(get_game_service)) -> GameResponse:
    return service.create_game(payload.difficulty.value, payload.player_id)


@router.get("/games/active/{player_id}", response_model=GameResponse)
def get_active_game(
    player_id: Annotated[str, Path(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")],
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    return service.get_active_game(player_id)


@router.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: str, service: GameService = Depends(get_game_service)) -> GameResponse:
    return service.get_game(game_id)


@router.patch("/games/{game_id}/cell", response_model=GameResponse)
def update_cell(
    game_id: str,
    payload: UpdateCellRequest,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    return service.update_cell(
        game_id=game_id,
        row=payload.row,
        col=payload.col,
        mode=payload.mode,
        value=payload.value,
        notes=payload.notes,
    )


@router.post("/games/{game_id}/check", response_model=CheckResponse)
def check_game(game_id: str, service: GameService = Depends(get_game_service)) -> CheckResponse:
    return service.check_game(game_id)


@router.post("/games/{game_id}/hint", response_model=HintResponse)
def hint_game(game_id: str, service: GameService = Depends(get_game_service)) -> HintResponse:
    return service.hint_game(game_id)


@router.get("/stats/{player_id}", response_model=StatsResponse)
def get_stats(
    player_id: Annotated[str, Path(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")],
    service: GameService = Depends(get_game_service),
) -> StatsResponse:
    return service.get_stats(player_id)

