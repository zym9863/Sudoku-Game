import pytest

from app.sudoku.generator import DIFFICULTY_HOLES, generate_puzzle
from app.sudoku.solver import count_solutions, has_unique_solution, solve_grid


KNOWN_PUZZLE = [
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

KNOWN_SOLUTION = [
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


def test_solver_solves_known_unique_puzzle():
    assert solve_grid(KNOWN_PUZZLE) == KNOWN_SOLUTION
    assert count_solutions(KNOWN_PUZZLE, limit=2) == 1
    assert has_unique_solution(KNOWN_PUZZLE)


def test_solver_rejects_duplicate_conflicts():
    invalid = [row[:] for row in KNOWN_PUZZLE]
    invalid[0][2] = 5

    assert solve_grid(invalid) is None
    assert count_solutions(invalid, limit=2) == 0


def test_generator_creates_unique_puzzle_with_expected_holes():
    puzzle, solution = generate_puzzle("easy", seed=42)
    holes = sum(1 for row in puzzle for value in row if value == 0)

    assert holes == DIFFICULTY_HOLES["easy"]
    assert solve_grid(puzzle) == solution
    assert has_unique_solution(puzzle)


def test_generator_rejects_unknown_difficulty():
    with pytest.raises(ValueError):
        generate_puzzle("expert", seed=1)

