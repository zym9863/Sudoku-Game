const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  constructor(message, code, details) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(body.msg || "请求失败", body.code || response.status, body.details);
  }
  return body;
}

export const api = {
  createGame(payload) {
    return request("/games", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  getGame(gameId) {
    return request(`/games/${gameId}`);
  },
  getActiveGame(playerId) {
    return request(`/games/active/${playerId}`);
  },
  updateCell(gameId, payload) {
    return request(`/games/${gameId}/cell`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  checkGame(gameId) {
    return request(`/games/${gameId}/check`, {
      method: "POST"
    });
  },
  hintGame(gameId) {
    return request(`/games/${gameId}/hint`, {
      method: "POST"
    });
  },
  getStats(playerId) {
    return request(`/stats/${playerId}`);
  }
};

