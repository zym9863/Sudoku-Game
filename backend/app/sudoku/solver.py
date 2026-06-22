from __future__ import annotations

import random
from collections.abc import Iterable
from copy import deepcopy

Grid = list[list[int]]

BOARD_SIZE = 9
BOX_SIZE = 3
DIGITS = set(range(1, 10))


def clone_grid(grid: Grid) -> Grid:
    return deepcopy(grid)


def validate_grid_shape(grid: Grid) -> None:
    if len(grid) != BOARD_SIZE:
        raise ValueError("Grid must contain 9 rows")
    for row in grid:
        if len(row) != BOARD_SIZE:
            raise ValueError("Each grid row must contain 9 cells")
        if any(not isinstance(value, int) or value < 0 or value > 9 for value in row):
            raise ValueError("Grid values must be integers between 0 and 9")


def unit_has_duplicates(values: Iterable[int]) -> bool:
    seen: set[int] = set()
    for value in values:
        if value == 0:
            continue
        if value in seen:
            return True
        seen.add(value)
    return False


def has_duplicate_conflicts(grid: Grid) -> bool:
    validate_grid_shape(grid)
    for index in range(BOARD_SIZE):
        if unit_has_duplicates(grid[index]):
            return True
        if unit_has_duplicates(grid[row][index] for row in range(BOARD_SIZE)):
            return True

    for box_row in range(0, BOARD_SIZE, BOX_SIZE):
        for box_col in range(0, BOARD_SIZE, BOX_SIZE):
            values = (
                grid[row][col]
                for row in range(box_row, box_row + BOX_SIZE)
                for col in range(box_col, box_col + BOX_SIZE)
            )
            if unit_has_duplicates(values):
                return True
    return False


def candidates_for(grid: Grid, row: int, col: int) -> set[int]:
    if grid[row][col] != 0:
        return set()

    used = set(grid[row])
    used.update(grid[r][col] for r in range(BOARD_SIZE))

    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    for r in range(start_row, start_row + BOX_SIZE):
        for c in range(start_col, start_col + BOX_SIZE):
            used.add(grid[r][c])

    return DIGITS - used


def find_empty_cell(grid: Grid) -> tuple[int, int] | None:
    best_cell: tuple[int, int] | None = None
    best_options: set[int] | None = None

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if grid[row][col] != 0:
                continue
            options = candidates_for(grid, row, col)
            if best_options is None or len(options) < len(best_options):
                best_cell = (row, col)
                best_options = options
                if len(options) <= 1:
                    return best_cell

    return best_cell


def solve_grid(grid: Grid) -> Grid | None:
    validate_grid_shape(grid)
    if has_duplicate_conflicts(grid):
        return None

    work = clone_grid(grid)
    if _solve_in_place(work):
        return work
    return None


def _solve_in_place(grid: Grid, rng: random.Random | None = None) -> bool:
    cell = find_empty_cell(grid)
    if cell is None:
        return True

    row, col = cell
    options = list(candidates_for(grid, row, col))
    if rng is not None:
        rng.shuffle(options)

    for value in options:
        grid[row][col] = value
        if _solve_in_place(grid, rng):
            return True
        grid[row][col] = 0

    return False


def count_solutions(grid: Grid, limit: int = 2) -> int:
    validate_grid_shape(grid)
    if limit < 1:
        raise ValueError("Solution limit must be at least 1")
    if has_duplicate_conflicts(grid):
        return 0

    work = clone_grid(grid)
    return _count_solutions_in_place(work, limit)


def _count_solutions_in_place(grid: Grid, limit: int) -> int:
    cell = find_empty_cell(grid)
    if cell is None:
        return 1

    row, col = cell
    total = 0
    for value in candidates_for(grid, row, col):
        grid[row][col] = value
        total += _count_solutions_in_place(grid, limit)
        grid[row][col] = 0
        if total >= limit:
            return total

    return total


def has_unique_solution(grid: Grid) -> bool:
    return count_solutions(grid, limit=2) == 1


def fill_complete_grid(rng: random.Random | None = None) -> Grid:
    work: Grid = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    if not _solve_in_place(work, rng or random.Random()):
        raise RuntimeError("Unable to generate a completed Sudoku grid")
    return work

