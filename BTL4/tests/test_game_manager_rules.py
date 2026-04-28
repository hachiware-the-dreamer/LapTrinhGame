import unittest

from scripts.cards import ACTION_DRAW_TWO, ACTION_REVERSE, ACTION_SKIP, ACTION_WILD_DRAW_FOUR, Card
from scripts.game_manager import (
    GameSettings,
    PlayerAction,
    RULE_REACTION,
    RULE_SEVEN_TARGET,
    RULE_ZERO_DIRECTION,
    UnoGameManager,
)


def number(color: str, value: int) -> Card:
    return Card(color=color, kind="number", number=value)


def action(color: str, kind: str) -> Card:
    return Card(color=color, kind=kind)


class UnoRuleSettingsTest(unittest.TestCase):
    def make_game(self, settings: GameSettings) -> UnoGameManager:
        game = UnoGameManager(settings=settings, seed=1)
        game.draw_pile = [number("blue", value) for value in range(9)]
        game.discard_pile = [number("red", 5)]
        game.current_color = "red"
        game.current_player = 0
        game.turn_direction = 1
        game.pending_effect = None
        game.pending_effect_player = None
        game.pending_draw_penalty_count = 0
        game.pending_draw_penalty_kind = None
        game.pending_draw_decision_player = None
        game.pending_draw_decision_card = None
        game.winner = None
        return game

    def test_disabled_rule_0_plays_as_normal_number_card(self) -> None:
        game = self.make_game(GameSettings(num_players=3, rule_0_enabled=False))
        game.player_hands = [
            [number("red", 0), number("yellow", 1), number("green", 2)],
            [number("red", 2)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0))

        self.assertTrue(result.ok)
        self.assertIsNone(game.pending_effect)
        self.assertEqual(game.current_player, 1)

    def test_disabled_rule_7_plays_as_normal_number_card(self) -> None:
        game = self.make_game(GameSettings(num_players=3, rule_7_enabled=False))
        game.player_hands = [
            [number("red", 7), number("yellow", 1), number("green", 2)],
            [number("red", 2)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0))

        self.assertTrue(result.ok)
        self.assertIsNone(game.pending_effect)
        self.assertEqual(game.current_player, 1)

    def test_disabled_rule_8_plays_as_normal_number_card(self) -> None:
        game = self.make_game(GameSettings(num_players=3, rule_8_enabled=False))
        game.player_hands = [
            [number("red", 8), number("yellow", 1), number("green", 2)],
            [number("red", 2)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0, timestamp_ms=100))

        self.assertTrue(result.ok)
        self.assertIsNone(game.pending_effect)
        self.assertIsNone(game.pending_reaction_due_ms)
        self.assertEqual(game.current_player, 1)

    def test_enabled_rules_still_create_pending_effects(self) -> None:
        cases = [
            (number("red", 0), RULE_ZERO_DIRECTION),
            (number("red", 7), RULE_SEVEN_TARGET),
            (number("red", 8), RULE_REACTION),
        ]
        for card, expected_effect in cases:
            with self.subTest(card=card.number):
                game = self.make_game(GameSettings(num_players=3))
                game.player_hands = [
                    [card, number("yellow", 1), number("green", 2)],
                    [number("red", 2)],
                    [number("blue", 3)],
                ]

                result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0, timestamp_ms=200))

                self.assertTrue(result.ok)
                self.assertEqual(game.pending_effect, expected_effect)
                self.assertEqual(game.pending_effect_player, 0)

    def test_two_player_reverse_skip_mode_gives_same_player_next_turn(self) -> None:
        game = self.make_game(GameSettings(num_players=2, two_player_reverse_behavior="skip"))
        game.player_hands = [
            [action("red", ACTION_REVERSE), number("yellow", 1), number("green", 2)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0))

        self.assertTrue(result.ok)
        self.assertEqual(game.current_player, 0)
        self.assertEqual(game.turn_direction, 1)

    def test_two_player_reverse_mode_flips_direction_and_passes_turn(self) -> None:
        game = self.make_game(GameSettings(num_players=2, two_player_reverse_behavior="reverse"))
        game.player_hands = [
            [action("red", ACTION_REVERSE), number("yellow", 1), number("green", 2)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0))

        self.assertTrue(result.ok)
        self.assertEqual(game.current_player, 1)
        self.assertEqual(game.turn_direction, -1)

    def test_action_card_cannot_be_winning_final_card(self) -> None:
        game = self.make_game(GameSettings(num_players=2))
        game.player_hands = [
            [action("red", ACTION_SKIP)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0))

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "You cannot win with that action card.")
        self.assertIsNone(game.winner)

    def test_draw_two_stack_allows_wild_draw_four(self) -> None:
        game = self.make_game(GameSettings(num_players=2))
        game.discard_pile = [action("red", ACTION_DRAW_TWO)]
        game.current_color = "red"
        game.pending_draw_penalty_count = 2
        game.pending_draw_penalty_kind = ACTION_DRAW_TWO
        game.player_hands = [
            [Card(color=None, kind=ACTION_WILD_DRAW_FOUR), number("yellow", 1)],
            [number("blue", 3)],
        ]

        result = game.submit_action(
            PlayerAction(player_id=0, action_type="play", card_index=0, chosen_color="blue")
        )

        self.assertTrue(result.ok)
        self.assertEqual(game.pending_draw_penalty_count, 6)
        self.assertEqual(game.pending_draw_penalty_kind, ACTION_WILD_DRAW_FOUR)

    def test_wild_draw_four_stack_rejects_draw_two(self) -> None:
        game = self.make_game(GameSettings(num_players=2))
        game.discard_pile = [Card(color=None, kind=ACTION_WILD_DRAW_FOUR, chosen_color="red")]
        game.current_color = "red"
        game.pending_draw_penalty_count = 4
        game.pending_draw_penalty_kind = ACTION_WILD_DRAW_FOUR
        game.player_hands = [
            [action("red", ACTION_DRAW_TWO), number("yellow", 1)],
            [number("blue", 3)],
        ]

        result = game.submit_action(PlayerAction(player_id=0, action_type="play", card_index=0))

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "Illegal card for current top card/color.")
        self.assertEqual(game.pending_draw_penalty_count, 4)


if __name__ == "__main__":
    unittest.main()
