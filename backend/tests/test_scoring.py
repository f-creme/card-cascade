from app.game.cards import (
    BlockCard,
    Block3Card,
    Color,
    DoubleCard,
    DrawCard,
    NumberCard,
    SecondChanceCard,
)
from app.game.scoring import compute_scores, ranked_players
from app.game.state import GameState, Player


def make_state(hands: list[list]) -> GameState:
    players = [
        Player(id=f"p{i}", username=f"Player {i}", hand=hand)
        for i, hand in enumerate(hands)
    ]
    top = NumberCard(id="top", value=0, color=Color.PINK)
    return GameState(players=players, draw_pile=[], discard_pile=[top])


def test_winner_with_empty_hand_scores_zero():
    state = make_state(hands=[[], [NumberCard(id="c1", value=7, color=Color.BROWN)]])

    scores = compute_scores(state)

    assert scores["p0"] == 0


def test_number_cards_score_their_value():
    hand = [
        NumberCard(id="c1", value=5, color=Color.GREEN),
        NumberCard(id="c2", value=3, color=Color.BLUE),
    ]
    state = make_state(hands=[hand])

    assert compute_scores(state)["p0"] == 8


def test_draw_cards_score_their_amount():
    hand = [DrawCard(id="d1", amount=4), DrawCard(id="d2", amount=10)]
    state = make_state(hands=[hand])

    assert compute_scores(state)["p0"] == 14


def test_block_block3_and_second_chance_score_zero():
    hand = [BlockCard(id="b1"), Block3Card(id="b3"), SecondChanceCard(id="sc1")]
    state = make_state(hands=[hand])

    assert compute_scores(state)["p0"] == 0


def test_double_card_doubles_the_total_hand_score():
    hand = [
        NumberCard(id="c1", value=5, color=Color.GREEN),
        DrawCard(id="d1", amount=4),
        DoubleCard(id="x2"),
    ]
    state = make_state(hands=[hand])

    # (5 + 4) * 2 = 18
    assert compute_scores(state)["p0"] == 18


def test_double_card_alone_scores_zero():
    hand = [DoubleCard(id="x2")]
    state = make_state(hands=[hand])

    assert compute_scores(state)["p0"] == 0


def test_double_only_affects_its_own_owner():
    state = make_state(
        hands=[
            [NumberCard(id="c1", value=5, color=Color.GREEN), DoubleCard(id="x2")],
            [NumberCard(id="c2", value=5, color=Color.GREEN)],
        ]
    )

    scores = compute_scores(state)

    assert scores["p0"] == 10
    assert scores["p1"] == 5 


def test_ranked_players_orders_from_lowest_to_highest_score():
    state = make_state(
        hands=[
            [NumberCard(id="c1", value=9, color=Color.GREEN)],
            [],
            [NumberCard(id="c2", value=3, color=Color.BLUE)],
        ]
    )

    ranking = ranked_players(state)

    assert ranking == [("p1", 0), ("p2", 3), ("p0", 9)]