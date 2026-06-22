const PLAYER_KEY = "sudoku_player_id";
const GAME_KEY = "sudoku_current_game_id";

function makePlayerId() {
  const randomPart =
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
  return `player_${randomPart.replace(/[^A-Za-z0-9_-]/g, "_")}`;
}

export function getOrCreatePlayerId(storage = window.localStorage) {
  const existing = storage.getItem(PLAYER_KEY);
  if (existing) {
    return existing;
  }

  const playerId = makePlayerId();
  storage.setItem(PLAYER_KEY, playerId);
  return playerId;
}

export function getStoredGameId(storage = window.localStorage) {
  return storage.getItem(GAME_KEY);
}

export function setStoredGameId(gameId, storage = window.localStorage) {
  storage.setItem(GAME_KEY, gameId);
}

