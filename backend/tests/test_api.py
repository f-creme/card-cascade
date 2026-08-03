from fastapi.testclient import TestClient

from app.main import app, rooms

def fresh_client() -> TestClient:
    return TestClient(app)

def test_create_room_returns_a_six_character_code():
    client = fresh_client()

    response = client.post("/rooms")

    assert response.status_code == 200
    room_id = response.json()["room_id"]
    assert len(room_id) == 6

def test_join_room_returns_the_lobby_player_list():
    client = fresh_client()
    room_id = client.post("/rooms").json()["room_id"]

    client.post(f"/rooms/{room_id}/join", json={"player_id": "p0", "username": "Alice"})
    response = client.post(f"/rooms/{room_id}/join", json={"player_id": "p1", "username": "Bob"})

    assert response.status_code == 200
    assert response.json()["players"] == [
        {"id": "p0", "username": "Alice"},
        {"id": "p1", "username": "Bob"},
    ]

def test_join_unknown_room_returns_404():
    client = fresh_client()

    response = client.post("/rooms/GHOST0/join", json={"player_id": "p0", "username": "Alice"})

    assert response.status_code == 404

def test_start_room_requires_two_players():
    client = fresh_client()
    room_id = client.post("/rooms").json()["room_id"]
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p0", "username": "Alice"})

    response = client.post(f"/rooms/{room_id}/start")

    assert response.status_code == 400

def test_cannot_join_after_start():
    client = fresh_client()
    room_id = client.post("/rooms").json()["room_id"]
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p0", "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p1", "username": "Bob"})
    client.post(f"/rooms/{room_id}/start")

    response = client.post(f"/rooms/{room_id}/join", json={"player_id": "p2", "username": "Charlie"})

    assert response.status_code == 409

def test_websocket_rejects_unknown_room():
    from starlette.websockets import WebSocketDisconnect

    client = fresh_client()

    try:
        with client.websocket_connect("/ws/GHOST0/p0"):
            pass
        assert False, "aurait dû fermer la connexion"
    except WebSocketDisconnect as exc:
        assert exc.code == 4404

def test_websocket_rejects_unregistered_player():
    from starlette.websockets import WebSocketDisconnect

    client = fresh_client()
    room_id = client.post("/rooms").json()["room_id"]
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p0", "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p1", "username": "Bob"})
    client.post(f"/rooms/{room_id}/start")

    try:
        with client.websocket_connect(f"/ws/{room_id}/never-joined"):
            pass
        assert False, "aurait dû fermer la connexion"
    except WebSocketDisconnect as exc:
        assert exc.code == 4403

def test_full_flow_two_players_draw_and_broadcast():
    client = fresh_client()
    room_id = client.post("/rooms").json()["room_id"]
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p0", "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p1", "username": "Bob"})
    client.post(f"/rooms/{room_id}/start")

    with client.websocket_connect(f"/ws/{room_id}/p0") as ws0:
        initial0 = ws0.receive_json()
        assert initial0["player_id"] == "p0"
        assert len(initial0["hand"]) == 7
        assert initial0["current_player_index"] == 0 

        with client.websocket_connect(f"/ws/{room_id}/p1") as ws1:
            initial1 = ws1.receive_json()
            assert initial1["player_id"] == "p1"

            ws0.send_json({"kind": "draw", "player_id": "p0"})

            update0 = ws0.receive_json()
            update1 = ws1.receive_json()

    assert len(update0["hand"]) == 8
    assert update0["has_drawn"] is True

    p0_from_p1_view = next(p for p in update1["players"] if p["id"] == "p0")
    assert p0_from_p1_view["hand_count"] == 8
    assert "hand" not in p0_from_p1_view

def test_illegal_action_returns_an_error_without_crashing():
    client = fresh_client()
    room_id = client.post("/rooms").json()["room_id"]
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p0", "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": "p1", "username": "Bob"})
    client.post(f"/rooms/{room_id}/start")

    with client.websocket_connect(f"/ws/{room_id}/p0") as ws0:
        ws0.receive_json()  # vue initiale

        ws0.send_json({"kind": "draw", "player_id": "p1"})

        response = ws0.receive_json()
        assert "error" in response