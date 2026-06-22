import pytest

from app.core.errors import AppError
from app.repositories.games import GameRepository
from app.services.games import GameService

SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

ONE_CELL_PUZZLE = [row[:] for row in SOLUTION]
ONE_CELL_PUZZLE[0][0] = 0


def factory(puzzle):
    def _factory(_difficulty):
        return [row[:] for row in puzzle], [row[:] for row in SOLUTION]

    return _factory


@pytest.fixture
def service():
    repository = GameRepository(":memory:")
    repository.init_schema()
    return GameService(repository, puzzle_factory=factory(PUZZLE))


def test_service_creates_and_persists_game(service):
    game = service.create_game("easy", "player_unit")
    stored = service.get_game(game.id)

    assert stored.id == game.id
    assert stored.player_id == "player_unit"
    assert stored.fixed_cells[0][0] is True
    assert stored.current_grid == PUZZLE


def test_service_protects_fixed_cells_and_validates_notes(service):
    game = service.create_game("easy", "player_unit")

    with pytest.raises(AppError) as fixed_error:
        service.update_cell(game.id, 0, 0, "value", value=1)
    assert fixed_error.value.status_code == 400

    updated = service.update_cell(game.id, 0, 2, "notes", notes=[1, 4, 9])
    assert updated.notes[0][2] == [1, 4, 9]

    updated = service.update_cell(game.id, 0, 2, "value", value=4)
    assert updated.current_grid[0][2] == 4
    assert updated.notes[0][2] == []

    with pytest.raises(AppError):
        service.update_cell(game.id, 0, 2, "notes", notes=[2])


def test_service_tracks_wrong_values_and_check_conflicts(service):
    game = service.create_game("easy", "player_unit")
    updated = service.update_cell(game.id, 0, 2, "value", value=9)

    assert updated.mistake_count == 1

    result = service.check_game(game.id)

    assert result.is_complete is False
    assert result.mistake_count == 1
    assert any(conflict.reason == "wrong_value" for conflict in result.conflicts)


def test_service_hint_fills_a_cell(service):
    game = service.create_game("easy", "player_unit")
    result = service.hint_game(game.id)

    assert result.row == 0
    assert result.col == 2
    assert result.value == SOLUTION[0][2]
    assert result.game.current_grid[0][2] == SOLUTION[0][2]
    assert result.hint_count == 1


def test_service_marks_completion_and_stats():
    repository = GameRepository(":memory:")
    repository.init_schema()
    service = GameService(repository, puzzle_factory=factory(ONE_CELL_PUZZLE))
    game = service.create_game("easy", "player_done")

    completed = service.update_cell(game.id, 0, 0, "value", value=5)
    stats = service.get_stats("player_done")

    assert completed.status == "completed"
    assert stats.completed_games == 1
    assert stats.best_times["easy"] is not None

    with pytest.raises(AppError) as completed_error:
        service.update_cell(game.id, 0, 0, "value", value=0)
    assert completed_error.value.status_code == 409
