from __future__ import annotations

import random

from .solver import BOARD_SIZE, Grid, clone_grid, count_solutions, fill_complete_grid

DIFFICULTY_HOLES = {
    "easy": 36,
    "medium": 44,
    "hard": 52,
}


def generate_puzzle(difficulty: str, seed: int | None = None) -> tuple[Grid, Grid]:
    if difficulty not in DIFFICULTY_HOLES:
        raise ValueError("Difficulty must be easy, medium, or hard")

    for attempt in range(20):
        attempt_seed = None if seed is None else seed + attempt
        rng = random.Random(attempt_seed)
        solution = fill_complete_grid(rng)
        puzzle = clone_grid(solution)
        target_holes = DIFFICULTY_HOLES[difficulty]
        holes = 0

        positions = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)]
        rng.shuffle(positions)

        for row, col in positions:
            if holes >= target_holes:
                break
            previous_value = puzzle[row][col]
            puzzle[row][col] = 0

            if count_solutions(puzzle, limit=2) == 1:
                holes += 1
            else:
                puzzle[row][col] = previous_value

        if holes >= target_holes:
            return puzzle, solution

    raise RuntimeError("Unable to generate a uniquely solvable Sudoku puzzle")

