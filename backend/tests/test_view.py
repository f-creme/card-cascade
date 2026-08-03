from app.game.cards import Color, NumberCard
from app.game.state import GameState, Player
from app.game.view import build_player_view

def make_state() -> GameState:
    hand0 = [NumberCard(id="secret0", value=5, color=Color.GREEN)]
    hand1 = [
        NumberCard(id="secret1", value=3, color=Color.BLUE),
        NumberCard(id="secret1b", value=4, color=Color.BLUE),
    ]
    players = [
        Player(id="p0", username="Alice", hand=hand0),
        Player(id="p1", username="Bob", hand=hand1),
    ]
    top = NumberCard(id="top", value=0, color=Color.PINK)
    return GameState(
        players=players,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(5)],
        discard_pile=[top],
    )

def test_own_hand_is_visible_in_full():
    state = make_state()

    view = build_player_view(state, "p0")

    assert [c.id for c in view.hand] == ["secret0"]

def test_other_players_only_expose_hand_count():
    state = make_state()

    view = build_player_view(state, "p0")

    bob = next(p for p in view.players if p.id == "p1")
    assert bob.hand_count == 2
    assert not hasattr(bob, "hand") 

def test_draw_pile_only_exposes_a_count():
    state = make_state()

    view = build_player_view(state, "p0")

    assert view.draw_pile_count == 5

def test_serialized_view_never_contains_other_players_card_ids():
    state = make_state()

    view = build_player_view(state, "p0")
    serialized = view.model_dump_json()

    assert "secret1" not in serialized
    assert "secret1b" not in serialized
    assert "secret0" in serialized  

def test_unknown_player_raises():
    state = make_state()

    try:
        build_player_view(state, "ghost")
        assert False, "should have raise an error"
    except ValueError:
        pass