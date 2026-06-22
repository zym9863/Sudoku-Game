from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.sudoku.solver import Grid

Notes = list[list[list[int]]]


@dataclass(frozen=True)
class GameRecord:
    id: str
    player_id: str
    difficulty: str
    puzzle: Grid
    solution: Grid
    current_grid: Grid
    notes: Notes
    status: str
    hint_count: int
    mistake_count: int
    started_at: str
    completed_at: str | None
    updated_at: str


class GameRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._memory_connection: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_connection.row_factory = sqlite3.Row
        else:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    puzzle TEXT NOT NULL,
                    solution TEXT NOT NULL,
                    current_grid TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    status TEXT NOT NULL,
                    hint_count INTEGER NOT NULL DEFAULT 0,
                    mistake_count INTEGER NOT NULL DEFAULT 0,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_games_player_status ON games(player_id, status, updated_at)"
            )

    def create(self, record: GameRecord) -> GameRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO games (
                    id, player_id, difficulty, puzzle, solution, current_grid,
                    notes, status, hint_count, mistake_count, started_at,
                    completed_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._to_row(record),
            )
        return record

    def get(self, game_id: str) -> GameRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
        return self._from_row(row) if row else None

    def get_latest_active(self, player_id: str) -> GameRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM games
                WHERE player_id = ? AND status = 'active'
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (player_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def update(self, record: GameRecord) -> GameRecord:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE games
                SET player_id = ?, difficulty = ?, puzzle = ?, solution = ?,
                    current_grid = ?, notes = ?, status = ?, hint_count = ?,
                    mistake_count = ?, started_at = ?, completed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    record.player_id,
                    record.difficulty,
                    json.dumps(record.puzzle),
                    json.dumps(record.solution),
                    json.dumps(record.current_grid),
                    json.dumps(record.notes),
                    record.status,
                    record.hint_count,
                    record.mistake_count,
                    record.started_at,
                    record.completed_at,
                    record.updated_at,
                    record.id,
                ),
            )
        return record

    def list_by_player(self, player_id: str) -> list[GameRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM games WHERE player_id = ? ORDER BY started_at DESC",
                (player_id,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        if self._memory_connection is not None:
            return self._memory_connection
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _to_row(self, record: GameRecord) -> tuple:
        return (
            record.id,
            record.player_id,
            record.difficulty,
            json.dumps(record.puzzle),
            json.dumps(record.solution),
            json.dumps(record.current_grid),
            json.dumps(record.notes),
            record.status,
            record.hint_count,
            record.mistake_count,
            record.started_at,
            record.completed_at,
            record.updated_at,
        )

    def _from_row(self, row: sqlite3.Row) -> GameRecord:
        return GameRecord(
            id=row["id"],
            player_id=row["player_id"],
            difficulty=row["difficulty"],
            puzzle=json.loads(row["puzzle"]),
            solution=json.loads(row["solution"]),
            current_grid=json.loads(row["current_grid"]),
            notes=json.loads(row["notes"]),
            status=row["status"],
            hint_count=row["hint_count"],
            mistake_count=row["mistake_count"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            updated_at=row["updated_at"],
        )
