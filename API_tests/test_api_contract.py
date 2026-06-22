def test_health_and_create_game(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": "sudoku-api"}

    created = client.post("/api/games", json={"difficulty": "medium", "playerId": "player_contract"})
    body = created.json()

    assert created.status_code == 201
    assert body["difficulty"] == "medium"
    assert body["playerId"] == "player_contract"
    assert "solution" not in body
    assert len(body["puzzle"]) == 9
    assert len(body["fixedCells"]) == 9


def test_create_game_validation_errors(client):
    missing_player = client.post("/api/games", json={"difficulty": "easy"})
    invalid_difficulty = client.post("/api/games", json={"difficulty": "expert", "playerId": "player_api"})

    assert missing_player.status_code == 422
    assert missing_player.json()["msg"] == "Validation failed"
    assert invalid_difficulty.status_code == 422
    assert invalid_difficulty.json()["code"] == 422


def test_get_game_active_game_and_stats(client, game):
    game_id = game["id"]

    fetched = client.get(f"/api/games/{game_id}")
    active = client.get("/api/games/active/player_api")
    stats = client.get("/api/stats/player_api")

    assert fetched.status_code == 200
    assert fetched.json()["id"] == game_id
    assert active.status_code == 200
    assert active.json()["id"] == game_id
    assert stats.status_code == 200
    assert stats.json()["activeGames"] == 1
    assert stats.json()["completedGames"] == 0


def test_get_game_not_found_returns_json_error(client):
    response = client.get("/api/games/not-found")

    assert response.status_code == 404
    assert response.json() == {"code": 404, "msg": "Game not found"}


def test_update_cell_value_notes_and_rejections(client, game):
    game_id = game["id"]

    notes = client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 0, "col": 2, "mode": "notes", "notes": [1, 4, 9]},
    )
    value = client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 0, "col": 2, "mode": "value", "value": 4},
    )
    fixed = client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 0, "col": 0, "mode": "value", "value": 1},
    )
    invalid_row = client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 9, "col": 0, "mode": "value", "value": 1},
    )

    assert notes.status_code == 200
    assert notes.json()["notes"][0][2] == [1, 4, 9]
    assert value.status_code == 200
    assert value.json()["currentGrid"][0][2] == 4
    assert value.json()["notes"][0][2] == []
    assert fixed.status_code == 400
    assert fixed.json()["msg"] == "Fixed puzzle cells cannot be edited"
    assert invalid_row.status_code == 422


def test_check_and_hint_interfaces(client, game):
    game_id = game["id"]
    wrong = client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 0, "col": 2, "mode": "value", "value": 9},
    )
    check = client.post(f"/api/games/{game_id}/check")
    hint = client.post(f"/api/games/{game_id}/hint")

    assert wrong.status_code == 200
    assert wrong.json()["mistakeCount"] == 1
    assert check.status_code == 200
    assert check.json()["isComplete"] is False
    assert any(item["reason"] == "wrong_value" for item in check.json()["conflicts"])
    assert hint.status_code == 200
    assert hint.json()["hintCount"] == 1
    assert hint.json()["currentGrid"][hint.json()["row"]][hint.json()["col"]] == hint.json()["value"]


def test_completed_game_rejects_mutations_and_updates_stats(completed_client):
    create = completed_client.post("/api/games", json={"difficulty": "easy", "playerId": "player_done"})
    game_id = create.json()["id"]
    complete = completed_client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 0, "col": 0, "mode": "value", "value": 5},
    )
    check = completed_client.post(f"/api/games/{game_id}/check")
    rejected_update = completed_client.patch(
        f"/api/games/{game_id}/cell",
        json={"row": 0, "col": 0, "mode": "value", "value": 0},
    )
    rejected_hint = completed_client.post(f"/api/games/{game_id}/hint")
    stats = completed_client.get("/api/stats/player_done")

    assert complete.status_code == 200
    assert complete.json()["status"] == "completed"
    assert check.status_code == 200
    assert check.json()["isComplete"] is True
    assert rejected_update.status_code == 409
    assert rejected_hint.status_code == 409
    assert stats.status_code == 200
    assert stats.json()["completedGames"] == 1
    assert stats.json()["bestTimes"]["easy"] is not None


def test_active_game_not_found_and_invalid_player(client):
    not_found = client.get("/api/games/active/player_none")
    invalid_player = client.get("/api/stats/bad player")

    assert not_found.status_code == 404
    assert not_found.json()["msg"] == "No active game found for this player"
    assert invalid_player.status_code == 422

