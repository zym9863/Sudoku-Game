from __future__ import annotations

from collections import defaultdict

from .solver import BOARD_SIZE, BOX_SIZE, Grid, validate_grid_shape


def _append_unit_conflicts(
    conflicts: dict[tuple[int, int], set[str]],
    cells_by_value: dict[int, list[tuple[int, int]]],
    reason: str,
) -> None:
    for value, cells in cells_by_value.items():
        if value == 0 or len(cells) < 2:
            continue
        for cell in cells:
            conflicts[cell].add(reason)


def find_conflicts(current_grid: Grid, solution: Grid | None = None) -> list[dict[str, int | str]]:
    validate_grid_shape(current_grid)
    if solution is not None:
        validate_grid_shape(solution)

    conflicts: dict[tuple[int, int], set[str]] = defaultdict(set)

    for row in range(BOARD_SIZE):
        values: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for col in range(BOARD_SIZE):
            values[current_grid[row][col]].append((row, col))
        _append_unit_conflicts(conflicts, values, "row_duplicate")

    for col in range(BOARD_SIZE):
        values = defaultdict(list)
        for row in range(BOARD_SIZE):
            values[current_grid[row][col]].append((row, col))
        _append_unit_conflicts(conflicts, values, "column_duplicate")

    for box_row in range(0, BOARD_SIZE, BOX_SIZE):
        for box_col in range(0, BOARD_SIZE, BOX_SIZE):
            values = defaultdict(list)
            for row in range(box_row, box_row + BOX_SIZE):
                for col in range(box_col, box_col + BOX_SIZE):
                    values[current_grid[row][col]].append((row, col))
            _append_unit_conflicts(conflicts, values, "box_duplicate")

    if solution is not None:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = current_grid[row][col]
                if value != 0 and value != solution[row][col]:
                    conflicts[(row, col)].add("wrong_value")

    rendered: list[dict[str, int | str]] = []
    for (row, col), reasons in sorted(conflicts.items()):
        for reason in sorted(reasons):
            rendered.append({"row": row, "col": col, "reason": reason})
    return rendered


def count_empty_cells(grid: Grid) -> int:
    validate_grid_shape(grid)
    return sum(1 for row in grid for value in row if value == 0)

