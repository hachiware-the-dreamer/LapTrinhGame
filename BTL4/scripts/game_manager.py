import random
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from scripts.cards import (
    ACTION_DRAW_TWO,
    ACTION_REVERSE,
    ACTION_SKIP,
    ACTION_WILD_DRAW_FOUR,
    COLORS,
    Card,
)
from scripts.deck import build_standard_uno_deck

RULE_ZERO_DIRECTION = "zero_direction"
RULE_SEVEN_TARGET = "seven_target"
RULE_REACTION = "reaction"

PASS_CLOCKWISE = 1
PASS_COUNTER_CLOCKWISE = -1


@dataclass
class PlayerAction:
    player_id: int
    action_type: str  # "play" or "draw"
    card_index: Optional[int] = None
    chosen_color: Optional[str] = None
    chosen_direction: Optional[int] = None
    target_player_id: Optional[int] = None
    timestamp_ms: Optional[int] = None


@dataclass
class ActionResult:
    ok: bool
    message: str
    played_card: Optional[Card] = None
    drew_card: Optional[Card] = None


class UnoGameManager:
    """Host-authoritative game state manager decoupled from input and rendering."""

    REACTION_WINDOW_MS = 3000

    def __init__(self, num_players: int, seed: Optional[int] = None):
        if not 2 <= num_players <= 4:
            raise ValueError("UNO supports 2 to 4 players in this module.")

        self.rng = random.Random(seed)
        self.num_players = num_players

        self.draw_pile: List[Card] = []
        self.discard_pile: List[Card] = []
        self.player_hands: List[List[Card]] = [[] for _ in range(num_players)]

        self.current_player = 0
        self.turn_direction = 1
        self.hand_pass_direction = PASS_CLOCKWISE
        self.current_color: Optional[str] = None
        self.winner: Optional[int] = None

        self.pending_effect: Optional[str] = None
        self.pending_effect_player: Optional[int] = None
        self.pending_reaction_started_at_ms: Optional[int] = None
        self.pending_reaction_due_ms: Optional[int] = None
        self.pending_reaction_players: Set[int] = set()
        self.pending_reaction_times: List[Tuple[int, int]] = []

        self.pending_draw_penalty_count = 0
        self.pending_draw_penalty_kind: Optional[str] = None

        self.is_animating = False

        self.start_game()

    @property
    def top_discard(self) -> Card:
        return self.discard_pile[-1]

    def start_game(self) -> None:
        self.draw_pile = build_standard_uno_deck()
        self.rng.shuffle(self.draw_pile)
        self.discard_pile.clear()

        for hand in self.player_hands:
            hand.clear()

        for _ in range(7):
            for player in range(self.num_players):
                self.player_hands[player].append(self.draw_from_pile())

        while True:
            card = self.draw_from_pile()
            if card.is_wild:
                self.draw_pile.insert(0, card)
                self.rng.shuffle(self.draw_pile)
                continue
            self.discard_pile.append(card)
            self.current_color = card.color
            break

        self.current_player = 0
        self.turn_direction = 1
        self.hand_pass_direction = PASS_CLOCKWISE
        self.winner = None
        self.pending_effect = None
        self.pending_effect_player = None
        self.pending_reaction_started_at_ms = None
        self.pending_reaction_due_ms = None
        self.pending_reaction_players.clear()
        self.pending_reaction_times.clear()
        self.pending_draw_penalty_count = 0
        self.pending_draw_penalty_kind = None

    def draw_from_pile(self) -> Card:
        self.rebuild_draw_pile_if_needed()
        return self.draw_pile.pop()

    def tick(self, now_ms: int) -> Optional[str]:
        if self.pending_effect == RULE_REACTION and self.pending_reaction_due_ms is not None and now_ms >= self.pending_reaction_due_ms:
            self._resolve_reaction_event()
            return "Rule of 8 resolved."

        return None

    def rebuild_draw_pile_if_needed(self) -> None:
        if self.draw_pile:
            return

        if len(self.discard_pile) <= 1:
            raise RuntimeError("No cards available to rebuild draw pile.")

        top = self.discard_pile[-1]
        to_shuffle = self.discard_pile[:-1]
        self.discard_pile = [top]
        self.rng.shuffle(to_shuffle)
        self.draw_pile = to_shuffle

    def get_legal_card_indices(self, player_id: int) -> List[int]:
        if self.pending_effect is not None:
            return []

        legal = []
        hand = self.player_hands[player_id]
        for i, card in enumerate(hand):
            if self.is_legal_play(card):
                legal.append(i)
        return legal

    def is_legal_play(self, candidate: Card) -> bool:
        if self.pending_effect is not None:
            return False

        top = self.top_discard

        if self.pending_draw_penalty_count > 0:
            if candidate.kind == ACTION_DRAW_TWO:
                return self.pending_draw_penalty_kind in (ACTION_DRAW_TWO, None)
            if candidate.kind == ACTION_WILD_DRAW_FOUR:
                return True
            return False

        if candidate.is_wild:
            return True
        if candidate.color == self.current_color:
            return True
        if candidate.kind == "number" and top.kind == "number":
            return candidate.number == top.number
        if candidate.kind != "number" and top.kind != "number":
            return candidate.kind == top.kind

        return False

    def submit_action(self, action: PlayerAction) -> ActionResult:
        if self.winner is not None:
            return ActionResult(False, "Game is already over.")

        if self.pending_effect == RULE_REACTION:
            if action.action_type == "react":
                return self._handle_reaction(action)
            return ActionResult(False, "Reaction window is active.")

        if self.pending_effect == RULE_ZERO_DIRECTION:
            if action.action_type == "choose_zero_direction":
                return self._resolve_zero_direction(action)
            return ActionResult(False, "Choose the hand pass direction first.")

        if self.pending_effect == RULE_SEVEN_TARGET:
            if action.action_type == "choose_seven_target":
                return self._resolve_seven_target(action)
            return ActionResult(False, "Choose a swap target first.")

        if action.player_id != self.current_player:
            return ActionResult(False, "Not this player's turn.")

        if action.action_type == "play":
            return self._handle_play(action)
        if action.action_type == "draw":
            return self._handle_draw(action.player_id)

        return ActionResult(False, "Unknown action.")

    def _handle_play(self, action: PlayerAction) -> ActionResult:
        self.is_animating = True
        hand = self.player_hands[action.player_id]
        if action.card_index is None or not (0 <= action.card_index < len(hand)):
            return ActionResult(False, "Invalid card index.")

        card = hand[action.card_index]
        if not self.is_legal_play(card):
            return ActionResult(False, "Illegal card for current top card/color.")

        if len(hand) == 1 and self._is_forbidden_last_card(card):
            return ActionResult(False, "You cannot win with that action card.")

        chosen_color = action.chosen_color
        if card.is_wild:
            if chosen_color not in COLORS:
                return ActionResult(False, "Wild cards require a chosen color.")
        else:
            chosen_color = card.color

        hand.pop(action.card_index)
        self.discard_pile.append(card)
        self.current_color = chosen_color if chosen_color is not None else card.color

        if card.kind == "number" and card.number == 0:
            self.pending_effect = RULE_ZERO_DIRECTION
            self.pending_effect_player = action.player_id
            return ActionResult(True, "Rule of 0: choose hand pass direction.", played_card=card)

        if card.kind == "number" and card.number == 7:
            self.pending_effect = RULE_SEVEN_TARGET
            self.pending_effect_player = action.player_id
            return ActionResult(True, "Rule of 7: choose a target player to swap hands with.", played_card=card)

        if card.kind == "number" and card.number == 8:
            self.pending_effect = RULE_REACTION
            self.pending_effect_player = action.player_id
            started_at = action.timestamp_ms or 0
            self.pending_reaction_started_at_ms = started_at
            self.pending_reaction_due_ms = started_at + self.REACTION_WINDOW_MS
            self.pending_reaction_players = set()
            self.pending_reaction_times = []
            return ActionResult(True, "Rule of 8: reaction event started.", played_card=card)

        if len(hand) == 0:
            self.winner = action.player_id
            return ActionResult(True, f"Player {action.player_id + 1} wins!", played_card=card)

        self._apply_played_card_effect(card)
        
        # Debug logging
        direction_str = "Clockwise" if self.turn_direction == 1 else "Counter-Clockwise"
        next_player = self._next_player_index(self.turn_direction)
        print(f"[TURN DEBUG] Player {action.player_id} played {card.short_label}. Current Direction: {direction_str}. Next player should be: Player {next_player}.")
        
        return ActionResult(True, "Card played.", played_card=card)

    def _handle_draw(self, player_id: int) -> ActionResult:
        self.is_animating = True
        legal_before_draw = self.get_legal_card_indices(player_id)
        if legal_before_draw:
            return ActionResult(False, "You must stack a draw card if you can.")

        if self.pending_draw_penalty_count > 0:
            return self._draw_pending_penalty(player_id)

        drawn = self.draw_from_pile()
        self.player_hands[player_id].append(drawn)

        if self.is_legal_play(drawn):
            self.player_hands[player_id].pop()
            self.discard_pile.append(drawn)

            self.current_color = drawn.color if not drawn.is_wild else self.choose_color_for_player(player_id)

            if len(self.player_hands[player_id]) == 1 and self._is_forbidden_last_card(drawn):
                return ActionResult(True, "Drew an action card but cannot win with it; it stays in hand.", drew_card=drawn)

            if len(self.player_hands[player_id]) == 0:
                self.winner = player_id
                return ActionResult(True, f"Player {player_id + 1} wins!", played_card=drawn, drew_card=drawn)

            self._apply_played_card_effect(drawn)
            return ActionResult(True, "Drew and auto-played a card.", played_card=drawn, drew_card=drawn)

        self._advance_turn(1)
        return ActionResult(True, "Drew one card and ended turn.", drew_card=drawn)

    def _apply_played_card_effect(self, card: Card) -> None:
        if card.kind == ACTION_SKIP:
            self._advance_turn(2)
            return

        if card.kind == ACTION_REVERSE:
            self.turn_direction *= -1
            self._advance_turn(1)
            return

        if card.kind == ACTION_DRAW_TWO:
            self._start_or_stack_draw_penalty(ACTION_DRAW_TWO)
            self._advance_turn(1)
            return

        if card.kind == ACTION_WILD_DRAW_FOUR:
            self._start_or_stack_draw_penalty(ACTION_WILD_DRAW_FOUR)
            self._advance_turn(1)
            return

        self._advance_turn(1)

    def _start_or_stack_draw_penalty(self, kind: str) -> None:
        self.pending_draw_penalty_count += 2 if kind == ACTION_DRAW_TWO else 4
        if kind == ACTION_WILD_DRAW_FOUR or self.pending_draw_penalty_kind is None:
            self.pending_draw_penalty_kind = kind

    def _draw_pending_penalty(self, player_id: int) -> ActionResult:
        for _ in range(self.pending_draw_penalty_count):
            self.player_hands[player_id].append(self.draw_from_pile())

        drawn_count = self.pending_draw_penalty_count
        self.pending_draw_penalty_count = 0
        self.pending_draw_penalty_kind = None
        self._advance_turn(1)
        return ActionResult(True, f"Player {player_id + 1} drew {drawn_count} cards and lost the turn.")

    def _resolve_zero_direction(self, action: PlayerAction) -> ActionResult:
        effect_player = self.pending_effect_player
        if action.player_id != self.pending_effect_player:
            return ActionResult(False, "Only the player who played the 0 chooses the direction.")

        if action.chosen_direction not in (PASS_CLOCKWISE, PASS_COUNTER_CLOCKWISE):
            return ActionResult(False, "Choose clockwise or counter-clockwise.")

        self.hand_pass_direction = action.chosen_direction
        self._pass_all_hands(self.hand_pass_direction)
        self.pending_effect = None
        self.pending_effect_player = None

        if effect_player is not None and len(self.player_hands[effect_player]) == 0:
            self.winner = effect_player

        self._advance_turn(1)
        return ActionResult(True, "Rule of 0 resolved: hands were passed.")

    def _resolve_seven_target(self, action: PlayerAction) -> ActionResult:
        effect_player = self.pending_effect_player
        if action.player_id != self.pending_effect_player:
            return ActionResult(False, "Only the player who played the 7 chooses the target.")

        if action.target_player_id is None or not (0 <= action.target_player_id < self.num_players):
            return ActionResult(False, "Choose a valid target player.")

        if action.target_player_id == action.player_id:
            return ActionResult(False, "You must choose another player.")

        self._swap_hands(action.player_id, action.target_player_id)
        self.pending_effect = None
        self.pending_effect_player = None

        if effect_player is not None and len(self.player_hands[effect_player]) == 0:
            self.winner = effect_player

        self._advance_turn(1)
        return ActionResult(True, f"Rule of 7 resolved: Player {action.player_id + 1} swapped hands with Player {action.target_player_id + 1}.")

    def _handle_reaction(self, action: PlayerAction) -> ActionResult:
        if action.player_id in self.pending_reaction_players:
            return ActionResult(False, "That player already reacted.")

        self.pending_reaction_players.add(action.player_id)
        self.pending_reaction_times.append((action.player_id, action.timestamp_ms or 0))
        return ActionResult(True, f"Player {action.player_id + 1} reacted.")

    def _resolve_reaction_event(self) -> None:
        effect_player = self.pending_effect_player
        responders = {player_id for player_id, _ in self.pending_reaction_times}
        if len(responders) == self.num_players:
            punish_targets = [self.pending_reaction_times[-1][0]]
        else:
            punish_targets = [player_id for player_id in range(self.num_players) if player_id not in responders]

        for target in punish_targets:
            for _ in range(2):
                self.player_hands[target].append(self.draw_from_pile())

        self.pending_effect = None
        self.pending_effect_player = None
        self.pending_reaction_started_at_ms = None
        self.pending_reaction_due_ms = None
        self.pending_reaction_players.clear()
        self.pending_reaction_times.clear()

        if effect_player is not None and len(self.player_hands[effect_player]) == 0:
            self.winner = effect_player

        self._advance_turn(1)

    def _next_player_index(self, steps: int) -> int:
        return (self.current_player + steps * self.turn_direction) % self.num_players

    def _advance_turn(self, steps: int) -> None:
        self.current_player = self._next_player_index(steps)

    def _pass_all_hands(self, direction: int) -> None:
        new_hands: List[List[Card]] = [[] for _ in range(self.num_players)]
        for player_id, hand in enumerate(self.player_hands):
            target = (player_id + direction) % self.num_players
            new_hands[target] = hand
        self.player_hands = new_hands

    def _swap_hands(self, first_player: int, second_player: int) -> None:
        self.player_hands[first_player], self.player_hands[second_player] = (
            self.player_hands[second_player],
            self.player_hands[first_player],
        )

    def _is_forbidden_last_card(self, card: Card) -> bool:
        return card.kind in (ACTION_SKIP, ACTION_REVERSE, ACTION_DRAW_TWO, ACTION_WILD_DRAW_FOUR)

    def choose_color_for_player(self, player_id: int) -> str:
        color_counts = {c: 0 for c in COLORS}
        for card in self.player_hands[player_id]:
            if card.color in color_counts:
                color_counts[card.color] += 1
        return max(color_counts, key=color_counts.get)

    def can_stack_draw_penalty(self, card: Card) -> bool:
        if self.pending_draw_penalty_count <= 0:
            return False
        if self.pending_draw_penalty_kind == ACTION_WILD_DRAW_FOUR:
            return card.kind == ACTION_WILD_DRAW_FOUR
        return card.kind in (ACTION_DRAW_TWO, ACTION_WILD_DRAW_FOUR)

    def is_waiting_for_input(self) -> bool:
        return self.pending_effect in {RULE_ZERO_DIRECTION, RULE_SEVEN_TARGET, RULE_REACTION}

    def get_reaction_remaining_ms(self, now_ms: int) -> int:
        if self.pending_effect != RULE_REACTION or self.pending_reaction_due_ms is None:
            return 0
        return max(0, self.pending_reaction_due_ms - now_ms)

    def get_active_effect_label(self, now_ms: int) -> Optional[str]:
        if self.pending_effect == RULE_ZERO_DIRECTION:
            return "Rule of 0: choose hand pass direction"
        if self.pending_effect == RULE_SEVEN_TARGET:
            return "Rule of 7: choose a target player to swap hands with"
        if self.pending_effect == RULE_REACTION:
            return f"Rule of 8: reaction window {self.get_reaction_remaining_ms(now_ms) / 1000:.1f}s"
        if self.pending_draw_penalty_count > 0:
            kind = "+4" if self.pending_draw_penalty_kind == ACTION_WILD_DRAW_FOUR else "+2"
            return f"Draw penalty pending: {self.pending_draw_penalty_count} cards ({kind} stack)"
        return None
