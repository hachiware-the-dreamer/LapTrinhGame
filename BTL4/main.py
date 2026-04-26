from pathlib import Path

import pygame

from scripts.screens import TitleScreen
from scripts.sprites import CardSpriteAtlas


def main() -> None:
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("UNO tay`")
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()

    # Asset loading
    atlas = CardSpriteAtlas(
        Path("assets") / "sprites" / "PC _ Computer - UNO - Cards - Cards (Classic).png"
    )
    bgm_path = Path("assets") / "bgm" / "domixi tay bac.mp3"
    pygame.mixer.music.load(str(bgm_path))
    pygame.mixer.music.set_volume(0.3)

    current_screen = TitleScreen(atlas)
    bgm_playing = False

    running = True
    while running:
        now = pygame.time.get_ticks()

        if current_screen.wants_bgm:
            if not bgm_playing:
                pygame.mixer.music.play(-1)
                bgm_playing = True
        elif bgm_playing:
            pygame.mixer.music.stop()
            bgm_playing = False

        events = pygame.event.get()
        result = current_screen.handle_events(events, screen, now)
        if not result.running:
            running = False
            continue
        if result.next_screen is not None:
            current_screen = result.next_screen

        next_screen = current_screen.update(screen, now)
        if next_screen is not None:
            current_screen = next_screen

        current_screen.draw(screen, now)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
