import pytest
from fastapi.testclient import TestClient

from app.main import create_app

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


def make_factory(puzzle):
    def _factory(_difficulty):
        return [row[:] for row in puzzle], [row[:] for row in SOLUTION]

    return _factory


@pytest.fixture
def client():
    app = create_app(":memory:", puzzle_factory=make_factory(PUZZLE))
    return TestClient(app)


@pytest.fixture
def completed_client():
    app = create_app(":memory:", puzzle_factory=make_factory(ONE_CELL_PUZZLE))
    return TestClient(app)


@pytest.fixture
def game(client):
    response = client.post("/api/games", json={"difficulty": "easy", "playerId": "player_api"})
    assert response.status_code == 201
    return response.json()
