from dataclasses import dataclass, field
from fastapi import WebSocket

from app.game.state import GameState, create_initial_state

@dataclass
class Room:
    id: str
    players: list[tuple[str, str]] = field(default_factory=list) # player_id, username
    state: GameState | None = None
    connections: dict[str, WebSocket] = field(default_factory=dict)

    def add_player(self, player_id: str, username: str) -> None: 
        if self.state is not None:
            raise ValueError("Game has already begun")
        if any(pid == player_id for pid, _ in self.players):
            return
        self.players.append((player_id, username))

    def start(self) -> None:
        if self.state is not None:
            raise ValueError("Game has already begun")
        if len(self.players) < 2:
            raise ValueError("2 players are required to start")
        self.state = create_initial_state(self.players)

class RoomManager:
    def __init__(self) -> None: 
        self._rooms: dict[str, Room] = {}

    def create_room(self, room_id: str) -> Room:
        if room_id in self._rooms:
            raise ValueError(f"The room '{room_id}' already exists")
        room = Room(id=room_id)
        self._rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> Room:
        room = self._rooms.get(room_id)
        if room is None:
            raise KeyError(f"Unknown room: '{room_id}'")
        return room