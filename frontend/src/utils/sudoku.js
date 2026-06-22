export function cellKey(row, col) {
  return `${row}-${col}`;
}

export function formatDuration(totalSeconds = 0) {
  const safeSeconds = Math.max(0, Number(totalSeconds) || 0);
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

export function toggleNote(notes, value) {
  const noteSet = new Set(notes || []);
  if (noteSet.has(value)) {
    noteSet.delete(value);
  } else {
    noteSet.add(value);
  }
  return Array.from(noteSet).sort((a, b) => a - b);
}

function markDuplicateUnit(conflicts, cells) {
  const byValue = new Map();
  cells.forEach(({ row, col, value }) => {
    if (!value) return;
    const bucket = byValue.get(value) || [];
    bucket.push({ row, col });
    byValue.set(value, bucket);
  });

  byValue.forEach((bucket) => {
    if (bucket.length < 2) return;
    bucket.forEach(({ row, col }) => conflicts.add(cellKey(row, col)));
  });
}

export function findDuplicateCells(grid) {
  const conflicts = new Set();

  for (let row = 0; row < 9; row += 1) {
    markDuplicateUnit(
      conflicts,
      Array.from({ length: 9 }, (_, col) => ({ row, col, value: grid[row][col] }))
    );
  }

  for (let col = 0; col < 9; col += 1) {
    markDuplicateUnit(
      conflicts,
      Array.from({ length: 9 }, (_, row) => ({ row, col, value: grid[row][col] }))
    );
  }

  for (let boxRow = 0; boxRow < 9; boxRow += 3) {
    for (let boxCol = 0; boxCol < 9; boxCol += 3) {
      const cells = [];
      for (let row = boxRow; row < boxRow + 3; row += 1) {
        for (let col = boxCol; col < boxCol + 3; col += 1) {
          cells.push({ row, col, value: grid[row][col] });
        }
      }
      markDuplicateUnit(conflicts, cells);
    }
  }

  return conflicts;
}

export function isSameHouse(a, b) {
  if (!a || !b) return false;
  return a.row === b.row || a.col === b.col || Math.floor(a.row / 3) === Math.floor(b.row / 3) && Math.floor(a.col / 3) === Math.floor(b.col / 3);
}

