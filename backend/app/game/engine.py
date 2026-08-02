from typing import Literal, Union
from pydantic import BaseModel

from app.game.cards import Card, Color, NumberCard
from app.game.state import GameState, Player, active_color

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

Action = Union[PlayCardAction, PlayPairAction, PlaySpecialAction, DrawAction]

def apply_action(state: GameState, action: Action) -> GameState:
    if action.kind == "play_card":
        return _apply_play_card(state, action)
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
    n = len(state.players)
    for _ in range(n): 
        state.current_player_index = (state.current_player_index + 1) %n
        next_player = state.players[state.current_player_index]
        if state.pending_skips.get(next_player.id, 0) > 0:
            state.pending_skips[next_player.id] -= 1
            continue
        return

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