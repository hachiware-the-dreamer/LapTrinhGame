import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pygame

from scripts.animation import ActiveCard, lerp, lerp_point, smooth_factor, transform_card_surface
from scripts.ai import AITurnOutcome, perform_simple_ai_turn
from scripts.cards import Card
from scripts.game_manager import (
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
    get_card_rect_from_pos,
    get_draw_decision_button_rects,
    get_draw_pile_rect,
    get_end_screen_button_rects,
    get_hovered_hand_index,
    get_discard_pile_rect,
    get_player_anchor_point,
    get_player_card_rotation,
    get_player_hand_card_rects,
    get_reaction_button_rect,
    get_rule_seven_target_rects,
    get_rule_zero_choice_rects,
    get_title_screen_button_rects,
    get_uno_button_rect,
    get_wild_color_at_pos,
    render_end_screen,
    render_title_screen,
    render_ui,
)

STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_END = "end"
HAND_TRANSFER_ANIMATION = "Hand_Transfer_Animation"


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

    def __init__(self, atlas: CardSpriteAtlas) -> None:
        self.atlas = atlas

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
                            game = UnoGameManager(num_players=4)
                            return ScreenResult(
                                next_screen=PlayingScreen(
                                    atlas=self.atlas,
                                    game=game,
                                    last_message="Player 1 starts.",
                                    next_ai_time=now_ms + PlayingScreen.AI_TURN_DELAY_MS,
                                )
                            )
                        break

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_title_screen(screen)


class EndScreen(BaseScreen):
    state_name = STATE_END

    def __init__(self, atlas: CardSpriteAtlas, game: UnoGameManager) -> None:
        self.atlas = atlas
        self.game = game

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
                            return ScreenResult(next_screen=TitleScreen(self.atlas))
                        break

        return ScreenResult()

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_end_screen(screen, self.game)


class PlayingScreen(BaseScreen):
    state_name = STATE_PLAYING
    AI_TURN_DELAY_MS = 1000
    DIRECTION_ARROW_BASE_SPEED = 90.0
    DIRECTION_ARROW_ACCEL = 4.5
    DIRECTION_ARROW_DECEL = 2.5

    def __init__(
        self,
        atlas: CardSpriteAtlas,
        game: UnoGameManager,
        last_message: str = "",
        selected_index: int = 0,
        pending_wild_card_index: Optional[int] = None,
        next_ai_time: int = 0,
    ) -> None:
        self.atlas = atlas
        self.game = game
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

    @property
    def wants_bgm(self) -> bool:
        return True

    def handle_events(
        self,
        events: list[pygame.event.Event],
        screen: pygame.Surface,
        now_ms: int,
    ) -> ScreenResult:
        if self.hand_transfer_animation is not None:
            for event in events:
                if event.type == pygame.QUIT:
                    return ScreenResult(running=False)
            return ScreenResult()

        for event in events:
            if event.type == pygame.QUIT:
                return ScreenResult(running=False)

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

        self._schedule_reaction_ai(now_ms)
        self._submit_ai_reactions(now_ms)
        self._update_direction_arrow(dt)
        self._update_active_cards(dt)

        if self.hand_transfer_animation is not None:
            self.visual_state = HAND_TRANSFER_ANIMATION
            self._update_hand_transfer_animation(screen, dt, now_ms)
            if self.game.winner is not None and self.hand_transfer_animation is None:
                return EndScreen(self.atlas, self.game)
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
                if ai_turn.result is not None and ai_turn.result.uno_caught_player is not None:
                    self._play_uno_catch_sound()
                self._spawn_ai_animation(previous_player, ai_turn, screen, now_ms)
                ai_delay = self.ai_rng.randint(1000, 1500)
                self.next_ai_time = now_ms + ai_delay

        if self.game.winner is not None:
            return EndScreen(self.atlas, self.game)

        return None

    def draw(self, screen: pygame.Surface, now_ms: int) -> None:
        render_ui(
            screen,
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
        self._draw_active_cards(screen)
        self._draw_hand_transfer_cards(screen)

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
        if result.ok and result.uno_caught_player is not None:
            self._play_uno_catch_sound()
        # Prevent same-frame AI actions from hiding turn transitions (e.g., after Reverse).
        if result.ok and self.game.winner is None and self.game.current_player != 0:
            self.next_ai_time = max(self.next_ai_time, now_ms + self.AI_TURN_DELAY_MS)

    def _load_uno_catch_sound(self) -> pygame.mixer.Sound | None:
        if not pygame.mixer.get_init():
            return None
        try:
            sound = pygame.mixer.Sound(str(Path("assets") / "sfx" / "woww.mp3"))
            sound.set_volume(0.75)
            return sound
        except pygame.error:
            return None

    def _play_uno_catch_sound(self) -> None:
        if self.uno_catch_sound is not None:
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
                    + self.ai_rng.uniform(-12.0, 12.0),
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
                    target_rotation=self.ai_rng.uniform(-12.0, 12.0),
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
                + self.ai_rng.uniform(-12.0, 12.0),
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
                target_rotation=self.ai_rng.uniform(-12.0, 12.0),
            )
            if outcome.result is not None:
                self._spawn_uno_penalty_animation(outcome.result, screen)

    def _spawn_uno_penalty_animation(self, result, screen: pygame.Surface) -> None:
        player_id = result.uno_caught_player
        if player_id is None or not result.uno_penalty_cards:
            return

        screen_rect = screen.get_rect()
        draw_center = get_draw_pile_rect(screen.get_width(), screen.get_height()).center
        target_center = get_player_anchor_point(screen_rect, player_id, self.game.num_players)

        for offset, card in enumerate(result.uno_penalty_cards):
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
                if active_card.reveal_hand_card:
                    self.hidden_hand_card_ids.discard(id(active_card.card))
                continue

            still_active.append(active_card)

        self.active_cards = still_active
        
        if not self.active_cards and self.game.is_animating:
            self.game.is_animating = False

    def _draw_active_cards(self, screen: pygame.Surface) -> None:
        for active_card in self.active_cards:
            card_img = self.atlas.get_card_surface(active_card.card, 88, 130)
            card_img = transform_card_surface(card_img, active_card.current_rotation, active_card.current_scale)
            rect = card_img.get_rect(center=(int(active_card.current_pos[0]), int(active_card.current_pos[1])))
            screen.blit(card_img, rect)

    def _draw_hand_transfer_cards(self, screen: pygame.Surface) -> None:
        if self.hand_transfer_animation is None:
            return

        for active_card in self.hand_transfer_animation.cards:
            card_img = self.atlas.get_card_surface(active_card.card, 88, 130)
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

            if not self._hand_layout_initialized:
                card.current_pos = card.target_pos
            else:
                factor = smooth_factor(dt, speed)
                card.current_pos = lerp_point(card.current_pos, card.target_pos, factor)

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
