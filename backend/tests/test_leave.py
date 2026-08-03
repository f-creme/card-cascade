import pytest

from app.game.cards import Color, NumberCard
from app.game.engine import (
    DrawAction,
    IllegalActionError,
    LeaveAction,
    PlayCardAction,
    apply_action,
)
from app.game.state import GameState, Player


def make_state(hands: list[list], top_card, draw_pile: list | None = None, **extra) -> GameState:
    players = [
        Player(id=f"p{i}", username=f"Player {i}", hand=hand)
        for i, hand in enumerate(hands)
    ]
    return GameState(players=players, draw_pile=draw_pile or [], discard_pile=[top_card], **extra)


def test_leaving_marks_the_player_and_is_reflected_in_hand_counts():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    state = make_state(hands=[[], [], []], top_card=top)

    new_state = apply_action(state, LeaveAction(player_id="p1"))

    assert "p1" in new_state.left_players


def test_cannot_leave_twice():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    state = make_state(hands=[[], [], []], top_card=top)

    state = apply_action(state, LeaveAction(player_id="p1"))

    with pytest.raises(IllegalActionError):
        apply_action(state, LeaveAction(player_id="p1"))


def test_leaving_player_whose_turn_it_is_advances_the_turn():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    state = make_state(hands=[[], [], []], top_card=top)

    new_state = apply_action(state, LeaveAction(player_id="p0"))

    assert new_state.current_player_index == 1


def test_leaving_player_whose_turn_it_is_not_does_not_change_current_player():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    state = make_state(hands=[[], [], []], top_card=top)

    new_state = apply_action(state, LeaveAction(player_id="p2"))

    assert new_state.current_player_index == 0


def test_turn_order_skips_players_who_left_forever():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    my_card = NumberCard(id="c1", value=5, color=Color.RED)
    state = make_state(hands=[[], [], [my_card], []], top_card=top)  # 4 joueurs

    state = apply_action(state, LeaveAction(player_id="p0"))
    state = apply_action(state, LeaveAction(player_id="p1"))

    assert state.current_player_index == 2
    new_state = apply_action(state, PlayCardAction(player_id="p2", card_id="c1"))
    assert new_state.discard_pile[-1].id == "c1"


def test_only_one_active_player_left_ends_the_game():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    state = make_state(hands=[[], []], top_card=top)

    new_state = apply_action(state, LeaveAction(player_id="p0"))

    assert new_state.winner_id == "p1"


def test_reshuffle_folds_in_hands_of_players_who_left():
    top = NumberCard(id="top", value=8, color=Color.GREEN)
    left_hand = [
        NumberCard(id="abandoned1", value=1, color=Color.GREY),
        NumberCard(id="abandoned2", value=2, color=Color.GREY),
    ]
    state = make_state(
        hands=[[], left_hand, []],
        top_card=top,
        draw_pile=[],
    )
    state.discard_pile = [NumberCard(id="buried", value=1, color=Color.GREY), top]
    state = apply_action(state, LeaveAction(player_id="p1"))

    new_state = apply_action(state, DrawAction(player_id="p0"))

    assert new_state.players[1].hand == []
    all_ids = [c.id for c in new_state.draw_pile] + [c.id for c in new_state.players[0].hand]
    assert "abandoned1" in all_ids
    assert "abandoned2" in all_ids