from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.repositories.games import Notes
from app.sudoku.solver import Grid


class CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class GameStatus(str, Enum):
    active = "active"
    completed = "completed"


class CreateGameRequest(CamelModel):
    difficulty: Difficulty = Difficulty.easy
    player_id: str = Field(alias="playerId", min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")


class UpdateCellRequest(CamelModel):
    row: int = Field(ge=0, le=8)
    col: int = Field(ge=0, le=8)
    mode: Literal["value", "notes"] = "value"
    value: int | None = Field(default=None, ge=0, le=9)
    notes: list[int] | None = None

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, notes: list[int] | None) -> list[int] | None:
        if notes is None:
            return notes
        if len(notes) > 9:
            raise ValueError("Notes can contain at most 9 numbers")
        unique_notes = sorted(set(notes))
        if unique_notes != sorted(notes):
            raise ValueError("Notes must not contain duplicates")
        if any(note < 1 or note > 9 for note in notes):
            raise ValueError("Notes must contain numbers between 1 and 9")
        return notes

    @model_validator(mode="after")
    def validate_payload(self) -> "UpdateCellRequest":
        if self.mode == "value" and self.value is None:
            raise ValueError("Value is required when mode is value")
        if self.mode == "notes" and self.notes is None:
            raise ValueError("Notes are required when mode is notes")
        return self


class Conflict(CamelModel):
    row: int
    col: int
    reason: str


class GameResponse(CamelModel):
    id: str
    player_id: str = Field(alias="playerId")
    difficulty: Difficulty
    puzzle: Grid
    current_grid: Grid = Field(alias="currentGrid")
    notes: Notes
    fixed_cells: list[list[bool]] = Field(alias="fixedCells")
    status: GameStatus
    hint_count: int = Field(alias="hintCount")
    mistake_count: int = Field(alias="mistakeCount")
    started_at: str = Field(alias="startedAt")
    completed_at: str | None = Field(alias="completedAt")
    elapsed_seconds: int = Field(alias="elapsedSeconds")


class CheckResponse(CamelModel):
    is_complete: bool = Field(alias="isComplete")
    conflicts: list[Conflict]
    mistake_count: int = Field(alias="mistakeCount")
    empty_cells: int = Field(alias="emptyCells")
    status: GameStatus
    game: GameResponse


class HintResponse(CamelModel):
    row: int
    col: int
    value: int
    hint_count: int = Field(alias="hintCount")
    status: GameStatus
    current_grid: Grid = Field(alias="currentGrid")
    game: GameResponse


class StatsResponse(CamelModel):
    player_id: str = Field(alias="playerId")
    completed_games: int = Field(alias="completedGames")
    active_games: int = Field(alias="activeGames")
    best_times: dict[str, int | None] = Field(alias="bestTimes")
    average_mistakes: float = Field(alias="averageMistakes")

