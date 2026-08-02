import pytest

from app.game.cards import BlockCard, Color, NumberCard
from app.game.engine import (
    DrawAction,
    IllegalActionError,
    PassAction,
    PlayCardAction,
    PlayPairAction,
    apply_action,
)
from app.game.state import GameState, Player


def make_state(hands: list[list], top_card: NumberCard, draw_pile: list | None = None) -> GameState:
    players = [
        Player(id=f"p{i}", username=f"Player {i}", hand=hand)
        for i, hand in enumerate(hands)
    ]
    return GameState(players=players, draw_pile=draw_pile or [], discard_pile=[top_card])

# --- play_card ---
def test_play_card_with_matching_number():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=5, color=Color.RED)
    state = make_state(hands=[[my_card], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

    assert new_state.discard_pile[-1].id == "c1"
    assert new_state.players[0].hand == []

def test_play_card_with_adjacent_value():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=6, color=Color.PINK)
    state = make_state(hands=[[my_card], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

    assert new_state.discard_pile[-1].id == "c1"

def test_play_card_with_matching_color():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=8, color=Color.GREEN) 
    state = make_state(hands=[[my_card], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

    assert new_state.discard_pile[-1].id == "c1"

def test_play_card_with_no_match_is_illegal():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=9, color=Color.ORANGE)  
    state = make_state(hands=[[my_card], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

def test_cannot_play_out_of_turn():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=5, color=Color.RED)
    state = make_state(hands=[[NumberCard(id="x", value=0, color=Color.PINK)], [my_card]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlayCardAction(player_id="p1", card_id="c1"))

def test_cannot_play_special_card_via_play_card_action():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = BlockCard(id="c1")
    state = make_state(hands=[[my_card], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

def test_turn_advances_to_next_player():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=5, color=Color.RED)
    other_card = NumberCard(id="c2", value=0, color=Color.PINK)
    state = make_state(hands=[[my_card, other_card], [other_card]], top_card=top)

    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

    assert new_state.current_player_index == 1

def test_emptying_hand_sets_winner_and_does_not_advance_turn():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=5, color=Color.RED)
    state = make_state(hands=[[my_card], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="c1"))

    assert new_state.winner_id == "p0"
    assert new_state.current_player_index == 0  

# --- play_pair ---
def test_play_pair_with_correct_sum():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    a = NumberCard(id="a", value=5, color=Color.RED)
    b = NumberCard(id="b", value=3, color=Color.BLUE)
    state = make_state(hands=[[a, b], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    new_state = apply_action(
        state, PlayPairAction(player_id="p0", card_id_1="a", card_id_2="b", top_card_id="a")
    )

    assert [c.id for c in new_state.discard_pile[-2:]] == ["b", "a"]
    assert new_state.players[0].hand == []

def test_play_pair_with_wrong_sum_is_illegal():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    a = NumberCard(id="a", value=5, color=Color.RED)
    b = NumberCard(id="b", value=1, color=Color.GREY)
    state = make_state(hands=[[a, b], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlayPairAction(player_id="p0", card_id_1="a", card_id_2="b", top_card_id="a"))

def test_play_pair_same_card_twice_is_illegal():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    a = NumberCard(id="a", value=4, color=Color.BLUE)
    state = make_state(hands=[[a], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlayPairAction(player_id="p0", card_id_1="a", card_id_2="a", top_card_id="a"))

def test_play_pair_on_special_top_is_illegal():
    top = BlockCard(id="top")
    a = NumberCard(id="a", value=5, color=Color.RED)
    b = NumberCard(id="b", value=3, color=Color.BLUE)
    state = make_state(hands=[[a, b], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlayPairAction(player_id="p0", card_id_1="a", card_id_2="b", top_card_id="a"))

# --- draw ---
def test_draw_adds_card_to_hand_without_ending_turn():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    drawn = NumberCard(id="drawn", value=9, color=Color.ORANGE) 
    state = make_state(
        hands=[[], [NumberCard(id="x", value=0, color=Color.PINK)]],
        top_card=top,
        draw_pile=[drawn],
    )

    new_state = apply_action(state, DrawAction(player_id="p0"))

    assert new_state.players[0].hand == [drawn]
    assert new_state.discard_pile[-1].id == "top"  
    assert new_state.current_player_index == 0  
    assert new_state.has_drawn is True

def test_cannot_draw_twice_in_the_same_turn():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    state = make_state(
        hands=[[], [NumberCard(id="x", value=0, color=Color.PINK)]],
        top_card=top,
        draw_pile=[NumberCard(id="d1", value=1, color=Color.GREY), NumberCard(id="d2", value=1, color=Color.GREY)],
    )

    state = apply_action(state, DrawAction(player_id="p0"))

    with pytest.raises(IllegalActionError):
        apply_action(state, DrawAction(player_id="p0"))

def test_draw_reshuffles_discard_when_pile_empty():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    buried = NumberCard(id="buried", value=1, color=Color.GREY)
    state = make_state(
        hands=[[], [NumberCard(id="x", value=0, color=Color.PINK)]],
        top_card=top,
        draw_pile=[],
    )
    state.discard_pile = [buried, top]  

    new_state = apply_action(state, DrawAction(player_id="p0"))

    assert new_state.discard_pile == [top]
    assert new_state.players[0].hand == [buried]

def test_draw_with_empty_draw_and_discard_pile_is_illegal():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    state = make_state(
        hands=[[], [NumberCard(id="x", value=0, color=Color.PINK)]],
        top_card=top,
        draw_pile=[],
    )

    with pytest.raises(IllegalActionError):
        apply_action(state, DrawAction(player_id="p0"))

def test_can_play_the_drawn_card_afterwards():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    drawn = NumberCard(id="drawn", value=9, color=Color.ORANGE)
    keep = NumberCard(id="keep", value=3, color=Color.RED)  
    state = make_state(
        hands=[[keep], [NumberCard(id="x", value=0, color=Color.PINK)]],
        top_card=top,
        draw_pile=[drawn],
    )

    state = apply_action(state, DrawAction(player_id="p0"))
    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="drawn"))

    assert new_state.discard_pile[-1].id == "drawn"
    assert new_state.players[0].hand == [keep]
    assert new_state.current_player_index == 1
    assert new_state.has_drawn is False  

# --- pass ---
def test_cannot_pass_without_drawing_first():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    state = make_state(hands=[[], [NumberCard(id="x", value=0, color=Color.PINK)]], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PassAction(player_id="p0"))

def test_pass_after_drawing_ends_turn():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    drawn = NumberCard(id="drawn", value=2, color=Color.ORANGE) 
    state = make_state(
        hands=[[], [NumberCard(id="x", value=0, color=Color.PINK)]],
        top_card=top,
        draw_pile=[drawn],
    )

    state = apply_action(state, DrawAction(player_id="p0"))
    new_state = apply_action(state, PassAction(player_id="p0"))

    assert new_state.current_player_index == 1
    assert new_state.players[0].hand == [drawn]  
    assert new_state.has_drawn is False