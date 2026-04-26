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
    y = height - card_h - 88
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
    if num_players == 4:
        anchors = {
            0: (screen_rect.centerx, screen_rect.bottom - 140),
            1: (screen_rect.left + 150, screen_rect.centery),
            2: (screen_rect.centerx, screen_rect.top + 135),
            3: (screen_rect.right - 150, screen_rect.centery),
        }
        return anchors.get(player_id, (screen_rect.centerx, screen_rect.centery))

    if player_id == 0:
        return (screen_rect.centerx, screen_rect.bottom - 140)
    if player_id == 1:
        return (screen_rect.centerx, screen_rect.top + 135)
    if player_id == 2:
        return (screen_rect.left + 150, screen_rect.centery)
    return (screen_rect.right - 150, screen_rect.centery)


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
    card_w, card_h = TABLE_CARD_SIZE
    return pygame.Rect(screen_rect.centerx + 18, screen_rect.centery - card_h // 2, card_w, card_h)


def get_direction_indicator_center(screen_rect: pygame.Rect) -> tuple[int, int]:
    draw_rect = get_draw_pile_rect(screen_rect.width, screen_rect.height)
    discard_rect = get_discard_pile_rect(screen_rect)
    return ((draw_rect.centerx + discard_rect.centerx) // 2, (draw_rect.centery + discard_rect.centery) // 2)


def _polar_point(center: tuple[float, float], radius: float, angle_degrees: float) -> tuple[float, float]:
    angle_radians = math.radians(angle_degrees)
    return (center[0] + math.cos(angle_radians) * radius, center[1] + math.sin(angle_radians) * radius)


def _draw_arrowhead(surface: pygame.Surface, center: tuple[float, float], angle_degrees: float, radius: float, color: tuple[int, int, int, int]) -> None:
    tip = _polar_point(center, radius, angle_degrees)
    left = _polar_point(center, radius - 26, angle_degrees - 18)
    right = _polar_point(center, radius - 26, angle_degrees + 18)
    pygame.draw.polygon(surface, color, [tip, left, right])


@lru_cache(maxsize=8)
def build_direction_arrow_surface(size: int) -> pygame.Surface:
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size / 2, size / 2)
    outer_radius = size * 0.42
    inner_radius = size * 0.28

    ring_color = (110, 120, 138, 90)
    accent_color = (225, 231, 242, 190)
    glow_color = (85, 95, 115, 70)

    pygame.draw.circle(surface, glow_color, (int(center[0]), int(center[1])), int(outer_radius + 8), width=12)
    pygame.draw.circle(surface, ring_color, (int(center[0]), int(center[1])), int(outer_radius), width=10)

    pygame.draw.arc(
        surface,
        accent_color,
        pygame.Rect(center[0] - outer_radius, center[1] - outer_radius, outer_radius * 2, outer_radius * 2),
        math.radians(-35),
        math.radians(150),
        width=10,
    )
    pygame.draw.arc(
        surface,
        accent_color,
        pygame.Rect(center[0] - inner_radius, center[1] - inner_radius, inner_radius * 2, inner_radius * 2),
        math.radians(145),
        math.radians(325),
        width=8,
    )

    _draw_arrowhead(surface, center, -35, outer_radius, accent_color)
    _draw_arrowhead(surface, center, 325, inner_radius, accent_color)
    return surface


def draw_direction_arrows(screen: pygame.Surface, center: tuple[int, int], angle: float) -> None:
    base = build_direction_arrow_surface(DIRECTION_ARROW_SIZE)
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
        y = 96
        for i in range(count):
            rects.append(pygame.Rect(start_x + i * spacing, y, card_w, card_h))
        return rects

    card_w, card_h = OPPONENT_SIDE_SIZE
    spacing = min(18, max(8, 180 // max(1, count - 1))) if count > 1 else 0
    col_height = card_h + (count - 1) * spacing
    start_y = (height - col_height) // 2
    x = 42 if position == "left" else width - card_w - 42
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
            label_rect = label.get_rect(center=(width // 2, rects[0].top - 18))
        elif position == "left" and rects:
            label_rect = label.get_rect(midleft=(28, rects[0].top - 14))
        elif position == "right" and rects:
            label_rect = label.get_rect(midright=(width - 28, rects[0].top - 14))
        else:
            label_rect = label.get_rect(topleft=(20, 20))
        screen.blit(label, label_rect)


def get_draw_pile_rect(width: int, height: int) -> pygame.Rect:
    card_w, card_h = TABLE_CARD_SIZE
    top_rect = pygame.Rect(width // 2 + 18, height // 2 - card_h // 2, card_w, card_h)
    return pygame.Rect(top_rect.left - card_w - 36, top_rect.top, card_w, card_h)


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
    return pygame.Rect(screen_rect.centerx - 130, screen_rect.centery + 128, 260, 84)


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
) -> None:
    width, height = screen.get_size()
    screen.fill((24, 28, 34))

    hidden_card_ids = hidden_card_ids or set()

    title_font = pygame.font.SysFont("consolas", 32, bold=True)
    body_font = pygame.font.SysFont("consolas", 24)
    small_font = pygame.font.SysFont("consolas", 20)

    draw_direction_arrows(screen, get_direction_indicator_center(screen.get_rect()), direction_arrow_angle)

    top = display_top_card or game.top_discard
    table_card_w, table_card_h = TABLE_CARD_SIZE
    top_rect = get_discard_pile_rect(screen.get_rect())
    top_img = atlas.get_card_surface(top, top_rect.width, top_rect.height)
    top_img = transform_card_surface(top_img, getattr(top, "current_rotation", 0.0), getattr(top, "current_scale", 1.0))
    screen.blit(top_img, top_img.get_rect(center=top_rect.center))

    draw_rect = get_draw_pile_rect(width, height)
    draw_img = atlas.get_back_surface(draw_rect.width, draw_rect.height)
    screen.blit(draw_img, draw_rect)

    turn_lbl = title_font.render(f"Turn: Player {game.current_player + 1}", True, (235, 235, 235))
    turn_direction_lbl = title_font.render(f"Turn Dir: {'CW' if game.turn_direction == 1 else 'CCW'}", True, (235, 235, 235))
    pass_direction_lbl = title_font.render(
        f"Pass Dir: {'CW' if game.hand_pass_direction == PASS_CLOCKWISE else 'CCW'}",
        True,
        (235, 235, 235),
    )
    color_lbl = title_font.render(f"Active Color: {game.current_color.upper()}", True, (235, 235, 235))
    screen.blit(turn_lbl, turn_lbl.get_rect(midleft=(48, 42)))
    screen.blit(turn_direction_lbl, turn_direction_lbl.get_rect(center=(width // 2, 42)))
    screen.blit(color_lbl, color_lbl.get_rect(midright=(width - 48, 42)))
    screen.blit(pass_direction_lbl, pass_direction_lbl.get_rect(midleft=(48, 78)))

    draw_count = body_font.render(f"Draw Pile: {len(game.draw_pile)}", True, (225, 225, 225))
    screen.blit(draw_count, draw_count.get_rect(midtop=(draw_rect.centerx, draw_rect.bottom + 18)))

    penalty_label = game.get_active_effect_label(now_ms)
    if penalty_label and game.pending_effect != RULE_REACTION:
        badge = small_font.render(penalty_label, True, (255, 224, 155))
        badge_bg = badge.get_rect(midtop=(width // 2, 92))
        pygame.draw.rect(screen, (64, 47, 24), badge_bg.inflate(24, 14), border_radius=10)
        screen.blit(badge, badge_bg)

    _draw_opponent_hands(screen, game, atlas, body_font)

    help_line = "Click card: select | Click selected / Enter / Space: play | Draw pile click or D: draw"
    help_text = small_font.render(help_line, True, (220, 220, 220))
    screen.blit(help_text, help_text.get_rect(center=(width // 2, height - 42)))

    msg_text = small_font.render(last_message, True, (245, 220, 120))
    screen.blit(msg_text, msg_text.get_rect(midleft=(48, height - 42)))

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

    screen_rect = screen.get_rect()
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

        prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
        prompt = prompt_font.render("Rule of 8: reaction window active", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 + 40)))

        timer = small_font.render(f"Time left: {game.get_reaction_remaining_ms(now_ms) / 1000:.1f}s", True, (255, 226, 145))
        screen.blit(timer, timer.get_rect(center=(width // 2, height // 2 + 74)))

        reacted = small_font.render(
            f"Reacted: {len(game.pending_reaction_players)} / {game.num_players}",
            True,
            (220, 220, 220),
        )
        screen.blit(reacted, reacted.get_rect(center=(width // 2, height // 2 + 102)))

        react_rect = get_reaction_button_rect(screen_rect)
        _draw_button(screen, react_rect, "REACT", (233, 126, 68))

    if wild_color_picker_active:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 125))
        screen.blit(overlay, (0, 0))

        prompt_font = pygame.font.SysFont("consolas", 28, bold=True)
        prompt = prompt_font.render("Choose a color for Wild / +4", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 + 95)))

        color_rgb = {
            "red": (220, 70, 70),
            "yellow": (230, 205, 80),
            "green": (75, 175, 90),
            "blue": (75, 125, 215),
        }
        for color, rect in get_color_picker_rects(screen.get_rect()).items():
            pygame.draw.rect(screen, color_rgb[color], rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), rect, width=2, border_radius=10)


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
