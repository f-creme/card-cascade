from pydantic import BaseModel

from app.game.cards import Card, Color
from app.game.state import DrawChain, GameState


class PublicPlayer(BaseModel):
    id: str
    username: str
    hand_count: int


class PlayerView(BaseModel):
    player_id: str
    hand: list[Card] 
    players: list[PublicPlayer]
    current_player_index: int
    draw_pile_count: int
    discard_pile: list[Card]
    announced_color: Color | None
    draw_chain: DrawChain | None
    pending_skips: dict[str, int]
    second_chance_pile: list[Card]
    winner_id: str | None
    has_drawn: bool
    second_chances_played: int


def build_player_view(state: GameState, player_id: str) -> PlayerView:
    viewer = next((p for p in state.players if p.id == player_id), None)
    if viewer is None:
        raise ValueError(f"Unknown player: {player_id}")

    return PlayerView(
        player_id=player_id,
        hand=viewer.hand,
        players=[
            PublicPlayer(id=p.id, username=p.username, hand_count=len(p.hand))
            for p in state.players
        ],
        current_player_index=state.current_player_index,
        draw_pile_count=len(state.draw_pile),
        discard_pile=state.discard_pile,
        announced_color=state.announced_color,
        draw_chain=state.draw_chain,
        pending_skips=state.pending_skips,
        second_chance_pile=state.second_chance_pile,
        winner_id=state.winner_id,
        has_drawn=state.has_drawn,
        second_chances_played=state.second_chances_played,
    )