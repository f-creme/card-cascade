from dataclasses import dataclass, field
from fastapi import WebSocket

from app.game.state import GameState, create_initial_state

@dataclass
class Room:
    id: str
    owner_id: str | None = None
    players: list[tuple[str, str]] = field(default_factory=list) # player_id, username
    player_avatars: dict[str, str] = field(default_factory=dict)
    state: GameState | None = None
    connections: dict[str, WebSocket] = field(default_factory=dict)
    result_recorded: bool = False

    def add_player(self, player_id: str, username: str, avatar: str) -> None: 
        if self.state is not None:
            raise ValueError("Game has already begun")
        if any(pid == player_id for pid, _ in self.players):
            return
        if self.owner_id is None:
            self.owner_id = player_id # The first player to join is the room's owner
        self.players.append((player_id, username))
        if avatar:
            self.player_avatars[player_id] = avatar

    def start(self, requester_id: str) -> None:
        if self.state is not None:
            raise ValueError("Game has already begun")
        if requester_id != self.owner_id:
            raise PermissionError("Only room's owner can start the game.")
        if len(self.players) < 2:
            raise ValueError("2 players are required to start")
        self.state = create_initial_state(self.players, avatars=self.player_avatars)

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