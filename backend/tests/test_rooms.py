import pytest

from app.rooms import Room, RoomManager

def test_create_and_get_room():
    manager = RoomManager()
    created = manager.create_room("abc123")

    fetched = manager.get_room("abc123")

    assert fetched is created
    assert fetched.players == []
    assert fetched.state is None
    assert fetched.owner_id is None

def test_cannot_create_duplicate_room():
    manager = RoomManager()
    manager.create_room("abc123")

    with pytest.raises(ValueError):
        manager.create_room("abc123")

def test_get_unknown_room_raises():
    manager = RoomManager()

    with pytest.raises(KeyError):
        manager.get_room("does-not-exist")

def test_add_player_appends_to_the_lobby():
    room = Room(id="r1")

    room.add_player("p0", "Alice")
    room.add_player("p1", "Bob")

    assert room.players == [("p0", "Alice"), ("p1", "Bob")]

def test_first_player_to_join_becomes_owner():
    room = Room(id="r1")

    room.add_player("p0", "Alice")
    room.add_player("p1", "Bob")

    assert room.owner_id == "p0"

def test_adding_the_same_player_twice_is_a_no_op():
    room = Room(id="r1")

    room.add_player("p0", "Alice")
    room.add_player("p0", "Alice")

    assert room.players == [("p0", "Alice")]
    assert room.owner_id == "p0"

def test_start_requires_at_least_two_players():
    room = Room(id="r1")
    room.add_player("p0", "Alice")

    with pytest.raises(ValueError):
        room.start("p0")


def test_start_requires_the_owner():
    room = Room(id="r1")
    room.add_player("p0", "Alice")
    room.add_player("p1", "Bob")

    with pytest.raises(PermissionError):
        room.start("p1")  # p1 n'est pas le propriétaire

def test_start_deals_a_real_game_state():
    room = Room(id="r1")
    room.add_player("p0", "Alice")
    room.add_player("p1", "Bob")

    room.start("p0")

    assert room.state is not None
    assert len(room.state.players) == 2
    assert all(len(p.hand) == 7 for p in room.state.players)

def test_cannot_add_player_after_start():
    room = Room(id="r1")
    room.add_player("p0", "Alice")
    room.add_player("p1", "Bob")
    room.start("p0")

    with pytest.raises(ValueError):
        room.add_player("p2", "Charlie")

def test_cannot_start_twice():
    room = Room(id="r1")
    room.add_player("p0", "Alice")
    room.add_player("p1", "Bob")
    room.start("p0")

    with pytest.raises(ValueError):
        room.start("p0")