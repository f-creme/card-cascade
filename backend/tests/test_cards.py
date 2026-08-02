from app.game.cards import (
    build_deck,
    NumberCard,
    DrawCard,
    DoubleCard,
    SecondChanceCard,
)

def test_deck_has_94_cards():
    deck = build_deck()
    assert len(deck) == 94

def test_deck_has_79_number_cards():
    deck = build_deck()
    number_cards = [card for card in deck if isinstance(card, NumberCard)]
    assert len(number_cards) == 79

def test_value_seven_has_seven_copies():
    deck = build_deck()
    sevens = [c for c in deck if isinstance(c, NumberCard) and c.value == 7]
    assert len(sevens) == 7

def test_value_zero_has_only_one_copy():
    deck = build_deck()
    zeros = [c for c in deck if isinstance(c, NumberCard) and c.value == 0]
    assert len(zeros) == 1

def test_all_card_ids_are_unique():
    deck = build_deck()
    ids = [card.id for card in deck]
    assert len(ids) == len(set(ids))