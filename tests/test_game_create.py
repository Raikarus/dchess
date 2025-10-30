from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_make_move_success():
    # Пример успешного хода – подставьте валидные координаты и формат запроса
    response = client.post("/api/game/make_move", json={
        "from_x": 6, "from_y": 0, "from_z": 1,
        "to_x": 6, "to_y": 0, "to_z": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "Move made successfully" in data["message"]


def test_make_move_invalid():
    # Пример для невалидного хода
    response = client.post("/api/game/make_move", json={
        "from_x": 100, "from_y": 100, "from_z": 100,
        "to_x": 101, "to_y": 101, "to_z": 101
    })
    assert response.status_code == 400


def test_get_state():
    response = client.get("/api/game/state")
    assert response.status_code == 200
    data = response.json()
    assert "current_turn" in data
    assert "game_state" in data
    assert "board" in data
    assert "move_history" in data
