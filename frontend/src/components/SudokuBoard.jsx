import { cellKey, isSameHouse } from "../utils/sudoku";

function NotesGrid({ notes }) {
  return (
    <span className="notes-grid" aria-hidden="true">
      {Array.from({ length: 9 }, (_, index) => {
        const value = index + 1;
        return <span key={value}>{notes?.includes(value) ? value : ""}</span>;
      })}
    </span>
  );
}

export function SudokuBoard({ game, selectedCell, conflictCells, hintCell, onSelect }) {
  if (!game) {
    return <div className="board-skeleton" aria-label="棋盘加载中" />;
  }

  const selectedValue =
    selectedCell && game.currentGrid[selectedCell.row]?.[selectedCell.col]
      ? game.currentGrid[selectedCell.row][selectedCell.col]
      : 0;

  return (
    <div className="sudoku-board" role="grid" aria-label="数独棋盘">
      {game.currentGrid.map((rowValues, row) =>
        rowValues.map((value, col) => {
          const fixed = game.fixedCells[row][col];
          const selected = selectedCell?.row === row && selectedCell?.col === col;
          const related = isSameHouse(selectedCell, { row, col });
          const sameValue = selectedValue !== 0 && value === selectedValue;
          const conflict = conflictCells.has(cellKey(row, col));
          const hinted = hintCell?.row === row && hintCell?.col === col;
          const notes = game.notes[row][col];

          return (
            <button
              key={cellKey(row, col)}
              type="button"
              role="gridcell"
              aria-label={`第 ${row + 1} 行第 ${col + 1} 列${value ? `，数字 ${value}` : ""}`}
              data-testid={`cell-${row}-${col}`}
              className={[
                "sudoku-cell",
                fixed ? "is-fixed" : "is-editable",
                selected ? "is-selected" : "",
                related && !selected ? "is-related" : "",
                sameValue && !selected ? "is-same-value" : "",
                conflict ? "is-conflict" : "",
                hinted ? "is-hinted" : "",
                row % 3 === 0 ? "thick-top" : "",
                col % 3 === 0 ? "thick-left" : "",
                row === 8 ? "thick-bottom" : "",
                col === 8 ? "thick-right" : ""
              ].join(" ")}
              onClick={() => onSelect({ row, col })}
            >
              {value ? <span className="cell-value">{value}</span> : <NotesGrid notes={notes} />}
            </button>
          );
        })
      )}
    </div>
  );
}

