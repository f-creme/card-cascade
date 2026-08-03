from app.game.cards import DoubleCard, DrawCard, NumberCard
from app.game.state import GameState


def compute_scores(state: GameState) -> dict[str, int]:
    """
    Compute the score for each player.
    The winner (empty hand) naturally gets 0.
    """
    scores: dict[str, int] = {}

    for player in state.players:
        total = 0
        has_double = False

        for card in player.hand:
            if isinstance(card, NumberCard):
                total += card.value
            elif isinstance(card, DrawCard):
                total += card.amount
            elif isinstance(card, DoubleCard):
                has_double = True

        if has_double:
            total *= 2

        scores[player.id] = total

    return scores


def ranked_players(state: GameState) -> list[tuple[str, int]]:
    """Ranking : less points = better ranking."""
    scores = compute_scores(state)
    return sorted(scores.items(), key=lambda item: item[1])