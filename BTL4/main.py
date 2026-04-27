import pygame

from scripts.assets import asset_path
from scripts.screens import AudioSettings, TitleScreen
from scripts.sprites import CardSpriteAtlas

DEFAULT_SCREEN_SIZE = (1920, 1080)
MIN_SCREEN_SIZE = (1100, 720)


def main() -> None:
    pygame.init()
    try:
        pygame.mixer.init()
        mixer_ready = True
    except pygame.error:
        mixer_ready = False
    pygame.display.set_caption("UNO tay`")
    screen = pygame.display.set_mode(DEFAULT_SCREEN_SIZE, pygame.RESIZABLE)
    clock = pygame.time.Clock()

    atlas_path = asset_path("sprites", "PC _ Computer - UNO - Cards - Cards (Classic).png")
    atlas = CardSpriteAtlas(atlas_path)
    audio_settings = AudioSettings()
    bgm_loaded = False
    if mixer_ready:
        bgm_path = asset_path("bgm", "domixi tay bac.mp3")
        if bgm_path.exists():
            try:
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(audio_settings.music_mix())
                bgm_loaded = True
            except pygame.error:
                bgm_loaded = False

    current_screen = TitleScreen(atlas, audio_settings)
    bgm_playing = False

    running = True
    while running:
        now = pygame.time.get_ticks()
        if bgm_loaded:
            pygame.mixer.music.set_volume(audio_settings.music_mix())

        if bgm_loaded and current_screen.wants_bgm:
            if not bgm_playing:
                pygame.mixer.music.play(-1)
                bgm_playing = True
        elif bgm_playing:
            pygame.mixer.music.stop()
            bgm_playing = False

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                new_size = (
                    max(MIN_SCREEN_SIZE[0], event.w),
                    max(MIN_SCREEN_SIZE[1], event.h),
                )
                screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)

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
