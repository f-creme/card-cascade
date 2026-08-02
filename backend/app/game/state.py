import random

from pydantic import BaseModel

from app.game.cards import Card, Color, NumberCard, build_deck

class Player(BaseModel):
    id: str
    username: str
    hand: list[Card]

class DrawChain(BaseModel):
    total: int = 0
    has_double: bool = False
    last_player_id: str

class GameState(BaseModel):
    players: list[Player]
    current_player_index: int = 0
    draw_pile: list[Card]
    discard_pile: list[Card]
    announced_color: Color | None = None
    draw_chain: DrawChain | None = None
    pending_skips: dict[str, int] = {}
    second_chance_pile: list[Card] = {}
    winner_id: str | None = None

def active_color(state: GameState):
    top = state.discard_pile[-1]
    if isinstance(top, NumberCard):
        return top.color
    assert state.announced_color is not None
    return state.announced_color

def create_initial_state(players: list[tuple[str, str]]) -> GameState:
    deck = build_deck()
    random.shuffle(deck)

    player_objs: list[Player] = []
    for player_id, username in players:
        hand = [deck.pop() for _ in range(7)]
        player_objs.append(Player(id=player_id, username=username, hand=hand))

    first_discard: NumberCard | None = None
    while first_discard is None:
        card = deck.pop()
        if isinstance(card, NumberCard):
            first_discard = card
        else:
            deck.insert(0, card)

    return GameState(
        players=player_objs,
        draw_pile=deck,
        discard_pile=[first_discard]
    )