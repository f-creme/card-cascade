import random

from typing import Literal, Union
from pydantic import BaseModel

from app.game.cards import (
    BlockCard,
    Block3Card,
    Card, 
    Color, 
    DoubleCard, 
    DrawCard, 
    NumberCard,
    SecondChanceCard
)
from app.game.state import GameState, DrawChain, Player, active_color

class IllegalActionError(Exception):
    """Raised when an action doesn't respect game rules"""

class PlayCardAction(BaseModel):
    kind: Literal["play_card"] = "play_card"
    player_id: str
    card_id: str

class PlayPairAction(BaseModel):
    kind: Literal["play_pair"] = "play_pair"
    player_id: str
    card_id_1: str
    card_id_2: str
    top_card_id: str

class PlaySpecialAction(BaseModel): 
    kind: Literal["play_special"] = "play_special"
    player_id: str
    card_id: str
    announced_color: Color | None = None
    skip_targets: list[str] = []

class DrawAction(BaseModel):
    kind: Literal["draw"] = "draw"
    player_id: str

class PassAction(BaseModel):
    kind: Literal["pass"] = "pass"
    player_id: str

Action = Union[PlayCardAction, PlayPairAction, PlaySpecialAction, DrawAction, PassAction]

def apply_action(state: GameState, action: Action) -> GameState:
    if action.kind == "play_card":
        return _apply_play_card(state, action)
    if action.kind == "play_pair":
        return _apply_play_pair(state, action)
    if action.kind == "play_special":
        return _apply_play_special(state, action)
    if action.kind == "draw": 
        return _apply_draw(state, action)
    if action.kind == "pass":
        return _apply_pass(state, action)
    
    raise NotImplementedError(f"Action '{action.kind}' hasn't been implemented yet.")

def _find_player(state: GameState, player_id: str) -> Player:
    for player in state.players:
        if player.id == player_id:
            return player
    raise IllegalActionError(f"Unknown player: {player_id}")

def _ensure_is_current_player(state: GameState, player: Player) -> None:
    current = state.players[state.current_player_index]
    if current.id != player.id:
        raise IllegalActionError("It's not this player's turn.")

def _take_card_from_hand(player: Player, card_id: str):
    for index, card in enumerate(player.hand):
        if card.id == card_id: 
            return player.hand.pop(index)
    raise IllegalActionError("This card is no longer in player's hand.")

def _matches_discard(card: NumberCard, state: GameState) -> bool: 
    top = state.discard_pile[-1]
    if isinstance(top, NumberCard):
        if card.value == top.value:
            return True
        if abs(card.value - top.value) == 1: 
            return True
    return card.color == active_color(state)

def _advance_turn(state: GameState) -> None:
    state.has_drawn = False
    state.second_chances_played = 0
    n = len(state.players)
    for _ in range(n): 
        state.current_player_index = (state.current_player_index + 1) %n
        next_player = state.players[state.current_player_index]
        if state.pending_skips.get(next_player.id, 0) > 0:
            state.pending_skips[next_player.id] -= 1
            continue
        return

def _peek_next_player_id(state: GameState) -> str:
    n = len(state.players)
    return state.players[(state.current_player_index + 1) % n].id

def _ensure_playable_on_number_top(state: GameState) -> None:
    if state.draw_chain is not None:
        raise IllegalActionError("A pick-up chain is active: you need to respond to it.")
    if not isinstance(state.discard_pile[-1], NumberCard):
        raise IllegalActionError("This card can only be played on a numbered card.")

def _refill_draw_pile_if_needed(state: GameState) -> None: 
    if state.draw_pile:
        return 
    if len(state.discard_pile) <= 1: 
        return

    top = state.discard_pile[-1]
    new_pile = state.discard_pile[:-1] + state.second_chance_pile
    random.shuffle(new_pile)

    state.draw_pile = new_pile
    state.discard_pile = [top]
    state.second_chance_pile = []

def _apply_play_card(state: GameState, action: PlayCardAction) -> GameState:
    new_state = state.model_copy(deep=True)
    player = _find_player(new_state, action.player_id)
    _ensure_is_current_player(new_state, player)

    if new_state.draw_chain is not None:
        raise IllegalActionError("A draw chain is active: it needs to be answered.")

    card = _take_card_from_hand(player, action.card_id)

    if not isinstance(card, NumberCard):
        raise IllegalActionError("Only a numbered card can be played with this action.")

    if not _matches_discard(card, new_state):
        raise IllegalActionError(
            "This card does not match the number, ±1 or the current color."
        )

    new_state.discard_pile.append(card)
    new_state.announced_color = None

    if not player.hand:
        new_state.winner_id = player.id
    else: 
        _advance_turn(new_state)

    return new_state

def _apply_draw(state: GameState, action: DrawAction) -> GameState:
    new_state = state.model_copy(deep=True)
    player = _find_player(new_state, action.player_id)
    _ensure_is_current_player(new_state, player)

    if new_state.draw_chain is not None:
        _resolve_draw_chain(new_state, player)
        return new_state

    if new_state.has_drawn:
        raise IllegalActionError("A card has already been drawn this turn.")

    _refill_draw_pile_if_needed(new_state)
    if not new_state.draw_pile:
        raise IllegalActionError("No more card to draw.")

    card = new_state.draw_pile.pop()
    player.hand.append(card)
    new_state.has_drawn = True

    return new_state

def _apply_pass(state: GameState, action: PassAction) -> GameState:
    new_state = state.model_copy(deep=True)
    player = _find_player(new_state, action.player_id)
    _ensure_is_current_player(new_state, player)

    if new_state.draw_chain is not None:
        _resolve_draw_chain(new_state, player)
        return new_state

    if not new_state.has_drawn and new_state.second_chances_played == 0:
        raise IllegalActionError("You have to draw a card before you can pass your turn")

    _advance_turn(new_state)
    return new_state

def _apply_play_pair(state: GameState, action: PlayPairAction) -> GameState:
    if action.card_id_1 == action.card_id_2:
        raise IllegalActionError("Both cards must be different")

    new_state = state.model_copy(deep=True)
    player = _find_player(new_state, action.player_id)
    _ensure_is_current_player(new_state, player)

    if new_state.draw_chain is not None:
        raise IllegalActionError("A draw chain is active and needs to be answered.")

    top = new_state.discard_pile[-1]
    if not isinstance(top, NumberCard):
        raise IllegalActionError("Unable to sum on a special card")

    card1 = _take_card_from_hand(player, action.card_id_1)
    card2 = _take_card_from_hand(player, action.card_id_2)

    if not (isinstance(card1, NumberCard) and isinstance(card2, NumberCard)):
        raise IllegalActionError("Only numbered cards can be combined")

    if card1.value + card2.value != top.value:
        raise IllegalActionError(
            "The sum of cards is not equal to the value of the card at the top of the discard pile"
        )

    if action.top_card_id not in (card1.id, card2.id):
        raise IllegalActionError(
            "The card chosen for the top is not part of the pair"
        )

    bottom, chosen_top = (card2, card1) if action.top_card_id == card1.id else (card1, card2)
    new_state.discard_pile.append(bottom)
    new_state.discard_pile.append(chosen_top)
    new_state.announced_color = None

    if not player.hand:
        new_state.winner_id = player.id
    else:
        _advance_turn(new_state)

    return new_state

def _apply_block(
        state: GameState, player: Player, card: BlockCard, action: PlaySpecialAction
) -> None:
    _ensure_playable_on_number_top(state)
    if action.announced_color is None:
        raise IllegalActionError("A color must be announced when this card is played.")

    target_id = _peek_next_player_id(state)
    state.pending_skips[target_id] = state.pending_skips.get(target_id, 0) + 1

    state.discard_pile.append(card)
    state.announced_color = action.announced_color
    _advance_turn(state)

def _apply_block3(
        state: GameState, player: Player, card: Block3Card, action: PlaySpecialAction
) -> None: 
    _ensure_playable_on_number_top(state)
    if action.announced_color is None:
        raise IllegalActionError("A color must be announced when this card is played.")
    if len(action.skip_targets) != 3:
        raise IllegalActionError("Exactly three passes must be spread out.")

    valid_ids = {p.id for p in state.players}
    for target_id in action.skip_targets:
        if target_id not in valid_ids:
            raise IllegalActionError(f"Unknown player among targets: {target_id}")
        state.pending_skips[target_id] = state.pending_skips.get(target_id, 0) + 1

    state.discard_pile.append(card)
    state.announced_color = action.announced_color
    _advance_turn(state)

def _apply_draw_or_double(
        state: GameState,
        player: Player, 
        card: DrawCard | DoubleCard,
        action: PlaySpecialAction
) -> None: 
    if action.announced_color is None:
            raise IllegalActionError("A color must be announced when this card is played.")

    if state.draw_chain is None:
        if not isinstance(state.discard_pile[-1], NumberCard):
            raise IllegalActionError("This card can only be played after a numbered card")
        state.draw_chain = DrawChain(pending_color=action.announced_color)

    if isinstance(card, DoubleCard):
        state.draw_chain.has_double = True
    else: 
        state.draw_chain.total += card.amount
    state.draw_chain.pending_color = action.announced_color
    _advance_turn(state)

def _draw_n_cards(state: GameState, player: Player, n: int) -> None:
    for _ in range(n):
        _refill_draw_pile_if_needed(state)
        if not state.draw_pile:
            break
        player.hand.append(state.draw_pile.pop())

def _resolve_draw_chain(state: GameState, player: Player) -> None:
    chain = state.draw_chain
    assert chain is not None

    if chain.has_double:
        _draw_n_cards(state, player, len(player.hand))

    _draw_n_cards(state, player, chain.total)

    state.announced_color = chain.pending_color
    state.draw_chain = None

def _apply_second_chance(state: GameState, player: Player, card: SecondChanceCard) -> None:
    state.second_chance_pile.append(card)
    state.second_chances_played += 1

    _refill_draw_pile_if_needed(state)
    if not state.draw_pile:
        raise IllegalActionError("No more card to draw.")

    drawn = state.draw_pile.pop()
    player.hand.append(drawn)

    if state.draw_chain is not None and not isinstance(drawn, (DrawCard, DoubleCard)):
        _resolve_draw_chain(state, player)

def _apply_play_special(state: GameState, action: PlaySpecialAction) -> GameState:
    new_state = state.model_copy(deep=True)
    player = _find_player(new_state, action.player_id)
    _ensure_is_current_player(new_state, player)

    card = _take_card_from_hand(player, action.card_id)

    if isinstance(card, SecondChanceCard):
        _apply_second_chance(new_state, player, card)
    elif isinstance(card, (DrawCard, DoubleCard)):
        _apply_draw_or_double(new_state, player, card, action)
    elif isinstance(card, BlockCard):
        _apply_block(new_state, player, card, action)
    elif isinstance(card, Block3Card):
        _apply_block3(new_state, player, card, action)
    else: 
        raise IllegalActionError("This card can't be played with this action")

    return new_state