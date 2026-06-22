import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { api, ApiError } from "./api/client";
import { GameToolbar } from "./components/GameToolbar";
import { NumberPad } from "./components/NumberPad";
import { StatsPanel } from "./components/StatsPanel";
import { SudokuBoard } from "./components/SudokuBoard";
import { Toast } from "./components/Toast";
import { getOrCreatePlayerId, setStoredGameId } from "./utils/player";
import { cellKey, findDuplicateCells, toggleNote } from "./utils/sudoku";

import "./styles.css";

function firstEditableCell(game) {
  if (!game) return null;
  for (let row = 0; row < 9; row += 1) {
    for (let col = 0; col < 9; col += 1) {
      if (!game.fixedCells[row][col] && game.currentGrid[row][col] === 0) {
        return { row, col };
      }
    }
  }
  return null;
}

function difficultyLabel(difficulty) {
  return { easy: "简单", medium: "中等", hard: "困难" }[difficulty] || "简单";
}

export default function App() {
  const [playerId, setPlayerId] = useState("");
  const [game, setGame] = useState(null);
  const [stats, setStats] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);
  const [serverConflictCells, setServerConflictCells] = useState(new Set());
  const [hintCell, setHintCell] = useState(null);
  const [noteMode, setNoteMode] = useState(false);
  const [busyAction, setBusyAction] = useState("");
  const [apiError, setApiError] = useState("");
  const [toast, setToast] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const toastTimer = useRef(null);

  const duplicateCells = useMemo(() => (game ? findDuplicateCells(game.currentGrid) : new Set()), [game]);
  const conflictCells = useMemo(
    () => new Set([...duplicateCells, ...serverConflictCells]),
    [duplicateCells, serverConflictCells]
  );

  const showToast = useCallback((message, type = "warning") => {
    setToast({ message, type });
    if (toastTimer.current) {
      window.clearTimeout(toastTimer.current);
    }
    toastTimer.current = window.setTimeout(() => setToast(null), 3200);
  }, []);

  const loadStats = useCallback(async (id) => {
    try {
      setStats(await api.getStats(id));
    } catch {
      setStats(null);
    }
  }, []);

  const activateGame = useCallback((nextGame) => {
    setGame(nextGame);
    setStoredGameId(nextGame.id);
    setSelectedCell(firstEditableCell(nextGame));
    setServerConflictCells(new Set());
    setHintCell(null);
  }, []);

  const startGame = useCallback(
    async (difficulty, id = playerId) => {
      if (!id) return;
      setBusyAction(`new-${difficulty}`);
      try {
        const nextGame = await api.createGame({ difficulty, playerId: id });
        activateGame(nextGame);
        await loadStats(id);
        setApiError("");
        showToast(`已开始${difficultyLabel(difficulty)}局`, "success");
      } catch (error) {
        const message = error instanceof ApiError ? error.message : "无法创建新局";
        setApiError(message);
        showToast(message, "error");
      } finally {
        setBusyAction("");
      }
    },
    [activateGame, loadStats, playerId, showToast]
  );

  const loadInitialGame = useCallback(async () => {
    const id = getOrCreatePlayerId();
    setPlayerId(id);
    setBusyAction("initial");

    try {
      const activeGame = await api.getActiveGame(id);
      activateGame(activeGame);
      setApiError("");
    } catch (error) {
      if (error instanceof ApiError && error.code === 404) {
        await startGame("easy", id);
      } else {
        const message = error instanceof ApiError ? error.message : "无法连接服务";
        setApiError(message);
        showToast(message, "error");
      }
    } finally {
      await loadStats(id);
      setBusyAction("");
    }
  }, [activateGame, loadStats, showToast, startGame]);

  useEffect(() => {
    loadInitialGame();
  }, [loadInitialGame]);

  useEffect(() => {
    if (!game) return undefined;

    const calculateElapsed = () => {
      if (game.status === "completed") {
        setElapsedSeconds(game.elapsedSeconds);
        return;
      }
      const startedAt = new Date(game.startedAt).getTime();
      setElapsedSeconds(Math.max(0, Math.floor((Date.now() - startedAt) / 1000)));
    };

    calculateElapsed();
    const timer = window.setInterval(calculateElapsed, 1000);
    return () => window.clearInterval(timer);
  }, [game]);

  const updateSelectedCell = useCallback(
    async (value, erase = false) => {
      if (!game || !selectedCell) {
        showToast("请选择一个格子");
        return;
      }

      const { row, col } = selectedCell;
      if (game.fixedCells[row][col]) {
        showToast("题目格不可修改");
        return;
      }
      if (game.status === "completed") {
        showToast("本局已完成");
        return;
      }

      setBusyAction("cell");
      try {
        const payload =
          noteMode && !erase
            ? {
                row,
                col,
                mode: "notes",
                notes: toggleNote(game.notes[row][col], value)
              }
            : {
                row,
                col,
                mode: "value",
                value: erase ? 0 : value
              };

        const updatedGame = await api.updateCell(game.id, payload);
        setGame(updatedGame);
        setServerConflictCells(new Set());
        if (updatedGame.status === "completed") {
          showToast("本局完成", "success");
          await loadStats(playerId);
        }
      } catch (error) {
        const message = error instanceof ApiError ? error.message : "更新失败";
        showToast(message, "error");
      } finally {
        setBusyAction("");
      }
    },
    [game, loadStats, noteMode, playerId, selectedCell, showToast]
  );

  const checkGame = useCallback(async () => {
    if (!game) return;
    setBusyAction("check");
    try {
      const result = await api.checkGame(game.id);
      setGame(result.game);
      setServerConflictCells(new Set(result.conflicts.map((item) => cellKey(item.row, item.col))));
      if (result.isComplete) {
        showToast("答案正确", "success");
      } else if (result.conflicts.length > 0) {
        showToast("有格子需要修正", "warning");
      } else {
        showToast(`还剩 ${result.emptyCells} 格`);
      }
      await loadStats(playerId);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "检查失败";
      showToast(message, "error");
    } finally {
      setBusyAction("");
    }
  }, [game, loadStats, playerId, showToast]);

  const getHint = useCallback(async () => {
    if (!game) return;
    setBusyAction("hint");
    try {
      const result = await api.hintGame(game.id);
      setGame(result.game);
      setHintCell({ row: result.row, col: result.col });
      setServerConflictCells(new Set());
      showToast("已填入一格提示", "success");
      window.setTimeout(() => setHintCell(null), 2600);
      if (result.status === "completed") {
        await loadStats(playerId);
      }
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "提示失败";
      showToast(message, "error");
    } finally {
      setBusyAction("");
    }
  }, [game, loadStats, playerId, showToast]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (!game || busyAction) return;
      if (/^[1-9]$/.test(event.key)) {
        updateSelectedCell(Number(event.key));
      }
      if (event.key === "Backspace" || event.key === "Delete" || event.key === "0") {
        updateSelectedCell(0, true);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [busyAction, game, updateSelectedCell]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Sudoku Studio</p>
          <h1>数独</h1>
        </div>
        <div className="status-pill">
          <span>{difficultyLabel(game?.difficulty)}</span>
          <strong>{game?.status === "completed" ? "完成" : "进行中"}</strong>
        </div>
      </header>

      {apiError && !game ? (
        <main className="error-state">
          <div>
            <p className="eyebrow">API</p>
            <h2>无法载入游戏</h2>
            <p>{apiError}</p>
          </div>
          <button type="button" className="command-button accent" onClick={loadInitialGame}>
            重试
          </button>
        </main>
      ) : (
        <main className="game-layout">
          <section className="board-column" aria-label="游戏区域">
            <SudokuBoard
              game={game}
              selectedCell={selectedCell}
              conflictCells={conflictCells}
              hintCell={hintCell}
              onSelect={setSelectedCell}
            />
          </section>
          <section className="control-column" aria-label="控制区">
            <GameToolbar
              difficulty={game?.difficulty || "easy"}
              busyAction={busyAction}
              disabled={!game || busyAction === "initial"}
              onNewGame={startGame}
              onCheck={checkGame}
              onHint={getHint}
            />
            <NumberPad
              noteMode={noteMode}
              busy={Boolean(busyAction) || game?.status === "completed"}
              onNumber={(value) => updateSelectedCell(value)}
              onErase={() => updateSelectedCell(0, true)}
              onToggleNotes={() => setNoteMode((enabled) => !enabled)}
            />
            <StatsPanel game={game} stats={stats} elapsedSeconds={elapsedSeconds} />
          </section>
        </main>
      )}

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}

