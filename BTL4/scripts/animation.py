from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

import pygame

from scripts.cards import Card

T = TypeVar("T", int, float)


def lerp(start: T, end: T, amount: float) -> float:
    amount = max(0.0, min(1.0, amount))
    return float(start) + (float(end) - float(start)) * amount


def lerp_point(
    start: tuple[float, float],
    end: tuple[float, float],
    amount: float,
) -> tuple[float, float]:
    return (lerp(start[0], end[0], amount), lerp(start[1], end[1], amount))


def smooth_factor(dt: float, speed: float) -> float:
    if dt <= 0.0:
        return 0.0
    if speed <= 0.0:
        return 1.0
    return max(0.0, min(1.0, dt * speed))


def transform_card_surface(surface: pygame.Surface, rotation: float, scale: float) -> pygame.Surface:
    if scale != 1.0 or rotation != 0.0:
        return pygame.transform.rotozoom(surface, -rotation, scale)
    return surface


@dataclass
class ActiveCard:
    card: Card
    owner_id: int
    kind: str
    current_pos: tuple[float, float]
    target_pos: tuple[float, float]
    current_rotation: float
    target_rotation: float
    current_scale: float = 1.0
    target_scale: float = 1.0
    travel_speed: float = 7.5
    rotation_speed: float = 7.5
    scale_speed: float = 8.5
    reveal_hand_card: bool = False

    def update(self, dt: float) -> bool:
        travel = smooth_factor(dt, self.travel_speed)
        rotate = smooth_factor(dt, self.rotation_speed)
        scale = smooth_factor(dt, self.scale_speed)

        self.current_pos = lerp_point(self.current_pos, self.target_pos, travel)
        self.current_rotation = lerp(self.current_rotation, self.target_rotation, rotate)
        self.current_scale = lerp(self.current_scale, self.target_scale, scale)

        reached_x = abs(self.current_pos[0] - self.target_pos[0]) < 1.0
        reached_y = abs(self.current_pos[1] - self.target_pos[1]) < 1.0
        reached_rot = abs(self.current_rotation - self.target_rotation) < 0.5
        reached_scale = abs(self.current_scale - self.target_scale) < 0.01
        return reached_x and reached_y and reached_rot and reached_scale
