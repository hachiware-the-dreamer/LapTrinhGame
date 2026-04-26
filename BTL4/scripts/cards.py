from dataclasses import dataclass
from typing import Optional

COLORS = ["red", "yellow", "green", "blue"]

ACTION_SKIP = "skip"
ACTION_REVERSE = "reverse"
ACTION_DRAW_TWO = "draw2"
ACTION_WILD = "wild"
ACTION_WILD_DRAW_FOUR = "wild_draw4"


@dataclass
class Card:
    color: Optional[str]
    kind: str
    number: Optional[int] = None
    current_pos: tuple[float, float] = (0.0, 0.0)
    target_pos: tuple[float, float] = (0.0, 0.0)
    current_rotation: float = 0.0
    target_rotation: float = 0.0
    current_scale: float = 1.0
    target_scale: float = 1.0

    @property
    def is_wild(self) -> bool:
        return self.kind in (ACTION_WILD, ACTION_WILD_DRAW_FOUR)

    @property
    def short_label(self) -> str:
        if self.kind == "number":
            return str(self.number)
        if self.kind == ACTION_SKIP:
            return "SKIP"
        if self.kind == ACTION_REVERSE:
            return "REV"
        if self.kind == ACTION_DRAW_TWO:
            return "+2"
        if self.kind == ACTION_WILD:
            return "WILD"
        return "+4"
