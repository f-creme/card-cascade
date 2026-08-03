import random
import string

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, TypeAdapter, ValidationError

from app.config import settings
from app.game.engine import Action, IllegalActionError, apply_action
from app.game.view import build_player_view
from app.rooms import RoomManager

app = FastAPI(title="card-cascade-api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

rooms = RoomManager()
action_adapter = TypeAdapter(Action)

ROOM_ID_ALPHABET = string.ascii_uppercase + string.digits
ROOM_ID_LENGHT = 6

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}

# --- REST : create a room, join, start ---
class LobbyPlayer(BaseModel):
    id: str
    username: str

class CreateRoomResponse(BaseModel):
    room_id: str

class JoinRoomRequest(BaseModel):
    player_id: str
    username: str

class JoinRoomResponse(BaseModel):
    players: list[LobbyPlayer]

class StartRoomResponse(BaseModel):
    status: str

@app.post("/rooms", response_model=CreateRoomResponse)
def create_room() -> CreateRoomResponse:
    for _ in range(10):
        candidate = "".join(random.choices(ROOM_ID_ALPHABET, k=ROOM_ID_LENGHT))
        try: 
            rooms.create_room(candidate)
        except ValueError:
            continue
        return CreateRoomResponse(room_id=candidate)
    raise HTTPException(status_code=500, detail="Unable to create an identifier for the room")

@app.post("/rooms/{room_id}/join", response_model=JoinRoomResponse)
def join_room(room_id: str, body: JoinRoomRequest) -> JoinRoomResponse:
    try:
        room = rooms.get_room(room_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown room")

    try: 
        room.add_player(body.player_id, body.username)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return JoinRoomResponse(players=[LobbyPlayer(id=pid, username=u) for pid, u in room.players])

@app.post("/rooms/{room_id}/start", response_model=StartRoomResponse)
def start_room(room_id: str) -> StartRoomResponse:
    try:
        room = rooms.get_room(room_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown room")

    try: 
        room.start()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StartRoomResponse(status="started")

# --- WebSocket only for playing, after registration via /join ---
@app.websocket("/ws/{room_id}/{player_id}")
async def play(websocket: WebSocket, room_id: str, player_id: str) -> None:
    try: 
        room = rooms.get_room(room_id)
    except KeyError:
        await websocket.close(code=4404)
        return

    if room.state is None:
        await websocket.close(code=4400)
        return

    if not any(p.id == player_id for p in room.state.players):
        await websocket.close(code=4403)
        return

    await websocket.accept()
    room.connections[player_id] = websocket

    try:
        await _send_view(room, player_id)

        while True:
            raw = await websocket.receive_json()
            try:
                action = action_adapter.validate_python(raw)
                room.state = apply_action(room.state, action)
            except (IllegalActionError, ValidationError) as e:
                await websocket.send_json({"error": str(e)})
                continue

            await _broadcast_view(room)

    except WebSocketDisconnect:
        pass

    finally:
        room.connections.pop(player_id, None)

async def _send_view(room, player_id: str) -> None:
    view = build_player_view(room.state, player_id)
    await room.connections[player_id].send_text(view.model_dump_json())

async def _broadcast_view(room) -> None:
    for pid, ws in room.connections.items():
        view = build_player_view(room.state, pid)
        await ws.send_text(view.model_dump_json())