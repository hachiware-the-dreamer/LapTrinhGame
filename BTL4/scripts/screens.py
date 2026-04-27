import random
from dataclasses import dataclass
from typing import Optional

import pygame

from scripts.animation import ActiveCard, lerp, lerp_point, smooth_factor, transform_card_surface
from scripts.assets import asset_path
from scripts.ai import AITurnOutcome, perform_simple_ai_turn
from scripts.cards import ACTION_WILD_DRAW_FOUR, Card
from scripts.game_manager import (
    GameSettings,
    PlayerAction,
    PASS_CLOCKWISE,
    PASS_COUNTER_CLOCKWISE,
    RULE_REACTION,
    RULE_SEVEN_TARGET,
    RULE_ZERO_DIRECTION,
    UnoGameManager,
)
from scripts.sprites import CardSpriteAtlas
from scripts.ui import (
    card_rect_for_hand,
    draw_theme_background,
    draw_theme_button,
    draw_theme_panel,
    get_card_rect_from_pos,
    get_draw_decision_button_rects,
    get_draw_pile_rect,
    get_end_screen_button_rects,
    get_hovered_hand_index,
    get_discard_pile_rect,
    get_player_anchor_point,
    get_player_card_rotation,
    get_player_hand_rotation,
    get_player_hand_card_rects,
    get_reaction_button_rect,
    get_rule_seven_target_rects,
    get_rule_zero_choice_rects,
    get_multiplayer_screen_button_rects,
    get_title_screen_button_rects,
    get_uno_button_rect,
    get_wild_color_at_pos,
    render_end_screen,
    render_multiplayer_screen,
    render_title_screen,
    render_ui,
    theme_font,
)

STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_END = "end"
HAND_TRANSFER_ANIMATION = "Hand_Transfer_Animation"
SETTINGS_BG_COLOR = (10, 18, 28)
SETTINGS_ACTIVE_FILL = (65, 175, 95)
SETTINGS_ACTIVE_BORDER = (164, 235, 178)
SETTINGS_IDLE_FILL = (84, 94, 110)
SETTINGS_IDLE_BORDER = (146, 158, 174)
SETTINGS_DANGER_FILL = (225, 55, 55)
SETTINGS_DANGER_BORDER = (246, 166, 166)
SETTINGS_LABEL_X_OFFSET = 430
SETTINGS_SLIDER_WIDTH = 400


@dataclass
class AudioSettings:
    master_volume: float = 1.0
    music_volume: float = 0.18
    sfx_volume: float = 1.0

    def music_mix(self) -> float:
        return max(0.0, min(1.0, self.master_volume * self.music_volume))

    def sfx_mix(self, base_volume: float = 1.0) -> float:
        return max(0.0, min(1.0, base_volume * self.master_volume * self.sfx_volume))


@dataclass
class ScreenResult:
    next_screen: Optional["BaseScreen"] = None
    running: bool = True


@dataclass
class HandTransferAnimation:
    choice_action: PlayerAction
    phase: int
    cards: list[ActiveCard]
    target_owner_by_card_id: dict[int, int]


class BaseScreen:
    state_name = ""

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        return ScreenResult()

    def update(self, screen: pygame.Surface, now_ms: int) -> Optional["BaseScreen"]:
        return None

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        raise NotImplementedError

    @property
    def wants_bgm(self) -> bool:
        return False


class TitleScreen(BaseScreen):
    state_name = STATE_TITLE

    def __init__(self, atlas: CardSpriteAtlas, audio_settings: AudioSettings) -> None:
        self.atlas = atlas
        self.audio_settings = audio_settings

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for button_name, rect in get_title_screen_button_rects(screen.get_rect()).items():
                    if rect.collidepoint(mouse_pos):
                        if button_name == "start_local":
                            return ScreenResult(
                                next_screen=GameSettingsScreen(self.atlas, self.audio_settings)
                            )
                        if button_name == "settings":
                            return ScreenResult(
                                next_screen=MainSettingsScreen(self.atlas, self.audio_settings)
                            )
                        if button_name == "multiplayer":
                            return ScreenResult(
                                next_screen=MultiplayerScreen(self.atlas, self.audio_settings)
                            )
                        if button_name == "quit":
                            return ScreenResult(running=False)
                        break

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_title_screen(screen)


class MultiplayerScreen(BaseScreen):
    state_name = "multiplayer"

    def __init__(self, atlas: CardSpriteAtlas, audio_settings: AudioSettings) -> None:
        self.atlas = atlas
        self.audio_settings = audio_settings

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for button_name, rect in get_multiplayer_screen_button_rects(screen.get_rect()).items():
                    if rect.collidepoint(mouse_pos):
                        if button_name == "back":
                            return ScreenResult(next_screen=TitleScreen(self.atlas, self.audio_settings))
                        break

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_multiplayer_screen(screen)


class EndScreen(BaseScreen):
    state_name = STATE_END

    def __init__(self, atlas: CardSpriteAtlas, game: UnoGameManager, audio_settings: AudioSettings) -> None:
        self.atlas = atlas
        self.game = game
        self.audio_settings = audio_settings

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for button_name, rect in get_end_screen_button_rects(screen.get_rect()).items():
                    if rect.collidepoint(mouse_pos):
                        if button_name == "return_title":
                            return ScreenResult(next_screen=TitleScreen(self.atlas, self.audio_settings))
                        break

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_end_screen(screen, self.game)


class GameSettingsScreen(BaseScreen):
    """Screen for configuring game settings before starting."""
    state_name = "settings"

    def __init__(self, atlas: CardSpriteAtlas, audio_settings: AudioSettings) -> None:
        self.atlas = atlas
        self.audio_settings = audio_settings
        self.settings = GameSettings()
        self.dragging_initial_cards = False
        self.dragging_rule_8_timer = False

    @staticmethod
    def _draw_button(
        screen: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        fill: tuple[int, int, int],
        border: tuple[int, int, int],
    ) -> None:
        draw_theme_button(screen, rect, label, fill, border)

    @staticmethod
    def _section_x(screen_rect: pygame.Rect) -> int:
        return screen_rect.centerx - SETTINGS_LABEL_X_OFFSET

    @staticmethod
    def _get_bottom_button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
        button_w = 240
        button_h = 64
        spacing = 40
        y = screen_rect.height - button_h - 50
        total_width = button_w * 2 + spacing
        left_x = screen_rect.centerx - total_width // 2
        return {
            "back": pygame.Rect(left_x, y, button_w, button_h),
            "start_game": pygame.Rect(left_x + button_w + spacing, y, button_w, button_h),
        }

    @staticmethod
    def _get_player_count_rects(screen_rect: pygame.Rect) -> dict[int, pygame.Rect]:
        start_y = max(150, int(screen_rect.height * 0.19))
        button_w = 86
        button_h = 70
        spacing = 60
        center_x = screen_rect.centerx
        return {
            2: pygame.Rect(center_x - button_w - spacing, start_y, button_w, button_h),
            3: pygame.Rect(center_x - button_w // 2, start_y, button_w, button_h),
            4: pygame.Rect(center_x + spacing, start_y, button_w, button_h),
        }

    @staticmethod
    def _get_initial_cards_slider_rect(screen_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(screen_rect.centerx - SETTINGS_SLIDER_WIDTH // 2, int(screen_rect.height * 0.34), SETTINGS_SLIDER_WIDTH, 30)

    @staticmethod
    def _get_rule_toggle_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
        start_y = int(screen_rect.height * 0.51)
        button_w = 120
        button_h = 60
        spacing = 26
        center_x = screen_rect.centerx
        return {
            "rule_0": pygame.Rect(center_x - button_w - spacing - button_w // 2, start_y, button_w, button_h),
            "rule_7": pygame.Rect(center_x - button_w // 2, start_y, button_w, button_h),
            "rule_8": pygame.Rect(center_x + button_w // 2 + spacing, start_y, button_w, button_h),
        }

    @staticmethod
    def _get_rule_8_timer_slider_rect(screen_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(screen_rect.centerx - SETTINGS_SLIDER_WIDTH // 2, int(screen_rect.height * 0.66), SETTINGS_SLIDER_WIDTH, 30)

    @staticmethod
    def _get_two_player_behavior_rects(screen_rect: pygame.Rect, show_rule_8_timer: bool) -> dict[str, pygame.Rect]:
        start_y = int(screen_rect.height * (0.79 if show_rule_8_timer else 0.66))
        button_width = 180
        button_height = 60
        spacing = 30
        block_x = screen_rect.centerx - (button_width * 2 + spacing) // 2
        return {
            "skip": pygame.Rect(block_x, start_y, button_width, button_height),
            "reverse": pygame.Rect(block_x + button_width + spacing, start_y, button_width, button_height),
        }

    @classmethod
    def _draw_slider(cls, screen: pygame.Surface, rect: pygame.Rect, value_ratio: float) -> None:
        pygame.draw.rect(screen, (31, 40, 52), rect, border_radius=8)
        pygame.draw.rect(screen, SETTINGS_IDLE_BORDER, rect, width=2, border_radius=8)
        knob_x = rect.x + value_ratio * rect.width
        pygame.draw.circle(screen, (0, 0, 0), (int(knob_x), rect.centery + 2), 17)
        pygame.draw.circle(screen, SETTINGS_ACTIVE_FILL, (int(knob_x), rect.centery), 15)
        pygame.draw.circle(screen, SETTINGS_ACTIVE_BORDER, (int(knob_x), rect.centery), 15, width=2)

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                # Player count buttons
                for count, rect in self._get_player_count_rects(screen.get_rect()).items():
                    if rect.collidepoint(mouse_pos):
                        self.settings.num_players = count
                        break
                
                # Initial cards slider
                slider_rect = self._get_initial_cards_slider_rect(screen.get_rect())
                if slider_rect.collidepoint(mouse_pos):
                    self.dragging_initial_cards = True
                
                # Rule toggles
                for rule, rect in self._get_rule_toggle_rects(screen.get_rect()).items():
                    if rect.collidepoint(mouse_pos):
                        if rule == "rule_0":
                            self.settings.rule_0_enabled = not self.settings.rule_0_enabled
                        elif rule == "rule_7":
                            self.settings.rule_7_enabled = not self.settings.rule_7_enabled
                        elif rule == "rule_8":
                            self.settings.rule_8_enabled = not self.settings.rule_8_enabled
                        break
                
                # Rule 8 timer slider
                timer_rect = self._get_rule_8_timer_slider_rect(screen.get_rect())
                if timer_rect.collidepoint(mouse_pos) and self.settings.rule_8_enabled:
                    self.dragging_rule_8_timer = True
                
                # 2-player behavior buttons
                if self.settings.num_players == 2:
                    for behavior, rect in self._get_two_player_behavior_rects(
                        screen.get_rect(),
                        show_rule_8_timer=self.settings.rule_8_enabled,
                    ).items():
                        if rect.collidepoint(mouse_pos):
                            self.settings.two_player_reverse_behavior = behavior
                            break
                
                # Back button
                back_rect = self._get_bottom_button_rects(screen.get_rect())["back"]
                if back_rect.collidepoint(mouse_pos):
                    return ScreenResult(next_screen=TitleScreen(self.atlas, self.audio_settings))
                
                # Start game button
                start_rect = self._get_bottom_button_rects(screen.get_rect())["start_game"]
                if start_rect.collidepoint(mouse_pos):
                    game = UnoGameManager(settings=self.settings)
                    return ScreenResult(
                        next_screen=PlayingScreen(
                            atlas=self.atlas,
                            game=game,
                            audio_settings=self.audio_settings,
                            last_message="Player 1 starts.",
                            next_ai_time=now_ms + PlayingScreen.AI_TURN_DELAY_MS,
                        )
                    )

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_initial_cards = False
                self.dragging_rule_8_timer = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_initial_cards:
                    slider_rect = self._get_initial_cards_slider_rect(screen.get_rect())
                    relative_x = max(0, min(1.0, (event.pos[0] - slider_rect.x) / slider_rect.width))
                    self.settings.initial_cards = int(2 + relative_x * 13)
                
                if self.dragging_rule_8_timer and self.settings.rule_8_enabled:
                    timer_rect = self._get_rule_8_timer_slider_rect(screen.get_rect())
                    relative_x = max(0, min(1.0, (event.pos[0] - timer_rect.x) / timer_rect.width))
                    raw_timer_ms = 1000 + relative_x * 4000
                    snapped_timer_ms = round((raw_timer_ms - 1000) / 250) * 250 + 1000
                    self.settings.rule_8_reaction_timer_ms = max(1000, min(5000, int(snapped_timer_ms)))

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        draw_theme_background(screen)
        screen_rect = screen.get_rect()
        section_x = self._section_x(screen_rect)

        font_title = theme_font(screen_rect.width, screen_rect.height, 72, bold=True)
        font_section = theme_font(screen_rect.width, screen_rect.height, 34, bold=True)
        font_label = theme_font(screen_rect.width, screen_rect.height, 28)

        panel_top = max(92, int(screen_rect.height * 0.13))
        panel_bottom = screen_rect.height - 36
        panel_rect = pygame.Rect(0, panel_top, min(1020, screen_rect.width - 96), panel_bottom - panel_top)
        panel_rect.centerx = screen_rect.centerx
        draw_theme_panel(screen, panel_rect, alpha=142)

        title = font_title.render("GAME SETTINGS", True, (255, 255, 255))
        screen.blit(title, title.get_rect(midtop=(screen_rect.centerx, max(18, int(screen_rect.height * 0.032)))))

        label = font_section.render("Players:", True, (255, 255, 255))
        player_rects = self._get_player_count_rects(screen_rect)
        screen.blit(label, (section_x, player_rects[2].y - 46))
        for count, rect in player_rects.items():
            fill = SETTINGS_ACTIVE_FILL if count == self.settings.num_players else SETTINGS_IDLE_FILL
            border = SETTINGS_ACTIVE_BORDER if count == self.settings.num_players else SETTINGS_IDLE_BORDER
            self._draw_button(screen, rect, str(count), fill, border)

        label = font_section.render("Initial Cards:", True, (255, 255, 255))
        slider_rect = self._get_initial_cards_slider_rect(screen_rect)
        screen.blit(label, (section_x, slider_rect.y - 54))
        self._draw_slider(screen, slider_rect, (self.settings.initial_cards - 2) / 13)
        cards_text = font_label.render(f"{self.settings.initial_cards}", True, (255, 255, 255))
        screen.blit(cards_text, (slider_rect.right + 40, slider_rect.centery - 14))

        label = font_section.render("Rules:", True, (255, 255, 255))
        rule_rects = self._get_rule_toggle_rects(screen_rect)
        screen.blit(label, (section_x, rule_rects["rule_0"].y - 54))
        rule_labels = {"rule_0": "Rule 0", "rule_7": "Rule 7", "rule_8": "Rule 8"}
        rule_states = {
            "rule_0": self.settings.rule_0_enabled,
            "rule_7": self.settings.rule_7_enabled,
            "rule_8": self.settings.rule_8_enabled,
        }
        for key, rect in rule_rects.items():
            enabled = rule_states[key]
            fill = SETTINGS_ACTIVE_FILL if enabled else SETTINGS_IDLE_FILL
            border = SETTINGS_ACTIVE_BORDER if enabled else SETTINGS_IDLE_BORDER
            self._draw_button(screen, rect, rule_labels[key], fill, border)

        if self.settings.rule_8_enabled:
            timer_rect = self._get_rule_8_timer_slider_rect(screen_rect)
            label = font_section.render("Rule 8 Timer (ms):", True, (255, 255, 255))
            screen.blit(label, (section_x, timer_rect.y - 54))
            self._draw_slider(screen, timer_rect, (self.settings.rule_8_reaction_timer_ms - 1000) / 4000)
            timer_text = font_label.render(f"{self.settings.rule_8_reaction_timer_ms}ms", True, (255, 255, 255))
            screen.blit(timer_text, (timer_rect.right + 40, timer_rect.centery - 14))

        if self.settings.num_players == 2:
            behavior_rects = self._get_two_player_behavior_rects(
                screen_rect,
                show_rule_8_timer=self.settings.rule_8_enabled,
            )
            label = font_section.render("2-Player Reverse:", True, (255, 255, 255))
            screen.blit(label, (section_x, behavior_rects["skip"].y - 54))
            for behavior, rect in behavior_rects.items():
                selected = behavior == self.settings.two_player_reverse_behavior
                fill = SETTINGS_ACTIVE_FILL if selected else SETTINGS_IDLE_FILL
                border = SETTINGS_ACTIVE_BORDER if selected else SETTINGS_IDLE_BORDER
                self._draw_button(screen, rect, behavior.capitalize(), fill, border)

        button_rects = self._get_bottom_button_rects(screen_rect)
        self._draw_button(screen, button_rects["back"], "BACK", SETTINGS_DANGER_FILL, SETTINGS_DANGER_BORDER)
        self._draw_button(screen, button_rects["start_game"], "START GAME", SETTINGS_ACTIVE_FILL, SETTINGS_ACTIVE_BORDER)


class MainSettingsScreen(BaseScreen):
    state_name = "main_settings"

    def __init__(self, atlas: CardSpriteAtlas, audio_settings: AudioSettings) -> None:
        self.atlas = atlas
        self.audio_settings = audio_settings
        self.dragging_slider: str | None = None

    @staticmethod
    def _draw_button(
        screen: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        fill: tuple[int, int, int],
        border: tuple[int, int, int],
    ) -> None:
        GameSettingsScreen._draw_button(screen, rect, label, fill, border)

    @staticmethod
    def _slider_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
        start_y = int(screen_rect.height * 0.28)
        row_gap = int(screen_rect.height * 0.17)
        return {
            "master": pygame.Rect(screen_rect.centerx - SETTINGS_SLIDER_WIDTH // 2, start_y, SETTINGS_SLIDER_WIDTH, 30),
            "music": pygame.Rect(screen_rect.centerx - SETTINGS_SLIDER_WIDTH // 2, start_y + row_gap, SETTINGS_SLIDER_WIDTH, 30),
            "sfx": pygame.Rect(screen_rect.centerx - SETTINGS_SLIDER_WIDTH // 2, start_y + row_gap * 2, SETTINGS_SLIDER_WIDTH, 30),
        }

    @staticmethod
    def _button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
        button_w = 240
        button_h = 64
        y = screen_rect.height - button_h - 50
        return {
            "back": pygame.Rect(screen_rect.centerx - button_w // 2, y, button_w, button_h),
        }

    def _set_slider_value(self, slider_name: str, rect: pygame.Rect, mouse_x: int) -> None:
        relative_x = max(0.0, min(1.0, (mouse_x - rect.x) / rect.width))
        stepped_value = round(relative_x * 20) / 20
        if slider_name == "master":
            self.audio_settings.master_volume = stepped_value
        elif slider_name == "music":
            self.audio_settings.music_volume = stepped_value
        elif slider_name == "sfx":
            self.audio_settings.sfx_volume = stepped_value

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        slider_rects = self._slider_rects(screen.get_rect())
        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for slider_name, rect in slider_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.dragging_slider = slider_name
                        self._set_slider_value(slider_name, rect, mouse_pos[0])
                        break

                back_rect = self._button_rects(screen.get_rect())["back"]
                if back_rect.collidepoint(mouse_pos):
                    return ScreenResult(next_screen=TitleScreen(self.atlas, self.audio_settings))

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_slider = None

            elif event.type == pygame.MOUSEMOTION and self.dragging_slider is not None:
                self._set_slider_value(self.dragging_slider, slider_rects[self.dragging_slider], event.pos[0])

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        draw_theme_background(screen)
        screen_rect = screen.get_rect()
        section_x = GameSettingsScreen._section_x(screen_rect)
        font_title = theme_font(screen_rect.width, screen_rect.height, 72, bold=True)
        font_section = theme_font(screen_rect.width, screen_rect.height, 34, bold=True)
        font_label = theme_font(screen_rect.width, screen_rect.height, 28)

        panel_top = max(92, int(screen_rect.height * 0.13))
        panel_bottom = screen_rect.height - 36
        panel_rect = pygame.Rect(0, panel_top, min(900, screen_rect.width - 96), panel_bottom - panel_top)
        panel_rect.centerx = screen_rect.centerx
        draw_theme_panel(screen, panel_rect, alpha=142)

        title = font_title.render("MAIN SETTINGS", True, (255, 255, 255))
        screen.blit(title, title.get_rect(midtop=(screen_rect.centerx, max(18, int(screen_rect.height * 0.032)))))

        slider_rects = self._slider_rects(screen_rect)
        slider_rows = (
            ("master", "Master Volume:", self.audio_settings.master_volume),
            ("music", "Music Volume:", self.audio_settings.music_volume),
            ("sfx", "SFX Volume:", self.audio_settings.sfx_volume),
        )
        for key, label_text, value in slider_rows:
            rect = slider_rects[key]
            label = font_section.render(label_text, True, (255, 255, 255))
            screen.blit(label, (section_x, rect.y - 54))
            GameSettingsScreen._draw_slider(screen, rect, value)
            value_text = font_label.render(f"{int(round(value * 100))}%", True, (255, 255, 255))
            screen.blit(value_text, (rect.right + 40, rect.centery - 14))

        back_rect = self._button_rects(screen_rect)["back"]
        self._draw_button(screen, back_rect, "BACK", SETTINGS_DANGER_FILL, SETTINGS_DANGER_BORDER)


class PlayingScreen(BaseScreen):
    state_name = STATE_PLAYING
    AI_TURN_DELAY_MS = 1000
    DIRECTION_ARROW_BASE_SPEED = 90.0
    DIRECTION_ARROW_ACCEL = 4.5
    DIRECTION_ARROW_DECEL = 2.5
    SHAKE_DURATION_MS = 260
    SHAKE_MAX_OFFSET = 10
    PAUSE_MENU_OPTIONS = ("resume", "return_title")

    def __init__(
        self,
        atlas: CardSpriteAtlas,
        game: UnoGameManager,
        audio_settings: AudioSettings,
        last_message: str = "",
        selected_index: int = 0,
        pending_wild_card_index: Optional[int] = None,
        next_ai_time: int = 0,
    ) -> None:
        self.atlas = atlas
        self.game = game
        self.audio_settings = audio_settings
        self.ai_rng = random.Random()
        self.selected_index = selected_index
        self.pending_wild_card_index = pending_wild_card_index
        self.last_message = last_message
        self.next_ai_time = next_ai_time
        self.reaction_ai_due_times: dict[int, int] = {}
        self.hovered_index: int | None = None
        self._last_update_ms: int | None = None
        self._hand_layout_initialized = False
        self.active_cards: list[ActiveCard] = []
        self.hidden_hand_card_ids: set[int] = set()
        self.display_top_card = game.top_discard
        self.direction_arrow_angle = 0.0
        self.direction_arrow_speed = self.DIRECTION_ARROW_BASE_SPEED * self.game.turn_direction
        self.visual_state = ""
        self.hand_transfer_animation: HandTransferAnimation | None = None
        self.wild_hovered_color: str | None = None
        self.pending_draw_decision_card: Card | None = None
        self.pending_draw_decision_choosing_color = False
        self.uno_catch_sound = self._load_uno_catch_sound()
        self.pause_menu_open = False
        self.pause_selected_index = 0
        self.pause_hovered_button: str | None = None
        self.screen_shake_remaining_ms = 0
        self.screen_shake_offset: tuple[int, int] = (0, 0)

    @property
    def wants_bgm(self) -> bool:
        return True

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.pause_menu_open:
                    self.pause_menu_open = False
                    self.pause_hovered_button = None
                    self.last_message = "Game resumed."
                    continue

                if self.game.winner is None and not self._has_modal_input():
                    self.pause_menu_open = True
                    self.pause_selected_index = 0
                    self.pause_hovered_button = None
                    self.last_message = "Game paused."
                    continue

            if self.pause_menu_open:
                pause_result = self._handle_pause_menu_event(event, screen)
                if pause_result is not None:
                    return pause_result
                continue

            if self.hand_transfer_animation is not None:
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.game.winner is None:
                self._handle_mouse_down(event.pos, screen, now_ms)

            if (
                event.type == pygame.KEYDOWN
                and self.game.winner is None
                and self.game.current_player == 0
            ):
                self._handle_key_down(event, screen, now_ms)

        return ScreenResult()

    def update(self, screen: pygame.Surface, now_ms: int) -> Optional[BaseScreen]:
        dt = 0.0 if self._last_update_ms is None else max(0.0, (now_ms - self._last_update_ms) / 1000.0)
        self._last_update_ms = now_ms
        self._update_screen_shake(dt)

        if self.game.winner is not None:
            return EndScreen(self.atlas, self.game, self.audio_settings)

        if self.pause_menu_open:
            return None

        self._schedule_reaction_ai(now_ms)
        self._submit_ai_reactions(now_ms)
        self._update_direction_arrow(dt)
        self._update_active_cards(dt)

        if self.hand_transfer_animation is not None:
            self.visual_state = HAND_TRANSFER_ANIMATION
            self._update_hand_transfer_animation(screen, dt, now_ms)
            if self.game.winner is not None and self.hand_transfer_animation is None:
                return EndScreen(self.atlas, self.game, self.audio_settings)
            return None

        self.visual_state = ""

        tick_message = self.game.tick(now_ms)
        if tick_message:
            self.last_message = tick_message

        self.hovered_index = None
        self.wild_hovered_color = None
        if self.game.pending_draw_decision_card is None:
            self.pending_draw_decision_card = None
            self.pending_draw_decision_choosing_color = False

        if self._wild_color_picker_active():
            self.wild_hovered_color = get_wild_color_at_pos(pygame.mouse.get_pos(), screen.get_rect())

        if (
            not self._has_modal_input()
            and self.game.winner is None
            and self.game.current_player == 0
        ):
            self.hovered_index = get_hovered_hand_index(
                pygame.mouse.get_pos(),
                self.game.player_hands[0],
                screen.get_width(),
                screen.get_height(),
                hidden_card_ids=self.hidden_hand_card_ids,
            )

        self._update_player_hand_animation(screen, dt)

        if (
            self.game.winner is None
            and self.game.current_player != 0
            and self.pending_draw_decision_card is None
            and not self.active_cards
            and not self.game.is_animating
        ):
            if self.game.pending_effect in (RULE_ZERO_DIRECTION, RULE_SEVEN_TARGET):
                ai_choice = self._build_ai_hand_transfer_action()
                if ai_choice is not None:
                    self._begin_hand_transfer_animation(ai_choice, screen, now_ms)
            elif self.game.pending_effect is None and now_ms >= self.next_ai_time:
                previous_player = self.game.current_player
                ai_turn = perform_simple_ai_turn(self.game, now_ms=now_ms)
                self.last_message = ai_turn.message
                if ai_turn.result is not None and getattr(ai_turn.result, "uno_caught_player", None) is not None:
                    self._play_uno_catch_sound()
                self._spawn_ai_animation(previous_player, ai_turn, screen, now_ms)
                ai_delay = self.ai_rng.randint(1000, 1500)
                self.next_ai_time = now_ms + ai_delay

        return None

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_target = screen
        if self.screen_shake_remaining_ms > 0:
            render_target = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        render_ui(
            render_target,
            self.game,
            self.atlas,
            now_ms,
            self.selected_index,
            self.last_message,
            hovered_index=self.hovered_index,
            wild_color_picker_active=self._wild_color_picker_active(),
            hidden_card_ids=self.hidden_hand_card_ids,
            display_top_card=self.display_top_card,
            direction_arrow_angle=self.direction_arrow_angle,
            wild_hovered_color=self.wild_hovered_color,
            draw_decision_card=self.pending_draw_decision_card,
        )
        self._draw_active_cards(render_target)
        self._draw_hand_transfer_cards(render_target)

        if render_target is not screen:
            upscale_margin = 12
            scaled = pygame.transform.smoothscale(
                render_target,
                (screen.get_width() + upscale_margin, screen.get_height() + upscale_margin),
            )
            scaled_rect = scaled.get_rect(
                center=(
                    screen.get_width() // 2 + self.screen_shake_offset[0],
                    screen.get_height() // 2 + self.screen_shake_offset[1],
                )
            )
            screen.blit(scaled, scaled_rect)

        if self.pause_menu_open:
            self._draw_pause_menu(screen)

    def _trigger_screen_shake(self, duration_ms: int | None = None) -> None:
        self.screen_shake_remaining_ms = max(self.screen_shake_remaining_ms, duration_ms or self.SHAKE_DURATION_MS)

    def _update_screen_shake(self, dt: float) -> None:
        if self.screen_shake_remaining_ms <= 0:
            self.screen_shake_remaining_ms = 0
            self.screen_shake_offset = (0, 0)
            return

        self.screen_shake_remaining_ms = max(0, self.screen_shake_remaining_ms - int(dt * 1000.0))
        intensity = max(1.0, (self.screen_shake_remaining_ms / self.SHAKE_DURATION_MS) * self.SHAKE_MAX_OFFSET)
        self.screen_shake_offset = (
            int(self.ai_rng.uniform(-intensity, intensity)),
            int(self.ai_rng.uniform(-intensity, intensity)),
        )

    @staticmethod
    def _pause_button_rects(screen_rect: pygame.Rect) -> dict[str, pygame.Rect]:
        panel_width = min(560, screen_rect.width - 120)
        panel_height = 340
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = screen_rect.center

        button_w = min(340, panel_rect.width - 80)
        button_h = 66
        gap = 24
        left = panel_rect.centerx - button_w // 2
        first_y = panel_rect.y + 150
        return {
            "resume": pygame.Rect(left, first_y, button_w, button_h),
            "return_title": pygame.Rect(left, first_y + button_h + gap, button_w, button_h),
        }

    def _handle_pause_menu_event(
        self,
        event: pygame.event.Event,
        screen: pygame.Surface,
    ) -> Optional[ScreenResult]:
        button_rects = self._pause_button_rects(screen.get_rect())

        if event.type == pygame.MOUSEMOTION:
            self.pause_hovered_button = None
            for button_name, rect in button_rects.items():
                if rect.collidepoint(event.pos):
                    self.pause_hovered_button = button_name
                    self.pause_selected_index = self.PAUSE_MENU_OPTIONS.index(button_name)
                    break
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.pause_selected_index = (self.pause_selected_index - 1) % len(self.PAUSE_MENU_OPTIONS)
                self.pause_hovered_button = None
                return None

            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.pause_selected_index = (self.pause_selected_index + 1) % len(self.PAUSE_MENU_OPTIONS)
                self.pause_hovered_button = None
                return None

            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                selected = self.PAUSE_MENU_OPTIONS[self.pause_selected_index]
                return self._activate_pause_menu_option(selected)
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_name, rect in button_rects.items():
                if rect.collidepoint(event.pos):
                    return self._activate_pause_menu_option(button_name)

        return None

    def _activate_pause_menu_option(self, option: str) -> ScreenResult:
        if option == "resume":
            self.pause_menu_open = False
            self.pause_hovered_button = None
            self.last_message = "Game resumed."
            return ScreenResult()

        if option == "return_title":
            self.pause_menu_open = False
            self.pause_hovered_button = None
            return ScreenResult(next_screen=TitleScreen(self.atlas, self.audio_settings))

        return ScreenResult()

    def _draw_pause_menu(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 185))
        screen.blit(overlay, (0, 0))

        screen_rect = screen.get_rect()
        panel_width = min(560, screen_rect.width - 120)
        panel_height = 340
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = screen_rect.center

        draw_theme_panel(screen, panel_rect, alpha=230)

        title_font = theme_font(screen_rect.width, screen_rect.height, 48, bold=True)
        hint_font = theme_font(screen_rect.width, screen_rect.height, 24)
        title_text = title_font.render("PAUSE MENU", True, (245, 245, 245))
        hint_text = hint_font.render("Esc: Resume", True, (200, 210, 220))
        screen.blit(title_text, title_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 62)))
        screen.blit(hint_text, hint_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 106)))

        labels = {
            "resume": "RESUME",
            "return_title": "RETURN TO TITLE",
        }
        for idx, option in enumerate(self.PAUSE_MENU_OPTIONS):
            rect = self._pause_button_rects(screen_rect)[option]
            is_selected = idx == self.pause_selected_index
            is_hovered = option == self.pause_hovered_button
            if option == "return_title":
                fill = SETTINGS_DANGER_FILL if (is_selected or is_hovered) else SETTINGS_IDLE_FILL
                border = SETTINGS_DANGER_BORDER if (is_selected or is_hovered) else SETTINGS_IDLE_BORDER
            else:
                fill = SETTINGS_ACTIVE_FILL if (is_selected or is_hovered) else SETTINGS_IDLE_FILL
                border = SETTINGS_ACTIVE_BORDER if (is_selected or is_hovered) else SETTINGS_IDLE_BORDER
            GameSettingsScreen._draw_button(screen, rect, labels[option], fill, border)

    def _schedule_reaction_ai(self, now_ms: int) -> None:
        if self.game.pending_effect == RULE_REACTION:
            if not self.reaction_ai_due_times:
                for pid in range(1, self.game.num_players):
                    self.reaction_ai_due_times[pid] = now_ms + self.ai_rng.randint(500, 2900)
        else:
            self.reaction_ai_due_times.clear()

    def _submit_ai_reactions(self, now_ms: int) -> None:
        for pid, due_time in list(self.reaction_ai_due_times.items()):
            if (
                now_ms >= due_time
                and pid not in self.game.pending_reaction_players
                and self.game.pending_effect == RULE_REACTION
            ):
                result = self.game.submit_action(
                    PlayerAction(player_id=pid, action_type="react", timestamp_ms=now_ms)
                )
                if result.ok:
                    self.last_message = result.message
                del self.reaction_ai_due_times[pid]

    def _handle_mouse_down(
        self,
        mouse_pos: tuple[int, int],
        screen: pygame.Surface,
        now_ms: int,
    ) -> None:
        if self.game.is_animating:
            return

        if self.game.pending_effect == RULE_ZERO_DIRECTION and self.game.current_player == 0:
            for direction, rect in get_rule_zero_choice_rects(screen.get_rect()).items():
                if rect.collidepoint(mouse_pos):
                    choice_action = PlayerAction(
                        player_id=self.game.current_player,
                        action_type="choose_zero_direction",
                        chosen_direction=direction,
                        timestamp_ms=now_ms,
                    )
                    self._begin_hand_transfer_animation(choice_action, screen, now_ms)
                    self.last_message = "Rule of 0: transferring hands."
                    break
            return

        if self.game.pending_effect == RULE_SEVEN_TARGET and self.game.current_player == 0:
            for target_player_id, rect in get_rule_seven_target_rects(
                self.game,
                screen.get_rect(),
            ).items():
                if rect.collidepoint(mouse_pos):
                    choice_action = PlayerAction(
                        player_id=self.game.current_player,
                        action_type="choose_seven_target",
                        target_player_id=target_player_id,
                        timestamp_ms=now_ms,
                    )
                    self._begin_hand_transfer_animation(choice_action, screen, now_ms)
                    self.last_message = "Rule of 7: transferring hands."
                    break
            return

        if self.game.pending_effect == RULE_REACTION:
            react_rect = get_reaction_button_rect(screen.get_rect())
            if react_rect.collidepoint(mouse_pos):
                result = self.game.submit_action(
                    PlayerAction(player_id=0, action_type="react", timestamp_ms=now_ms)
                )
                self._record_player_action_result(result, now_ms)
            return

        if self._wild_color_picker_active():
            color = get_wild_color_at_pos(mouse_pos, screen.get_rect())
            if color is not None:
                if self.pending_draw_decision_choosing_color:
                    result = self.game.play_pending_draw_decision(
                        0,
                        chosen_color=color,
                        timestamp_ms=now_ms,
                    )
                    if result.ok:
                        self.pending_draw_decision_card = None
                        self.pending_draw_decision_choosing_color = False
                        self._spawn_player_animation(0, result, "draw", screen, now_ms)
                    self._record_player_action_result(result, now_ms)
                else:
                    result = self.game.submit_action(
                        PlayerAction(
                            player_id=0,
                            action_type="play",
                            card_index=self.pending_wild_card_index,
                            chosen_color=color,
                            timestamp_ms=now_ms,
                        )
                    )
                    self.pending_wild_card_index = None
                    self._spawn_player_animation(0, result, "play", screen, now_ms)
                    self._record_player_action_result(result, now_ms)
                    self._clamp_selected_index()
            return

        if self.pending_draw_decision_card is not None:
            for button_name, rect in get_draw_decision_button_rects(screen.get_rect()).items():
                if rect.collidepoint(mouse_pos):
                    if button_name == "play":
                        self._play_pending_draw_decision(screen, now_ms)
                    elif button_name == "keep":
                        self._keep_pending_draw_decision(screen, now_ms)
                    break
            return

        if self.game.current_player != 0 or self.game.pending_effect is not None:
            return

        uno_rect = get_uno_button_rect(screen.get_rect())
        if uno_rect.collidepoint(mouse_pos):
            result = self.game.submit_action(
                PlayerAction(player_id=0, action_type="uno", timestamp_ms=now_ms)
            )
            self._record_player_action_result(result, now_ms)
            return

        hand = self.game.player_hands[0]
        clicked_card = False
        for i in range(len(hand) - 1, -1, -1):
            if id(hand[i]) in self.hidden_hand_card_ids:
                continue
            rect = self._hand_card_rect(hand[i])
            if rect.collidepoint(mouse_pos):
                self.selected_index = i
                card = hand[i]
                if card.is_wild:
                    self.pending_wild_card_index = i
                    self.last_message = "Choose a color for the wild card."
                else:
                    result = self.game.submit_action(
                        PlayerAction(
                            player_id=0,
                            action_type="play",
                            card_index=i,
                            timestamp_ms=now_ms,
                        )
                    )
                    self._spawn_player_animation(0, result, "play", screen, now_ms)
                    self._record_player_action_result(result, now_ms)
                    self._clamp_selected_index()
                clicked_card = True
                break

        if not clicked_card:
            draw_rect = get_draw_pile_rect(screen.get_width(), screen.get_height())
            if draw_rect.collidepoint(mouse_pos):
                self._draw_for_decision(screen, now_ms)

    def _handle_key_down(self, event: pygame.event.Event, screen: pygame.Surface, now_ms: int) -> None:
        hand = self.game.player_hands[0]

        if self._wild_color_picker_active():
            if event.key == pygame.K_ESCAPE:
                if self.pending_draw_decision_choosing_color:
                    self.pending_draw_decision_choosing_color = False
                    self.last_message = "Choose whether to play or keep the drawn card."
                else:
                    self.pending_wild_card_index = None
                    self.last_message = "Wild color selection canceled."
            return

        if self.pending_draw_decision_card is not None:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_p):
                self._play_pending_draw_decision(screen, now_ms)
            elif event.key in (pygame.K_k, pygame.K_ESCAPE):
                self._keep_pending_draw_decision(screen, now_ms)
            return

        if event.key == pygame.K_LEFT and hand:
            self.selected_index = (self.selected_index - 1) % len(hand)
        elif event.key == pygame.K_RIGHT and hand:
            self.selected_index = (self.selected_index + 1) % len(hand)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and hand and self.game.pending_effect is None:
            card = hand[self.selected_index]
            if card.is_wild:
                self.pending_wild_card_index = self.selected_index
                self.last_message = "Choose a color for the wild card."
            else:
                result = self.game.submit_action(
                    PlayerAction(
                        player_id=0,
                        action_type="play",
                        card_index=self.selected_index,
                        timestamp_ms=now_ms,
                    )
                )
                self._record_player_action_result(result, now_ms)
                self._clamp_selected_index()
        elif event.key == pygame.K_d and self.game.pending_effect is None:
            self._draw_for_decision(screen, now_ms)
        elif event.key == pygame.K_u and self.game.pending_effect is None:
            result = self.game.submit_action(
                PlayerAction(player_id=0, action_type="uno", timestamp_ms=now_ms)
            )
            self._record_player_action_result(result, now_ms)

    def _has_modal_input(self) -> bool:
        return self._wild_color_picker_active() or self.pending_draw_decision_card is not None

    def _wild_color_picker_active(self) -> bool:
        return self.pending_wild_card_index is not None or self.pending_draw_decision_choosing_color

    def _draw_for_decision(self, screen: pygame.Surface, now_ms: int) -> None:
        result = self.game.draw_for_decision(0)
        if result.ok and self.game.pending_draw_decision_card is result.drew_card:
            self.pending_draw_decision_card = result.drew_card
            self.pending_draw_decision_choosing_color = False
            self._record_player_action_result(result, now_ms)
            return

        self._spawn_player_animation(0, result, "draw", screen, now_ms)
        self._record_player_action_result(result, now_ms)

    def _play_pending_draw_decision(self, screen: pygame.Surface, now_ms: int) -> None:
        card = self.pending_draw_decision_card
        if card is None:
            return
        if card.is_wild:
            self.pending_draw_decision_choosing_color = True
            self.last_message = "Choose a color for the drawn wild card."
            return

        result = self.game.play_pending_draw_decision(0, timestamp_ms=now_ms)
        if result.ok:
            self.pending_draw_decision_card = None
            self.pending_draw_decision_choosing_color = False
            self._spawn_player_animation(0, result, "draw", screen, now_ms)
        self._record_player_action_result(result, now_ms)

    def _keep_pending_draw_decision(self, screen: pygame.Surface, now_ms: int) -> None:
        result = self.game.keep_pending_draw_decision(0)
        if result.ok:
            self.pending_draw_decision_card = None
            self.pending_draw_decision_choosing_color = False
            self._spawn_player_animation(0, result, "draw", screen, now_ms)
            self._clamp_selected_index()
        self._record_player_action_result(result, now_ms)

    def _record_player_action_result(self, result, now_ms: int) -> None:
        self.last_message = result.message
        if result.ok and getattr(result, "uno_caught_player", None) is not None:
            self._play_uno_catch_sound()
        # Prevent same-frame AI actions from hiding turn transitions (e.g., after Reverse).
        if result.ok and self.game.winner is None and self.game.current_player != 0:
            self.next_ai_time = max(self.next_ai_time, now_ms + self.AI_TURN_DELAY_MS)

    def _load_uno_catch_sound(self) -> pygame.mixer.Sound | None:
        if not pygame.mixer.get_init():
            return None
        sound_path = asset_path("sfx", "woww.mp3")
        if not sound_path.exists():
            return None
        try:
            sound = pygame.mixer.Sound(str(sound_path))
            sound.set_volume(self.audio_settings.sfx_mix(0.75))
            return sound
        except pygame.error:
            return None

    def _play_uno_catch_sound(self) -> None:
        if self.uno_catch_sound is not None:
            self.uno_catch_sound.set_volume(self.audio_settings.sfx_mix(0.75))
            self.uno_catch_sound.play()

    def _build_ai_hand_transfer_action(self) -> PlayerAction | None:
        if self.game.pending_effect == RULE_ZERO_DIRECTION:
            return PlayerAction(
                player_id=self.game.current_player,
                action_type="choose_zero_direction",
                chosen_direction=self.ai_rng.choice([1, -1]),
                timestamp_ms=self._last_update_ms,
            )

        if self.game.pending_effect == RULE_SEVEN_TARGET:
            targets = [pid for pid in range(self.game.num_players) if pid != self.game.pending_effect_player]
            if not targets:
                return None
            return PlayerAction(
                player_id=self.game.current_player,
                action_type="choose_seven_target",
                target_player_id=self.ai_rng.choice(targets),
                timestamp_ms=self._last_update_ms,
            )

        return None

    def _begin_hand_transfer_animation(self, choice_action: PlayerAction, screen: pygame.Surface, now_ms: int) -> None:
        if self.hand_transfer_animation is not None:
            return

        screen_rect = screen.get_rect()
        center = get_discard_pile_rect(screen_rect).center
        center_point = (float(center[0]), float(center[1]))

        if choice_action.action_type == "choose_zero_direction":
            assert choice_action.chosen_direction in (PASS_CLOCKWISE, PASS_COUNTER_CLOCKWISE)
            affected_players = list(range(self.game.num_players))
        elif choice_action.action_type == "choose_seven_target":
            if choice_action.target_player_id is None:
                return
            affected_players = [self.game.pending_effect_player, choice_action.target_player_id]
        else:
            return

        cards: list[ActiveCard] = []
        target_owner_by_card_id: dict[int, int] = {}

        for source_player in affected_players:
            if source_player is None:
                continue
            source_hand = list(self.game.player_hands[source_player])
            source_rects = get_player_hand_card_rects(
                screen_rect,
                source_player,
                self.game.num_players,
                len(source_hand),
                source_hand,
                use_current_positions=(source_player == 0),
            )

            for index, card in enumerate(source_hand):
                if choice_action.action_type == "choose_zero_direction":
                    target_owner = (source_player + choice_action.chosen_direction) % self.game.num_players
                else:
                    target_owner = choice_action.target_player_id if source_player == self.game.pending_effect_player else self.game.pending_effect_player

                target_owner_by_card_id[id(card)] = target_owner
                self.hidden_hand_card_ids.add(id(card))

                source_center = source_rects[index].center
                source_rotation = get_player_card_rotation(source_player, self.game.num_players)

                cards.append(
                    ActiveCard(
                        card=card,
                        owner_id=source_player,
                        kind="transfer",
                        current_pos=(float(source_center[0]), float(source_center[1])),
                        target_pos=center_point,
                        current_rotation=source_rotation,
                        target_rotation=source_rotation,
                        current_scale=1.0,
                        target_scale=0.88,
                    )
                )

        self.hand_transfer_animation = HandTransferAnimation(
            choice_action=choice_action,
            phase=1,
            cards=cards,
            target_owner_by_card_id=target_owner_by_card_id,
        )
        self.visual_state = HAND_TRANSFER_ANIMATION
        self.game.is_animating = True

    def _update_hand_transfer_animation(self, screen: pygame.Surface, dt: float, now_ms: int) -> None:
        animation = self.hand_transfer_animation
        if animation is None:
            return

        if animation.phase == 1:
            all_finished = True
            for active_card in animation.cards:
                finished = active_card.update(dt)
                active_card.card.current_pos = active_card.current_pos
                active_card.card.current_rotation = active_card.current_rotation
                active_card.card.current_scale = active_card.current_scale
                if not finished:
                    all_finished = False

            if not all_finished:
                return

            resolution_result = self.game.submit_action(animation.choice_action)
            self.last_message = resolution_result.message
            if not resolution_result.ok:
                for active_card in animation.cards:
                    self.hidden_hand_card_ids.discard(id(active_card.card))
                self.hand_transfer_animation = None
                self.visual_state = ""
                return

            screen_rect = screen.get_rect()
            center = get_discard_pile_rect(screen_rect).center
            center_point = (float(center[0]), float(center[1]))

            for active_card in animation.cards:
                new_owner = animation.target_owner_by_card_id[id(active_card.card)]
                new_hand = self.game.player_hands[new_owner]
                hand_rects = get_player_hand_card_rects(
                    screen_rect,
                    new_owner,
                    self.game.num_players,
                    len(new_hand),
                    new_hand,
                    use_current_positions=False,
                )
                new_index = new_hand.index(active_card.card)
                target_rect = hand_rects[new_index]

                active_card.owner_id = new_owner
                active_card.current_pos = center_point
                active_card.target_pos = (float(target_rect.centerx), float(target_rect.centery))
                active_card.current_rotation = 0.0
                active_card.target_rotation = get_player_card_rotation(new_owner, self.game.num_players)
                active_card.current_scale = 0.88
                active_card.target_scale = 1.0

            animation.phase = 2
            self.next_ai_time = max(self.next_ai_time, now_ms + self.AI_TURN_DELAY_MS)
            return

        all_finished = True
        for active_card in animation.cards:
            finished = active_card.update(dt)
            active_card.card.current_pos = active_card.current_pos
            active_card.card.current_rotation = active_card.current_rotation
            active_card.card.current_scale = active_card.current_scale
            if not finished:
                all_finished = False

        if not all_finished:
            return

        for active_card in animation.cards:
            self.hidden_hand_card_ids.discard(id(active_card.card))

        self.hand_transfer_animation = None
        self.visual_state = ""
        self._hand_layout_initialized = False
        self.next_ai_time = max(self.next_ai_time, now_ms + self.AI_TURN_DELAY_MS)
        self.game.is_animating = False

    def _update_direction_arrow(self, dt: float) -> None:
        target_speed = self.DIRECTION_ARROW_BASE_SPEED * self.game.turn_direction

        if self.direction_arrow_speed * target_speed < 0 and abs(self.direction_arrow_speed) > 8.0:
            self.direction_arrow_speed = lerp(self.direction_arrow_speed, 0.0, smooth_factor(dt, self.DIRECTION_ARROW_DECEL))
        else:
            self.direction_arrow_speed = lerp(
                self.direction_arrow_speed,
                target_speed,
                smooth_factor(dt, self.DIRECTION_ARROW_ACCEL),
            )

        self.direction_arrow_angle = (self.direction_arrow_angle + self.direction_arrow_speed * dt) % 360.0

    def _spawn_player_animation(
        self,
        player_id: int,
        result,
        action_kind: str,
        screen: pygame.Surface,
        now_ms: int,
    ) -> None:
        if not result.ok:
            return

        screen_rect = screen.get_rect()

        if action_kind == "play":
            card = result.played_card
            if card is not None:
                self._spawn_active_card(
                    card=card,
                    owner_id=player_id,
                    kind="play",
                    start_pos=get_player_anchor_point(screen_rect, player_id, self.game.num_players),
                    target_pos=get_discard_pile_rect(screen_rect).center,
                    start_rotation=get_player_card_rotation(player_id, self.game.num_players),
                    target_rotation=get_player_card_rotation(player_id, self.game.num_players)
                    + self.ai_rng.uniform(-15.0, 15.0),
                )
            self._spawn_uno_penalty_animation(result, screen)
            return

        if action_kind == "draw":
            if result.played_card is not None and result.drew_card is not None:
                # The drawn card was auto-played; animate it from the draw pile to the discard pile.
                self._spawn_active_card(
                    card=result.played_card,
                    owner_id=player_id,
                    kind="play",
                    start_pos=get_draw_pile_rect(screen.get_width(), screen.get_height()).center,
                    target_pos=get_discard_pile_rect(screen_rect).center,
                    start_rotation=0.0,
                    target_rotation=self.ai_rng.uniform(-15.0, 15.0),
                )
                self._spawn_uno_penalty_animation(result, screen)
                return

            card = result.drew_card
            if card is not None:
                self.hidden_hand_card_ids.add(id(card))
                self._spawn_active_card(
                    card=card,
                    owner_id=player_id,
                    kind="draw",
                    start_pos=get_draw_pile_rect(screen.get_width(), screen.get_height()).center,
                    target_pos=get_player_anchor_point(screen_rect, player_id, self.game.num_players),
                    start_rotation=0.0,
                    target_rotation=get_player_card_rotation(player_id, self.game.num_players),
                    reveal_hand_card=True,
                )
            self._spawn_uno_penalty_animation(result, screen)

    def _spawn_ai_animation(self, player_id: int, outcome: AITurnOutcome, screen: pygame.Surface, now_ms: int) -> None:
        if outcome.action_type == "play" and outcome.card is not None:
            self._spawn_active_card(
                card=outcome.card,
                owner_id=player_id,
                kind="play",
                start_pos=get_player_anchor_point(screen.get_rect(), player_id, self.game.num_players),
                target_pos=get_discard_pile_rect(screen.get_rect()).center,
                start_rotation=get_player_card_rotation(player_id, self.game.num_players),
                target_rotation=get_player_card_rotation(player_id, self.game.num_players)
                + self.ai_rng.uniform(-15.0, 15.0),
            )
            if outcome.result is not None:
                self._spawn_uno_penalty_animation(outcome.result, screen)
            return

        if outcome.action_type == "draw" and outcome.card is not None:
            self._spawn_active_card(
                card=outcome.card,
                owner_id=player_id,
                kind="draw",
                start_pos=get_draw_pile_rect(screen.get_width(), screen.get_height()).center,
                target_pos=get_player_anchor_point(screen.get_rect(), player_id, self.game.num_players),
                start_rotation=0.0,
                target_rotation=get_player_card_rotation(player_id, self.game.num_players),
            )
            if outcome.result is not None:
                self._spawn_uno_penalty_animation(outcome.result, screen)
            return

        if outcome.action_type == "draw_played" and outcome.card is not None:
            self._spawn_active_card(
                card=outcome.card,
                owner_id=player_id,
                kind="play",
                start_pos=get_draw_pile_rect(screen.get_width(), screen.get_height()).center,
                target_pos=get_discard_pile_rect(screen.get_rect()).center,
                start_rotation=0.0,
                target_rotation=self.ai_rng.uniform(-15.0, 15.0),
            )
            if outcome.result is not None:
                self._spawn_uno_penalty_animation(outcome.result, screen)

    def _spawn_uno_penalty_animation(self, result, screen: pygame.Surface) -> None:
        player_id = getattr(result, "uno_caught_player", None)
        penalty_cards = getattr(result, "uno_penalty_cards", None) or []
        if player_id is None or not penalty_cards:
            return

        screen_rect = screen.get_rect()
        draw_center = get_draw_pile_rect(screen.get_width(), screen.get_height()).center
        target_center = get_player_anchor_point(screen_rect, player_id, self.game.num_players)

        for offset, card in enumerate(penalty_cards):
            if player_id == 0:
                self.hidden_hand_card_ids.add(id(card))
            stagger = float((offset - 0.5) * 14)
            self._spawn_active_card(
                card=card,
                owner_id=player_id,
                kind="draw",
                start_pos=(float(draw_center[0] + stagger), float(draw_center[1] - stagger)),
                target_pos=(float(target_center[0] + stagger), float(target_center[1])),
                start_rotation=0.0,
                target_rotation=get_player_card_rotation(player_id, self.game.num_players),
                reveal_hand_card=(player_id == 0),
            )

    def _spawn_active_card(
        self,
        card,
        owner_id: int,
        kind: str,
        start_pos: tuple[float, float],
        target_pos: tuple[float, float],
        start_rotation: float,
        target_rotation: float,
        reveal_hand_card: bool = False,
    ) -> None:
        card.current_pos = start_pos
        card.target_pos = target_pos
        card.current_rotation = start_rotation
        card.target_rotation = target_rotation
        card.current_scale = 1.0
        card.target_scale = 1.0
        duration = 0.24 if kind == "play" else 0.32
        if kind == "draw" and owner_id != 0:
            duration = 0.28
        self.active_cards.append(
            ActiveCard(
                card=card,
                owner_id=owner_id,
                kind=kind,
                current_pos=start_pos,
                target_pos=target_pos,
                current_rotation=start_rotation,
                target_rotation=target_rotation,
                current_scale=1.0,
                target_scale=1.0,
                reveal_hand_card=reveal_hand_card,
                duration=duration,
            )
        )

    def _update_active_cards(self, dt: float) -> None:
        still_active: list[ActiveCard] = []
        for active_card in self.active_cards:
            finished = active_card.update(dt)
            active_card.card.current_pos = active_card.current_pos
            active_card.card.target_pos = active_card.target_pos
            active_card.card.current_rotation = active_card.current_rotation
            active_card.card.target_rotation = active_card.target_rotation
            active_card.card.current_scale = active_card.current_scale
            active_card.card.target_scale = active_card.target_scale

            if finished:
                active_card.card.current_pos = active_card.target_pos
                active_card.card.current_rotation = active_card.target_rotation
                active_card.card.current_scale = active_card.target_scale
                if active_card.kind == "play":
                    self.display_top_card = active_card.card
                    if active_card.card.kind == ACTION_WILD_DRAW_FOUR:
                        self._trigger_screen_shake()
                if active_card.reveal_hand_card:
                    self.hidden_hand_card_ids.discard(id(active_card.card))
                continue

            still_active.append(active_card)

        self.active_cards = still_active
        
        if not self.active_cards and self.game.is_animating:
            self.game.is_animating = False

    def _draw_active_cards(self, screen: pygame.Surface) -> None:
        for active_card in self.active_cards:
            card_center = (int(active_card.current_pos[0]), int(active_card.current_pos[1]))
            shadow = pygame.Surface((66, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 95), shadow.get_rect())
            shadow_rect = shadow.get_rect(center=(card_center[0], card_center[1] + 10))
            screen.blit(shadow, shadow_rect)

            if active_card.kind == "draw" and active_card.owner_id == 0:
                showing_front = active_card.progress >= 0.5
                base_surface = (
                    self.atlas.get_card_surface(active_card.card, 88, 130)
                    if showing_front
                    else self.atlas.get_back_surface(88, 130)
                )
                flip_x = max(0.08, abs(0.5 - active_card.progress) * 2.0)
                flip_width = max(8, int(88 * flip_x))
                card_img = pygame.transform.smoothscale(base_surface, (flip_width, 130))
            elif active_card.kind == "draw" and active_card.owner_id != 0:
                card_img = self.atlas.get_back_surface(88, 130)
            else:
                card_img = self.atlas.get_card_surface(active_card.card, 88, 130)
            card_img = transform_card_surface(card_img, active_card.current_rotation, active_card.current_scale)
            rect = card_img.get_rect(center=card_center)
            screen.blit(card_img, rect)

    def _draw_hand_transfer_cards(self, screen: pygame.Surface) -> None:
        if self.hand_transfer_animation is None:
            return

        for active_card in self.hand_transfer_animation.cards:
            shadow = pygame.Surface((66, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), shadow.get_rect())
            shadow_rect = shadow.get_rect(
                center=(int(active_card.current_pos[0]), int(active_card.current_pos[1] + 10))
            )
            screen.blit(shadow, shadow_rect)
            card_img = self.atlas.get_back_surface(88, 130)
            card_img = transform_card_surface(card_img, active_card.current_rotation, active_card.current_scale)
            rect = card_img.get_rect(center=(int(active_card.current_pos[0]), int(active_card.current_pos[1])))
            screen.blit(card_img, rect)

    def _update_player_hand_animation(self, screen: pygame.Surface, dt: float) -> None:
        hand = self.game.player_hands[0]
        if not hand:
            self._hand_layout_initialized = True
            return

        speed = 14.0
        width = screen.get_width()
        height = screen.get_height()

        for i, card in enumerate(hand):
            if id(card) in self.hidden_hand_card_ids:
                continue
            target_rect = card_rect_for_hand(
                i,
                len(hand),
                width,
                height,
                hovered=(i == self.hovered_index),
            )
            card.target_pos = (float(target_rect.x), float(target_rect.y))
            target_rotation = get_player_hand_rotation(i, len(hand))
            if i == self.hovered_index:
                target_rotation *= 0.78
            card.target_rotation = target_rotation

            if not self._hand_layout_initialized:
                card.current_pos = card.target_pos
                card.current_rotation = target_rotation
            else:
                factor = smooth_factor(dt, speed)
                card.current_pos = lerp_point(card.current_pos, card.target_pos, factor)
                card.current_rotation = lerp(card.current_rotation, card.target_rotation, smooth_factor(dt, speed * 0.75))

            if i == self.hovered_index:
                card.target_scale = 1.04
            else:
                card.target_scale = 1.0

            card.current_scale = card.current_scale + (card.target_scale - card.current_scale) * smooth_factor(dt, 12.0)

        self._hand_layout_initialized = True

    def _clamp_selected_index(self) -> None:
        hand = self.game.player_hands[0]
        if hand:
            self.selected_index = min(self.selected_index, len(hand) - 1)
        else:
            self.selected_index = 0

    def _hand_card_rect(self, card) -> pygame.Rect:
        return get_card_rect_from_pos(card)
