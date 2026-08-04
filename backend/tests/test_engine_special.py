import pytest

from app.game.cards import (
    Block3Card,
    BlockCard,
    Color,
    DoubleCard,
    DrawCard,
    NumberCard,
    SecondChanceCard,
)
from app.game.engine import (
    DrawAction,
    IllegalActionError,
    PassAction,
    PlaySpecialAction,
    apply_action,
)
from app.game.state import DrawChain, GameState, Player


def make_state(hands: list[list], top_card, draw_pile: list | None = None, **extra) -> GameState:
    players = [
        Player(id=f"p{i}", username=f"Player {i}", hand=hand)
        for i, hand in enumerate(hands)
    ]
    return GameState(players=players, draw_pile=draw_pile or [], discard_pile=[top_card], **extra)


# --- block ---

def test_block_skips_the_next_player():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    block = BlockCard(id="b1")
    # 2 joueurs : bloquer l'autre doit renvoyer le tour à soi-même
    state = make_state(hands=[[block], []], top_card=top)

    new_state = apply_action(
        state, PlaySpecialAction(player_id="p0", card_id="b1", announced_color=Color.RED)
    )

    assert new_state.pending_skips.get("p1", 0) == 0
    assert new_state.current_player_index == 0
    assert new_state.discard_pile[-1].id == "b1"
    assert new_state.announced_color == Color.RED


def test_block_actually_causes_a_skip_on_next_turn():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    block = BlockCard(id="b1")
    card_p2 = NumberCard(id="c2", value=1, color=Color.RED)
    state = make_state(hands=[[block], [], [card_p2]], top_card=top)

    state = apply_action(
        state, PlaySpecialAction(player_id="p0", card_id="b1", announced_color=Color.RED)
    )
    from app.game.engine import PlayCardAction
    new_state = apply_action(state, PlayCardAction(player_id="p2", card_id="c2"))

    assert new_state.discard_pile[-1].id == "c2"


def test_block_requires_a_numbered_top():
    top = BlockCard(id="top")
    block = BlockCard(id="b1")
    state = make_state(hands=[[block], []], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlaySpecialAction(player_id="p0", card_id="b1", announced_color=Color.RED))


def test_block_requires_announced_color():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    block = BlockCard(id="b1")
    state = make_state(hands=[[block], []], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlaySpecialAction(player_id="p0", card_id="b1"))


# --- block3 ---

def test_block3_distributes_three_skips():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    block3 = Block3Card(id="b3")
    state = make_state(hands=[[block3], [], [], []], top_card=top)

    new_state = apply_action(
        state,
        PlaySpecialAction(
            player_id="p0", card_id="b3", announced_color=Color.BLUE,
            skip_targets=["p1", "p1", "p2"],
        ),
    )

    assert new_state.pending_skips == {"p1": 1, "p2": 0}
    assert new_state.current_player_index == 3


def test_block3_requires_exactly_three_targets():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    block3 = Block3Card(id="b3")
    state = make_state(hands=[[block3], [], []], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(
            state,
            PlaySpecialAction(
                player_id="p0", card_id="b3", announced_color=Color.BLUE, skip_targets=["p1", "p2"]
            ),
        )


def test_block3_rejects_unknown_target():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    block3 = Block3Card(id="b3")
    state = make_state(hands=[[block3], [], []], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(
            state,
            PlaySpecialAction(
                player_id="p0", card_id="b3", announced_color=Color.BLUE,
                skip_targets=["p1", "p2", "ghost"],
            ),
        )


# --- chain: formation & extension ---

def test_playing_a_draw_card_starts_a_chain():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    plus4 = DrawCard(id="d1", amount=4)
    state = make_state(hands=[[plus4], []], top_card=top)

    new_state = apply_action(
        state, PlaySpecialAction(player_id="p0", card_id="d1", announced_color=Color.RED)
    )

    assert new_state.draw_chain == DrawChain(total=4, has_double=False, pending_color=Color.RED)
    assert new_state.announced_color is None


def test_draw_card_cannot_start_chain_on_special_top():
    top = BlockCard(id="top")
    plus4 = DrawCard(id="d1", amount=4)
    state = make_state(hands=[[plus4], []], top_card=top)

    with pytest.raises(IllegalActionError):
        apply_action(state, PlaySpecialAction(player_id="p0", card_id="d1", announced_color=Color.RED))


def test_extending_an_existing_chain_sums_the_total():
    top = DrawCard(id="top", amount=4)
    plus2 = DrawCard(id="d2", amount=2)
    state = make_state(
        hands=[[plus2], []],
        top_card=top,
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    new_state = apply_action(
        state, PlaySpecialAction(player_id="p0", card_id="d2", announced_color=Color.BLUE)
    )

    assert new_state.draw_chain.total == 6
    assert new_state.draw_chain.pending_color == Color.BLUE


def test_cannot_play_block_while_chain_is_active():
    top = DrawCard(id="top", amount=4)
    block = BlockCard(id="b1")
    state = make_state(hands=[[block], []], top_card=top, draw_chain=DrawChain(total=4, pending_color=Color.RED))

    with pytest.raises(IllegalActionError):
        apply_action(state, PlaySpecialAction(player_id="p0", card_id="b1", announced_color=Color.RED))


# --- chain: resolution ---
def test_resolving_a_simple_chain_draws_the_total():
    top = DrawCard(id="top", amount=6)
    state = make_state(
        hands=[[], []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(6)],
        draw_chain=DrawChain(total=6, pending_color=Color.BLUE),
    )

    new_state = apply_action(state, DrawAction(player_id="p0"))

    assert len(new_state.players[0].hand) == 6
    assert new_state.draw_chain is None
    assert new_state.announced_color == Color.BLUE
    assert new_state.current_player_index == 0  
    assert new_state.has_drawn is False


def test_resolving_a_chain_with_double_doubles_the_hand_first():
    top = DrawCard(id="top", amount=3)
    existing = [NumberCard(id="h1", value=1, color=Color.GREY), NumberCard(id="h2", value=2, color=Color.GREY)]
    state = make_state(
        hands=[existing, []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(20)],
        draw_chain=DrawChain(total=3, has_double=True, pending_color=Color.BLUE),
    )

    new_state = apply_action(state, DrawAction(player_id="p0"))

    assert len(new_state.players[0].hand) == 7  # 2 doublé (+2) + total (3)


# --- second chance ---

def test_second_chance_draws_a_card_without_ending_turn():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    sc = SecondChanceCard(id="sc1")
    drawn = NumberCard(id="drawn", value=1, color=Color.GREY)
    state = make_state(hands=[[sc], []], top_card=top, draw_pile=[drawn])

    new_state = apply_action(state, PlaySpecialAction(player_id="p0", card_id="sc1"))

    assert drawn in new_state.players[0].hand
    assert new_state.current_player_index == 0
    assert new_state.second_chances_played == 1
    assert new_state.second_chance_pile == [sc]
    assert new_state.discard_pile[-1].id == "top"


def test_second_chance_while_chain_succeeds_leaves_chain_open():
    top = DrawCard(id="top", amount=4)
    sc = SecondChanceCard(id="sc1")
    lucky_draw = DrawCard(id="lucky", amount=2)
    state = make_state(
        hands=[[sc], []],
        top_card=top,
        draw_pile=[lucky_draw],
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    new_state = apply_action(state, PlaySpecialAction(player_id="p0", card_id="sc1"))

    assert lucky_draw in new_state.players[0].hand
    assert new_state.draw_chain is not None
    assert new_state.current_player_index == 0


def test_second_chance_while_chain_fails_resolves_it():
    top = DrawCard(id="top", amount=4)
    sc = SecondChanceCard(id="sc1")
    useless_draw = NumberCard(id="useless", value=1, color=Color.GREY)
    state = make_state(
        hands=[[sc], []],
        top_card=top,
        draw_pile=[useless_draw] + [NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(4)],
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    new_state = apply_action(state, PlaySpecialAction(player_id="p0", card_id="sc1"))

    assert len(new_state.players[0].hand) == 5  
    assert new_state.draw_chain is None
    assert new_state.current_player_index == 0

def test_after_resolving_a_chain_the_player_can_play_on_the_resumed_color():
    top = DrawCard(id="top", amount=2)
    playable = NumberCard(id="pc", value=9, color=Color.BLUE)
    state = make_state(
        hands=[[playable], []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(2)],
        draw_chain=DrawChain(total=2, pending_color=Color.BLUE),
    )

    state = apply_action(state, DrawAction(player_id="p0"))
    from app.game.engine import PlayCardAction
    new_state = apply_action(state, PlayCardAction(player_id="p0", card_id="pc"))

    assert new_state.discard_pile[-1].id == "pc"
    assert new_state.current_player_index == 1

def test_pass_while_chain_active_resolves_it_instead_of_ending_turn():
    top = DrawCard(id="top", amount=4)
    state = make_state(
        hands=[[], []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(4)],
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    new_state = apply_action(state, PassAction(player_id="p0"))

    assert len(new_state.players[0].hand) == 4
    assert new_state.draw_chain is None
    assert new_state.current_player_index == 0
    assert new_state.has_drawn is False

def test_cannot_pass_immediately_after_resolving_a_chain_without_trying_first():
    top = DrawCard(id="top", amount=4)
    state = make_state(
        hands=[[], []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(4)],
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    state = apply_action(state, PassAction(player_id="p0"))  # résout la chaîne, tour toujours à p0

    with pytest.raises(IllegalActionError):
        apply_action(state, PassAction(player_id="p0"))

def test_draw_again_then_pass_after_resolving_a_chain_ends_the_turn():
    top = DrawCard(id="top", amount=4)
    state = make_state(
        hands=[[], []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(4)]
        + [NumberCard(id="extra", value=2, color=Color.GREY)],
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    state = apply_action(state, PassAction(player_id="p0"))  # résout la chaîne (4 cartes)
    state = apply_action(state, DrawAction(player_id="p0"))  # pioche normale supplémentaire
    new_state = apply_action(state, PassAction(player_id="p0"))  # cette fois, ça termine le tour

    assert new_state.current_player_index == 1

def test_second_chance_success_but_player_declines_and_passes():
    top = DrawCard(id="top", amount=4)
    sc = SecondChanceCard(id="sc1")
    lucky_draw = DrawCard(id="lucky", amount=2)
    state = make_state(
        hands=[[sc], []],
        top_card=top,
        draw_pile=[NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(4)] + [lucky_draw],
        draw_chain=DrawChain(total=4, pending_color=Color.RED),
    )

    state = apply_action(state, PlaySpecialAction(player_id="p0", card_id="sc1"))
    assert state.draw_chain is not None  # la carte tirée peut continuer la chaîne...

    new_state = apply_action(state, PassAction(player_id="p0"))  # ...mais le joueur décline

    assert new_state.draw_chain is None
    assert len(new_state.players[0].hand) == 1 + 4  # la carte de la 2nde chance + le total
    assert new_state.current_player_index == 0

def test_playing_a_draw_card_actually_appears_on_the_discard_pile():
    top = NumberCard(id="top", value=5, color=Color.GREEN)
    plus4 = DrawCard(id="d1", amount=4)
    state = make_state(hands=[[plus4], []], top_card=top)

    new_state = apply_action(
        state, PlaySpecialAction(player_id="p0", card_id="d1", announced_color=Color.RED)
    )

    assert new_state.discard_pile[-1].id == "d1"


def test_after_resolving_a_chain_the_announced_color_is_actually_usable():
    from app.game.engine import PlayCardAction

    numbered_top = NumberCard(id="old-top", value=5, color=Color.GREEN)
    plus2 = DrawCard(id="d1", amount=2)

    playable = NumberCard(id="pc", value=9, color=Color.RED)
    state = make_state(hands=[[plus2], [playable]], top_card=numbered_top)

    state = apply_action(
        state, PlaySpecialAction(player_id="p0", card_id="d1", announced_color=Color.RED)
    )

    state.draw_pile = [NumberCard(id=f"d{i}", value=1, color=Color.GREY) for i in range(2)]
    state = apply_action(state, DrawAction(player_id="p1"))

    new_state = apply_action(state, PlayCardAction(player_id="p1", card_id="pc"))

    assert new_state.discard_pile[-1].id == "pc"