from typing import Literal, Union
from enum import Enum
from pydantic import BaseModel

class Color(str, Enum):
    PINK = "pink"
    GREY = "gray"
    GREEN = "green"
    RED = "red"
    BLUE = "blue"
    ORANGE = "orange"
    BROWN = "brown"

class NumberCard(BaseModel):
    id: str
    kind: Literal["number"] = "number"
    value: int 
    color: Color

class DrawCard(BaseModel):
    id: str
    kind: Literal["draw"] = "draw"
    amount: int

class DoubleCard(BaseModel):
    id: str
    kind: Literal["double"] = "double"

class SecondChanceCard(BaseModel):
    id: str
    kind: Literal["second_chance"] = "second_chance"

class BlockCard(BaseModel):
    id: str
    kind: Literal["block"] = "block"

class Block3Card(BaseModel):
    id: str
    kind: Literal["block3"] = "block3"

Card = Union[
    NumberCard, DrawCard, DoubleCard, SecondChanceCard, BlockCard, Block3Card
]

COLOR_BY_VALUE: dict[int, Color] = {
    0: Color.PINK,
    1: Color.GREY,
    2: Color.GREEN,
    3: Color.RED, 
    4: Color.BLUE, 
    5: Color.GREEN, 
    6: Color.PINK, 
    7: Color.BROWN, 
    8: Color.GREEN, 
    9: Color.ORANGE, 
    10: Color.RED,
    11: Color.BLUE,
    12: Color.GREY
}

def build_deck() -> list[Card]:
    deck: list[Card] = []
    next_id = 0

    def new_id(prefix: str) -> str:
        nonlocal next_id
        next_id += 1
        return f"{prefix}{next_id}"

    for value, color in COLOR_BY_VALUE.items():
        copies = 1 if value in (0, 1) else value
        for _ in range(copies):
            deck.append(NumberCard(id=new_id("n"), value=value, color=color))

    for amount in (2, 4, 6, 8, 10):
        deck.append(DrawCard(id=new_id("s"), amount=amount))

    deck.append(DoubleCard(id=new_id("s")))

    for _ in range(3):
        deck.append(SecondChanceCard(id=new_id("s")))

    for _ in range(3):
        deck.append(BlockCard(id=new_id("s")))

    for _ in range(3):
        deck.append(Block3Card(id=new_id("s")))

    return deck