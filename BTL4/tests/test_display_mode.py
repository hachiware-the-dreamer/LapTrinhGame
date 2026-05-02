import unittest

import pygame

from main import DEFAULT_SCREEN_SIZE, MIN_SCREEN_SIZE, DisplayModeState, fit_window_size_to_desktop
from scripts.screens import AudioSettings, GameSettingsScreen, MainSettingsScreen


class DisplayModeStateTest(unittest.TestCase):
    def test_remembers_windowed_size_with_minimum_clamp(self) -> None:
        state = DisplayModeState(windowed_size=DEFAULT_SCREEN_SIZE)

        state.remember_windowed_size((900, 600))

        self.assertEqual(state.windowed_size, MIN_SCREEN_SIZE)

    def test_remembered_size_can_shrink_below_minimum_to_fit_small_desktop(self) -> None:
        state = DisplayModeState(windowed_size=DEFAULT_SCREEN_SIZE, desktop_size=(1000, 650))

        state.remember_windowed_size(DEFAULT_SCREEN_SIZE)

        self.assertLessEqual(state.windowed_size[0], 1000)
        self.assertLessEqual(state.windowed_size[1], 650)

    def test_os_resize_preserves_reported_size_without_refitting(self) -> None:
        state = DisplayModeState(windowed_size=DEFAULT_SCREEN_SIZE, desktop_size=(1366, 768))

        state.remember_os_windowed_size((1366, 768))

        self.assertEqual(state.windowed_size, (1366, 768))

    def test_restore_down_size_is_not_forced_to_aspect_ratio(self) -> None:
        state = DisplayModeState(windowed_size=DEFAULT_SCREEN_SIZE, desktop_size=(1920, 1080))

        state.remember_os_windowed_size((1200, 800))

        self.assertEqual(state.windowed_size, (1200, 800))


class WindowSizingTest(unittest.TestCase):
    def test_large_desktop_uses_default_window_size(self) -> None:
        self.assertEqual(fit_window_size_to_desktop((2560, 1440)), DEFAULT_SCREEN_SIZE)

    def test_smaller_desktop_scales_window_down_to_fit(self) -> None:
        size = fit_window_size_to_desktop((1366, 768))

        self.assertLess(size[0], DEFAULT_SCREEN_SIZE[0])
        self.assertLess(size[1], DEFAULT_SCREEN_SIZE[1])
        self.assertLessEqual(size[0], 1366)
        self.assertLessEqual(size[1], 768)

    def test_tiny_desktop_does_not_force_minimum_size(self) -> None:
        size = fit_window_size_to_desktop((1000, 650))

        self.assertLess(size[0], MIN_SCREEN_SIZE[0])
        self.assertLess(size[1], MIN_SCREEN_SIZE[1])
        self.assertLessEqual(size[0], 1000)
        self.assertLessEqual(size[1], 650)

    def test_fitted_window_keeps_sixteen_by_nine_aspect_ratio(self) -> None:
        width, height = fit_window_size_to_desktop((1366, 768))

        self.assertAlmostEqual(width / height, 16 / 9, delta=0.02)


class MainSettingsDisplayModeTest(unittest.TestCase):
    def test_clicking_fullscreen_requests_immediate_display_mode_change(self) -> None:
        screen = pygame.Surface(DEFAULT_SCREEN_SIZE)
        settings_screen = MainSettingsScreen(object(), AudioSettings())
        fullscreen_rect = settings_screen._display_mode_rects(screen.get_rect())["fullscreen"]
        click = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": fullscreen_rect.center},
        )

        result = settings_screen.handle_events([click], screen, now_ms=0)

        self.assertEqual(result.display_mode, "fullscreen")
        self.assertIsNone(result.next_screen)

    def test_display_mode_row_does_not_overlap_audio_sliders_at_minimum_size(self) -> None:
        screen_rect = pygame.Rect((0, 0), MIN_SCREEN_SIZE)
        slider_rects = MainSettingsScreen._slider_rects(screen_rect)
        display_rects = MainSettingsScreen._display_mode_rects(screen_rect)

        display_label_top = display_rects["windowed"].y - 54

        self.assertLessEqual(slider_rects["sfx"].bottom + 8, display_label_top)


class GameSettingsLayoutTest(unittest.TestCase):
    def test_two_player_reverse_row_does_not_overlap_bottom_buttons_at_minimum_size(self) -> None:
        screen_rect = pygame.Rect((0, 0), MIN_SCREEN_SIZE)
        behavior_rects = GameSettingsScreen._get_two_player_behavior_rects(
            screen_rect,
            show_rule_8_timer=True,
        )
        bottom_rects = GameSettingsScreen._get_bottom_button_rects(screen_rect)

        lowest_behavior_bottom = max(rect.bottom for rect in behavior_rects.values())
        highest_bottom_button_top = min(rect.top for rect in bottom_rects.values())

        self.assertLessEqual(lowest_behavior_bottom + 8, highest_bottom_button_top)


if __name__ == "__main__":
    unittest.main()
