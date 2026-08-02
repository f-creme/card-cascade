import pytest

from app.game.cards import BlockCard, Color, NumberCard
from app.game.engine import IllegalActionError, PlayCardAction, apply_action
from app.game.state import GameState, Player

def make_state(hands: list[list], top_card: NumberCard) -> GameState:
    players = [
        Player(id=f"p{i}", username=f"Player {i}", hand=hand)
        for i, hand in enumerate(hands)
    ]
    return GameState(players=players, draw_pile=[], discard_pile=[top_card])

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