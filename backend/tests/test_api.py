import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from app.game.cards import Color, NumberCard
from app.main import app, rooms

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def new_player_id() -> str:
    return str(uuid.uuid4())


def run(coro):
    return asyncio.run(coro)

def test_create_room_returns_a_six_character_code(client):
    response = client.post("/rooms")

    assert response.status_code == 200
    room_id = response.json()["room_id"]
    assert len(room_id) == 6

def test_join_room_returns_the_lobby_player_list_and_owner(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()

    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    response = client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})

    assert response.status_code == 200
    body = response.json()
    assert body["owner_id"] == alice  # premier arrivé
    assert body["players"] == [
        {"id": alice, "username": "Alice"},
        {"id": bob, "username": "Bob"},
    ]

def test_join_unknown_room_returns_404(client):
    response = client.post("/rooms/GHOST0/join", json={"player_id": new_player_id(), "username": "Alice"})

    assert response.status_code == 404

def test_start_room_requires_two_players(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice = new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})

    response = client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    assert response.status_code == 400

def test_start_room_requires_the_owner(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})

    response = client.post(f"/rooms/{room_id}/start", json={"player_id": bob})

    assert response.status_code == 403

def test_cannot_join_after_start(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice = new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": new_player_id(), "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    response = client.post(f"/rooms/{room_id}/join", json={"player_id": new_player_id(), "username": "Charlie"})

    assert response.status_code == 409

def test_websocket_rejects_unknown_room(client):
    from starlette.websockets import WebSocketDisconnect

    try:
        with client.websocket_connect(f"/ws/GHOST0/{new_player_id()}"):
            pass
        assert False, "aurait dû fermer la connexion"
    except WebSocketDisconnect as exc:
        assert exc.code == 4404

def test_websocket_rejects_unregistered_player(client):
    from starlette.websockets import WebSocketDisconnect

    room_id = client.post("/rooms").json()["room_id"]
    alice = new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": new_player_id(), "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    try:
        with client.websocket_connect(f"/ws/{room_id}/{new_player_id()}"):
            pass
        assert False, "aurait dû fermer la connexion"
    except WebSocketDisconnect as exc:
        assert exc.code == 4403

def test_full_flow_two_players_draw_and_broadcast(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    with client.websocket_connect(f"/ws/{room_id}/{alice}") as ws0:
        initial0 = ws0.receive_json()
        assert initial0["player_id"] == alice
        assert len(initial0["hand"]) == 7
        assert initial0["current_player_index"] == 0  # alice commence toujours

        with client.websocket_connect(f"/ws/{room_id}/{bob}") as ws1:
            initial1 = ws1.receive_json()
            assert initial1["player_id"] == bob

            ws0.send_json({"kind": "draw", "player_id": alice})

            update0 = ws0.receive_json()
            update1 = ws1.receive_json()

    assert len(update0["hand"]) == 8
    assert update0["has_drawn"] is True

    alice_from_bob_view = next(p for p in update1["players"] if p["id"] == alice)
    assert alice_from_bob_view["hand_count"] == 8
    assert "hand" not in alice_from_bob_view

def test_illegal_action_returns_an_error_without_crashing(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    with client.websocket_connect(f"/ws/{room_id}/{alice}") as ws0:
        ws0.receive_json()  # vue initiale

        ws0.send_json({"kind": "draw", "player_id": bob})  # ce n'est pas le tour de bob

        response = ws0.receive_json()
        assert "error" in response

def test_winning_a_game_persists_stats_to_the_database(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    # on force une main sur le point de gagner plutôt que de jouer plusieurs
    # coups légaux juste pour vider une main distribuée au hasard
    room = rooms.get_room(room_id)
    room.state.discard_pile = [NumberCard(id="top", value=5, color=Color.GREEN)]
    room.state.players[0].hand = [NumberCard(id="win", value=5, color=Color.GREEN)]
    room.state.current_player_index = 0

    with client.websocket_connect(f"/ws/{room_id}/{alice}") as ws0:
        ws0.receive_json()  # vue initiale
        ws0.send_json({"kind": "play_card", "player_id": alice, "card_id": "win"})

        final_view = ws0.receive_json()

    assert final_view["winner_id"] == alice

    import asyncpg

    from app.config import settings

    async def fetch_stats():
        conn = await asyncpg.connect(settings.database_url)
        try:
            row_alice = await conn.fetchrow("SELECT games_played, games_won FROM users WHERE uuid = $1", alice)
            row_bob = await conn.fetchrow("SELECT games_played, games_won FROM users WHERE uuid = $1", bob)
            return row_alice, row_bob
        finally:
            await conn.close()

    row_alice, row_bob = run(fetch_stats())

    assert dict(row_alice) == {"games_played": 1, "games_won": 1}
    assert dict(row_bob) == {"games_played": 1, "games_won": 0}

def test_get_user_profile_after_joining(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice = new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})

    response = client.get(f"/users/{alice}")

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "Alice"
    assert body["games_played"] == 0
    assert body["games_won"] == 0

def test_get_unknown_user_profile_returns_404(client):
    response = client.get(f"/users/{new_player_id()}")

    assert response.status_code == 404

def test_rejoining_with_a_new_username_updates_it(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice = new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})

    # une deuxième room, même uuid, nouveau pseudo
    room_id_2 = client.post("/rooms").json()["room_id"]
    client.post(f"/rooms/{room_id_2}/join", json={"player_id": alice, "username": "Alicia"})

    response = client.get(f"/users/{alice}")

    assert response.json()["username"] == "Alicia"

def test_leaving_via_websocket_is_broadcast_and_can_end_the_game(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    with client.websocket_connect(f"/ws/{room_id}/{alice}") as ws0:
        ws0.receive_json()

        with client.websocket_connect(f"/ws/{room_id}/{bob}") as ws1:
            ws1.receive_json()

            ws0.send_json({"kind": "leave", "player_id": alice})

            update0 = ws0.receive_json()
            update1 = ws1.receive_json()

    assert update1["winner_id"] == bob
    alice_from_bob_view = next(p for p in update1["players"] if p["id"] == alice)
    assert alice_from_bob_view["has_left"] is True
    assert update0["winner_id"] == bob

def test_get_room_status_returns_players_with_stats(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice", "avatar": "avatar-1"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob", "avatar": "avatar-2"})

    response = client.get(f"/rooms/{room_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["owner_id"] == alice
    assert body["started"] is False
    assert body["players"] == [
        {"id": alice, "username": "Alice", "avatar": "avatar-1", "games_played": 0, "games_won": 0},
        {"id": bob, "username": "Bob", "avatar": "avatar-2", "games_played": 0, "games_won": 0},
    ]


def test_get_room_status_reflects_started_flag(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    response = client.get(f"/rooms/{room_id}")

    assert response.json()["started"] is True


def test_get_room_status_unknown_room_returns_404(client):
    response = client.get("/rooms/GHOST0")

    assert response.status_code == 404

def test_get_room_scores_before_game_ends_returns_400(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    response = client.get(f"/rooms/{room_id}/scores")

    assert response.status_code == 400

def test_get_room_scores_unknown_room_returns_404(client):
    response = client.get("/rooms/GHOST0/scores")

    assert response.status_code == 404

def test_get_room_scores_after_win_returns_ranking(client):
    room_id = client.post("/rooms").json()["room_id"]
    alice, bob = new_player_id(), new_player_id()
    client.post(f"/rooms/{room_id}/join", json={"player_id": alice, "username": "Alice", "avatar": "avatar-1"})
    client.post(f"/rooms/{room_id}/join", json={"player_id": bob, "username": "Bob", "avatar": "avatar-2"})
    client.post(f"/rooms/{room_id}/start", json={"player_id": alice})

    room = rooms.get_room(room_id)
    room.state.discard_pile = [NumberCard(id="top", value=5, color=Color.GREEN)]
    room.state.players[0].hand = [NumberCard(id="win", value=5, color=Color.GREEN)]
    room.state.players[1].hand = [
        NumberCard(id="left1", value=7, color=Color.BROWN),
        NumberCard(id="left2", value=3, color=Color.RED),
    ]
    room.state.current_player_index = 0

    with client.websocket_connect(f"/ws/{room_id}/{alice}") as ws0:
        ws0.receive_json()
        ws0.send_json({"kind": "play_card", "player_id": alice, "card_id": "win"})
        ws0.receive_json()

    response = client.get(f"/rooms/{room_id}/scores")

    assert response.status_code == 200
    body = response.json()
    assert body["winner_id"] == alice
    assert body["ranking"] == [
        {"id": alice, "username": "Alice", "avatar": "avatar-1", "score": 0, "cards_remaining": 0},
        {"id": bob, "username": "Bob", "avatar": "avatar-2", "score": 10, "cards_remaining": 2},
    ]