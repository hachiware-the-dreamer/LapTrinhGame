from typing import List

from scripts.cards import (
    ACTION_DRAW_TWO,
    ACTION_REVERSE,
    ACTION_SKIP,
    ACTION_WILD,
    ACTION_WILD_DRAW_FOUR,
    COLORS,
    Card,
)


def build_standard_uno_deck() -> List[Card]:
    """Create a standard 108-card UNO deck."""
    deck: List[Card] = []

    for color in COLORS:
        deck.append(Card(color=color, kind="number", number=0))

        for number in range(1, 10):
            deck.append(Card(color=color, kind="number", number=number))
            deck.append(Card(color=color, kind="number", number=number))

        for _ in range(2):
            deck.append(Card(color=color, kind=ACTION_SKIP))
            deck.append(Card(color=color, kind=ACTION_REVERSE))
            deck.append(Card(color=color, kind=ACTION_DRAW_TWO))

    for _ in range(4):
        deck.append(Card(color=None, kind=ACTION_WILD))
        deck.append(Card(color=None, kind=ACTION_WILD_DRAW_FOUR))

    return deck
