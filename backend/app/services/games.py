from __future__ import annotations

import logging
import uuid
from dataclasses import replace
from datetime import datetime, timezone

from app.core.errors import AppError
from app.repositories.games import GameRecord, GameRepository, Notes
from app.schemas import CheckResponse, GameResponse, HintResponse, StatsResponse
from app.sudoku.conflicts import count_empty_cells, find_conflicts
from app.sudoku.generator import DIFFICULTY_HOLES, generate_puzzle
from app.sudoku.solver import BOARD_SIZE, Grid, clone_grid

logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def empty_notes() -> Notes:
    return [[[] for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


class GameService:
    def __init__(self, repository: GameRepository, puzzle_factory=generate_puzzle):
        self.repository = repository
        self.puzzle_factory = puzzle_factory

    def create_game(self, difficulty: str, player_id: str) -> GameResponse:
        if difficulty not in DIFFICULTY_HOLES:
            raise AppError(400, "Difficulty must be easy, medium, or hard")

        puzzle, solution = self.puzzle_factory(difficulty)
        timestamp = utc_now()
        record = GameRecord(
            id=str(uuid.uuid4()),
            player_id=player_id,
            difficulty=difficulty,
            puzzle=puzzle,
            solution=solution,
            current_grid=clone_grid(puzzle),
            notes=empty_notes(),
            status="active",
            hint_count=0,
            mistake_count=0,
            started_at=timestamp,
            completed_at=None,
            updated_at=timestamp,
        )
        self.repository.create(record)
        logger.info("created sudoku game", extra={"game_id": record.id, "difficulty": difficulty})
        return self.to_response(record)

    def get_game(self, game_id: str) -> GameResponse:
        return self.to_response(self._get_record(game_id))

    def get_active_game(self, player_id: str) -> GameResponse:
        record = self.repository.get_latest_active(player_id)
        if record is None:
            raise AppError(404, "No active game found for this player")
        return self.to_response(record)

    def update_cell(
        self,
        game_id: str,
        row: int,
        col: int,
        mode: str,
        value: int | None = None,
        notes: list[int] | None = None,
    ) -> GameResponse:
        record = self._require_active(game_id)
        self._ensure_editable(record, row, col)

        current_grid = clone_grid(record.current_grid)
        next_notes = [[list(cell) for cell in note_row] for note_row in record.notes]
        mistake_count = record.mistake_count

        if mode == "notes":
            if current_grid[row][col] != 0:
                raise AppError(400, "Cannot add notes to a filled cell")
            next_notes[row][col] = sorted(notes or [])
        else:
            assert value is not None
            current_grid[row][col] = value
            next_notes[row][col] = []
            if value != 0 and value != record.solution[row][col]:
                mistake_count += 1

        next_record = self._with_progress(
            replace(
                record,
                current_grid=current_grid,
                notes=next_notes,
                mistake_count=mistake_count,
                updated_at=utc_now(),
            )
        )
        self.repository.update(next_record)
        logger.info("updated sudoku cell", extra={"game_id": game_id, "row": row, "col": col, "mode": mode})
        return self.to_response(next_record)

    def check_game(self, game_id: str) -> CheckResponse:
        record = self._get_record(game_id)
        conflicts = find_conflicts(record.current_grid, record.solution)
        empty_cells = count_empty_cells(record.current_grid)
        is_complete = empty_cells == 0 and not conflicts and record.current_grid == record.solution

        next_record = record
        if is_complete and record.status != "completed":
            next_record = replace(record, status="completed", completed_at=utc_now(), updated_at=utc_now())
            self.repository.update(next_record)
            logger.info("completed sudoku game by check", extra={"game_id": game_id})

        return CheckResponse(
            is_complete=is_complete,
            conflicts=conflicts,
            mistake_count=next_record.mistake_count,
            empty_cells=empty_cells,
            status=next_record.status,
            game=self.to_response(next_record),
        )

    def hint_game(self, game_id: str) -> HintResponse:
        record = self._require_active(game_id)
        target = self._find_hint_target(record.current_grid, record.solution)
        if target is None:
            completed = replace(record, status="completed", completed_at=utc_now(), updated_at=utc_now())
            self.repository.update(completed)
            raise AppError(409, "No hint is available because the puzzle is already solved")

        row, col = target
        current_grid = clone_grid(record.current_grid)
        next_notes = [[list(cell) for cell in note_row] for note_row in record.notes]
        current_grid[row][col] = record.solution[row][col]
        next_notes[row][col] = []

        next_record = self._with_progress(
            replace(
                record,
                current_grid=current_grid,
                notes=next_notes,
                hint_count=record.hint_count + 1,
                updated_at=utc_now(),
            )
        )
        self.repository.update(next_record)
        logger.info("provided sudoku hint", extra={"game_id": game_id, "row": row, "col": col})

        return HintResponse(
            row=row,
            col=col,
            value=record.solution[row][col],
            hint_count=next_record.hint_count,
            status=next_record.status,
            current_grid=next_record.current_grid,
            game=self.to_response(next_record),
        )

    def get_stats(self, player_id: str) -> StatsResponse:
        records = self.repository.list_by_player(player_id)
        completed = [record for record in records if record.status == "completed"]
        active_games = len([record for record in records if record.status == "active"])

        best_times: dict[str, int | None] = {"easy": None, "medium": None, "hard": None}
        for record in completed:
            elapsed = self._elapsed_seconds(record)
            best = best_times[record.difficulty]
            if best is None or elapsed < best:
                best_times[record.difficulty] = elapsed

        average_mistakes = 0.0
        if completed:
            average_mistakes = round(sum(record.mistake_count for record in completed) / len(completed), 2)

        return StatsResponse(
            player_id=player_id,
            completed_games=len(completed),
            active_games=active_games,
            best_times=best_times,
            average_mistakes=average_mistakes,
        )

    def to_response(self, record: GameRecord) -> GameResponse:
        return GameResponse(
            id=record.id,
            player_id=record.player_id,
            difficulty=record.difficulty,
            puzzle=record.puzzle,
            current_grid=record.current_grid,
            notes=record.notes,
            fixed_cells=[[value != 0 for value in row] for row in record.puzzle],
            status=record.status,
            hint_count=record.hint_count,
            mistake_count=record.mistake_count,
            started_at=record.started_at,
            completed_at=record.completed_at,
            elapsed_seconds=self._elapsed_seconds(record),
        )

    def _get_record(self, game_id: str) -> GameRecord:
        record = self.repository.get(game_id)
        if record is None:
            raise AppError(404, "Game not found")
        return record

    def _require_active(self, game_id: str) -> GameRecord:
        record = self._get_record(game_id)
        if record.status != "active":
            raise AppError(409, "Completed games cannot be changed")
        return record

    def _ensure_editable(self, record: GameRecord, row: int, col: int) -> None:
        if record.puzzle[row][col] != 0:
            raise AppError(400, "Fixed puzzle cells cannot be edited")

    def _with_progress(self, record: GameRecord) -> GameRecord:
        if record.current_grid == record.solution and record.status != "completed":
            return replace(record, status="completed", completed_at=utc_now(), updated_at=utc_now())
        return record

    def _find_hint_target(self, current_grid: Grid, solution: Grid) -> tuple[int, int] | None:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if current_grid[row][col] == 0:
                    return row, col
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if current_grid[row][col] != solution[row][col]:
                    return row, col
        return None

    def _elapsed_seconds(self, record: GameRecord) -> int:
        start = self._parse_datetime(record.started_at)
        end = self._parse_datetime(record.completed_at) if record.completed_at else datetime.now(timezone.utc)
        return max(0, int((end - start).total_seconds()))

    def _parse_datetime(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
