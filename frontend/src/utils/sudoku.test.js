import { describe, expect, it } from "vitest";

import { cellKey, findDuplicateCells, formatDuration, toggleNote } from "./sudoku";

describe("sudoku utilities", () => {
  it("formats elapsed seconds as mm:ss", () => {
    expect(formatDuration(0)).toBe("00:00");
    expect(formatDuration(65)).toBe("01:05");
    expect(formatDuration(-3)).toBe("00:00");
  });

  it("toggles notes in sorted order", () => {
    expect(toggleNote([3, 1], 2)).toEqual([1, 2, 3]);
    expect(toggleNote([1, 2, 3], 2)).toEqual([1, 3]);
  });

  it("finds duplicate cells across rows, columns, and boxes", () => {
    const grid = Array.from({ length: 9 }, () => Array(9).fill(0));
    grid[0][0] = 5;
    grid[0][7] = 5;
    grid[1][1] = 9;
    grid[7][1] = 9;
    grid[3][3] = 4;
    grid[4][4] = 4;

    const conflicts = findDuplicateCells(grid);

    expect(conflicts.has(cellKey(0, 0))).toBe(true);
    expect(conflicts.has(cellKey(0, 7))).toBe(true);
    expect(conflicts.has(cellKey(1, 1))).toBe(true);
    expect(conflicts.has(cellKey(7, 1))).toBe(true);
    expect(conflicts.has(cellKey(3, 3))).toBe(true);
    expect(conflicts.has(cellKey(4, 4))).toBe(true);
  });
});

