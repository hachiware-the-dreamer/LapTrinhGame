"""UI functions for the game settings screen."""
import pygame


SECTION_LABEL_X_OFFSET = 500
SLIDER_WIDTH = 400


def get_settings_screen_button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
    """Return button rectangles for the settings screen."""
    button_w = 240
    button_h = 64
    spacing = 40
    y = screen_rect.height - button_h - 28
    total_width = button_w * 2 + spacing
    left_x = screen_rect.centerx - total_width // 2

    return {
        "back": pygame.Rect(left_x, y, button_w, button_h),
        "start_game": pygame.Rect(left_x + button_w + spacing, y, button_w, button_h),
    }


def get_player_count_rects(screen_rect: pygame.Rect) -> dict[int, pygame.Rect]:
    """Return button rectangles for player count selection (2, 3, 4)."""
    start_y = 165
    button_w = 86
    button_h = 70
    spacing = 60
    center_x = screen_rect.centerx

    return {
        2: pygame.Rect(center_x - button_w - spacing, start_y, button_w, button_h),
        3: pygame.Rect(center_x - button_w // 2, start_y, button_w, button_h),
        4: pygame.Rect(center_x + spacing, start_y, button_w, button_h),
    }


def get_initial_cards_slider_rect(screen_rect: pygame.Rect) -> pygame.Rect:
    """Return slider rect for initial cards setting."""
    return pygame.Rect(screen_rect.centerx - SLIDER_WIDTH // 2, 320, SLIDER_WIDTH, 30)


def get_rule_toggle_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
    """Return button rects for rule toggles."""
    start_y = 445
    button_w = 120
    button_h = 60
    spacing = 26
    center_x = screen_rect.centerx

    return {
        "rule_0": pygame.Rect(center_x - button_w - spacing - button_w // 2, start_y, button_w, button_h),
        "rule_7": pygame.Rect(center_x - button_w // 2, start_y, button_w, button_h),
        "rule_8": pygame.Rect(center_x + button_w // 2 + spacing, start_y, button_w, button_h),
    }


def get_rule_8_timer_slider_rect(screen_rect: pygame.Rect, show_two_player_behavior: bool = False) -> pygame.Rect:
    """Return slider rect for Rule 8 reaction timer."""
    return pygame.Rect(screen_rect.centerx - SLIDER_WIDTH // 2, 585, SLIDER_WIDTH, 30)


def get_two_player_behavior_rects(screen_rect: pygame.Rect, show_rule_8_timer: bool = False) -> dict[str, pygame.Rect]:
    """Return button rects for 2-player reverse behavior selection."""
    start_y = 715 if show_rule_8_timer else 585
    button_width = 180
    button_height = 60
    spacing = 30
    block_x = screen_rect.centerx - (button_width * 2 + spacing) // 2

    return {
        "skip": pygame.Rect(block_x, start_y, button_width, button_height),
        "reverse": pygame.Rect(block_x + button_width + spacing, start_y, button_width, button_height),
    }


def _draw_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    fill: tuple[int, int, int],
    border: tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Draw a styled button."""
    pygame.draw.rect(screen, fill, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, width=3, border_radius=12)
    font = pygame.font.SysFont("consolas", 24, bold=True)
    text = font.render(label, True, (20, 20, 20))
    screen.blit(text, text.get_rect(center=rect.center))

def render_settings_screen(
    screen: pygame.Surface,
    num_players: int,
    initial_cards: int,
    rule_0_enabled: bool,
    rule_7_enabled: bool,
    rule_8_enabled: bool,
    rule_8_timer_ms: int,
    two_player_behavior: str,
) -> None:
    """Render the game settings screen."""
    screen.fill((24, 28, 34))

    screen_rect = screen.get_rect()

    font_title = pygame.font.SysFont("consolas", 72, bold=True)
    font_section = pygame.font.SysFont("consolas", 36, bold=True)
    font_label = pygame.font.SysFont("consolas", 28)
    section_x = screen_rect.centerx - SECTION_LABEL_X_OFFSET

    # Title
    title = font_title.render("GAME SETTINGS", True, (255, 255, 255))
    title_rect = title.get_rect(midtop=(screen_rect.centerx, 20))
    screen.blit(title, title_rect)

    # Player count section
    label = font_section.render("Players:", True, (255, 255, 255))
    screen.blit(label, (section_x, 130))

    player_rects = get_player_count_rects(screen_rect)
    for count, rect in player_rects.items():
        if count == num_players:
            _draw_button(screen, rect, str(count), (75, 175, 90), (100, 200, 100))
        else:
            _draw_button(screen, rect, str(count), (100, 100, 110), (130, 130, 140))

    # Initial cards
    label = font_section.render("Initial Cards:", True, (255, 255, 255))
    screen.blit(label, (section_x, 270))

    slider_rect = get_initial_cards_slider_rect(screen_rect)
    pygame.draw.rect(screen, (60, 60, 70), slider_rect, border_radius=8)
    pygame.draw.rect(screen, (130, 130, 140), slider_rect, width=2, border_radius=8)

    # Slider knob
    slider_pos = slider_rect.x + (initial_cards - 2) / 13 * slider_rect.width
    pygame.draw.circle(screen, (100, 200, 100), (int(slider_pos), slider_rect.centery), 15)

    cards_text = font_label.render(f"{initial_cards}", True, (255, 255, 255))
    screen.blit(cards_text, (slider_rect.right + 40, slider_rect.centery - 14))

    # Rules section
    label = font_section.render("Rules:", True, (255, 255, 255))
    screen.blit(label, (section_x, 390))

    rule_rects = get_rule_toggle_rects(screen_rect)
    rule_labels = {"rule_0": "Rule 0", "rule_7": "Rule 7", "rule_8": "Rule 8"}
    rule_states = {"rule_0": rule_0_enabled, "rule_7": rule_7_enabled, "rule_8": rule_8_enabled}

    for key, rect in rule_rects.items():
        if rule_states[key]:
            _draw_button(screen, rect, rule_labels[key], (75, 175, 90), (100, 200, 100))
        else:
            _draw_button(screen, rect, rule_labels[key], (100, 100, 110), (130, 130, 140))

    # Rule 8 timer
    if rule_8_enabled:
        label = font_section.render("Rule 8 Timer (ms):", True, (255, 255, 255))
        timer_rect = get_rule_8_timer_slider_rect(screen_rect, show_two_player_behavior=(num_players == 2))
        screen.blit(label, (section_x, timer_rect.y - 60))

        pygame.draw.rect(screen, (60, 60, 70), timer_rect, border_radius=8)
        pygame.draw.rect(screen, (130, 130, 140), timer_rect, width=2, border_radius=8)

        timer_pos = timer_rect.x + (rule_8_timer_ms - 1000) / 4000 * timer_rect.width
        pygame.draw.circle(screen, (100, 200, 100), (int(timer_pos), timer_rect.centery), 15)

        timer_text = font_label.render(f"{rule_8_timer_ms}ms", True, (255, 255, 255))
        screen.blit(timer_text, (timer_rect.right + 40, timer_rect.centery - 14))

    # 2-player behavior
    if num_players == 2:
        label = font_section.render("2-Player Reverse:", True, (255, 255, 255))
        behavior_rects = get_two_player_behavior_rects(screen_rect, show_rule_8_timer=rule_8_enabled)
        behavior_label_y = behavior_rects["skip"].y - 60
        screen.blit(label, (section_x, behavior_label_y))

        for behavior, rect in behavior_rects.items():
            if behavior == two_player_behavior:
                _draw_button(screen, rect, behavior.capitalize(), (75, 175, 90), (100, 200, 100))
            else:
                _draw_button(screen, rect, behavior.capitalize(), (100, 100, 110), (130, 130, 140))

    # Buttons
    button_rects = get_settings_screen_button_rects(screen_rect)
    _draw_button(screen, button_rects["back"], "BACK", (200, 100, 100), (220, 130, 100))
    _draw_button(screen, button_rects["start_game"], "START GAME", (75, 175, 90), (100, 200, 100))
