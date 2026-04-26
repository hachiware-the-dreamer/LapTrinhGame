import math
from functools import lru_cache

import pygame
from scripts.cards import Card
from scripts.game_manager import (
    PASS_CLOCKWISE,
    PASS_COUNTER_CLOCKWISE,
    RULE_REACTION,
    RULE_SEVEN_TARGET,
    RULE_ZERO_DIRECTION,
    UnoGameManager,
)
from scripts.sprites import CardSpriteAtlas
from scripts.animation import transform_card_surface

PLAYER_CARD_SIZE = (88, 130)
OPPONENT_HORIZONTAL_SIZE = (70, 102)
OPPONENT_SIDE_SIZE = (102, 70)
HAND_SPACING = 30
HOVER_LIFT = 28
TABLE_CARD_SIZE = (104, 154)
DIRECTION_ARROW_SIZE = 360
TOP_OPPONENT_CARD_Y = 170
TOP_OPPONENT_LABEL_GAP = 24
PENALTY_BADGE_TOP_Y = 92
WILD_WHEEL_RADIUS = 142
WILD_WHEEL_SEGMENTS = (
    ("red", 180.0, 270.0),
    ("blue", 270.0, 360.0),
    ("green", 0.0, 90.0),
    ("yellow", 90.0, 180.0),
)
WILD_COLOR_RGB = {
    "red": (220, 70, 70),
    "yellow": (230, 205, 80),
    "green": (75, 175, 90),
    "blue": (75, 125, 215),
}


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def _ui_scale(width: int, height: int) -> float:
    return max(0.75, min(1.08, min(width / 1920, height / 1080)))


def _scaled_font(width: int, height: int, size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("consolas", _clamp(int(size * _ui_scale(width, height)), 14, size), bold=bold)


def _render_fit_text(
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    max_width: int,
) -> pygame.Surface:
    if max_width <= 0:
        return font.render("", True, color)

    rendered = font.render(text, True, color)
    if rendered.get_width() <= max_width:
        return rendered

    ellipsis = "..."
    trimmed = text
    while trimmed and font.size(trimmed + ellipsis)[0] > max_width:
        trimmed = trimmed[:-1]
    return font.render(trimmed.rstrip() + ellipsis, True, color)


def _top_opponent_card_y(height: int) -> int:
    return _clamp(int(height * 0.157), 112, TOP_OPPONENT_CARD_Y)


def _bottom_hand_margin(height: int) -> int:
    return _clamp(int(height * 0.09), 72, 96)


def _side_opponent_margin(width: int) -> int:
    return _clamp(int(width * 0.022), 24, 42)


def get_table_card_size(screen_rect: pygame.Rect) -> tuple[int, int]:
    scale = _ui_scale(screen_rect.width, screen_rect.height)
    return (int(TABLE_CARD_SIZE[0] * scale), int(TABLE_CARD_SIZE[1] * scale))


def get_direction_arrow_size(screen_rect: pygame.Rect) -> int:
    return _clamp(int(min(screen_rect.width, screen_rect.height) * 0.34), 220, DIRECTION_ARROW_SIZE)


def card_rect_for_hand(
    index: int,
    hand_size: int,
    width: int,
    height: int,
    hovered: bool = False,
) -> pygame.Rect:
    card_w, card_h = PLAYER_CARD_SIZE
    spacing = HAND_SPACING
    row_width = card_w + (hand_size - 1) * spacing
    start_x = (width - row_width) // 2
    x = start_x + index * spacing
    y = height - card_h - _bottom_hand_margin(height)
    if hovered:
        y -= HOVER_LIFT
    return pygame.Rect(x, y, card_w, card_h)


def get_hovered_hand_index(
    mouse_pos: tuple[int, int],
    hand: list,
    width: int,
    height: int,
    hidden_card_ids: set[int] | None = None,
) -> int | None:
    hidden_card_ids = hidden_card_ids or set()
    for i in range(len(hand) - 1, -1, -1):
        card = hand[i]
        if id(card) in hidden_card_ids:
            continue
        rect = pygame.Rect(int(card.current_pos[0]), int(card.current_pos[1]), *PLAYER_CARD_SIZE)
        if rect.collidepoint(mouse_pos):
            return i
    return None


def get_card_rect_from_pos(card) -> pygame.Rect:
    return pygame.Rect(int(card.current_pos[0]), int(card.current_pos[1]), *PLAYER_CARD_SIZE)


def get_player_hand_card_rects(
    screen_rect: pygame.Rect,
    player_id: int,
    num_players: int,
    hand_size: int,
    cards: list[Card] | None = None,
    use_current_positions: bool = False,
) -> list[pygame.Rect]:
    if player_id == 0:
        if use_current_positions and cards is not None and cards:
            return [get_card_rect_from_pos(card) for card in cards]
        return [card_rect_for_hand(i, hand_size, screen_rect.width, screen_rect.height, hovered=False) for i in range(hand_size)]

    return _opponent_card_rects(_opponent_positions(num_players).get(player_id, "top"), hand_size, screen_rect.width, screen_rect.height)


def get_player_anchor_point(screen_rect: pygame.Rect, player_id: int, num_players: int) -> tuple[float, float]:
    top_opponent_anchor_y = screen_rect.top + _top_opponent_card_y(screen_rect.height) + OPPONENT_HORIZONTAL_SIZE[1] // 2
    bottom_player_anchor_y = screen_rect.bottom - PLAYER_CARD_SIZE[1] // 2 - _bottom_hand_margin(screen_rect.height)
    side_anchor_x = _side_opponent_margin(screen_rect.width) + OPPONENT_SIDE_SIZE[0] + 6
    if num_players == 4:
        anchors = {
            0: (screen_rect.centerx, bottom_player_anchor_y),
            1: (screen_rect.left + side_anchor_x, screen_rect.centery),
            2: (screen_rect.centerx, top_opponent_anchor_y),
            3: (screen_rect.right - side_anchor_x, screen_rect.centery),
        }
        return anchors.get(player_id, (screen_rect.centerx, screen_rect.centery))

    if player_id == 0:
        return (screen_rect.centerx, bottom_player_anchor_y)
    if player_id == 1:
        return (screen_rect.centerx, top_opponent_anchor_y)
    if player_id == 2:
        return (screen_rect.left + side_anchor_x, screen_rect.centery)
    return (screen_rect.right - side_anchor_x, screen_rect.centery)


def get_player_card_rotation(player_id: int, num_players: int) -> float:
    if num_players == 4:
        rotations = {0: 0.0, 1: 90.0, 2: 0.0, 3: -90.0}
        return rotations.get(player_id, 0.0)
    if player_id == 2:
        return 90.0
    if player_id == 3:
        return -90.0
    return 0.0


def get_discard_pile_rect(screen_rect: pygame.Rect) -> pygame.Rect:
    card_w, card_h = get_table_card_size(screen_rect)
    gap = int(36 * _ui_scale(screen_rect.width, screen_rect.height))
    return pygame.Rect(screen_rect.centerx + gap // 2, screen_rect.centery - card_h // 2, card_w, card_h)


def get_direction_indicator_center(screen_rect: pygame.Rect) -> tuple[int, int]:
    draw_rect = get_draw_pile_rect(screen_rect.width, screen_rect.height)
    discard_rect = get_discard_pile_rect(screen_rect)
    return ((draw_rect.centerx + discard_rect.centerx) // 2, (draw_rect.centery + discard_rect.centery) // 2)


def _polar_point(center: tuple[float, float], radius: float, angle_degrees: float) -> tuple[float, float]:
    angle_radians = math.radians(angle_degrees)
    return (center[0] + math.cos(angle_radians) * radius, center[1] + math.sin(angle_radians) * radius)


def _draw_tangent_arrowhead(
    surface: pygame.Surface,
    center: tuple[float, float],
    angle_degrees: float,
    radius: float,
    color: tuple[int, int, int, int],
) -> None:
    angle_radians = math.radians(angle_degrees)
    tip = _polar_point(center, radius, angle_degrees)
    tangent = (-math.sin(angle_radians), math.cos(angle_radians))
    normal = (-tangent[1], tangent[0])
    head_length = 30.0
    head_width = 18.0
    base = (tip[0] - tangent[0] * head_length, tip[1] - tangent[1] * head_length)
    left = (base[0] + normal[0] * head_width, base[1] + normal[1] * head_width)
    right = (base[0] - normal[0] * head_width, base[1] - normal[1] * head_width)
    pygame.draw.polygon(surface, color, [tip, left, right])


@lru_cache(maxsize=8)
def build_direction_arrow_surface(size: int) -> pygame.Surface:
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size / 2, size / 2)
    radius = size * 0.36

    guide_color = (84, 96, 118, 48)
    accent_color = (225, 231, 242, 176)
    shadow_color = (32, 37, 46, 64)
    glow_color = (110, 130, 160, 42)

    arc_rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    pygame.draw.circle(surface, glow_color, (int(center[0]), int(center[1])), int(radius + 16), width=12)
    pygame.draw.circle(surface, guide_color, (int(center[0]), int(center[1])), int(radius), width=3)

    for start_angle in (-76, 14, 104, 194):
        end_angle = start_angle + 58
        pygame.draw.arc(
            surface,
            shadow_color,
            arc_rect.move(0, 3),
            math.radians(start_angle),
            math.radians(end_angle),
            width=14,
        )
        pygame.draw.arc(
            surface,
            accent_color,
            arc_rect,
            math.radians(start_angle),
            math.radians(end_angle),
            width=10,
        )
        _draw_tangent_arrowhead(surface, center, end_angle, radius, accent_color)
    return surface


def draw_direction_arrows(screen: pygame.Surface, center: tuple[int, int], angle: float, size: int) -> None:
    base = build_direction_arrow_surface(size)
    rotated = pygame.transform.rotozoom(base, -angle, 1.0)
    rect = rotated.get_rect(center=center)
    screen.blit(rotated, rect)


def _opponent_positions(num_players: int) -> dict[int, str]:
    if num_players == 2:
        return {1: "top"}
    if num_players == 3:
        return {1: "left", 2: "right"}
    return {1: "left", 2: "top", 3: "right"}


def _opponent_card_rects(position: str, count: int, width: int, height: int) -> list[pygame.Rect]:
    rects: list[pygame.Rect] = []
    if count <= 0:
        return rects

    if position == "top":
        card_w, card_h = OPPONENT_HORIZONTAL_SIZE
        spacing = min(22, max(10, 220 // max(1, count - 1))) if count > 1 else 0
        row_width = card_w + (count - 1) * spacing
        start_x = (width - row_width) // 2
        y = _top_opponent_card_y(height)
        for i in range(count):
            rects.append(pygame.Rect(start_x + i * spacing, y, card_w, card_h))
        return rects

    card_w, card_h = OPPONENT_SIDE_SIZE
    spacing = min(18, max(8, 180 // max(1, count - 1))) if count > 1 else 0
    col_height = card_h + (count - 1) * spacing
    start_y = (height - col_height) // 2
    side_margin = _side_opponent_margin(width)
    x = side_margin if position == "left" else width - card_w - side_margin
    for i in range(count):
        rects.append(pygame.Rect(x, start_y + i * spacing, card_w, card_h))
    return rects


def _draw_opponent_hands(
    screen: pygame.Surface,
    game: UnoGameManager,
    atlas: CardSpriteAtlas,
    body_font: pygame.font.Font,
) -> None:
    width, height = screen.get_size()
    back_h = atlas.get_back_surface(*OPPONENT_HORIZONTAL_SIZE)
    side_base = atlas.get_back_surface(OPPONENT_SIDE_SIZE[1], OPPONENT_SIDE_SIZE[0])
    back_left = pygame.transform.rotate(side_base, 90)
    back_right = pygame.transform.rotate(side_base, -90)

    for pid, position in _opponent_positions(game.num_players).items():
        rects = _opponent_card_rects(position, len(game.player_hands[pid]), width, height)
        if position == "top":
            image = back_h
        elif position == "left":
            image = back_left
        else:
            image = back_right
        for rect in rects:
            screen.blit(image, rect)

        label = body_font.render(f"P{pid + 1}: {len(game.player_hands[pid])}", True, (220, 220, 220))
        if position == "top" and rects:
            label_rect = label.get_rect(center=(width // 2, rects[0].top - TOP_OPPONENT_LABEL_GAP))
        elif position == "left" and rects:
            label_rect = label.get_rect(midleft=(28, rects[0].top - 14))
        elif position == "right" and rects:
            label_rect = label.get_rect(midright=(width - 28, rects[0].top - 14))
        else:
            label_rect = label.get_rect(topleft=(20, 20))
        screen.blit(label, label_rect)


def get_draw_pile_rect(width: int, height: int) -> pygame.Rect:
    screen_rect = pygame.Rect(0, 0, width, height)
    card_w, card_h = get_table_card_size(screen_rect)
    gap = int(36 * _ui_scale(width, height))
    top_rect = pygame.Rect(width // 2 + gap // 2, height // 2 - card_h // 2, card_w, card_h)
    return pygame.Rect(top_rect.left - card_w - gap, top_rect.top, card_w, card_h)


def get_color_picker_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
    picker_w = 420
    picker_h = 90
    start_x = screen_rect.centerx - picker_w // 2
    y = screen_rect.centery + 140
    size = 80
    gap = 20

    return {
        "red": pygame.Rect(start_x, y, size, size),
        "yellow": pygame.Rect(start_x + (size + gap), y, size, size),
        "green": pygame.Rect(start_x + 2 * (size + gap), y, size, size),
        "blue": pygame.Rect(start_x + 3 * (size + gap), y, size, size),
    }


def get_wild_color_wheel_center(screen_rect: pygame.Rect) -> tuple[int, int]:
    return screen_rect.center


def get_wild_color_at_pos(mouse_pos: tuple[int, int], screen_rect: pygame.Rect) -> str | None:
    center = get_wild_color_wheel_center(screen_rect)
    dx = mouse_pos[0] - center[0]
    dy = mouse_pos[1] - center[1]
    if dx * dx + dy * dy > WILD_WHEEL_RADIUS * WILD_WHEEL_RADIUS:
        return None

    if dx == 0 and dy == 0:
        return None

    angle = (math.degrees(math.atan2(dy, dx)) + 360.0) % 360.0
    for color, start_angle, end_angle in WILD_WHEEL_SEGMENTS:
        if start_angle <= angle < end_angle:
            return color
    return "blue"


def get_rule_zero_choice_rects(screen_rect: pygame.Rect) -> dict[int, pygame.Rect]:
    button_w = 220
    button_h = 76
    gap = 24
    total_w = button_w * 2 + gap
    start_x = screen_rect.centerx - total_w // 2
    y = screen_rect.centery + 132

    return {
        PASS_CLOCKWISE: pygame.Rect(start_x, y, button_w, button_h),
        PASS_COUNTER_CLOCKWISE: pygame.Rect(start_x + button_w + gap, y, button_w, button_h),
    }


def get_rule_seven_target_rects(game: UnoGameManager, screen_rect: pygame.Rect) -> dict[int, pygame.Rect]:
    targets = [player_id for player_id in range(game.num_players) if player_id != game.pending_effect_player]
    count = len(targets)
    button_w = 190
    button_h = 76
    gap = 18
    total_w = count * button_w + max(0, count - 1) * gap
    start_x = screen_rect.centerx - total_w // 2
    y = screen_rect.centery + 132

    rects: dict[int, pygame.Rect] = {}
    for index, player_id in enumerate(targets):
        rects[player_id] = pygame.Rect(start_x + index * (button_w + gap), y, button_w, button_h)
    return rects


def get_reaction_button_rect(screen_rect: pygame.Rect) -> pygame.Rect:
    return pygame.Rect(screen_rect.centerx - 130, screen_rect.centery + 188, 260, 76)


def get_reaction_panel_rect(screen_rect: pygame.Rect) -> pygame.Rect:
    panel_w = min(700, screen_rect.width - 96)
    panel_h = 238
    y = min(screen_rect.centery + 72, screen_rect.bottom - panel_h - 34)
    return pygame.Rect(screen_rect.centerx - panel_w // 2, y, panel_w, panel_h)


def get_draw_decision_button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
    button_w = 150
    button_h = 64
    gap = 22
    total_w = button_w * 2 + gap
    start_x = screen_rect.centerx - total_w // 2
    y = screen_rect.centery + 94
    return {
        "play": pygame.Rect(start_x, y, button_w, button_h),
        "keep": pygame.Rect(start_x + button_w + gap, y, button_w, button_h),
    }


def get_uno_button_rect(screen_rect: pygame.Rect) -> pygame.Rect:
    button_w = 128
    button_h = 64
    margin = max(24, int(screen_rect.width * 0.025))
    footer_height = _clamp(int(screen_rect.height * 0.045), 34, 48)
    y = screen_rect.bottom - footer_height - button_h - 22
    return pygame.Rect(screen_rect.right - margin - button_w, y, button_w, button_h)


def _draw_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    fill: tuple[int, int, int],
    border: tuple[int, int, int] = (255, 255, 255),
) -> None:
    pygame.draw.rect(screen, fill, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, width=2, border_radius=12)
    font = pygame.font.SysFont("consolas", 22, bold=True)
    text = font.render(label, True, (20, 20, 20))
    screen.blit(text, text.get_rect(center=rect.center))


def _draw_uno_button(screen: pygame.Surface, rect: pygame.Rect, enabled: bool, armed: bool) -> None:
    if armed:
        fill = (255, 214, 82)
        border = (255, 255, 255)
        label = "UNO READY"
    elif enabled:
        fill = (232, 64, 62)
        border = (255, 235, 90)
        label = "UNO"
    else:
        fill = (74, 78, 86)
        border = (126, 132, 142)
        label = "UNO"

    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, width=2, border_radius=8)
    font_size = 18 if armed else 24
    font = pygame.font.SysFont("consolas", font_size, bold=True)
    text_color = (24, 24, 24) if enabled or armed else (185, 188, 194)
    text = font.render(label, True, text_color)
    screen.blit(text, text.get_rect(center=rect.center))


def _draw_modal_panel(screen: pygame.Surface, rect: pygame.Rect) -> None:
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 22, 29, 232), panel.get_rect(), border_radius=8)
    pygame.draw.rect(panel, (235, 235, 235, 90), panel.get_rect(), width=2, border_radius=8)
    screen.blit(panel, rect)


def _sector_points(
    center: tuple[int, int],
    radius: int,
    start_angle: float,
    end_angle: float,
    steps: int = 28,
) -> list[tuple[int, int]]:
    points = [center]
    for step in range(steps + 1):
        angle = start_angle + (end_angle - start_angle) * (step / steps)
        points.append(
            (
                int(center[0] + math.cos(math.radians(angle)) * radius),
                int(center[1] + math.sin(math.radians(angle)) * radius),
            )
        )
    return points


def _brighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, component + amount) for component in color)


def _draw_wild_color_wheel(
    screen: pygame.Surface,
    screen_rect: pygame.Rect,
    hovered_color: str | None,
) -> None:
    center = get_wild_color_wheel_center(screen_rect)
    radius = WILD_WHEEL_RADIUS

    glow = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 255, 255, 24), center, radius + 16)
    screen.blit(glow, (0, 0))

    for color, start_angle, end_angle in WILD_WHEEL_SEGMENTS:
        fill = WILD_COLOR_RGB[color]
        if color == hovered_color:
            fill = _brighten(fill, 34)
        pygame.draw.polygon(screen, fill, _sector_points(center, radius, start_angle, end_angle))

    line_color = (245, 245, 245)
    pygame.draw.circle(screen, line_color, center, radius, width=4)
    pygame.draw.line(screen, line_color, (center[0] - radius, center[1]), (center[0] + radius, center[1]), width=4)
    pygame.draw.line(screen, line_color, (center[0], center[1] - radius), (center[0], center[1] + radius), width=4)

    if hovered_color is not None:
        for color, start_angle, end_angle in WILD_WHEEL_SEGMENTS:
            if color == hovered_color:
                pygame.draw.polygon(
                    screen,
                    (255, 255, 255),
                    _sector_points(center, radius, start_angle, end_angle),
                    width=3,
                )
                break


def _draw_draw_decision_prompt(
    screen: pygame.Surface,
    screen_rect: pygame.Rect,
    atlas: CardSpriteAtlas,
    card: Card,
) -> None:
    width, height = screen.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 130))
    screen.blit(overlay, (0, 0))

    prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
    body_font = pygame.font.SysFont("consolas", 20)
    prompt = prompt_font.render("Play the drawn card?", True, (255, 255, 255))
    screen.blit(prompt, prompt.get_rect(center=(screen_rect.centerx, screen_rect.centery - 164)))

    card_rect = pygame.Rect(0, 0, *TABLE_CARD_SIZE)
    card_rect.center = (screen_rect.centerx, screen_rect.centery - 42)
    shadow = pygame.Surface(card_rect.size, pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 70))
    screen.blit(shadow, card_rect.move(0, 8))
    card_img = atlas.get_card_surface(card, card_rect.width, card_rect.height)
    screen.blit(card_img, card_rect)

    label = body_font.render(card.short_label, True, (235, 235, 235))
    screen.blit(label, label.get_rect(center=(screen_rect.centerx, screen_rect.centery + 52)))

    rects = get_draw_decision_button_rects(screen_rect)
    _draw_button(screen, rects["play"], "Play", (84, 186, 102))
    _draw_button(screen, rects["keep"], "Keep", (230, 196, 86))


def render_ui(
    screen: pygame.Surface,
    game: UnoGameManager,
    atlas: CardSpriteAtlas,
    now_ms: int,
    selected_index: int,
    last_message: str,
    hovered_index: int | None = None,
    wild_color_picker_active: bool = False,
    hidden_card_ids: set[int] | None = None,
    display_top_card: Card | None = None,
    direction_arrow_angle: float = 0.0,
    wild_hovered_color: str | None = None,
    draw_decision_card: Card | None = None,
) -> None:
    width, height = screen.get_size()
    screen.fill((24, 28, 34))

    hidden_card_ids = hidden_card_ids or set()

    title_font = _scaled_font(width, height, 32, bold=True)
    body_font = _scaled_font(width, height, 24)
    small_font = _scaled_font(width, height, 20)

    screen_rect = screen.get_rect()
    arrow_size = get_direction_arrow_size(screen_rect)
    draw_direction_arrows(screen, get_direction_indicator_center(screen_rect), direction_arrow_angle, arrow_size)

    top = display_top_card or game.top_discard
    top_rect = get_discard_pile_rect(screen_rect)
    top_img = atlas.get_card_surface(top, top_rect.width, top_rect.height)
    top_img = transform_card_surface(top_img, getattr(top, "current_rotation", 0.0), getattr(top, "current_scale", 1.0))
    screen.blit(top_img, top_img.get_rect(center=top_rect.center))

    draw_rect = get_draw_pile_rect(width, height)
    draw_img = atlas.get_back_surface(draw_rect.width, draw_rect.height)
    screen.blit(draw_img, draw_rect)

    header_margin = max(24, int(width * 0.025))
    turn_lbl = title_font.render(f"Turn: Player {game.current_player + 1}", True, (235, 235, 235))
    turn_direction_lbl = title_font.render(f"Turn Dir: {'CW' if game.turn_direction == 1 else 'CCW'}", True, (235, 235, 235))
    pass_direction_lbl = title_font.render(
        f"Pass Dir: {'CW' if game.hand_pass_direction == PASS_CLOCKWISE else 'CCW'}",
        True,
        (235, 235, 235),
    )
    color_lbl = _render_fit_text(
        title_font,
        f"Active Color: {game.current_color.upper()}",
        (235, 235, 235),
        max(180, width // 3),
    )
    screen.blit(turn_lbl, turn_lbl.get_rect(midleft=(header_margin, 42)))
    screen.blit(turn_direction_lbl, turn_direction_lbl.get_rect(center=(width // 2, 42)))
    screen.blit(color_lbl, color_lbl.get_rect(midright=(width - header_margin, 42)))
    screen.blit(pass_direction_lbl, pass_direction_lbl.get_rect(midleft=(header_margin, 78)))

    draw_count = body_font.render(f"Draw Pile: {len(game.draw_pile)}", True, (225, 225, 225))
    draw_count_y = min(height - 126, screen_rect.centery + int(arrow_size * 0.35) + 22)
    screen.blit(draw_count, draw_count.get_rect(center=(draw_rect.centerx, draw_count_y)))

    penalty_label = game.get_active_effect_label(now_ms)
    if penalty_label and game.pending_effect != RULE_REACTION:
        badge = small_font.render(penalty_label, True, (255, 224, 155))
        badge_bg = badge.get_rect(midtop=(width // 2, PENALTY_BADGE_TOP_Y))
        pygame.draw.rect(screen, (64, 47, 24), badge_bg.inflate(24, 14), border_radius=10)
        screen.blit(badge, badge_bg)

    _draw_opponent_hands(screen, game, atlas, body_font)

    if last_message:
        max_status_width = max(240, min(int(width * 0.32), width // 2 - header_margin - 140))
        status_text = _render_fit_text(small_font, last_message, (245, 220, 120), max_status_width)
        status_rect = status_text.get_rect(midleft=(header_margin, 122))
        pygame.draw.rect(screen, (38, 35, 23), status_rect.inflate(18, 10), border_radius=7)
        screen.blit(status_text, status_rect)

    footer_height = _clamp(int(height * 0.045), 34, 48)
    footer = pygame.Surface((width, footer_height), pygame.SRCALPHA)
    footer.fill((0, 0, 0, 82))
    screen.blit(footer, (0, height - footer_height))

    help_line = "Click card: select | Enter/Space: play | Draw pile/D: draw | UNO button/U: call UNO"
    help_text = _render_fit_text(small_font, help_line, (220, 220, 220), width - header_margin * 2)
    screen.blit(help_text, help_text.get_rect(center=(width // 2, height - footer_height // 2)))

    hand = game.player_hands[0]
    if hand:
        selected_index = max(0, min(selected_index, len(hand) - 1))

    draw_order = [i for i in range(len(hand)) if i != hovered_index]
    if hovered_index is not None and 0 <= hovered_index < len(hand):
        draw_order.append(hovered_index)

    for i in draw_order:
        card = hand[i]
        if id(card) in hidden_card_ids:
            continue
        is_hovered = i == hovered_index
        rect = get_card_rect_from_pos(card)
        card_img = atlas.get_card_surface(card, rect.width, rect.height)
        card_img = transform_card_surface(card_img, getattr(card, "current_rotation", 0.0), getattr(card, "current_scale", 1.0))
        if is_hovered:
            shadow_rect = rect.move(0, 8)
            shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 55))
            screen.blit(shadow, shadow_rect)
        screen.blit(card_img, card_img.get_rect(center=rect.center))

        if i == selected_index:
            pygame.draw.rect(screen, (255, 255, 255), rect, width=3, border_radius=8)

    uno_rect = get_uno_button_rect(screen_rect)
    uno_enabled = game.current_player == 0 and game.pending_effect is None and len(hand) <= 2 and len(hand) > 0
    uno_armed = 0 in game.uno_called_players
    _draw_uno_button(screen, uno_rect, uno_enabled, uno_armed)

    if game.pending_effect == RULE_ZERO_DIRECTION and game.current_player == 0:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
        prompt = prompt_font.render("Rule of 0: choose hand pass direction", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 + 58)))

        for direction, rect in get_rule_zero_choice_rects(screen_rect).items():
            label = "Clockwise" if direction == PASS_CLOCKWISE else "Counter-Clockwise"
            fill = (230, 196, 86) if direction == PASS_CLOCKWISE else (86, 151, 230)
            _draw_button(screen, rect, label, fill)

    elif game.pending_effect == RULE_SEVEN_TARGET and game.current_player == 0:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
        prompt = prompt_font.render("Rule of 7: choose a target player to swap hands with", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 + 58)))

        for player_id, rect in get_rule_seven_target_rects(game, screen_rect).items():
            label = f"Player {player_id + 1}"
            fill = (98, 180, 105)
            _draw_button(screen, rect, label, fill)

    elif game.pending_effect == RULE_REACTION:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        panel_rect = get_reaction_panel_rect(screen_rect)
        _draw_modal_panel(screen, panel_rect)

        prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
        prompt = _render_fit_text(
            prompt_font,
            "Rule of 8: reaction window active",
            (255, 255, 255),
            panel_rect.width - 48,
        )
        screen.blit(prompt, prompt.get_rect(center=(panel_rect.centerx, panel_rect.top + 42)))

        timer = small_font.render(f"Time left: {game.get_reaction_remaining_ms(now_ms) / 1000:.1f}s", True, (255, 226, 145))
        screen.blit(timer, timer.get_rect(center=(panel_rect.centerx, panel_rect.top + 82)))

        reacted = small_font.render(
            f"Reacted: {len(game.pending_reaction_players)} / {game.num_players}",
            True,
            (220, 220, 220),
        )
        screen.blit(reacted, reacted.get_rect(center=(panel_rect.centerx, panel_rect.top + 112)))

        react_rect = get_reaction_button_rect(screen_rect)
        _draw_button(screen, react_rect, "REACT", (233, 126, 68))

    if draw_decision_card is not None and not wild_color_picker_active:
        _draw_draw_decision_prompt(screen, screen_rect, atlas, draw_decision_card)

    if wild_color_picker_active:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 125))
        screen.blit(overlay, (0, 0))

        prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
        prompt = prompt_font.render("Choose a color for Wild / +4", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 - WILD_WHEEL_RADIUS - 48)))
        _draw_wild_color_wheel(screen, screen_rect, wild_hovered_color)


def get_title_screen_button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
    """Get button rectangles for the title screen."""
    button_w = 320
    button_h = 90
    gap = 28
    y_start = screen_rect.centery + 80

    return {
        "start_local": pygame.Rect(screen_rect.centerx - button_w // 2, y_start, button_w, button_h),
        "host_game": pygame.Rect(screen_rect.centerx - button_w // 2, y_start + button_h + gap, button_w, button_h),
        "join_game": pygame.Rect(screen_rect.centerx - button_w // 2, y_start + 2 * (button_h + gap), button_w, button_h),
    }


def render_title_screen(screen: pygame.Surface) -> None:
    """Render the main title screen."""
    width, height = screen.get_size()
    screen.fill((24, 28, 34))

    # Title
    title_font = pygame.font.SysFont("consolas", 86, bold=True)
    title = title_font.render("UNO Online", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(width // 2, height // 2 - 180)))

    # Subtitle
    subtitle_font = pygame.font.SysFont("consolas", 36)
    subtitle = subtitle_font.render("Custom Game with Module 2-4 Rules", True, (180, 180, 180))
    screen.blit(subtitle, subtitle.get_rect(center=(width // 2, height // 2 - 100)))

    # Buttons
    screen_rect = screen.get_rect()
    button_rects = get_title_screen_button_rects(screen_rect)

    _draw_button(screen, button_rects["start_local"], "Start Local Match", (75, 175, 90))
    _draw_button(screen, button_rects["host_game"], "Host Game", (233, 126, 68), border=(160, 100, 50))
    _draw_button(screen, button_rects["join_game"], "Join Game", (75, 125, 215), border=(50, 90, 150))

    # Footer
    footer_font = pygame.font.SysFont("consolas", 18)
    footer = footer_font.render("Host and Join features coming soon...", True, (120, 120, 120))
    screen.blit(footer, footer.get_rect(center=(width // 2, height - 100)))


def get_end_screen_button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
    """Get button rectangles for the end screen."""
    button_w = 360
    button_h = 96
    y = screen_rect.centery + 240

    return {
        "return_title": pygame.Rect(screen_rect.centerx - button_w // 2, y, button_w, button_h),
    }


def render_end_screen(screen: pygame.Surface, game: UnoGameManager) -> None:
    """Render the game end screen with winner info."""
    width, height = screen.get_size()
    screen.fill((24, 28, 34))

    title_font = pygame.font.SysFont("consolas", 88, bold=True)
    section_font = pygame.font.SysFont("consolas", 40, bold=True)
    info_font = pygame.font.SysFont("consolas", 34)

    if game.winner is not None:
        winner_text = title_font.render(f"Player {game.winner + 1} Wins!", True, (255, 240, 135))
    else:
        winner_text = title_font.render("Game Over", True, (255, 240, 135))

    center_x = width // 2
    title_y = height // 2 - 220
    section_y = title_y + 150
    list_start_y = section_y + 70
    line_gap = 56

    screen.blit(winner_text, winner_text.get_rect(center=(center_x, title_y)))

    final_hands_text = section_font.render("Final Hands", True, (220, 220, 220))
    screen.blit(final_hands_text, final_hands_text.get_rect(center=(center_x, section_y)))

    for pid in range(game.num_players):
        hand_size = len(game.player_hands[pid])
        label = f"Player {pid + 1}: {hand_size} card{'s' if hand_size != 1 else ''}"
        color = (75, 175, 90) if pid == game.winner else (220, 220, 220)
        text = info_font.render(label, True, color)
        screen.blit(text, text.get_rect(center=(center_x, list_start_y + pid * line_gap)))

    screen_rect = screen.get_rect()
    button_rects = get_end_screen_button_rects(screen_rect)
    _draw_button(screen, button_rects["return_title"], "Return to Title", (98, 180, 105))
