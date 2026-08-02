from app.game.cards import NumberCard
from app.game.state import create_initial_state, active_color

def make_players(n: int) -> list[tuple[str, str]]:
    return [(f"p{i}", f"Player {i}") for i in range(n)]

def test_each_player_gets_seven_cards():
    state = create_initial_state(make_players(4))
    for player in state.players:
        assert len(player.hand) == 7

def test_discard_pile_starts_with_one_number_card():
    state = create_initial_state(make_players(4))
    assert len(state.discard_pile) == 1
    assert isinstance(state.discard_pile[0], NumberCard)

def test_draw_pile_and_hands_and_discard_add_up_to_94():
    state = create_initial_state(make_players(4))
    total = len(state.draw_pile) + len(state.discard_pile)
    for player in state.players:
        total += len(player.hand)
    assert total == 94

def test_all_card_ids_still_unique_after_dealing():
    state = create_initial_state(make_players(4))
    ids = [c.id for c in state.draw_pile] + [c.id for c in state.discard_pile]
    for player in state.players:
        ids += [c.id for c in player.hand]
    assert len(ids) == len(set(ids))

def test_active_color_matches_first_discard_color():
    state = create_initial_state(make_players(4))
    assert active_color(state) == state.discard_pile[0].color

def test_works_with_eight_players():
    state = create_initial_state(make_players(8))
    assert len(state.players) == 8
    assert len(state.draw_pile) < 94