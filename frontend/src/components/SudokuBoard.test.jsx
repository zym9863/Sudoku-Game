import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SudokuBoard } from "./SudokuBoard";

const game = {
  currentGrid: [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
  ],
  notes: Array.from({ length: 9 }, () => Array.from({ length: 9 }, () => [])),
  fixedCells: [
    [true, true, false, false, true, false, false, false, false],
    [true, false, false, true, true, true, false, false, false],
    [false, true, true, false, false, false, false, true, false],
    [true, false, false, false, true, false, false, false, true],
    [true, false, false, true, false, true, false, false, true],
    [true, false, false, false, true, false, false, false, true],
    [false, true, false, false, false, false, true, true, false],
    [false, false, false, true, true, true, false, false, true],
    [false, false, false, false, true, false, false, true, true]
  ]
};
game.notes[0][2] = [1, 4, 9];

describe("SudokuBoard", () => {
  it("renders fixed values and candidate notes", () => {
    render(
      <SudokuBoard game={game} selectedCell={{ row: 0, col: 0 }} conflictCells={new Set()} onSelect={() => {}} />
    );

    expect(screen.getByTestId("cell-0-0")).toHaveTextContent("5");
    expect(screen.getByTestId("cell-0-2")).toHaveTextContent("1");
    expect(screen.getByTestId("cell-0-2")).toHaveTextContent("4");
    expect(screen.getByTestId("cell-0-2")).toHaveTextContent("9");
  });

  it("notifies parent when a cell is selected", () => {
    const onSelect = vi.fn();
    render(
      <SudokuBoard game={game} selectedCell={null} conflictCells={new Set(["0-2"])} onSelect={onSelect} />
    );

    fireEvent.click(screen.getByTestId("cell-0-2"));

    expect(onSelect).toHaveBeenCalledWith({ row: 0, col: 2 });
    expect(screen.getByTestId("cell-0-2")).toHaveClass("is-conflict");
  });
});

